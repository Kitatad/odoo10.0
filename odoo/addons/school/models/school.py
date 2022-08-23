# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

# import time
import re
import calendar
from datetime import datetime
from odoo import models, fields, api, tools
from odoo.tools.translate import _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, \
    DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import except_orm, UserError, AccessError
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta


EM = (r"[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$")


def emailvalidation(email):

    if email:
        EMAIL_REGEX = re.compile(EM)
        if not EMAIL_REGEX.match(email):
            raise ValidationError(_('''This seems not to be valid email.
            Please enter email in correct format!'''))
        else:
            return True


class CertificateName(models.Model):
    ''' Defines an academic year '''
    _name = "certificate.type"
    _description = "Certificate Type"
    _order = "name"

    name = fields.Char(String='Certificate Type')
    name_seque = fields.Char(string='Order Reference', required=True, copy=False, readonly=True,index=True, default=lambda self: _('New'))

    @api.model
    def create(self, vals):
        vals['name_seque'] = self.env['ir.sequence'].next_by_code('certificate.type.seq') or _('New')
        result = super(CertificateName, self).create(vals)
        return result

class CertificateRequest(models.Model):
        ''' Defines an academic year '''
        _name = "certificate.request"
        _inherit = ['mail.thread', 'ir.needaction_mixin']
        _description = "Certificate Request"
        _order = "request_seque"

        partner_id = fields.Many2one('res.partner', 'Farm Name')
        farm_id = fields.Char(String='Farm Name')
        request_seque = fields.Char(string='Order Reference', required=True, copy=False, readonly=True, index=True,
                                 default=lambda self: _('New'))
        certificatetype_id = fields.Many2one('certificate.type','Code Audit Request Type',required=True)
        certificate_name = fields.Char(related='certificatetype_id.name',String='Certificate Type',required=True,)
        contact_person = fields.Char(String='Contact Person',required=True)
        request_date = fields.Date(String='Request Date',required=True, readonly=True, index=True, copy=False, default=fields.Datetime.now)
        position = fields.Char(String='Position')
        Phone_number = fields.Char(String='Phone number')
        comp_email = fields.Char(String='Email',required=True)
        request_farm = fields.Char(String='Request Farm')
        school_id = fields.Many2one('school.school', 'School')

        @api.model
        def create(self, vals):
            vals['request_seque'] = self.env['ir.sequence'].next_by_code('certificate.request.seq') or _('New')
            result = super(CertificateRequest,self).create(vals)
            return result

        @api.multi
        def name_get(self):
            res = []
            for field in self:
                res.append((field.id, '%s %s' % (field.request_seque, field.certificate_name)))
            return res


    # class TemesgenForGod(models.Model):
#     _name = 'family.my'
#     _inherit = 'res.partner'
#     _description = 'Partner'
#
#     temesgen_god = fields.Char(String='new')
# _INTERVALS = {
#     'hours': lambda interval: relativedelta(hours=interval),
#     'days': lambda interval: relativedelta(days=interval),
#     'weeks': lambda interval: relativedelta(days=7*interval),
#     'months': lambda interval: relativedelta(months=interval),
#     'now': lambda interval: relativedelta(hours=0),
# }
#

