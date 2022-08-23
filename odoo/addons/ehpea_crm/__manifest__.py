# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

{
    'name': 'EHPEA',
    'version': '10.0.1.0.1',
    'author': '''WECODE ICT Solution PLC.''',
    'website': 'http://www.Wecodethiopia.com',
    'category': 'EHPEA Customer  Management',
    'license': "AGPL-3",
    'complexity': 'easy',
    'Summary': 'A Module For EHPE CR Management',
    'images': ['static/description/EMS.jpg'],
    'depends': ['hr', 'crm', 'report', 'account', 'account_accountant','mail'],
    'data': ['views/ehpe_crm.xml',
             'data/ehpe_sequence.xml',
             ],
    'installable': True,
    'application': True
}
