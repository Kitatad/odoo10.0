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

class WecodeLobbySupportFprm(models.Model):
    ''' Defines an academic year '''
    _name = "lobby.support.form"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Lobby Support Form"
    _order = "lobby_seque"
    _rec_name = 'lobbyrequest_id'

    lobby_seque = fields.Char(string='Lobby Vist',required=True, copy=False, readonly=True, index=True,default=lambda self: _('New'))
    lobbyrequest_id = fields.Many2one('lobby.registration', 'Lobby Request Type',required=True,)
    request_person = fields.Char(related='lobbyrequest_id.requested_by',String='Request By')
    date_reque = fields.Date(related='lobbyrequest_id.request_date', String='Request Date')
    request_farm = fields.Char(related='lobbyrequest_id.farm_name', String='Request Date')
    date_vist = fields.Date(String='Date of Visit',required=True, readonly=True, index=True, copy=False, default=fields.Datetime.now)
    cluster_name = fields.Char(String='Cluster Name')
    support_provide = fields.Char(String='Support Provide')
    challenge = fields.Char(String='Challenge Encountered')
    state = fields.Selection([('draft','Draft'),
                              ('ong-going','On-going'),
                              ('completed','Completed'),
                              ], String='Status', readonly=True,default='draft',track_visibility="always")
    vist_camp_email = fields.Char(related='lobbyrequest_id.camp_email', String='Email')
    visite_history = fields.Html(String='Visit History',required=True,)

    @api.model
    def create(self, vals):
        vals['lobby_seque'] = self.env['ir.sequence'].next_by_code('lobby.visit.seq') or _('New')
        result = super(WecodeLobbySupportFprm, self).create(vals)
        return result
    # name_seque = fields.Char(string='Order Reference', required=True, copy=False, readonly=True,index=True, default=lambda self: _('New'))

    def action_ongoing(self):
        for rec in self:
            rec.state = 'ong-going'

    def action_completed(self):
        for rec in self:
            rec.state = 'completed'


class WecodeLobbyRequest(models.Model):
    ''' Defines an academic year '''
    _name = "lobby.request_last"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Lobby Request"
    _order = "lobby_requ_seque"
    _rec_name = 'request_name'

    partner_id = fields.Many2one('res.partner', 'Farm Name')
    lobby_requ_seque = fields.Char(string='Lobby Sequence', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))
    request_name = fields.Char(String='Support Request Type',required=True,)
    request_person = fields.Char(String='Request Person')
    request_date = fields.Date(String='Request Date', required=True, readonly=True, index=True, copy=False,
                               default=fields.Datetime.now)
    user_id = fields.Many2one('res.users', 'User ID', ondelete="cascade",
                              required=True, delegate=True)
    position = fields.Char(String='Position')
    comp_email = fields.Char(related='partner_id.email', String='Email')
    request_farm = fields.Char(related='partner_id.name', String='Request Farm')

    @api.model
    def create(self, vals):
        vals['lobby_requ_seque'] = self.env['ir.sequence'].next_by_code('lobby.request.seq') or _('New')
        result = super(WecodeLobbyRequest, self).create(vals)
        return result

    # @api.multi
    # def name_get(self):
    #     res = []
    #     for field in self:
    #         res.append((field.id, '%s %s' % (field.lobby_requ_seque, field.request_name)))
    #     return res


