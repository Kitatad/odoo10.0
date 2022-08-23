
# -*- coding: utf-8 -*-

import pytz

from odoo import _, api, fields, models
from odoo.addons.mail.models.mail_template import format_tz
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.translate import html_translate

from dateutil.relativedelta import relativedelta


class ExhibitorRegistration(models.Model):
    _name = 'exhibitor.registration'
    _description = 'Exhibitor'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = 'name, create_date desc'


    email = fields.Char(string='Email')
    phone = fields.Char(string='Phone')
    name = fields.Char(string='Exhibitor  Name', index=True)
    company_name = fields.Char(String='Company Name')
    country_id = fields.Many2one('res.country', string='Country', required=True)
    contact_email = fields.Char(string='Contact Email')
    vat_identification_number = fields.Char(string='VAT identification number')
    undersigned = fields.Char(string='The undersigned')
    position = fields.Char(string='Position')
    address = fields.Char(string='Address')
    city = fields.Char(string='City')
    campony_state = fields.Char(string='State')
    zipcode = fields.Char(string='Zipcode')
    website = fields.Char(string='Website')
    fax = fields.Char(string='Fax')
    invocies_name = fields.Char(string='Invoicing Contact Person Name')
    invocies_email = fields.Char(string='Invoicing Email')
    booth_one = fields.Char(string='1st ')
    booth_two = fields.Char(string='2nd ')
    booth_three = fields.Char(string='3rd ')
    booth_size_one = fields.Char(string='Both Size one ')
    booth_size_second = fields.Char(string='Both Size two ')
    booth_size_three = fields.Char(string='Both Size three ')
    short_company_description = fields.Char(string='Short company description')
    flower_buyer = fields.Boolean('Flower')
    fruit_buyer = fields.Boolean(String='Fruit')
    vegetable_buyer = fields.Boolean(String='Vegetable')
    herbs_buyer = fields.Boolean(String='Vegetable')
    other_buyer = fields.Char(String='Other')
    buyer = fields.Boolean(String='Buyer')
    producer = fields.Boolean(String='Producer')
    other = fields.Char(String='Other')
    date_open = fields.Datetime(string='Registration Date', readonly=True,
                                default=lambda self: fields.datetime.now())  # weird crash is directly now
    date_closed = fields.Datetime(string='Attended Date', readonly=True)
    event_id = fields.Many2one(
        'event.event', string='Event', required=True)
    state = fields.Selection([
        ('draft', 'Unconfirmed'), ('cancel', 'Cancelled'),
        ('open', 'Confirmed'), ('done', 'Attended')],
        string='Status', default='draft', readonly=True, copy=False, track_visibility='onchange')