# class CertificateExpireMailScheduler(models.Model):
#     """ Event automated mailing. This model replaces all existing fields and
#     configuration allowing to send emails on events since Odoo 9. A cron exists
#     that periodically checks for mailing to run. """
#     _name = 'expire.mail'
#
#     expire_id = fields.Many2one('certificate.audit.visit', string='Certificate Audit', required=True, ondelete='cascade')
#     sequence = fields.Integer('Display order')
#     interval_nbr = fields.Integer('Interval', default=1)
#     interval_unit = fields.Selection([
#         ('now', 'Immediately'),
#         ('hours', 'Hour(s)'), ('days', 'Day(s)'),
#         ('weeks', 'Week(s)'), ('months', 'Month(s)')],
#         string='Unit', default='hours', required=True)
#     interval_type = fields.Selection([
#         ('after_sub', 'After each registration'),
#         ('before_event', 'Before the Expire '),
#         ('after_event', 'After the Expire')],
#         string='When to Run ', default="before_event", required=True)
#     # template_id = fields.Many2one(
#     #     'mail.template', string='Email to Send',
#     #     domain=[('model', '=', 'event.registration')], required=True, ondelete='restrict',
#     #     help='This field contains the template of the mail that will be automatically sent')
#     scheduled_date = fields.Datetime('Scheduled Sent Mail', compute='_compute_scheduled_date', store=True)
#     # mail_registration_ids = fields.One2many('expire.mail.registration', 'scheduler_id')
#     mail_sent = fields.Boolean('Mail Sent on Event')
#     done = fields.Boolean('Sent', compute='_compute_done', store=True)
#
#     @api.one
#     @api.depends('mail_sent', 'interval_type', 'expire_id.registration_ids', 'mail_registration_ids')
#     def _compute_done(self):
#         if self.interval_type in ['before_event', 'after_event']:
#             self.done = self.mail_sent
#         else:
#             self.done = len(self.mail_registration_ids) == len(self.expire_id.registration_ids) and all(line.mail_sent for line in self.mail_registration_ids)
#
#     @api.one
#     @api.depends('expire_id.state', 'expire_id.date_begin', 'interval_type', 'interval_unit', 'interval_nbr')
#     def _compute_scheduled_date(self):
#         if self.expire_id.state not in ['confirm', 'done']:
#             self.scheduled_date = False
#         else:
#             if self.interval_type == 'after_sub':
#                 date, sign = self.expire_id.create_date, 1
#             elif self.interval_type == 'before_event':
#                 date, sign = self.expire_id.date_begin, -1
#             else:
#                 date, sign = self.expire_id.date_end, 1
#
#             self.scheduled_date = datetime.strptime(date, tools.DEFAULT_SERVER_DATETIME_FORMAT) + _INTERVALS[self.interval_unit](sign * self.interval_nbr)
#
#     @api.one
#     def execute(self):
#         if self.interval_type == 'after_sub':
#             # update registration lines
#             lines = []
#             reg_ids = [mail_reg.registration_id for mail_reg in self.mail_registration_ids]
#             for registration in filter(lambda item: item not in reg_ids, self.expire_id.registration_ids):
#                 lines.append((0, 0, {'registration_id': registration.id}))
#             if lines:
#                 self.write({'mail_registration_ids': lines})
#             # execute scheduler on registrations
#             self.mail_registration_ids.filtered(lambda reg: reg.scheduled_date and reg.scheduled_date <= datetime.strftime(fields.datetime.now(), tools.DEFAULT_SERVER_DATETIME_FORMAT)).execute()
#         else:
#             if not self.mail_sent:
#                 self.expire_id.mail_attendees(self.template_id.id)
#                 self.write({'mail_sent': True})
#         return True
#
#     @api.model
#     def run(self, autocommit=False):
#         schedulers = self.search([('done', '=', False), ('scheduled_date', '<=', datetime.strftime(fields.datetime.now(), tools.DEFAULT_SERVER_DATETIME_FORMAT))])
#         for scheduler in schedulers:
#             scheduler.execute()
#             if autocommit:
#                 self.env.cr.commit()
#         return True
#

# class CertificateExpireMailRegistration(models.Model):
#     _name = 'expire.mail.registration'
#     _description = 'Registration Mail Scheduler'
#     _rec_name = 'scheduler_id'
#     _order = 'scheduled_date DESC'
#
#     scheduler_id = fields.Many2one('expire.mail', 'Mail Scheduler', required=True, ondelete='cascade')
#     registration_id = fields.Many2one('expire.registration', 'Certified', required=True, ondelete='cascade')
#     scheduled_date = fields.Datetime('Scheduled Time', compute='_compute_scheduled_date', store=True)
#     mail_sent = fields.Boolean('Mail Sent')
#
#     @api.one
#     def execute(self):
#         if self.registration_id.state in ['open', 'done'] and not self.mail_sent:
#             self.scheduler_id.template_id.send_mail(self.registration_id.id)
#             self.write({'mail_sent': True})
#
#     @api.one
#     @api.depends('registration_id', 'scheduler_id.interval_unit', 'scheduler_id.interval_type')
#     def _compute_scheduled_date(self):
#         if self.registration_id:
#             date_open = self.registration_id.date_open
#             date_open_datetime = date_open and datetime.strptime(date_open, tools.DEFAULT_SERVER_DATETIME_FORMAT) or fields.datetime.now()
#             self.scheduled_date = date_open_datetime + _INTERVALS[self.scheduler_id.interval_unit](self.scheduler_id.interval_nbr)
#         else:
#             self.scheduled_date = False