class WecodeIPMStudy(models.Model):
        _name = "ipm.study.tracking"
        _inherit = ['mail.thread', 'ir.needaction_mixin']
        _description = "IPM Study Progress Tracking"
        _order = "ipm_study_sequ"

        ipm_study_sequ = fields.Char(string='IPM Visit No', required=True, copy=False, readonly=True, index=True,
                                     default=lambda self: _('New'))
        ipm_request_id = fields.Many2one('ipm.study.request', 'IPM Request Name',required=True,)
        ipm_request_farm = fields.Char(related='ipm_request_id.camp_name', String='Request Farm')
        request_person = fields.Char(related='ipm_request_id.requested_by', String='Request By')
        date_reque = fields.Date(related='ipm_request_id.request_date', String='Request Date',required=True,)
        date_vist = fields.Date(String='Date of Visit', required=True, readonly=True, index=True, copy=False,
                                default=fields.Datetime.now)
        cluster_names = fields.Char(related='ipm_request_id.Cluster_name', String='Cluster Name')
        support_provide = fields.Char(String='Support Provide')
        challenge = fields.Char(String='Challenge Encountered')
        state = fields.Selection([('identification', 'Identification'),
                                  ('verification', 'Verification/Testing'),
                                  ('registration', 'Registration'),
                                  ('replication_other', 'Replication in other Farms'),
                                  ], String='Progress Status', readonly=True, default='identification',
                                 track_visibility="always")
        vist_camp_email = fields.Char(related='ipm_request_id.camp_email', String='Email')
        narrate_progress = fields.Html(String='Narrate Progress')

        @api.model
        def create(self, vals):
            vals['ipm_study_sequ'] = self.env['ir.sequence'].next_by_code('IPM.tracking.seq') or _('New')
            result = super(WecodeIPMStudy, self).create(vals)
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

class WecodeIPMStudyRequest(models.Model):
        _name = "ipm.study.request"
        _inherit = ['mail.thread', 'ir.needaction_mixin']
        _description = "IPM Study Request"
        _rec_name = 'requested_support'
        _order = "ipm_study_request_sequ"

        ipm_farm_name = fields.Char(string='Farm Name')
        requested_support = fields.Char(String="Support Request Type",required=True,)
        requested_by = fields.Char(String="Support Request By")
        Cluster_name = fields.Char(String="Cluster Name")
        request_date = fields.Date(String='Request Date', required=True, readonly=True, index=True, copy=False,
                                   default=fields.Datetime.now)
        camp_name = fields.Char(String='Farm Name')
        camp_email = fields.Char(String='Farm Email')
        ipm_study_request_sequ = fields.Char(string='IPM Request No', required=True, copy=False, readonly=True, index=True, default=lambda self: ('New'))

        @api.model
        def create(self, vals):
            vals['ipm_study_request_sequ'] = self.env['ir.sequence'].next_by_code('ipm.sequence.regstration.sequ') or ('New')
            result = super(WecodeIPMStudyRequest, self).create(vals)
            return result

        @api.multi
        def name_get(self):
            res = []
            for field in self:
                res.append((field.id, '%s %s' % (field.ipm_study_request_sequ, field.ipm_farm_name)))
            return res

class WecodeWasteManagementRequest(models.Model):
    _name = "waste.management.request"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Weste Management Request"
    _rec_name = 'requested_support_name'

    waste_farm = fields.Char(String="Request Farm Name", required=True)
    requested_support_name = fields.Char(String="Support Request Type",required=True)
    weste_requested_by = fields.Char(String="Support Request By",required=True)
    west_cluster_name = fields.Char(String="Cluster Name")
    weste_request_date = fields.Date(String='Request Date',required=True, readonly=True, index=True, copy=False, default=fields.Datetime.now)
    Service_Proposed_Date = fields.Date(String='Service Proposed Date',required=True,  index=True, copy=False)
    # request_camp_name = fields.Char(String='Farm Name')
    west_camp_email = fields.Char(String='Farm Email')
    west_mana_reqe = fields.Char(string='Order Reference', required=True, copy=False, readonly=True, index=True,
                                default=lambda self: _('New'))

    @api.model
    def create(self, vals):
        vals['west_mana_reqe'] = self.env['ir.sequence'].next_by_code('waste.management.seq') or ('New')
        result = super(WecodeWasteManagementRequest, self).create(vals)
        return result

    @api.multi
    def name_get(self):
        res = []
        for field in self:
            res.append((field.id, '%s %s' % (field.west_mana_reqe, field.waste_farm)))
        return res


