# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

import time
# import re
from datetime import date, datetime
from odoo import models, fields, api, tools
from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo.tools.translate import _
from odoo.modules import get_module_resource
# from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import except_orm, UserError, AccessError
from odoo.exceptions import ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
# from dateutil.relativedelta import relativedelta
from .import school



_INTERVALS = {
    'hours': lambda interval: relativedelta(hours=interval),
    'days': lambda interval: relativedelta(days=interval),
    'weeks': lambda interval: relativedelta(days=7*interval),
    'months': lambda interval: relativedelta(months=interval),
    'now': lambda interval: relativedelta(hours=0),
}


class CertificateExpireMailScheduler(models.Model):
    """ Event automated mailing. This model replaces all existing fields and
    configuration allowing to send emails on events since Odoo 9. A cron exists
    that periodically checks for mailing to run. """
    _name = 'expire.mail'

    expire_id = fields.Many2one('certificate.audit.last', string='Certificate Audit', required=True, ondelete='cascade')
    sequence = fields.Integer('Display order')
    interval_nbr = fields.Integer('Interval', default=1)
    interval_unit = fields.Selection([
        ('now', 'Immediately'),
        ('hours', 'Hour(s)'), ('days', 'Day(s)'),
        ('weeks', 'Week(s)'), ('months', 'Month(s)')],
        string='Unit', default='hours', required=True)
    interval_type = fields.Selection([
        ('after_sub', 'After each registration'),
        ('before_event', 'Before the Expire '),
        ('after_event', 'After the Expire')],
        string='When to Run ', default="before_event", required=True)
    template_id = fields.Many2one(
        'mail.template', string='Email to Send',
        domain=[('model', '=', 'expire.registration')], required=True, ondelete='restrict',
        help='This field contains the template of the mail that will be automatically sent')
    scheduled_date = fields.Datetime('Scheduled Sent Mail', compute='_compute_scheduled_date', store=True)
    mail_registration_ids = fields.One2many('expire.mail.registration','scheduler_id')
    mail_sent = fields.Boolean('Mail Sent on Expire')
    certified = fields.Boolean('Sent', compute='_compute_done', store=True)

    @api.one
    @api.depends('mail_sent', 'interval_type', 'expire_id.registration_ids', 'mail_registration_ids')
    def _compute_done(self):
        if self.interval_type in ['before_event', 'after_event']:
            self.certified = self.mail_sent
        else:
            self.certified = len(self.mail_registration_ids) == len(self.expire_id.registration_ids) and all(line.mail_sent for line in self.mail_registration_ids)

    @api.one
    @api.depends('expire_id.date_begin', 'interval_type', 'interval_unit', 'interval_nbr')
    def _compute_scheduled_date(self):
        if self.expire_id.state not in ['certified']:
            self.scheduled_date = False
        else:
            if self.interval_type == 'after_sub':
                date, sign = self.expire_id.create_date, 1
            elif self.interval_type == 'before_event':
                date, sign = self.expire_id.date_begin, -1
            else:
                date, sign = self.expire_id.date_expire, 1

            self.scheduled_date = datetime.strptime(date, tools.DEFAULT_SERVER_DATETIME_FORMAT) + _INTERVALS[self.interval_unit](sign * self.interval_nbr)

    @api.one
    def execute(self):
        if self.interval_type == 'after_sub':
            # update registration lines
            lines = []
            reg_ids = [mail_reg.registration_id for mail_reg in self.mail_registration_ids]
            for registration in filter(lambda item: item not in reg_ids, self.expire_id.registration_ids):
                lines.append((0, 0, {'registration_id': registration.id}))
            if lines:
                self.write({'mail_registration_ids': lines})
            # execute scheduler on registrations
            self.mail_registration_ids.filtered(lambda reg: reg.scheduled_date and reg.scheduled_date <= datetime.strftime(fields.datetime.now(), tools.DEFAULT_SERVER_DATETIME_FORMAT)).execute()
        else:
            if not self.mail_sent:
                self.expire_id.mail_attendees(self.template_id.id)
                self.write({'mail_sent': True})
        return True

    @api.model
    def run(self, autocommit=False):
        schedulers = self.search([('certified', '=', False), ('scheduled_date', '<=', datetime.strftime(fields.datetime.now(), tools.DEFAULT_SERVER_DATETIME_FORMAT))])
        for scheduler in schedulers:
            scheduler.execute()
            if autocommit:
                self.env.cr.commit()
        return True

class CertificateExpireMailRegistration(models.Model):
    _name = 'expire.mail.registration'
    _description = 'Registration Mail Scheduler'
    _rec_name = 'scheduler_id'
    _order = 'scheduled_date DESC'

    scheduler_id = fields.Many2one('expire.mail', 'Mail Scheduler', required=True, ondelete='cascade')
    registration_id = fields.Many2one('certificate.audit.last', 'Certified', required=True, ondelete='cascade')
    scheduled_date = fields.Datetime(String='Scheduled Time',related='registration_id.date_begin')
    mail_sent = fields.Boolean('Mail Sent')

    @api.one
    def execute(self):
        if self.registration_id.state in ['certified'] and not self.mail_sent:
            self.scheduler_id.template_id.send_mail(self.registration_id.id)
            self.write({'mail_sent': True})

    @api.one
    @api.depends('registration_id', 'scheduler_id.interval_unit', 'scheduler_id.interval_type')
    def _compute_scheduled_date(self, _INTERVALS=None):
        if self.registration_id:
            date_starts = self.registration_id.date_begin
            date_open_datetime = date_starts and datetime.strptime(date_starts, tools.DEFAULT_SERVER_DATETIME_FORMAT) or fields.datetime.now()
            self.scheduled_date = date_open_datetime + _INTERVALS[self.scheduler_id.interval_unit](self.scheduler_id.interval_nbr)
        else:
            self.scheduled_date = False