# class CertificateExpireDateRegistration(models.Model):
#     _name = 'expire.registration'
#     _description = 'Certified'
#     _inherit = ['mail.thread', 'ir.needaction_mixin']
#     _order = 'name, create_date desc'
#
#     origin = fields.Char(
#         string='Source Document', readonly=True,
#         help="Reference of the document that created the registration, for example a sale order")
#     expire_id = fields.Many2one(
#         'certificate.audit.visit', string='Certificate Audit', required=True,
#         readonly=True, states={'draft': [('readonly', False)]})
#     partner_id = fields.Many2one(
#         'res.partner', string='Contact',
#         states={'done': [('readonly', True)]})
#     date_open = fields.Datetime(string='Registration Date', readonly=True, default=lambda self: fields.datetime.now())  # weird crash is directly now
#     date_closed = fields.Datetime(string='Expire Date', readonly=True)
#     event_begin_date = fields.Datetime(string="Certificate Awared Date", related='expire_id.date_begin', readonly=True)
#     event_end_date = fields.Datetime(string="Certificate Expire Date", related='expire_id.date_end', readonly=True)
#     company_id = fields.Many2one(
#         'res.company', string='Company', related='expire_id.company_id',
#         store=True, readonly=True, states={'draft': [('readonly', False)]})
#     state = fields.Selection([
#         ('draft', 'Unconfirmed'), ('cancel', 'Cancelled'),
#         ('open', 'Confirmed'), ('done', 'Attended')],
#         string='Status', default='draft', readonly=True, copy=False, track_visibility='onchange')
#     email = fields.Char(string='Email')
#     phone = fields.Char(string='Phone')
#     name = fields.Char(string='Attendee Name', index=True)
#     company_name = fields.Char(String='Company Name')
#
#     @api.multi
#     def _check_auto_confirmation(self):
#         if self._context.get('registration_force_draft'):
#             return False
#         if any(registration.expire_id.state != 'confirm' or
#                not registration.expire_id.auto_confirm or
#                (not registration.expire_id.seats_available and registration.expire_id.seats_availability == 'limited') for registration in self):
#             return False
#         return True
#
#     @api.model
#     def create(self, vals):
#         registration = super(CertificateExpireDateRegistration, self).create(vals)
#         if registration._check_auto_confirmation():
#             registration.sudo().confirm_registration()
#         return registration
#
#     @api.model
#     def _prepare_attendee_values(self, registration):
#         """ Method preparing the values to create new attendees based on a
#         sale order line. It takes some registration data (dict-based) that are
#         optional values coming from an external input like a web page. This method
#         is meant to be inherited in various addons that sell events. """
#         partner_id = registration.pop('partner_id', self.env.user.partner_id)
#         expire_id = registration.pop('expire_id', False)
#         data = {
#             'name': registration.get('name', partner_id.name),
#             'phone': registration.get('phone', partner_id.phone),
#             'email': registration.get('email', partner_id.email),
#             'company_name': registration.get('company_name', partner_id.company_name),
#             'partner_id': partner_id.id,
#             'expire_id': expire_id and expire_id.id or False,
#         }
#         data.update({key: registration[key] for key in registration.keys() if key in self._fields})
#         return data
#
#     @api.one
#     def do_draft(self):
#         self.state = 'draft'
#
#     @api.one
#     def confirm_registration(self):
#         self.state = 'open'
#
#         # auto-trigger after_sub (on subscribe) mail schedulers, if needed
#         onsubscribe_schedulers = self.expire_id.expire_mail_ids.filtered(
#             lambda s: s.interval_type == 'after_sub')
#         onsubscribe_schedulers.execute()
#
#     @api.one
#     def button_reg_close(self):
#         """ Close Registration """
#         today = fields.Datetime.now()
#         if self.expire_id.date_begin <= today:
#             self.write({'state': 'done', 'date_closed': today})
#         else:
#             raise UserError(_("You must wait for the starting day of the event to do this action."))
#
#     @api.one
#     def button_reg_cancel(self):
#         self.state = 'cancel'
#
#     @api.onchange('partner_id')
#     def _onchange_partner(self):
#         if self.partner_id:
#             contact_id = self.partner_id.address_get().get('contact', False)
#             if contact_id:
#                 contact = self.env['res.partner'].browse(contact_id)
#                 self.name = contact.name or self.name
#                 self.email = contact.email or self.email
#                 self.phone = contact.phone or self.phone
#                 self.company_name = contact.company_name or self.company_name
#
#     @api.multi
#     def message_get_suggested_recipients(self):
#         recipients = super(CertificateExpireDateRegistration, self).message_get_suggested_recipients()
#         public_users = self.env['res.users'].sudo()
#         public_groups = self.env.ref("base.group_public", raise_if_not_found=False)
#         if public_groups:
#             public_users = public_groups.sudo().with_context(active_test=False).mapped("users")
#         try:
#             for attendee in self:
#                 is_public = attendee.sudo().with_context(active_test=False).partner_id.user_ids in public_users if public_users else False
#                 if attendee.partner_id and not is_public:
#                     attendee._message_add_suggested_recipient(recipients, partner=attendee.partner_id, reason=_('Customer'))
#                 elif attendee.email:
#                     attendee._message_add_suggested_recipient(recipients, email=attendee.email, reason=_('Customer Email'))
#         except AccessError:     # no read access rights -> ignore suggested recipients
#             pass
#         return recipients
#
#     @api.multi
#     def action_send_badge_email(self):
#         """ Open a window to compose an email, with the template - 'event_badge'
#             message loaded by default
#         """
#         self.ensure_one()
#         template = self.env.ref('event.event_registration_mail_template_badge')
#         compose_form = self.env.ref('mail.email_compose_message_wizard_form')
#         ctx = dict(
#             default_model='event.registration',
#             default_res_id=self.id,
#             default_use_template=bool(template),
#             default_template_id=template.id,
#             default_composition_mode='comment',
#         )
#         return {
#             'name': _('Compose Email'),
#             'type': 'ir.actions.act_window',
#             'view_type': 'form',
#             'view_mode': 'form',
#             'res_model': 'mail.compose.message',
#             'views': [(compose_form.id, 'form')],
#             'view_id': compose_form.id,
#             'target': 'new',
#             'context': ctx,
#         }

