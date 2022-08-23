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


class WasteManagementRequest(models.Model):
    _name = "waste.management.request"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Weste Management Request"
    _order = "west_mana_reqe"

    partner_id = fields.Many2one('res.partner', 'Request Farm Name')
    requested_support_name = fields.Char(String="Support Request Type")
    weste_requested_by = fields.Char(String="Support Request By")
    west_cluster_name = fields.Char(String="Cluster Name")
    weste_request_date = fields.Date(String='Request Date',required=True, readonly=True, index=True, copy=False, default=fields.Datetime.now)
    request_camp_name = fields.Char(related='partner_id.name',String='Farm Name')
    west_camp_email = fields.Char(related='partner_id.email',String='Farm Email')
    west_mana_reqe = fields.Char(string='Order Reference', required=True, copy=False, readonly=True, index=True,
                                default=lambda self: _('New'))

    @api.model
    def create(self, vals):
        vals['west_mana_reqe'] = self.env['ir.sequence'].next_by_code('waste.management.seq') or _('New')
        result = super(WasteManagementRequest, self).create(vals)
        return result


class WasteManagementProgress(models.Model):
    _name = "waste.management.pilot"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Waste Management Pilot"
    _order = "west_manage_sequs"

    west_manage_sequs = fields.Char(string='Order Reference', required=True, copy=False, readonly=True, index=True,
                                default=lambda self: _('New'))
    waste_request_id = fields.Many2one('waste.management.request', 'Request Name')
    request_farm = fields.Char(related='waste_request_id.request_camp_name',String='Request Farm')
    request_person = fields.Char(related='waste_request_id.weste_requested_by',String='Request By')
    date_reque = fields.Date(related='waste_request_id.weste_request_date', String='Request Date')
    date_vist = fields.Date(String='Date of Visit',required=True, readonly=True, index=True, copy=False, default=fields.Datetime.now)
    cluster_names = fields.Char(related='waste_request_id.west_cluster_name',String='Cluster Name')
    technology_name = fields.Char(String='Technology Selection')
    challenge = fields.Char(String='Challenge Encountered')
    state = fields.Selection([('draft','Draft'),
                              ('ongoing','On-going'),
                              ('completed','Completed'),
                              ], String='Progress Status', readonly=True,default='draft',track_visibility="always")
    vist_camp_email = fields.Char(related='waste_request_id.west_camp_email', String='Email')
    narrate_progress = fields.Html(String='Narrate Progress')

    @api.model
    def create(self, vals):
        vals['west_manage_sequs'] = self.env['ir.sequence'].next_by_code('waste.management.prog.seq') or _('New')
        result = super(WasteManagementProgress, self).create(vals)
        return result

    def action_ongoing(self):
        for rec in self:
            rec.state = 'ongoing'

    def action_completed(self):
        for rec in self:
            rec.state = 'completed'