class WecodeWasteManagementProgress(models.Model):
    _name = "waste.management.pilot"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Waste Management Pilot"
    # _order = "west_manage_sequs"

    west_manage_sequs = fields.Char(string='West Order Number', required=True, copy=False, readonly=True, index=True,
                                default=lambda self: _('New'))
    waste_request_id = fields.Many2one('waste.management.request', 'Request Name',required=True,)
    request_farm = fields.Char(related='waste_request_id.waste_farm',String='Request Farm')
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
        vals['west_manage_sequs'] = self.env['ir.sequence'].next_by_code('waste.management.prog.seq') or ('New')
        result = super(WecodeWasteManagementProgress, self).create(vals)
        return result

    def action_ongoing(self):
        for rec in self:
            rec.state = 'ongoing'

    def action_completed(self):
        for rec in self:
            rec.state = 'completed'


class WecodeAnnualFarmSurvey(models.Model):
    _name = "annual.farm.survey"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Annual Farm Information Survey"
    _order = "survey_seque"

    farm_survey = fields.Char(string='Farm Name',required=True)
    survey_seque = fields.Char(string='Survey Sequence', required=True, copy=False, readonly=True, index=True,
                                   default=lambda self: ('New'))
    developed_land = fields.Integer('Developed Land Size(in hek)')
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
    not_underproduction_business = fields.Char(String='Not Under Productions')
    custom_volume_exp = fields.Char(String='Volume of Export(year)')
    custom_value_exp = fields.Char(String='Value of Export(year)')
    national_volume_exp = fields.Char(String='Volume of Export(year)')
    national_value_exp = fields.Char(String='Value of Export(year)')
    survey_year =fields.Date(String='Year Of Survey',required=True, readonly=True, index=True, copy=False, default=fields.Datetime.now)

    @api.model
    def create(self, vals):
        vals['survey_seque'] = self.env['ir.sequence'].next_by_code('lobby.request.seq') or ('New')
        result = super(WecodeAnnualFarmSurvey, self).create(vals)
        return result
    
class WecodeClusterTaskForceComit(models.Model):
    _name = 'cluster.taskforce.met'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Cluster TaskForce Committee"
    # _order = "meeting_reqe"

    prepared_by = fields.Char(String='Prepared By',required=True)
    region_of_taskforce = fields.Char(Strings='Region of Task Force')
    venue_of_meeting = fields.Char(String='Venue of the Meeting')
    # date_of_meeting = fields.Date(String='Date Of Meetings',required=True, readonly=True,index=True,
    #                               copy=False,default=fields.Datetime.Now)
    meeting_agenda = fields.Char(String='Meeting Agenda',required=True)
    way_forward = fields.Html(String='Way Forward')
    # participant_id = fields.Many2many('participant.list','Participant List')

class WecodeParticipantList(models.Model):
    _name = 'participant.list'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Participant List"

    participant_name = fields.Char(String='Participant Name')
    organazition_name = fields.Char(String='Organization Name')


class WecodeLobbyRegistration(models.Model):
    ''' Defines an academic year '''
    _name = "lobby.registration"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Lobby Registration"


    farm_name = fields.Char('Request Farm Name')
    requested_support = fields.Char(String="Support Request Type", required=True, )
    requested_by = fields.Char(String="Support Request By")
    Cluster_name = fields.Char(String="Cluster Name")
    request_date = fields.Date(String='Request Date', required=True, readonly=True, index=True, copy=False,
                               default=fields.Datetime.now)
    position = fields.Char(String='Position')
    camp_email = fields.Char('Farm Email')
    lobby_registration_seque = fields.Char(string='Sequence', required=True, copy=False, readonly=True,
                                         index=True,
                                         default=lambda self: ('New'))

    @api.model
    def create(self, vals):
        vals['lobby_registration_seque'] = self.env['ir.sequence'].next_by_code('lobby.registration.seq') or _('New')
        result = super(WecodeLobbyRegistration, self).create(vals)
        return result

    @api.multi
    def name_get(self):
        res = []
        for field in self:
            res.append((field.id, '%s %s' % (field.lobby_registration_seque, field.farm_name)))
        return res

