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


class IPMStudy(models.Model):
    _name = "ipm.study.tracking"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "IPM Study Progress Tracking"
    _order = "ipm_study_sequ"

    ipm_study_sequ = fields.Char(string='Order Reference', required=True, copy=False, readonly=True, index=True,
                                default=lambda self: _('New'))
    ipm_request_id = fields.Many2one('ipm.study.request', 'IPM Request Name')
    ipm_request_farm = fields.Char(related='ipm_request_id.camp_name',String='Request Farm')
    request_person = fields.Char(related='ipm_request_id.requested_by',String='Request By')
    date_reque = fields.Date(related='ipm_request_id.request_date', String='Request Date')
    date_vist = fields.Date(String='Date of Visit',required=True, readonly=True, index=True, copy=False, default=fields.Datetime.now)
    cluster_names = fields.Char(related='ipm_request_id.Cluster_name',String='Cluster Name')
    support_provide = fields.Char(String='Support Provide')
    challenge = fields.Char(String='Challenge Encountered')
    state = fields.Selection([('identification','Identification'),
                              ('verification','Verification/Testing'),
                              ('registration','Registration'),
                              ('replication_other','Replication in other Farms'),
                              ], String='Progress Status', readonly=True,default='identification',track_visibility="always")
    vist_camp_email = fields.Char(related='ipm_request_id.camp_email', String='Email')
    narrate_progress = fields.Html(String='Narrate Progress')

    @api.model
    def create(self, vals):
        vals['ipm_study_sequ'] = self.env['ir.sequence'].next_by_code('lobby.visit.seq') or _('New')
        result = super(IPMStudy, self).create(vals)
        return result

    def action_verification(self):
        for rec in self:
            rec.state = 'verification'

    def action_registration(self):
        for rec in self:
            rec.state = 'registration'

    def action_replication(self):
        for rec in self:
            rec.state = 'replication_other'


class IPMStudyRequest(models.Model):
    _name = "ipm.study.request"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "IPM Study Request"
    _order = "ipm_study_request_sequ"

    partner_id = fields.Many2one('res.partner', 'Request Farm Name')
    requested_support = fields.Char(String="Support Request Type")
    requested_by = fields.Char(String="Support Request By")
    Cluster_name = fields.Char(String="Cluster Name")
    request_date = fields.Date(String='Request Date',required=True, readonly=True, index=True, copy=False, default=fields.Datetime.now)
    camp_name = fields.Char(related='partner_id.name',String='Farm Name')
    camp_email = fields.Char(related='partner_id.email',String='Farm Email')
    ipm_study_request_sequ = fields.Char(string='Order Reference', required=True, copy=False, readonly=True, index=True,
                                default=lambda self: _('New'))


    @api.model
    def create(self, vals):
        vals['ipm_study_request_sequ'] = self.env['ir.sequence'].next_by_code('ipm.study.seq') or _('New')
        result = super(IPMStudyRequest, self).create(vals)
        return result