#     @api.multi
#     def get_date_range_str(self):
#         self.ensure_one()
#         today = fields.Datetime.from_string(fields.Datetime.now())
#         event_date = fields.Datetime.from_string(self.event_begin_date)
#         diff = (event_date.date() - today.date())
#         if diff.days == 0:
#             return _('Today')
#         elif diff.days == 1:
#             return _('Tomorrow')
#         elif event_date.isocalendar()[1] == today.isocalendar()[1]:
#             return _('This week')
#         elif today.month == event_date.month:
#             return _('This month')
#         elif event_date.month == (today + relativedelta(months=+1)):
#             return _('Next month')
#         else:
#             return format_tz(self.env, self.event_begin_date, tz='UTC', format='%Y%m%dT%H%M%SZ')
#
class AcademicYear(models.Model):
    ''' Defines an academic year '''
    _name = "academic.year"
    _description = "Academic Year"
    _order = "sequence"

    sequence = fields.Integer('Sequence', required=True,
                              help="Sequence order you want to see this year.")
    name = fields.Char('Name', required=True, help='Name of academic year')
    code = fields.Char('Code', required=True, help='Code of academic year')
    date_start = fields.Date('Start Date', required=True,
                             help='Starting date of academic year')
    date_stop = fields.Date('End Date', required=True,
                            help='Ending of academic year')
    month_ids = fields.One2many('academic.month', 'year_id', 'Months',
                                help="related Academic months")
    grade_id = fields.Many2one('grade.master', "Grade")
    current = fields.Boolean('Current', help="Set Active Current Year")
    description = fields.Text('Description')

    @api.model
    def next_year(self, sequence):
        '''This method assign sequence to years'''
        year_id = self.search([('sequence', '>', sequence)], order='id',
                              limit=1)
        if year_id:
            return year_id.id
        return False

    @api.multi
    def name_get(self):
        '''Method to display name and code'''
        return [(rec.id, ' [' + rec.code + ']' + rec.name) for rec in self]

    @api.multi
    def generate_academicmonth(self):
        interval = 1
        month_obj = self.env['academic.month']
        for data in self:
            ds = datetime.strptime(data.date_start, '%Y-%m-%d')
            while ds.strftime('%Y-%m-%d') < data.date_stop:
                de = ds + relativedelta(months=interval, days=-1)
                if de.strftime('%Y-%m-%d') > data.date_stop:
                    de = datetime.strptime(data.date_stop, '%Y-%m-%d')
                month_obj.create({
                    'name': ds.strftime('%B'),
                    'code': ds.strftime('%m/%Y'),
                    'date_start': ds.strftime('%Y-%m-%d'),
                    'date_stop': de.strftime('%Y-%m-%d'),
                    'year_id': data.id,
                })
                ds = ds + relativedelta(months=interval)
        return True

    @api.constrains('date_start', 'date_stop')
    def _check_academic_year(self):
        '''Method to check start date should be greater than end date
           also check that dates are not overlapped with existing academic
           year'''
        new_start_date = datetime.strptime(self.date_start, '%Y-%m-%d')
        new_stop_date = datetime.strptime(self.date_stop, '%Y-%m-%d')
        delta = new_stop_date - new_start_date
        if delta.days > 365 and not calendar.isleap(new_start_date.year):
            raise ValidationError(_('''Error! The duration of the academic year
                                      is invalid.'''))
        if (self.date_stop and self.date_start and
                self.date_stop < self.date_start):
            raise ValidationError(_('''The start date of the academic year'
                                      should be less than end date.'''))
        for old_ac in self.search([('id', 'not in', self.ids)]):
            # Check start date should be less than stop date
            if (old_ac.date_start <= self.date_start <= old_ac.date_stop or
                    old_ac.date_start <= self.date_stop <= old_ac.date_stop):
                raise ValidationError(_('''Error! You cannot define overlapping
                                          academic years.'''))
        return True

    @api.constrains('current')
    def check_current_year(self):
        check_year = self.search([('current', '=', True)])
        if len(check_year.ids) >= 2:
            raise ValidationError(_('''Error! You cannot set two current
            year active!'''))


class AcademicMonth(models.Model):
    ''' Defining a month of an academic year '''
    _name = "academic.month"
    _description = "Academic Month"
    _order = "date_start"

    name = fields.Char('Name', required=True, help='Name of Academic month')
    code = fields.Char('Code', required=True, help='Code of Academic month')
    date_start = fields.Date('Start of Period', required=True,
                             help='Starting of academic month')
    date_stop = fields.Date('End of Period', required=True,
                            help='Ending of academic month')
    year_id = fields.Many2one('academic.year', 'Academic Year', required=True,
                              help="Related academic year ")
    description = fields.Text('Description')

    _sql_constraints = [
        ('month_unique', 'unique(date_start, date_stop, year_id)',
         'Academic Month should be unique!'),
    ]

    @api.constrains('date_start', 'date_stop')
    def _check_duration(self):
        '''Method to check duration of date'''
        if (self.date_stop and self.date_start and
                self.date_stop < self.date_start):
            raise ValidationError(_(''' End of Period date should be greater
                                    than Start of Peroid Date!'''))

    @api.constrains('year_id', 'date_start', 'date_stop')
    def _check_year_limit(self):
        '''Method to check year limit'''
        if self.year_id and self.date_start and self.date_stop:
            if (self.year_id.date_stop < self.date_stop or
                    self.year_id.date_stop < self.date_start or
                    self.year_id.date_start > self.date_start or
                    self.year_id.date_start > self.date_stop):
                raise ValidationError(_('''Invalid Months ! Some months overlap
                                    or the date period is not in the scope
                                    of the academic year!'''))

    @api.constrains('date_start', 'date_stop')
    def check_months(self):
        for old_month in self.search([('id', 'not in', self.ids)]):
            # Check start date should be less than stop date
            if old_month.date_start <= \
                    self.date_start <= old_month.date_stop \
                    or old_month.date_start <= \
                    self.date_stop <= old_month.date_stop:
                    raise ValidationError(_('''Error! You cannot define
                    overlapping months!'''))


