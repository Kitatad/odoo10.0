import re
import calendar
from datetime import datetime
from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, \
    DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import except_orm
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


class AnnualFarmSurvey(models.Model):
    _name = "annual.farm.survey"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Annual Farm Information Survey"
    _order = "survey_seque"

    partner_id = fields.Many2one('res.partner', 'Farm Name')
    survey_seque = fields.Char(string='Order Reference', required=True, copy=False, readonly=True, index=True,
                                   default=lambda self: _('New'))
    developed_land = fields.Integer('Developed Land Size')
    undeveloped_land = fields.Integer('Undeveloped Land Size')
    total_land_size = fields.Integer('Total Land Size')
    cut_flower = fields.Boolean(String='Cut Flower')
    fruit = fields.Boolean(String='Fruit')
    vegertables = fields.Boolean(String='Vegetebel')
    herbs = fields.Boolean(String='Herbs')
    area_not_production = fields.Char(String='Area not under Production')
    managerial = fields.Integer('Managerial')
    daily_laborer = fields.Integer('Daily Laborer')
    total_work_force = fields.Integer('Total Work Force')
    wage_rate = fields.Integer('Wage rate')
    farm_volume_exp = fields.Char(String='Volume of Export(year)')
    farm_value_exp = fields.Char(String='Value of Export(year)')
    custom_volume_exp = fields.Char(String='Volume of Export(year)')
    custom_value_exp = fields.Char(String='Value of Export(year)')
    national_volume_exp = fields.Char(String='Volume of Export(year)')
    national_value_exp = fields.Char(String='Value of Export(year)')
    survey_year =fields.Date(String='Year Of Survey',required=True, readonly=True, index=True, copy=False, default=fields.Datetime.now)
    @api.model
    def create(self, vals):
        vals['survey_seque'] = self.env['ir.sequence'].next_by_code('lobby.request.seq') or _('New')
        result = super(AnnualFarmSurvey, self).create(vals)
        return result
