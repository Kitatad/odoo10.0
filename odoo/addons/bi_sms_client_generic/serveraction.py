# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2013 Julius Network Solutions SARL <contact@julius.fr>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import api, fields, models, _
from odoo.tools.safe_eval import safe_eval
import time
import logging
import urllib
from odoo import tools

_logger = logging.getLogger('smsclient')

class ServerAction(models.Model):
    """
    Possibility to specify the SMS Gateway when configure this server action
    """
    _inherit = 'ir.actions.server'

    @api.model
    def _get_states(self):
        """ Override me in order to add new states in the server action. Please
        note that the added key length should not be higher than already-existing
        ones. """
        return [('code', 'Execute Python Code'),
                ('trigger', 'Trigger a Workflow Signal'),
                ('client_action', 'Run a Client Action'),
                ('object_create', 'Create or Copy a new Record'),
                ('object_write', 'Write on a Record'),
                ('multi', 'Execute several actions'),
                ('sms', 'Run a SMS Gateway')]

    action_type = fields.Selection([('sms','SMS')], 'Action Type')
    sms =  fields.Char('sms')
    mobile = fields.Char('Mobile')
    sms_server = fields.Many2one('sms.smsclient', 'SMS Server',
            help='Select the SMS Gateway configuration to use with this action')
    sms_template_id  = fields.Many2one('mail.template', 'SMS Template',
            help='Select the SMS Template configuration to use with this action')

    @api.multi
    def run(self):
        """ Runs the server action. For each server action, the condition is
        checked. Note that a void (``False``) condition is considered as always
        valid. If it is verified, the run_action_<STATE> method is called. This
        allows easy overriding of the server actions.

        :param dict context: context should contain following keys

                             - active_id: id of the current object (single mode)
                             - active_model: current model that should equal the action's model

                             The following keys are optional:

                             - active_ids: ids of the current records (mass mode). If active_ids
                               and active_id are present, active_ids is given precedence.

        :return: an action_id to be executed, or False is finished correctly without
                 return action
        """
        res = False
        for action in self:
            eval_context = self._get_eval_context(action)
            condition = action.condition
            if condition is False:
                # Void (aka False) conditions are considered as True
                condition = True
            if hasattr(self, 'run_action_%s_multi' % action.state):
                expr = safe_eval(str(condition), eval_context)
                if not expr:
                    continue
                # call the multi method
                run_self = self.with_context(eval_context['context'])
                func = getattr(run_self, 'run_action_%s_multi' % action.state)
                res = func(action, eval_context=eval_context)

            elif hasattr(self, 'run_action_%s' % action.state):
                active_id = self._context.get('active_id')
                if not active_id and self._context.get('onchange_self'):
                    active_id = self._context['onchange_self']._origin.id
                active_ids = self._context.get('active_ids', [active_id] if active_id else [])
                for active_id in active_ids:
                    # run context dedicated to a particular active_id
                    run_self = self.with_context(active_ids=[active_id], active_id=active_id)
                    eval_context["context"] = run_self._context
                    expr = safe_eval(str(condition), eval_context)
                    if not expr:
                        continue
                    # call the single method related to the action: run_action_<STATE>
                    func = getattr(run_self, 'run_action_%s' % action.state)
                    res = func(action, eval_context=eval_context)
            obj_pool = self.env[action.model_id.model]
            obj = obj_pool.browse(self._context.get('active_id', False))
            email_template_obj = self.env['mail.template']
            cxt = {
                'context': self._context,
                'object': obj,
                'time': time,
                'cr': self._cr,
                'pool': self.env,
                'uid': self._uid,
            }
            expr = eval(str(action.condition), cxt)
            if not expr:
                continue
            if action.state == 'sms':
                _logger.info('Send SMS')
                queue_obj = self.env['sms.smsclient.queue']
                mobile = str(action.mobile)
                to = None
                try:
                    cxt.update({'gateway': action.sms_server})
                    gateway = action.sms_server
                    if mobile:
                        to = eval(action.mobile, cxt)
                    res_id = self._context.get('active_id')
                    template = action.sms_template_id.get_email_template(res_id)
                    values = {}
                    for field in ['subject', 'body_html', 'email_from',
                                  'email_to', 'email_cc', 'reply_to']:
                        values[field] = email_template_obj.render_template( getattr(template, field),
                                                             template.model, res_id) \
                                                             or False
                    url = gateway.url
                    body_alternative = tools.html2plaintext(values['body_html'])
                    if gateway.method == 'http':
                        prms = {}
                        for p in gateway.property_ids:
                            if str(p.type) == 'sender':
                                prms[str(p.name)] = str(p.value)
                            elif str(p.type) == 'user':
                                prms[str(p.name)] = str(p.value)
                            elif str(p.type) == 'password':
                                prms[str(p.name)] = str(p.value)
                            elif str(p.type) == 'to':
                                prms[str(p.name)] = str(mobile)
                            elif str(p.type) == 'sms':
                                prms[str(p.name)] = str(body_alternative)
                            elif str(p.type) == 'extra':
                                prms[str(p.name)] = str(p.value)
                        params = urllib.urlencode(prms)
                        name = url + "?" + params
                    vals ={
                        'name': name or url,
                        'gateway_id': gateway.id,
                        'state': 'draft',
                        'mobile': to,
                        'msg': body_alternative,
                        'validity': gateway.validity, 
                        'classes': gateway.classes, 
                        'deferred': gateway.deferred, 
                        'priority': gateway.priority, 
                        'coding': gateway.coding,
                        'tag': gateway.tag, 
                        'nostop': gateway.nostop,
                    }
                    sms_in_q = queue_obj.search([
                        ('name','=',name or url),
                        ('gateway_id','=',gateway.id),
                        ('state','=','draft'),
                        ('mobile','=',to),
                        ('msg','=',body_alternative),
                        ('validity','=',gateway.validity), 
                        ('classes','=',gateway.classes), 
                        ('deferred','=',gateway.deferred), 
                        ('priority','=',gateway.priority), 
                        ('coding','=',gateway.coding),
                        ('tag','=',gateway.tag), 
                        ('nostop','=',gateway.nostop)
                        ])
                    if not sms_in_q:
                        queue_obj.create(vals)
                        _logger.info('SMS successfully send to : %s' % (to))
                except Exception, e:
                    _logger.error('Failed to send SMS : %s' % repr(e))
        return res


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