class StandardMedium(models.Model):
    ''' Defining a medium(ENGLISH, HINDI, GUJARATI) related to standard'''
    _name = "standard.medium"
    _description = "Standard Medium"
    _order = "sequence"

    sequence = fields.Integer('Sequence', required=True)
    name = fields.Char('Name', required=True)
    code = fields.Char('Code', required=True)
    description = fields.Text('Description')


class StandardDivision(models.Model):
    ''' Defining a division(A, B, C) related to standard'''
    _name = "standard.division"
    _description = "Standard Division"
    _order = "sequence"

    sequence = fields.Integer('Sequence', required=True)
    name = fields.Char('Name', required=True)
    code = fields.Char('Code', required=True)
    description = fields.Text('Description')


class StandardStandard(models.Model):
    ''' Defining Standard Information '''
    _name = 'standard.standard'
    _description = 'Standard Information'
    _order = "sequence"

    sequence = fields.Integer('Sequence', required=True)
    name = fields.Char('Name', required=True)
    code = fields.Char('Code', required=True)
    description = fields.Text('Description')

    @api.model
    def next_standard(self, sequence):
        '''This method check sequence of standard'''
        stand_ids = self.search([('sequence', '>', sequence)], order='id',
                                limit=1)
        if stand_ids:
            return stand_ids.id
        return False


class SchoolStandard(models.Model):
    ''' Defining a standard related to school '''
    _name = 'school.standard'
    _description = 'School Standards'
    _rec_name = "standard_id"

    @api.multi
    @api.depends('standard_id', 'school_id', 'division_id', 'medium_id',
                 'school_id')
    def _compute_student(self):
        '''Compute student of done state'''
        student_obj = self.env['student.student']
        for rec in self:
            domain = [('standard_id', '=', rec.id),
                      ('school_id', '=', rec.school_id.id),
                      ('division_id', '=', rec.division_id.id),
                      ('medium_id', '=', rec.medium_id.id),
                      ('state', '=', 'done')]
            rec.student_ids = student_obj.search(domain)

    @api.onchange('standard_id', 'division_id')
    def onchange_combine(self):
        self.name = str(self.standard_id.name
                        ) + '-' + str(self.division_id.name)

    @api.multi
    @api.depends('subject_ids')
    def _compute_subject(self):
        '''Method to compute subjects'''
        for rec in self:
            rec.total_no_subjects = len(rec.subject_ids)

    @api.multi
    @api.depends('student_ids')
    def _compute_total_student(self):
        for rec in self:
            rec.total_students = len(rec.student_ids)

    @api.depends("capacity", "total_students")
    def _compute_remain_seats(self):
        for rec in self:
            rec.remaining_seats = rec.capacity - rec.total_students

    school_id = fields.Many2one('school.school', 'School', required=True)
    standard_id = fields.Many2one('standard.standard', 'Standard',
                                  required=True)
    division_id = fields.Many2one('standard.division', 'Division',
                                  required=True)
    medium_id = fields.Many2one('standard.medium', 'Medium', required=True)
    subject_ids = fields.Many2many('subject.subject', 'subject_standards_rel',
                                   'subject_id', 'standard_id', 'Subject')
    user_id = fields.Many2one('school.teacher', 'Class Teacher')
    student_ids = fields.One2many('student.student', 'standard_id',
                                  'Student In Class',
                                  compute='_compute_student', store=True
                                  )
    color = fields.Integer('Color Index')
    cmp_id = fields.Many2one('res.company', 'Company Name',
                             related='school_id.company_id', store=True)
    syllabus_ids = fields.One2many('subject.syllabus', 'standard_id',
                                   'Syllabus')
    total_no_subjects = fields.Integer('Total No of Subject',
                                       compute="_compute_subject")
    name = fields.Char('Name')
    capacity = fields.Integer("Total Seats")
    total_students = fields.Integer("Total Students",
                                    compute="_compute_total_student",
                                    store=True)
    remaining_seats = fields.Integer("Available Seats",
                                     compute="_compute_remain_seats",
                                     store=True)
    class_room_id = fields.Many2one('class.room', 'Room Number')

    @api.constrains('standard_id', 'division_id')
    def check_standard_unique(self):
        standard_search = self.env['school.standard'
                                   ].search([('standard_id', '=',
                                              self.standard_id.id),
                                             ('division_id', '=',
                                              self.division_id.id),
                                             ('school_id', '=',
                                              self.school_id.id),
                                             ('id', 'not in', self.ids)])
        if standard_search:
            raise ValidationError(_('''Division and class should be unique!'''
                                    ))

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.student_ids or rec.subject_ids or rec.syllabus_ids:
                raise ValidationError(_('''You cannot delete this standard
                because it has reference with student or subject or
                syllabus!'''))
        return super(SchoolStandard, self).unlink()

    @api.constrains('capacity')
    def check_seats(self):
        if self.capacity <= 0:
            raise ValidationError(_('''Total seats should be greater than
                0!'''))

    @api.multi
    def name_get(self):
        '''Method to display standard and division'''
        return [(rec.id, rec.standard_id.name + '[' + rec.division_id.name +
                 ']') for rec in self]


