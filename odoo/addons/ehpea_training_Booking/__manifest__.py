# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

{
    'name': 'WECODE_Training_Booking_form',
    'version': '10.0.1.0.2',
    'author': '''WECODE ICT Solution PLC.''',
    'website': 'http://www.Wecodethiopia.com',
    'category': 'Training Department Booking Form',
    'license': "AGPL-3",
    'complexity': 'easy',
    'Summary': 'A Module For EHPE Training Department Booking',
    'images': ['static/description/EMS.jpg'],
    'depends': ['hr', 'crm', 'report', 'account', 'account_accountant','mail'],
    'data': [
             'views/training_ehpe.xml',
             'data/training_sequnce.xml',
             'security/ir.model.access.csv',
             ],
    'installable': True,
    'application': True
}
