##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>)
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
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

from odoo import api, fields, models, _
from odoo.exceptions import UserError



class part_sms(models.TransientModel):
    _name = 'part.sms'

    @api.model
    def _default_get_gateway(self):
        if self._context is None:
            self._context = {}
        sms_obj = self.env['sms.smsclient']
        gateway_ids = sms_obj.search([], limit=1)
        return gateway_ids and gateway_ids[0] or False

    @api.onchange('gateway')
    def onchange_gateway_mass(self):
        if self.gateway:
            self.validity = self.gateway.validity 
            self.classes  = self.gateway.classes
            self.deferred = self.gateway.deferred
            self.priority = self.gateway.priority
            self.coding   = self.gateway.coding
            self.tag      = self.gateway.tag
            self.nostop   = self.gateway.nostop

    @api.multi
    def sms_mass_send(self):
        client_obj = self.env['sms.smsclient']
        partner_obj = self.env['res.partner']
        active_ids = self._context.get('active_ids')
        for data in self:
            if not data.gateway:
                raise UserError(_('You can only select one partner'))
            else:
                for partner in partner_obj.browse(active_ids):
                    data.mobile_to = partner.mobile
                    client_obj.send_msg(data)
        return True

    gateway = fields.Many2one('sms.smsclient', 'SMS Gateway', required=True, default = _default_get_gateway)
    text  = fields.Text('Text', required=True)
    validity  = fields.Integer('Validity',
            help='The maximum time -in minute(s)- before the message is dropped')
    classes = fields.Selection([
                ('0', 'Flash'),
                ('1', 'Phone display'),
                ('2', 'SIM'),
                ('3', 'Toolkit')
            ], 'Class',
            help='The SMS class: flash(0),phone display(1),SIM(2),toolkit(3)', default ='1')
    deferred = fields.Integer('Deferred',
            help='The time -in minute(s)- to wait before sending the message')
    priority = fields.Selection([
                ('0', '0'),
                ('1', '1'),
                ('2', '2'),
                ('3', '3')
            ], 'Priority', help='The priority of the message')
    coding  = fields.Selection([
                ('1', '7 bit'),
                ('2', 'Unicode')
            ], 'Coding', help='The sms coding: 1 for 7 bit or 2 for unicode')
    tag  = fields.Char('Tag', size=256, help='An optional tag')
    nostop = fields.Boolean('NoStop', help='Do not display STOP clause in the message, this requires that this is not an advertising message', default = True )


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
