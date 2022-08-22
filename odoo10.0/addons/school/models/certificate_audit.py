# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

import time
# import re
from datetime import datetime
from odoo import models, fields, api, tools
from odoo.tools.translate import _
from odoo.modules import get_module_resource
# from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import except_orm, UserError, AccessError
from odoo.exceptions import ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
# from dateutil.relativedelta import relativedelta
from .import school

# from lxml import etree
# added import statement in try-except because when server runs on
# windows operating system issue arise because this library is not in Windows.
try:
    from odoo.tools import image_colorize, image_resize_image_big
except:
    image_colorize = False
    image_resize_image_big = False


class CertificateAuditVisitLast(models.Model):
    _name = "certificate.audit.last"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Code Audit Visit"
    _order = "viste_seque"
    _rec_name = 'certificaterequest_id'

    def action_pre_audit(self):
        for rec in self:
            rec.state = 'pre_audit'

    def action_apply_external_audit(self):
        for rec in self:
            rec.state = 'apply_external_audit'

    def action_apply_external_audit_accept(self):
        for rec in self:
            rec.state = 'accepted_external_audit'

    def action_rejected_external_audit(self):
        for rec in self:
            rec.state = 'rejected_external_audit'

    def action_accepted_external_audit(self):
        for rec in self:
            rec.state = 'accepted_external_audit'

    def action_audit_conducted(self):
        for rec in self:
            rec.state = 'audit_conducted'

    def action_audit_certified(self):
        for rec in self:
            rec.state = 'certified'

    def action_audit_noncomplien(self):
        for rec in self:
            rec.state = 'non_compliant'

    viste_seque = fields.Char(string='Order Reference', required=True, copy=False, readonly=True, index=True,
                              default=lambda self: _('New'))
    certificaterequest_id = fields.Many2one('certificate.request', 'Code Audit Request Type', required=True)
    # request_person = fields.Char(related='certificaterequest_id.contact_person',String='Request By')
    request_date = fields.Date(String='Request Date', required=True, readonly=True, default=fields.Datetime.now)
    position = fields.Char(String='Position')
    date_reque = fields.Date(related='certificaterequest_id.request_date', String='Request Date')
    date_begin = fields.Datetime(String='Date of Visit', required=True, default=lambda self: fields.datetime.now())
    date_end = fields.Datetime(String='Date of expire', required=True, default=lambda self: fields.datetime.now())
    date_expire = fields.Date(String='Date of Expire')
    Certificate_Issue_Date = fields.Date(String='Certificate Issue-Date')
    audit_finding = fields.Char(String='Finding During the Audit', required=True)
    recommended_support = fields.Char(String='Recommended Support', required=True)
    support_requested = fields.Char(String='Support Requested')
    reply_to = fields.Char(String='Reply To')
    certificate_award = fields.Many2one('res.partner',String='Certificate Award By')
    expire_mail_ids = fields.One2many('expire.mail', 'expire_id', string='Mail Schedule',
                                     default=lambda self: self._default_event_mail_ids(), copy=True)

    @api.model
    def _default_event_mail_ids(self):
        return [(0, 0, {
            'interval_unit': 'now',
            'interval_type': 'after_sub',
            'template_id': self.env.ref('school.event_subscription')
        }), (0, 0, {
            'interval_nbr': 2,
            'interval_unit': 'days',
            'interval_type': 'before_event',
            'template_id': self.env.ref('school.event_reminder')
        }), (0, 0, {
            'interval_nbr': 15,
            'interval_unit': 'days',
            'interval_type': 'before_event',
            'template_id': self.env.ref('school.event_reminder')
        })]

    state = fields.Selection([
        ('baseline_audit', 'Baseline Audit'),
        ('baseline_home', 'Baseline Audit'),
        ('pre_audit', 'Pre audit'),
        ('apply_external_audit', 'Apply For external Audit'),
        ('rejected_external_audit', 'Rejected External Audit'),
        ('accepted_external_audit', 'Accepted External Audit'),
        ('audit_conducted', 'Audit conducted'),
        ('certified', 'Certified'),
        ('non_compliant', 'Non-compliant'),
    ], String='Status', readonly=True, default='baseline_audit', track_visibility="always")
    vist_camp_email = fields.Char(related='certificaterequest_id.comp_email', String='Email')
    camp_name = fields.Char(related='certificaterequest_id.request_farm', String='Request Farm')
    visite_history = fields.Html(String='Visit History')
    follow_up = fields.Html(String='Follow Up')
    registration_ids = fields.One2many(
        'expire.registration', 'expire_id', string='Certified',
        readonly=False, states={'certified': [('readonly', True)]})
    states = fields.Selection([
        ('draft', 'Unconfirmed'), ('cancel', 'Cancelled'),
        ('confirm', 'Confirmed'), ('done', 'Done')],
        string='Status', default='draft', readonly=True, required=True, copy=False,
        help="If event is created, the status is 'Draft'. If event is confirmed for the particular dates the status is set to 'Confirmed'. If the event is over, the status is set to 'Done'. If event is cancelled the status is set to 'Cancelled'.")
    @api.model
    def create(self, vals):
        vals['viste_seque'] = self.env['ir.sequence'].next_by_code('certificate.audit.seq') or _('New')
        result = super(CertificateAuditVisitLast, self).create(vals)
        return result


