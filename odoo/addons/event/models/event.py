# -*- coding: utf-8 -*-

import pytz

from odoo import _, api, fields, models
from odoo.addons.mail.models.mail_template import format_tz
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.translate import html_translate

from dateutil.relativedelta import relativedelta


class EventType(models.Model):
    """ Event Type """
    _name = 'event.type'
    _description = 'Event Type'

    name = fields.Char('Event Type', required=True, translate=True)
    default_reply_to = fields.Char('Reply To')
    default_registration_min = fields.Integer(
        'Default Minimum Registration', default=0,
        help="It will select this default minimum value when you choose this event")
    default_registration_max = fields.Integer(
        'Default Maximum Registration', default=0,
        help="It will select this default maximum value when you choose this event")


class EventEvent(models.Model):
    """Event"""
    _name = 'event.event'
    _description = 'Event'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = 'date_begin'

    name = fields.Char(
        string='Event Name', translate=True, required=True,
        readonly=False, states={'done': [('readonly', True)]})
    active = fields.Boolean(default=True, track_visibility="onchange")
    user_id = fields.Many2one(
        'res.users', string='Responsible',
        default=lambda self: self.env.user,
        readonly=False, states={'done': [('readonly', True)]})
    company_id = fields.Many2one(
        'res.company', string='Company', change_default=True,
        default=lambda self: self.env['res.company']._company_default_get('event.event'),
        required=False, readonly=False, states={'done': [('readonly', True)]})
    organizer_id = fields.Many2one(
        'res.partner', string='Organizer',
        default=lambda self: self.env.user.company_id.partner_id)
    event_type_id = fields.Many2one(
        'event.type', string='Category',
        readonly=False, states={'done': [('readonly', True)]},
        oldname='type')
    color = fields.Integer('Kanban Color Index')
    event_mail_ids = fields.One2many('event.mail', 'event_id', string='Mail Schedule', default=lambda self: self._default_event_mail_ids(), copy=True)

    @api.model
    def _default_event_mail_ids(self):
        return [(0, 0, {
            'interval_unit': 'now',
            'interval_type': 'after_sub',
            'template_id': self.env.ref('event.event_subscription')
        }), (0, 0, {
            'interval_nbr': 2,
            'interval_unit': 'days',
            'interval_type': 'before_event',
            'template_id': self.env.ref('event.event_reminder')
        }), (0, 0, {
            'interval_nbr': 15,
            'interval_unit': 'days',
            'interval_type': 'before_event',
            'template_id': self.env.ref('event.event_reminder')
        })]

    # Seats and computation
    seats_max = fields.Integer(
        string='Maximum Attendees Number', oldname='register_max',
        readonly=True, states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]},
        help="For each event you can define a maximum registration of seats(number of attendees), above this numbers the registrations are not accepted.")
    seats_availability = fields.Selection(
        [('limited', 'Limited'), ('unlimited', 'Unlimited')],
        'Maximum Attendees', required=True, default='unlimited')
    seats_min = fields.Integer(
        string='Minimum Attendees', oldname='register_min',
        help="For each event you can define a minimum reserved seats (number of attendees), if it does not reach the mentioned registrations the event can not be confirmed (keep 0 to ignore this rule)")
    seats_reserved = fields.Integer(
        oldname='register_current', string='Reserved Seats',
        store=True, readonly=True, compute='_compute_seats')
    seats_available = fields.Integer(
        oldname='register_avail', string='Available Seats',
        store=True, readonly=True, compute='_compute_seats')
    seats_unconfirmed = fields.Integer(
        oldname='register_prospect', string='Unconfirmed Seat Reservations',
        store=True, readonly=True, compute='_compute_seats')
    seats_used = fields.Integer(
        oldname='register_attended', string='Number of Participants',
        store=True, readonly=True, compute='_compute_seats')
    seats_expected = fields.Integer(
        string='Number of Expected Attendees',
        readonly=True, compute='_compute_seats')

    @api.multi
    @api.depends('seats_max', 'registration_ids.state')
    def _compute_seats(self):
        """ Determine reserved, available, reserved but unconfirmed and used seats. """
        # initialize fields to 0
        for event in self:
            event.seats_unconfirmed = event.seats_reserved = event.seats_used = event.seats_available = 0
        # aggregate registrations by event and by state
        if self.ids:
            state_field = {
                'draft': 'seats_unconfirmed',
                'open': 'seats_reserved',
                'done': 'seats_used',
            }
            query = """ SELECT event_id, state, count(event_id)
                        FROM event_registration
                        WHERE event_id IN %s AND state IN ('draft', 'open', 'done')
                        GROUP BY event_id, state
                    """
            self._cr.execute(query, (tuple(self.ids),))
            for event_id, state, num in self._cr.fetchall():
                event = self.browse(event_id)
                event[state_field[state]] += num
        # compute seats_available
        for event in self:
            if event.seats_max > 0:
                event.seats_available = event.seats_max - (event.seats_reserved + event.seats_used)
            event.seats_expected = event.seats_unconfirmed + event.seats_reserved + event.seats_used

    # Registration fields
    registration_ids = fields.One2many(
        'event.registration', 'event_id', string='Attendees',
        readonly=False, states={'done': [('readonly', True)]})
    # Date fields
    date_tz = fields.Selection('_tz_get', string='Timezone', required=True, default=lambda self: self.env.user.tz or 'UTC')
    date_begin = fields.Datetime(
        string='Start Date', required=True,
        track_visibility='onchange', states={'done': [('readonly', True)]})
    date_end = fields.Datetime(
        string='End Date', required=True,
        track_visibility='onchange', states={'done': [('readonly', True)]})
    date_begin_located = fields.Datetime(string='Start Date Located', compute='_compute_date_begin_tz')
    date_end_located = fields.Datetime(string='End Date Located', compute='_compute_date_end_tz')

    @api.model
    def _tz_get(self):
        return [(x, x) for x in pytz.all_timezones]

    @api.one
    @api.depends('date_tz', 'date_begin')
    def _compute_date_begin_tz(self):
        if self.date_begin:
            self_in_tz = self.with_context(tz=(self.date_tz or 'UTC'))
            date_begin = fields.Datetime.from_string(self.date_begin)
            self.date_begin_located = fields.Datetime.to_string(fields.Datetime.context_timestamp(self_in_tz, date_begin))
        else:
            self.date_begin_located = False

    @api.one
    @api.depends('date_tz', 'date_end')
    def _compute_date_end_tz(self):
        if self.date_end:
            self_in_tz = self.with_context(tz=(self.date_tz or 'UTC'))
            date_end = fields.Datetime.from_string(self.date_end)
            self.date_end_located = fields.Datetime.to_string(fields.Datetime.context_timestamp(self_in_tz, date_end))
        else:
            self.date_end_located = False

    state = fields.Selection([
        ('draft', 'Unconfirmed'), ('cancel', 'Cancelled'),
        ('confirm', 'Confirmed'), ('done', 'Done')],
        string='Status', default='draft', readonly=True, required=True, copy=False,
        help="If event is created, the status is 'Draft'. If event is confirmed for the particular dates the status is set to 'Confirmed'. If the event is over, the status is set to 'Done'. If event is cancelled the status is set to 'Cancelled'.")
    auto_confirm = fields.Boolean(string='Confirmation not required', compute='_compute_auto_confirm')

    @api.one
    def _compute_auto_confirm(self):
        self.auto_confirm = self.env['ir.values'].get_default('event.config.settings', 'auto_confirmation')

    reply_to = fields.Char(
        'Reply-To Email', readonly=False, states={'done': [('readonly', True)]},
        help="The email address of the organizer is likely to be put here, with the effect to be in the 'Reply-To' of the mails sent automatically at event or registrations confirmation. You can also put the email address of your mail gateway if you use one.")
    address_id = fields.Many2one(
        'res.partner', string='Location', default=lambda self: self.env.user.company_id.partner_id,
        readonly=False, states={'done': [('readonly', True)]})
    country_id = fields.Many2one('res.country', 'Country',  related='address_id.country_id', store=True)
    description = fields.Html(
        string='Description', oldname='note', translate=html_translate, sanitize_attributes=False,
        readonly=False, states={'done': [('readonly', True)]})
    # badge fields
    badge_front = fields.Html(string='Badge Front')
    badge_back = fields.Html(string='Badge Back')
    badge_innerleft = fields.Html(string='Badge Inner Left')
    badge_innerright = fields.Html(string='Badge Inner Right')
    event_logo = fields.Html(string='Event Logo')

    @api.multi
    @api.depends('name', 'date_begin', 'date_end')
    def name_get(self):
        result = []
        for event in self:
            date_begin = fields.Datetime.from_string(event.date_begin)
            date_end = fields.Datetime.from_string(event.date_end)
            dates = [fields.Date.to_string(fields.Datetime.context_timestamp(event, dt)) for dt in [date_begin, date_end] if dt]
            dates = sorted(set(dates))
            result.append((event.id, '%s (%s)' % (event.name, ' - '.join(dates))))
        return result

    @api.one
    @api.constrains('seats_max', 'seats_available')
    def _check_seats_limit(self):
        if self.seats_availability == 'limited' and self.seats_max and self.seats_available < 0:
            raise ValidationError(_('No more available seats.'))

    @api.one
    @api.constrains('date_begin', 'date_end')
    def _check_closing_date(self):
        if self.date_end < self.date_begin:
            raise ValidationError(_('Closing Date cannot be set before Beginning Date.'))

    @api.model
    def create(self, vals):
        res = super(EventEvent, self).create(vals)
        if res.organizer_id:
            res.message_subscribe([res.organizer_id.id])
        if res.auto_confirm:
            res.button_confirm()
        return res

    @api.multi
    def write(self, vals):
        res = super(EventEvent, self).write(vals)
        if vals.get('organizer_id'):
            self.message_subscribe([vals['organizer_id']])
        return res

    @api.one
    def button_draft(self):
        self.state = 'draft'

    @api.one
    def button_cancel(self):
        for event_reg in self.registration_ids:
            if event_reg.state == 'done':
                raise UserError(_("You have already set a registration for this event as 'Attended'. Please reset it to draft if you want to cancel this event."))
        self.registration_ids.write({'state': 'cancel'})
        self.state = 'cancel'

    @api.one
    def button_done(self):
        self.state = 'done'

    @api.one
    def button_confirm(self):
        self.state = 'confirm'

    @api.onchange('event_type_id')
    def _onchange_type(self):
        if self.event_type_id:
            self.seats_min = self.event_type_id.default_registration_min
            self.seats_max = self.event_type_id.default_registration_max
            self.reply_to = self.event_type_id.default_reply_to

    @api.multi
    def action_event_registration_report(self):
        res = self.env['ir.actions.act_window'].for_xml_id('event', 'action_report_event_registration')
        res['context'] = {
            "search_default_event_id": self.id,
            "group_by": ['create_date:day'],
        }
        return res

    @api.one
    def mail_attendees(self, template_id, force_send=False, filter_func=lambda self: self.state != 'cancel'):
        for attendee in self.registration_ids.filtered(filter_func):
            self.env['mail.template'].browse(template_id).send_mail(attendee.id, force_send=force_send)

    @api.multi
    def _is_event_registrable(self):
        return True

