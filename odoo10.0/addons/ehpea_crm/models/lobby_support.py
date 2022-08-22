import re
import calendar
from datetime import datetime
from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, \
    DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import except_orm


class LobbySupportFprm(models.Model):
    ''' Defines an academic year '''
    _name = "lobby.support.form"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Lobby Support Form"
    _order = "lobby_seque"

    lobby_seque = fields.Char(string='Order Reference', required=True, copy=False, readonly=True, index=True,
                                default=lambda self: _('New'))
    lobbyrequest_id = fields.Many2one('lobby.request_last', 'Lobby Request Type')
    request_person = fields.Char(related='lobbyrequest_id.request_person',String='Request By')
    date_reque = fields.Date(related='lobbyrequest_id.request_date', String='Request Date')
    date_vist = fields.Date(String='Date of Visit',required=True, readonly=True, index=True, copy=False, default=fields.Datetime.now)
    cluster_name = fields.Char(String='Cluster Name')
    support_provide = fields.Char(String='Support Provide')
    challenge = fields.Char(String='Challenge Encountered')
    state = fields.Selection([('ong-going','On-going'),
                              ('completed','Completed'),
                              ], String='Status', readonly=True,default='ong-going',track_visibility="always")
    vist_camp_email = fields.Char(related='lobbyrequest_id.comp_email', String='Email')
    visite_history = fields.Html(String='Visit History')

    @api.model
    def create(self, vals):
        vals['lobby_seque'] = self.env['ir.sequence'].next_by_code('lobby.visit.seq') or _('New')
        result = super(LobbySupportFprm, self).create(vals)
        return result
    # name_seque = fields.Char(string='Order Reference', required=True, copy=False, readonly=True,index=True, default=lambda self: _('New'))


class LobbyRequest(models.Model):
        ''' Defines an academic year '''
        _name = "lobby.request_last"
        _inherit = ['mail.thread', 'ir.needaction_mixin']
        _description = "Lobby Request"
        _order = "lobby_requ_seque"

        partner_id = fields.Many2one('res.partner', 'Farm Name')
        lobby_requ_seque = fields.Char(string='Order Reference', required=True, copy=False, readonly=True, index=True,
                                    default=lambda self: _('New'))
        request_name = fields.Char(String='Support Request Type')
        request_person = fields.Char(String='Request Person')
        request_date = fields.Date(String='Request Date', required=True, readonly=True, index=True, copy=False,
                                   default=fields.Datetime.now)
        position = fields.Char(String='Position')
        comp_email = fields.Char(related='partner_id.email', String='Email')
        request_farm = fields.Char(related='partner_id.name', String='Request Farm')

        @api.model
        def create(self, vals):
            vals['lobby_requ_seque'] = self.env['ir.sequence'].next_by_code('lobby.request.seq') or _('New')
            result = super(LobbyRequest, self).create(vals)
            return result

        # @api.multi
        # def name_get(self):
        #     res = []
        #     for field in self:
        #         res.append((field.id, '%s %s' % (field.lobby_requ_seque, field.request_name)))
        #     return res


class AnnualFarmSurvey(models.Model):
    _name = "annual.farm.survey"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Annual Farm Information Survey"
    _order = "survey_seque"

    partner_id = fields.Many2one('res.partner', 'Farm Name')
    survey_seque = fields.Char(string='Order Reference', required=True, copy=False, readonly=True, index=True,
                               default=lambda self:('New'))
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
    survey_year = fields.Date(String='Year Of Survey', required=True, readonly=True, index=True, copy=False,
                              default=fields.Datetime.now)

    @api.model
    def create(self, vals):
        vals['survey_seque'] = self.env['ir.sequence'].next_by_code('lobby.request.seq') or _('New')
        result = super(AnnualFarmSurvey, self).create(vals)
        return result

