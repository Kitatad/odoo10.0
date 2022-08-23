
# -*- coding: utf-8 -*-

import pytz

from odoo import _, api, fields, models
from odoo.addons.mail.models.mail_template import format_tz
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.translate import html_translate

from dateutil.relativedelta import relativedelta


class BuyerInterest(models.Model):
    _name = 'buyer.interest'
    _description = 'Exhibitor'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = 'company_name'

    company_name = fields.Char(string='Company Name')
    country_id = fields.Many2one('res.country', string='Country Origin', required=True)
    contact_person = fields.Char(String='Contact Person')
    office_phone = fields.Char(String='Office Phone')
    mobile_phone = fields.Char(String='Mobile Phone')
    contact_email = fields.Char(string='Contact Email')
    flower_buyer = fields.Boolean(String='Flower')
    fruit_buyer = fields.Boolean(String='Fruit')
    vegetable_buyer = fields.Boolean(String='Vegetable')
    herbs_buyer = fields.Boolean(String='Vegetable')
    other_buyer = fields.Char(String='Other')
    variety_colour = fields.Char(String='Variety/Color')
    head_size = fields.Char(String='size or Specification')
    volume = fields.Char(String='Volume')
    type_of_package = fields.Char(String='Type Of Packaging Material')
    fob_cif = fields.Char(String='FOB CIF')
    other_remark =fields.Char(String='Other Remark')
    date_open = fields.Datetime(string='Registration Date', readonly=True,
                                default=lambda self: fields.datetime.now())  # weird crash is directly now
    date_closed = fields.Datetime(string='Attended Date', readonly=True)
    event_id = fields.Many2one(
        'event.event', string='Expo Title', required=True)
    state = fields.Selection([
        ('draft', 'Unconfirmed'), ('cancel', 'Cancelled'),
        ('open', 'Confirmed'), ('done', 'Attended')],
        string='Status', default='draft', readonly=True, copy=False, track_visibility='onchange')