class SchoolSchool(models.Model):
    ''' Defining School Information '''
    _name = 'school.school'
    _inherits = {'res.company': 'company_id'}
    _description = 'School Information'
    _rec_name = "com_name"

    @api.model
    def _lang_get(self):
        '''Method to get language'''
        languages = self.env['res.lang'].search([])
        return [(language.code, language.name) for language in languages]

    company_id = fields.Many2one('res.company', 'Company',
                                 ondelete="cascade",
                                 required=True)
    com_name = fields.Char('School Name', related='company_id.name',
                           store=True)
    code = fields.Char('Code', required=True)
    standards = fields.One2many('school.standard', 'school_id',
                                'Standards')
    lang = fields.Selection(_lang_get, 'Language',
                            help='''If the selected language is loaded in the
                                system, all documents related to this partner
                                will be printed in this language.
                                If not, it will be English.''')


class SubjectSubject(models.Model):
    '''Defining a subject '''
    _name = "subject.subject"
    _description = "Subjects"

    name = fields.Char('Name', required=True)
    code = fields.Char('Code', required=True)
    maximum_marks = fields.Integer("Maximum marks")
    minimum_marks = fields.Integer("Minimum marks")
    weightage = fields.Integer("WeightAge")
    teacher_ids = fields.Many2many('school.teacher', 'subject_teacher_rel',
                                   'subject_id', 'teacher_id', 'Teachers')
#    standard_ids = fields.Many2many('standard.standard',
#                                    'subject_standards_rel',
#                                    'standard_id', 'subject_id', 'Standards')
    standard_ids = fields.Many2many('standard.standard',
                                    string='Standards')
    standard_id = fields.Many2one('standard.standard', 'Class')
    is_practical = fields.Boolean('Is Practical',
                                  help='Check this if subject is practical.')
    elective_id = fields.Many2one('subject.elective')
    student_ids = fields.Many2many('student.student',
                                   'elective_subject_student_rel',
                                   'subject_id', 'student_id', 'Students')


class SubjectSyllabus(models.Model):
    '''Defining a  syllabus'''
    _name = "subject.syllabus"
    _description = "Syllabus"
    _rec_name = "subject_id"

    standard_id = fields.Many2one('standard.standard', 'Standard')
    subject_id = fields.Many2one('subject.subject', 'Subject')
    syllabus_doc = fields.Binary("Syllabus Doc",
                                 help="Attach syllabus related to Subject")


class SubjectElective(models.Model):
    ''' Defining Subject Elective '''
    _name = 'subject.elective'

    name = fields.Char("Name")
    subject_ids = fields.One2many('subject.subject', 'elective_id',
                                  'Elective Subjects')


class MotherTongue(models.Model):
    _name = 'mother.toungue'
    _description = "Mother Toungue"

    name = fields.Char("Mother Tongue")


class StudentAward(models.Model):
    _name = 'student.award'
    _description = "Student Awards"

    award_list_id = fields.Many2one('student.student', 'Student')
    name = fields.Char('Award Name')
    description = fields.Char('Description')


class AttendanceType(models.Model):
    _name = "attendance.type"
    _description = "School Type"

    name = fields.Char('Name', required=True)
    code = fields.Char('Code', required=True)


class StudentDocument(models.Model):
    _name = 'student.document'
    _rec_name = "doc_type"

    doc_id = fields.Many2one('student.student', 'Student')
    file_no = fields.Char('File No', readonly="1", default=lambda obj:
                          obj.env['ir.sequence'].
                          next_by_code('student.document'))
    submited_date = fields.Date('Submitted Date')
    doc_type = fields.Many2one('document.type', 'Document Type', required=True)
    file_name = fields.Char('File Name',)
    return_date = fields.Date('Return Date')
    new_datas = fields.Binary('Attachments')