class LegaleDocument(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'
    _description = 'Partner'

    document_ids = fields.One2many('legale.document', 'certife_id',
                                      'Certificate')
    business_document1= fields.Binary('Business Document 1', required=True)
    business_document2= fields.Binary('Business Document 2', required=True)
    investment_document1= fields.Binary('Investment Document 1', required=True)
    investment_document2= fields.Binary('Investment Document 2', required=True)

class LegaleCertificate(models.Model):
    _name = "legale.document"

    certife_id = fields.Many2one('res.partner', 'Document')
    description = fields.Char('Document Type')
    document_number = fields.Char('Document Number')
    certi = fields.Binary('Certificate', required=True)
    date_renewable = fields.Date('Renewal Validity Year')


class MonitoringTrackingTool(models.Model):
    _name = "monitoring.tracking.tool"
    _description = "Monitoring Tracking Tool"
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    farm_name = fields.Char(String='Farm Name')
    farm_name_land_size = fields.Char(String='Farm Name Size')
    developed = fields.Char(String='Developed ')
    undeveloped = fields.Char(String='Undeveloped ')
    additional_expansion = fields.Char(String='Additional Expansion')
    cut_flower = fields.Boolean(String='Cut Flower')
    fruit = fields.Boolean(String='Fruit')
    vegertables = fields.Boolean(String='Vegetebel')
    herbs = fields.Boolean(String='Herbs')
    area_not_production = fields.Char(String='Area not under Production')
    managerial = fields.Integer('Managerial')
    daily_laborer = fields.Integer('Daily Laborer')
    total_work_force = fields.Integer('Total Work Force')
    wage_rate = fields.Integer('Wage rate')
    workers_productivity = fields.Integer('Workers productivity')
    productivity= fields.Integer('Productivity')
    market_destination = fields.Integer('Market Destination country/ies')
    volume_of_export = fields.Integer('Volume of export')
    value_of_export = fields.Integer('Value of export')

class WecodeGenderSupportRequest(models.Model):
    _name = "gender.support.request"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Gender Support Request"
    _rec_name = 'gender_requested_support'
    _order = "gender_study_request_sequ"

    gender_farm_name = fields.Char(string='Farm Name')
    gender_requested_support = fields.Char(String="Support Request Type", required=True, )
    gender_requested_by = fields.Char(String="Support Request By")
    gender_Cluster_name = fields.Char(String="Cluster Name")
    gender_request_date = fields.Date(String='Request Date', required=True, readonly=True, index=True, copy=False,
                                   default=fields.Datetime.now)
    Service_Proposed_Date = fields.Date(String='Service Proposed Date', required=True, index=True, copy=False)
    camp_name = fields.Char(String='Farm Name')
    camp_email = fields.Char(String='Farm Email')
    gender_study_request_sequ = fields.Char(string='Gender Request No', required=True, copy=False, readonly=True,
                                             index=True, default=lambda self: ('New'))

    @api.model
    def create(self, vals):
        vals['gender_study_request_sequ'] = self.env['ir.sequence'].next_by_code('gender.sequence.regstration.sequ') or (
                'New')
        result = super(WecodeGenderSupportRequest, self).create(vals)
        return result

    @api.multi
    def name_get(self):
        res = []
        for field in self:
            res.append((field.id, '%s %s' % (field.gender_study_request_sequ, field.gender_farm_name)))
        return res

class WecodeGenderStudy(models.Model):
    _name = "gender.study.tracking"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Gender Study Progress Tracking"
    _order = "gender_study_sequ"

    gender_study_sequ = fields.Char(string='Gender Visit No', required=True, copy=False, readonly=True, index=True,
                                        default=lambda self: _('New'))
    gender_request_id = fields.Many2one('gender.support.request', 'Gender Support Request Name', required=True, )
    gender_request_farm = fields.Char(related='gender_request_id.camp_name', String='Request Farm')
    gender_request_person = fields.Char(related='gender_request_id.gender_requested_by', String='Request By')
    gender_date_reque = fields.Date(related='gender_request_id.gender_request_date', String='Request Date',
                                        required=True, )
    gender_date_vist = fields.Date(String='Date of Visit', required=True, readonly=True, index=True, copy=False,
                                       default=fields.Datetime.now)
    gender_visit_cluster_names = fields.Char(related='gender_request_id.gender_Cluster_name', String='Cluster Name')
    gender_support_provide = fields.Char(String='Support Provide')
    gender_challenge = fields.Char(String='Challenge Encountered')
    state = fields.Selection([('identification', 'Identification'),
                                  ('verification', 'Verification/Testing'),
                                  ('registration', 'Registration'),
                                  ('replication_other', 'Replication in other Farms'),
                                  ], String='Progress Status', readonly=True, default='identification',
                                 track_visibility="always")
    vist_camp_email = fields.Char(related='gender_request_id.camp_email', String='Email')
    gender_narrate_progress = fields.Html(String='Narrate Progress')

    @api.model
    def create(self, vals):
        vals['gender_study_sequ'] = self.env['ir.sequence'].next_by_code('gender.tracking.seq') or _('New')
        result = super(WecodeGenderStudy, self).create(vals)
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


    # # @api.depends('stage_id', 'timesheet_ids.unit_amount', 'planned_hours', 'child_ids.stage_id',
    # #              'child_ids.planned_hours', 'child_ids.effective_hours', 'child_ids.children_hours', 'child_ids.timesheet_ids.unit_amount')
    # # def _hours_get(self):
    # #     for task in self.sorted(key='id', reverse=True):
    # #         children_hours = 0
    # #         for child_task in task.child_ids:
    # #             if child_task.stage_id and child_task.stage_id.fold:
    # #                 children_hours += child_task.effective_hours + child_task.children_hours
    # #             else:
    # #                 children_hours += max(child_task.planned_hours, child_task.effective_hours + child_task.children_hours)
    # #
    # #         task.children_hours = children_hours
    # #         task.effective_hours = sum(task.timesheet_ids.mapped('unit_amount'))
    # #         task.remaining_hours = task.planned_hours - task.effective_hours - task.children_hours
    # #         task.total_hours = max(task.planned_hours, task.effective_hours)
    # #         task.total_hours_spent = task.effective_hours + task.children_hours
    # #         task.delay_hours = max(-task.remaining_hours, 0.0)
    # #
    # #         if task.stage_id and task.stage_id.fold:
    # #             task.progress = 100.0
    # #         elif (task.planned_hours > 0.0):
    # #             task.progress = round(100.0 * (task.effective_hours + task.children_hours) / task.planned_hours, 2)
    # #         else:
    # #             task.progress = 0.0
    #
    # remaining_hours = fields.Float(compute='_hours_get', store=True, string='Target Progress', help="Total remaining time, can be re-estimated periodically by the assignee of the task.")
    # effective_hours = fields.Float(compute='_hours_get', store=True, string='Hours Spent', help="Computed using the sum of the task work done.")
    # total_hours = fields.Float(compute='_hours_get', store=True, string='Total', help="Computed as: Time Spent + Remaining Time.")
    # total_hours_spent = fields.Float(compute='_hours_get', store=True, string='Total Hours', help="Computed as: Time Spent + Sub-tasks Hours.")
    # progress = fields.Float(compute='_hours_get', store=True, string='Target Progress in Percent', group_operator="avg")
    # delay_hours = fields.Float(compute='_hours_get', store=True, string='Delay Hours', help="Computed as difference between planned hours by the project manager and the total hours of the task.")
    # children_hours = fields.Float(compute='_hours_get', store=True, string='Sub-tasks Hours', help="Sum of the planned hours of all sub-tasks (when a sub-task is closed or its spent hours exceed its planned hours, spent hours are counted instead)")
    # timesheet_ids = fields.One2many('account.analytic.line', 'task_id', 'Timesheets')
    #
    #
    # # _constraints = [(models.BaseModel._check_recursion, 'Circular references are not permitted between tasks and sub-tasks', ['parent_id'])]
    #
