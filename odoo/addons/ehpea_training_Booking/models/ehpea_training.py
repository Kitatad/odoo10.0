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

class EhpeaTrainingBooking(models.Model):
    ''' Defines an academic year '''
    _name = "training.department.book"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Training Department Booking"

    training_booking_seque =fields.Char(string='Booking Sequence', required=True, copy=False, readonly=True, index=True,
                                   default=lambda self: ('New'))
    farm_name = fields.Char(String='Farm Name', required=True)
    farm_location = fields.Char(String='Farm Location',required=True)
    contact_person = fields.Char(String='Contact Person For the Training',required=True)
    position = fields.Char(String='Postion')
    tel = fields.Char(String='Tel')
    cell_phone = fields.Char(String='Cell Phone')
    email = fields.Char(String='E-mail')
    safe_use_of_pesticide = fields.Boolean(String='Safe Use of Pesticide')
    planned_date_safe = fields.Date( String='Planned Date For the Safe Use of Pesticide Training')
    number_of_safepesticide= fields.Integer('No of Safe Use of Pesticide Trainer')
    pesticide_store = fields.Boolean(String='Pesticide Store')
    planned_date_pesticide = fields.Date(String='Plan Date For the Pesticide Store Training')
    number_of_pesticide_store = fields.Integer('No of Pesticide Store Trainer')
    supervision_skill = fields.Boolean(String='Supervision Skill')
    planned_date_supervision = fields.Date(String='Plan Date For the Supervision Skill Training')
    number_of_supervision = fields.Integer('No of Supervision Skill Trainer')
    crop_scouting = fields.Boolean(String='Crop Scouting')
    planned_date_crop = fields.Date(String='Plan Date For the Crop Scouting Training')
    number_of_crop_scouting = fields.Integer('No of Crop Scouting Trainer')
    internal_auditing = fields.Boolean(String='Internal Auditing')
    planned_date_internal = fields.Date(String='Plan Date For the Internal Auditing Training')
    number_of_internal_auditing = fields.Integer('No of Internal Auditing Trainer')
    environment_officer = fields.Boolean(String='Environment Officer')
    planned_date_officer = fields.Date(String='Planned Date For the Environment Officer Training')
    number_of_enviroment_officer = fields.Integer('No of Environment Officer Trainer')
    environment = fields.Boolean(String='Environment')
    planned_date_environment = fields.Date(String='Planned Date For the Environment Training')
    number_enviroment = fields.Integer('No of Environment Trainer')
    farm_safety_officer = fields.Boolean(String='Farm Safety Officer')
    planned_date_safety_officer = fields.Date(String='Planned Date For the Safety Officer Training')
    number_farm_safety_officer = fields.Integer('No of Farm Safety Officer Trainer')
    farm_safety = fields.Boolean(String='Farm Safety')
    planned_date_farm_safety = fields.Date(String='Planned Date For the Safety Training')
    number_farm_safety = fields.Integer('NO Farm Safety')
    other = fields.Char(String='Other')
    planned_date_other = fields.Date(String='Plan Date For the other Training')
    number_other = fields.Integer('Numbers')
    IPM_one = fields.Boolean(string='IPM')
    plane_date_IPM_one = fields.Date(String='Plan date For IMP One Trainer')
    number_of_IPM_One_trainer = fields.Integer('Number of IPM Trainer ')
    IPM_Two = fields.Boolean(string='IPM Two')
    plane_date_IPM_Two = fields.Date(string='Plan Date for IPM tow Trainer')
    number_of_IPM_two_trainer = fields.Integer(string='No IPM Two Trainer')
    waste_management = fields.Boolean('Waste Management Trainer')
    date_waste_management = fields.Integer(string='Schedule Time')
    number_waste_management = fields.Integer(String='Number of Waste Management Training')
    Gender_Sensitive_Management = fields.Boolean(String='Gender Sensitive Management')
    date_Gender_sensitive_management = fields.Date('Schedule Time')
    number_of_gender_sensitive_management_trainer = fields.Integer(String='Number of Gender Trainer')
    workplace_sexual_harassment = fields.Boolean(strin='Workplace Sexual Harassment')
    date_work_place_harassment = fields.Date(String='Schedule Time')
    number_of_trainer_work = fields.Integer(String='No of Workplace sexual Harassment Trainer')
    gender_base_violence = fields.Boolean('Gender Based Violence')
    date_of_training_gender_base_violence = fields.Date(String='Schedule Date for the Training')
    number_of_trainer_gender_base_violence = fields.Integer(String='No of Gender base violence Trainer')
    hygiene_training = fields.Boolean('Hygiene Training')
    date_of_hygiene_training = fields.Date(String='Schedule Date')
    number_of_hygiene_trainer = fields.Integer(string='No of Hygiene Trainer')
    family_planning = fields.Boolean('Family planning')
    date_of_family_planning = fields.Date(Sting='Schedule Date')
    number_of_family_planning_trainer = fields.Integer(String='No of Family Planning Trainer')
    total_number = fields.Integer(String='Total number of Trainer')


    @api.model
    def create(self, vals):
        vals['training_booking_seque'] = self.env['ir.sequence'].next_by_code('training.booking.seq') or _('New')
        result = super(EhpeaTrainingBooking, self).create(vals)
        return result