class DocumentType(models.Model):
    ''' Defining a Document Type(SSC,Leaving)'''
    _name = "document.type"
    _description = "Document Type"
    _rec_name = "doc_type"
    _order = "seq_no"

    seq_no = fields.Char('Sequence', readonly=True,
                         default=lambda self: _('New'))
    doc_type = fields.Char('Document Type', required=True)

    @api.model
    def create(self, vals):
        if vals.get('seq_no', _('New')) == _('New'):
            vals['seq_no'] = self.env['ir.sequence'
                                      ].next_by_code('document.type'
                                                     ) or _('New')
        return super(DocumentType, self).create(vals)


class StudentDescription(models.Model):
    ''' Defining a Student Description'''
    _name = 'student.description'

    des_id = fields.Many2one('student.student', 'Description')
    name = fields.Char('Name')
    description = fields.Char('Description')


class StudentDescipline(models.Model):
    _name = 'student.descipline'

    student_id = fields.Many2one('student.student', 'Student')
    teacher_id = fields.Many2one('school.teacher', 'Teacher')
    date = fields.Date('Date')
    class_id = fields.Many2one('standard.standard', 'Class')
    note = fields.Text('Note')
    action_taken = fields.Text('Action Taken')


class StudentHistory(models.Model):
    _name = "student.history"

    student_id = fields.Many2one('student.student', 'Student')
    academice_year_id = fields.Many2one('academic.year', 'Academic Year',
                                        )
    standard_id = fields.Many2one('school.standard', 'Standard')
    percentage = fields.Float("Percentage", readonly=True)
    result = fields.Char('Result', readonly=True)


class StudentCertificate(models.Model):
    _name = "student.certificate"

    student_id = fields.Many2one('student.student', 'Student')
    description = fields.Char('Description')
    certi = fields.Binary('Certificate', required=True)


class StudentReference(models.Model):
    ''' Defining a student reference information '''
    _name = "student.reference"
    _description = "Student Reference"

    reference_id = fields.Many2one('student.student', 'Student')
    name = fields.Char('First Name', required=True)
    middle = fields.Char('Middle Name', required=True)
    last = fields.Char('Surname', required=True)
    designation = fields.Char('Designation', required=True)
    phone = fields.Char('Phone', required=True)
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')],
                              'Gender')


class StudentPreviousSchool(models.Model):
    ''' Defining a student previous school information '''
    _name = "student.previous.school"
    _description = "Student Previous School"

    previous_school_id = fields.Many2one('student.student', 'Student')
    name = fields.Char('Name', required=True)
    registration_no = fields.Char('Registration No.', required=True)
    admission_date = fields.Date('Admission Date')
    exit_date = fields.Date('Exit Date')
    course_id = fields.Many2one('standard.standard', 'Course', required=True)
    add_sub = fields.One2many('academic.subject', 'add_sub_id', 'Add Subjects')

    @api.constrains('admission_date', 'exit_date')
    def check_date(self):
        curr_dt = datetime.now()
        new_dt = datetime.strftime(curr_dt,
                                   DEFAULT_SERVER_DATE_FORMAT)
        if self.admission_date >= new_dt or self.exit_date >= new_dt:
            raise ValidationError(_('''Your admission date and exit date
            should be less than current date in previous school details!'''))
        if self.admission_date > self.exit_date:
            raise ValidationError(_(''' Admission date should be less than
            exit date in previous school!'''))


class AcademicSubject(models.Model):
    ''' Defining a student previous school information '''
    _name = "academic.subject"
    _description = "Student Previous School"

    add_sub_id = fields.Many2one('student.previous.school', 'Add Subjects',
                                 invisible=True)
    name = fields.Char('Name', required=True)
    maximum_marks = fields.Integer("Maximum marks")
    minimum_marks = fields.Integer("Minimum marks")


class StudentFamilyContact(models.Model):
    ''' Defining a student emergency contact information '''
    _name = "student.family.contact"
    _description = "Student Family Contact"

    @api.multi
    @api.depends('relation', 'stu_name')
    def _compute_get_name(self):
        for rec in self:
            if rec.stu_name:
                rec.relative_name = rec.stu_name.name
            else:
                rec.relative_name = rec.name

    family_contact_id = fields.Many2one('student.student', 'Student')
    exsting_student = fields.Many2one('student.student',
                                      'Student')
    rel_name = fields.Selection([('exist', 'Link to Existing Student'),
                                 ('new', 'Create New Relative Name')],
                                'Related Student', help="Select Name",
                                required=True)
    user_id = fields.Many2one('res.users', 'User ID', ondelete="cascade")
    stu_name = fields.Many2one('student.student', 'Name',
                               help="Select Student From Existing List")
    name = fields.Char('Name')
    relation = fields.Many2one('student.relation.master', 'Relation',
                               required=True)
    phone = fields.Char('Phone', required=True)
    email = fields.Char('E-Mail')
    relative_name = fields.Char(compute='_compute_get_name', string='Name')


class StudentRelationMaster(models.Model):
    ''' Student Relation Information '''
    _name = "student.relation.master"
    _description = "Student Relation Master"

    name = fields.Char('Name', required=True, help="Enter Relation name")
    seq_no = fields.Integer('Sequence')


