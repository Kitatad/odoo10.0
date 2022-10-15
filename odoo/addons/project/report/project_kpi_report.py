# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, tools

class ReportTaskReport(models.Model):
    _name = "report.kpi.task."
    _description = "General KPI Report"
    _order = 'name desc, project_id'
    _auto = False


    name = fields.Char(string='Task Title', readonly=True)
    user_id = fields.Many2one('res.users', string='Assigned To', readonly=True)
    date_start = fields.Datetime(string='Assignation Date', readonly=True)
    no_of_days = fields.Integer(string='# Working Days', readonly=True)
    date_end = fields.Datetime(string='Ending Date', readonly=True)
    date_deadline = fields.Date(string='Deadline', readonly=True)
    date_last_stage_update = fields.Datetime(string='Last Stage Update', readonly=True)
    project_id = fields.Many2one('project.project', string='Project', readonly=True)
    closing_days = fields.Float(string='# Days to Close',
        digits=(16,2), readonly=True, group_operator="avg",
        help="Number of Days to close the task")
    opening_days = fields.Float(string='# Days to Assign',
        digits=(16,2), readonly=True, group_operator="avg",
        help="Number of Days to Open the task")
    delay_endings_days = fields.Float(string='# Days to Deadline', digits=(16,2), readonly=True)
    nbr = fields.Integer('# of Tasks', readonly=True)  # TDE FIXME master: rename into nbr_tasks
    priority = fields.Selection([
            ('0','Low'),
            ('1','Normal'),
            ('2','High')
        ], size=1, readonly=True)
    state = fields.Selection([
            ('normal', 'In Progress'),
            ('blocked', 'Blocked'),
            ('done', 'Ready for next stage')
        ], string='Kanban State', readonly=True)
    company_id = fields.Many2one('res.company', string='Company', readonly=True)
    partner_id = fields.Many2one('res.partner', string='Contact', readonly=True)
    stage_id = fields.Many2one('project.task.type', string='Stage', readonly=True)
    task_id = fields.Many2one('project.task',string='KPI')
    report_list = fields.Char(related='task_id.task_report',String='Report')
    task_start_date = fields.Char(related='task_id.date_start',String='Start Date')
    task_end_date = fields.Char(related='task_id.date_end',String='Start Date')
    task_end_date = fields.Char(related='task_id.date_end',String='Start Date')
    project_id = fields.Many2one('project.project', string='Project')
