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

class ClusterTaskForceComit(models.Model):
    _name = 'cluster.taskforce.met'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Cluster TaskForce Committee"
    # _order = "meeting_reqe"

    prepared_by = fields.Char(String='Prepared By',required=True)
    region_of_taskforce = fields.Char(Strings='Region of Task Force')
    venue_of_meeting = fields.Char(String='Venue of the Meeting')
    date_of_meeting = fields.Date(String='Date Of Meetings',required=True, readonly=True,index=True,
                                  copy=False,default=fields.Datetime.Now)
    meeting_agenda = fields.Char(String='Meeting Agenda',required=True)
    way_forward = fields.Html(String='Way Forward')
    # participant_id = fields.Many2many('participant.list','Participant List')

class ParticipantList(models.Model):
    _name = 'participant.list'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Participant List"

    participant_name = fields.Char(String='Participant Name')
    organazition_name = fields.Char(String='Organization Name')