class GradeMaster(models.Model):
    _name = 'grade.master'

    name = fields.Char('Grade', required=True)
    grade_ids = fields.One2many('grade.line', 'grade_id', 'Grade Name')


class GradeLine(models.Model):
    _name = 'grade.line'
    _rec_name = 'grade'

    from_mark = fields.Integer('From Marks', required=True,
                               help='The grade will starts from this marks.')
    to_mark = fields.Integer('To Marks', required=True,
                             help='The grade will ends to this marks.')
    grade = fields.Char('Grade', required=True, help="Grade")
    sequence = fields.Integer('Sequence', help="Sequence order of the grade.")
    fail = fields.Boolean('Fail', help='If fail field is set to True,\
                                  it will allow you to set the grade as fail.')
    grade_id = fields.Many2one("grade.master", 'Grade')
    name = fields.Char('Name')


class StudentNews(models.Model):
    _name = 'student.news'
    _description = 'Student News'
    _rec_name = 'subject'
    _order = 'date asc'

    subject = fields.Char('Subject', required=True,
                          help='Subject of the news.')
    description = fields.Text('Description', help="Description")
    date = fields.Datetime('Expiry Date', help='Expiry date of the news.')
    user_ids = fields.Many2many('res.users', 'user_news_rel', 'id', 'user_ids',
                                'User News',
                                help='Name to whom this news is related.')
    color = fields.Integer('Color Index', default=0)

    @api.constrains("date")
    def checknews_dates(self):
        curr_dt = datetime.now()
        new_date = datetime.strftime(curr_dt, DEFAULT_SERVER_DATETIME_FORMAT)
        if self.date < new_date:
            raise ValidationError(_('''Configure expiry date greater than
            current date!'''))

    @api.multi
    def news_update(self):
        '''Method to send email to student for news update'''
        emp_obj = self.env['hr.employee']
        obj_mail_server = self.env['ir.mail_server']
        user = self.env['res.users'].browse(self._context.get('uid'))
        # Check if out going mail configured
        mail_server_ids = obj_mail_server.search([])
        if not mail_server_ids:
            raise except_orm(_('Mail Error'),
                             _('''No mail outgoing mail server
                               specified!'''))
        mail_server_record = mail_server_ids[0]
        email_list = []
        # Check email is defined in student
        for news in self:
            if news.user_ids and news.date:
                email_list = [news_user.email for news_user in news.user_ids
                              if news_user.email]
                if not email_list:
                    raise except_orm(_('User Email Configuration!'),
                                     _("Email not found in users !"))
            # Check email is defined in user created from employee
            else:
                for employee in emp_obj.search([]):
                    if employee.work_email:
                        email_list.append(employee.work_email)
                    elif employee.user_id and employee.user_id.email:
                        email_list.append(employee.user_id.email)
                if not email_list:
                    raise except_orm(_('Email Configuration!'),
                                     _("Email not defined!"))
            news_date = datetime.strptime(news.date,
                                          DEFAULT_SERVER_DATETIME_FORMAT)
            # Add company name while sending email
            company = user.company_id.name or ''
            body = """Hi,<br/><br/>
                    This is a news update from <b>%s</b> posted at %s<br/>
                    <br/> %s <br/><br/>
                    Thank you.""" % (company,
                                     news_date.strftime('%d-%m-%Y %H:%M:%S'),
                                     news.description or '')
            smtp_user = mail_server_record.smtp_user or False
            # Check if mail of outgoing server configured
            if not smtp_user:
                raise except_orm(_('Email Configuration '),
                                 _("Kindly,Configure Outgoing Mail Server!"))
            notification = 'Notification for news update.'
            # Configure email
            message = obj_mail_server.build_email(email_from=smtp_user,
                                                  email_to=email_list,
                                                  subject=notification,
                                                  body=body,
                                                  body_alternative=body,
                                                  reply_to=smtp_user,
                                                  subtype='html')
            # Send Email configured above with help of send mail method
            obj_mail_server.send_email(message=message,
                                       mail_server_id=mail_server_ids[0].id)
        return True


class StudentReminder(models.Model):
    _name = 'student.reminder'

    @api.model
    def check_user(self):
        '''Method to get default value of logged in Student'''
        return self.env['student.student'].search([('user_id', '=',
                                                    self._uid)]).id

    stu_id = fields.Many2one('student.student', 'Student Name', required=True,
                             default=check_user)
    name = fields.Char('Title')
    date = fields.Date('Date')
    description = fields.Text('Description')
    color = fields.Integer('Color Index', default=0)


class StudentCast(models.Model):
    _name = "student.cast"

    name = fields.Char("Name", required=True)


class ClassRoom(models.Model):
    _name = "class.room"

    name = fields.Char("Name")
    number = fields.Char("Room Number")


class Report(models.Model):
    _inherit = "report"

    @api.multi
    def render(self, template, values=None):
        for data in values.get('docs'):
            if (values.get('doc_model') == 'student.student' and
                    data.state == 'draft'):
                    raise ValidationError(_('''You cannot print report for
                student in unconfirm state!'''))
        res = super(Report, self).render(template, values)
        return res