class CertificateExpireDateRegistration(models.Model):
    _name = 'expire.registration'
    _description = 'Certified'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    # _order = 'name, create_date desc'

    origin = fields.Char(
        string='Source Document', readonly=True,
        help="Reference of the document that created the registration, for example a sale order")
    expire_id = fields.Many2one('certificate.audit.last', string='Certificate Audit', required=True,
        readonly=True)
    partner_id = fields.Many2one('res.partner', string='Contact')
    date_open = fields.Datetime(string='Registration Date', readonly=True, default=lambda self: fields.datetime.now())  # weird crash is directly now
    # date_closed = fields.Datetime(string='Expire Date', readonly=True)
    # event_begin_date = fields.Datetime(string="Certificate Awared Date", related='expire_id.date_begin', readonly=True)
    # event_end_date = fields.Datetime(string="Certificate Expire Date", related='expire_id.date_end', readonly=True)
    # company_id = fields.Many2one(
    #     'res.company', string='Company', related='expire_id.company_id',
    #     store=True, readonly=True, states={'draft': [('readonly', False)]})
    # state = fields.Selection([
    #     ('draft', 'Unconfirmed'), ('cancel', 'Cancelled'),
    #     ('open', 'Confirmed'), ('done', 'Attended')],
    #     string='Status', default='draft', readonly=True, copy=False, track_visibility='onchange')
    # email = fields.Char(string='Email')
    # phone = fields.Char(string='Phone')
    # name = fields.Char(string='Attendee Name', index=True)
    # company_name = fields.Char(String='Company Name')

    # @api.multi
    # def _check_auto_confirmation(self):
    #     if self._context.get('registration_force_draft'):
    #         return False
    #     if any(registration.expire_id.state != 'confirm' or
    #            not registration.expire_id.auto_confirm or
    #            (not registration.expire_id.seats_available and registration.expire_id.seats_availability == 'limited') for registration in self):
    #         return False
    #     return True
    #
    @api.model
    def create(self, vals):
        registration = super(CertificateExpireDateRegistration, self).create(vals)
        if registration._check_auto_confirmation():
            registration.sudo().confirm_registration()
        return registration

    # @api.model
    # def _prepare_attendee_values(self, registration):
    #     """ Method preparing the values to create new attendees based on a
    #     sale order line. It takes some registration data (dict-based) that are
    #     optional values coming from an external input like a web page. This method
    #     is meant to be inherited in various addons that sell events. """
    #     partner_id = registration.pop('partner_id', self.env.user.partner_id)
    #     expire_id = registration.pop('expire_id', False)
    #     data = {
    #         'name': registration.get('name', partner_id.name),
    #         'phone': registration.get('phone', partner_id.phone),
    #         'email': registration.get('email', partner_id.email),
    #         'company_name': registration.get('company_name', partner_id.company_name),
    #         'partner_id': partner_id.id,
    #         'expire_id': expire_id and expire_id.id or False,
    #     }
    #     data.update({key: registration[key] for key in registration.keys() if key in self._fields})
    #     return data
    #
    # @api.one
    # def do_draft(self):
    #     self.state = 'draft'
    #
    # @api.one
    # def confirm_registration(self):
    #     self.state = 'open'
    #
    #     # auto-trigger after_sub (on subscribe) mail schedulers, if needed
    #     onsubscribe_schedulers = self.expire_id.expire_mail_ids.filtered(
    #         lambda s: s.interval_type == 'after_sub')
    #     onsubscribe_schedulers.execute()
    #
    # @api.one
    # def button_reg_close(self):
    #     """ Close Registration """
    #     today = fields.Datetime.now()
    #     if self.expire_id.date_begin <= today:
    #         self.write({'state': 'done', 'date_closed': today})
    #     else:
    #         raise UserError(_("You must wait for the starting day of the event to do this action."))
    #
    # @api.one
    # def button_reg_cancel(self):
    #     self.state = 'cancel'
    #
    # @api.onchange('partner_id')
    # def _onchange_partner(self):
    #     if self.partner_id:
    #         contact_id = self.partner_id.address_get().get('contact', False)
    #         if contact_id:
    #             contact = self.env['res.partner'].browse(contact_id)
    #             self.name = contact.name or self.name
    #             self.email = contact.email or self.email
    #             self.phone = contact.phone or self.phone
    #             self.company_name = contact.company_name or self.company_name
    #
    # @api.multi
    # def message_get_suggested_recipients(self):
    #     recipients = super(CertificateExpireDateRegistration, self).message_get_suggested_recipients()
    #     public_users = self.env['res.users'].sudo()
    #     public_groups = self.env.ref("base.group_public", raise_if_not_found=False)
    #     if public_groups:
    #         public_users = public_groups.sudo().with_context(active_test=False).mapped("users")
    #     try:
    #         for attendee in self:
    #             is_public = attendee.sudo().with_context(active_test=False).partner_id.user_ids in public_users if public_users else False
    #             if attendee.partner_id and not is_public:
    #                 attendee._message_add_suggested_recipient(recipients, partner=attendee.partner_id, reason=_('Customer'))
    #             elif attendee.email:
    #                 attendee._message_add_suggested_recipient(recipients, email=attendee.email, reason=_('Customer Email'))
    #     except AccessError:     # no read access rights -> ignore suggested recipients
    #         pass
    #     return recipients
    #
    # @api.multi
    # def action_send_badge_email(self):
    #     """ Open a window to compose an email, with the template - 'event_badge'
    #         message loaded by default
    #     """
    #     self.ensure_one()
    #     template = self.env.ref('event.event_registration_mail_template_badge')
    #     compose_form = self.env.ref('mail.email_compose_message_wizard_form')
    #     ctx = dict(
    #         default_model='event.registration',
    #         default_res_id=self.id,
    #         default_use_template=bool(template),
    #         default_template_id=template.id,
    #         default_composition_mode='comment',
    #     )
    #     return {
    #         'name': _('Compose Email'),
    #         'type': 'ir.actions.act_window',
    #         'view_type': 'form',
    #         'view_mode': 'form',
    #         'res_model': 'mail.compose.message',
    #         'views': [(compose_form.id, 'form')],
    #         'view_id': compose_form.id,
    #         'target': 'new',
    #         'context': ctx,
    #     }
    #
    # @api.multi
    # def get_date_range_str(self):
    #     self.ensure_one()
    #     today = fields.Datetime.from_string(fields.Datetime.now())
    #     event_date = fields.Datetime.from_string(self.event_begin_date)
    #     diff = (event_date.date() - today.date())
    #     if diff.days == 0:
    #         return _('Today')
    #     elif diff.days == 1:
    #         return _('Tomorrow')
    #     elif event_date.isocalendar()[1] == today.isocalendar()[1]:
    #         return _('This week')
    #     elif today.month == event_date.month:
    #         return _('This month')
    #     elif event_date.month == (today + relativedelta(months=+1)):
    #         return _('Next month')
    #     else:
    #         return format_tz(self.env, self.event_begin_date, tz='UTC', format='%Y%m%dT%H%M%SZ')