class EventRegistration(models.Model):
    _name = 'event.registration'
    _description = 'Attendee'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = 'name, create_date desc'

    origin = fields.Char(
        string='Source Document', readonly=True,
        help="Reference of the document that created the registration, for example a sale order")
    event_id = fields.Many2one(
        'event.event', string='Event', required=True,
        readonly=True, states={'draft': [('readonly', False)]})
    partner_id = fields.Many2one(
        'res.partner', string='Contact',
        states={'done': [('readonly', True)]})
    date_open = fields.Datetime(string='Registration Date', readonly=True, default=lambda self: fields.datetime.now())  # weird crash is directly now
    date_closed = fields.Datetime(string='Attended Date', readonly=True)
    event_begin_date = fields.Datetime(string="Event Start Date", related='event_id.date_begin', readonly=True)
    event_end_date = fields.Datetime(string="Event End Date", related='event_id.date_end', readonly=True)
    company_id = fields.Many2one(
        'res.company', string='Company', related='event_id.company_id',
        store=True, readonly=True, states={'draft': [('readonly', False)]})
    state = fields.Selection([
        ('draft', 'Unconfirmed'), ('cancel', 'Cancelled'),
        ('open', 'Confirmed'), ('done', 'Attended')],
        string='Status', default='draft', readonly=True, copy=False, track_visibility='onchange')
    email = fields.Char(string='Email')
    buyer_visiter = fields.Boolean(string='Buyer')
    producer_visiter = fields.Boolean(string='producer')
    other_visiter = fields.Char(String='Other')
    buyer_description = fields.Char(String='Buyer Description')
    producer_description = fields.Char(String='Producer Description')
    fruit_visiter = fields.Boolean(string='Fruit')
    fruit_description = fields.Char(string='Description')
    vegetables_visiter = fields.Boolean(string='Vegetables')
    vegetables_description = fields.Char(string='Description')
    herb = fields.Boolean(String='Herb')
    herb_description = fields.Char(String='Description')
    cut_flower_visitor = fields.Boolean(String='Cut flower')
    cut_flower_description = fields.Char(String='Description')
    cutting_visitor = fields.Char(String='Cutting')
    cutting_description = fields.Char(String='Description')
    vegetable_seed = fields.Boolean(String=' Vegetable Seed')
    vegetable_seed_description = fields.Char(String='Description')
    other_prodocut = fields.Char(string='Other Description')
    phone = fields.Char(string='Phone')
    name = fields.Char(string='Attendee Name', index=True)
    country_id = fields.Many2one('res.country', string='Country', required=True)
    company_name = fields.Char(String='Company Name')
    country_of_origin = fields.Char(String='Country of Origin')
    contact_email = fields.Char(string='Contact Email')
    website = fields.Char(Srtring='website')
    fax = fields.Char(Srtring='fax')
    booth_size_three = fields.Char(Srtring='booth_size_three')
    vat_identification_number = fields.Char(Srtring='vat identification number')
    undersigned = fields.Char(Srtring='undersigned')
    booth_three = fields.Char(Srtring='Booth Three')
    address = fields.Char(Srtring='Address')
    invocies_email = fields.Char(Srtring='Invocies email')
    city = fields.Char(Srtring='City')
    booth_size_second = fields.Char(Srtring='Booth size second')
    position = fields.Char(Srtring='position')
    booth_size_one = fields.Char(Srtring='booth size one')
    zipcode = fields.Char(Srtring='zip code')
    invocies_name = fields.Char(Srtring='invocies name')
    booth_two = fields.Char(Srtring='booth two')
    booth_one = fields.Char(Srtring='booth one')
    short_company_description = fields.Char(Srtring='short company description')
    campony_state = fields.Char(Srtring='campony state')


    @api.one
    @api.constrains('event_id', 'state')
    def _check_seats_limit(self):
        if self.event_id.seats_availability == 'limited' and self.event_id.seats_max and self.event_id.seats_available < (1 if self.state == 'draft' else 0):
            raise ValidationError(_('No more seats available for this event.'))

    @api.multi
    def _check_auto_confirmation(self):
        if self._context.get('registration_force_draft'):
            return False
        if any(registration.event_id.state != 'confirm' or
               not registration.event_id.auto_confirm or
               (not registration.event_id.seats_available and registration.event_id.seats_availability == 'limited') for registration in self):
            return False
        return True

    @api.model
    def create(self, vals):
        registration = super(EventRegistration, self).create(vals)
        if registration._check_auto_confirmation():
            registration.sudo().confirm_registration()
        return registration

    @api.model
    def _prepare_attendee_values(self, registration):
        """ Method preparing the values to create new attendees based on a
        sale order line. It takes some registration data (dict-based) that are
        optional values coming from an external input like a web page. This method
        is meant to be inherited in various addons that sell events. """
        partner_id = registration.pop('partner_id', self.env.user.partner_id)
        event_id = registration.pop('event_id', False)
        data = {
            'name': registration.get('name', partner_id.name),
            'phone': registration.get('phone', partner_id.phone),
            'email': registration.get('email', partner_id.email),
            'company_name': registration.get('company_name', partner_id.company_name),
            'partner_id': partner_id.id,
            'event_id': event_id and event_id.id or False,
        }
        data.update({key: registration[key] for key in registration.keys() if key in self._fields})
        return data

    @api.one
    def do_draft(self):
        self.state = 'draft'

    @api.one
    def confirm_registration(self):
        self.state = 'open'

        # auto-trigger after_sub (on subscribe) mail schedulers, if needed
        onsubscribe_schedulers = self.event_id.event_mail_ids.filtered(
            lambda s: s.interval_type == 'after_sub')
        onsubscribe_schedulers.execute()

    @api.one
    def button_reg_close(self):
        """ Close Registration """
        today = fields.Datetime.now()
        if self.event_id.date_begin <= today:
            self.write({'state': 'done', 'date_closed': today})
        else:
            raise UserError(_("You must wait for the starting day of the event to do this action."))

    @api.one
    def button_reg_cancel(self):
        self.state = 'cancel'

    @api.onchange('partner_id')
    def _onchange_partner(self):
        if self.partner_id:
            contact_id = self.partner_id.address_get().get('contact', False)
            if contact_id:
                contact = self.env['res.partner'].browse(contact_id)
                self.name = contact.name or self.name
                self.email = contact.email or self.email
                self.phone = contact.phone or self.phone
                self.company_name = contact.company_name or self.company_name

    @api.multi
    def message_get_suggested_recipients(self):
        recipients = super(EventRegistration, self).message_get_suggested_recipients()
        public_users = self.env['res.users'].sudo()
        public_groups = self.env.ref("base.group_public", raise_if_not_found=False)
        if public_groups:
            public_users = public_groups.sudo().with_context(active_test=False).mapped("users")
        try:
            for attendee in self:
                is_public = attendee.sudo().with_context(active_test=False).partner_id.user_ids in public_users if public_users else False
                if attendee.partner_id and not is_public:
                    attendee._message_add_suggested_recipient(recipients, partner=attendee.partner_id, reason=_('Customer'))
                elif attendee.email:
                    attendee._message_add_suggested_recipient(recipients, email=attendee.email, reason=_('Customer Email'))
        except AccessError:     # no read access rights -> ignore suggested recipients
            pass
        return recipients

    @api.multi
    def action_send_badge_email(self):
        """ Open a window to compose an email, with the template - 'event_badge'
            message loaded by default
        """
        self.ensure_one()
        template = self.env.ref('event.event_registration_mail_template_badge')
        compose_form = self.env.ref('mail.email_compose_message_wizard_form')
        ctx = dict(
            default_model='event.registration',
            default_res_id=self.id,
            default_use_template=bool(template),
            default_template_id=template.id,
            default_composition_mode='comment',
        )
        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }

    @api.multi
    def get_date_range_str(self):
        self.ensure_one()
        today = fields.Datetime.from_string(fields.Datetime.now())
        event_date = fields.Datetime.from_string(self.event_begin_date)
        diff = (event_date.date() - today.date())
        if diff.days == 0:
            return _('Today')
        elif diff.days == 1:
            return _('Tomorrow')
        elif event_date.isocalendar()[1] == today.isocalendar()[1]:
            return _('This week')
        elif today.month == event_date.month:
            return _('This month')
        elif event_date.month == (today + relativedelta(months=+1)):
            return _('Next month')
        else:
            return format_tz(self.env, self.event_begin_date, tz='UTC', format='%Y%m%dT%H%M%SZ')
