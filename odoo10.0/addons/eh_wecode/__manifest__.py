# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

{
    'name': 'WECODE_EHPEA',
    'version': '10.0.1.0.2',
    'author': '''WECODE ICT Solution PLC.''',
    'website': 'http://www.Wecodethiopia.com',
    'category': 'EHPEA Customer  Management',
    'license': "AGPL-3",
    'complexity': 'easy',
    'Summary': 'A Module For EHPE CR Management',
    'images': ['static/description/EMS.jpg'],
    'depends': ['hr', 'crm', 'report', 'account', 'account_accountant','mail'],
    'data': [
             'views/wecode_ehpea_views.xml',
             'views/template.xml',
             'views/website_form.xml',
             'views/registration_exhibitor_views.xml',
             'data/wecode_ehpea_sequence.xml',
             'reports/report.xml',
             'reports/report_lobby_support.xml',
             'reports/report_lobby_support_main.xml',
             'security/ir.model.access.csv',
             'security/security.xml',
             ],
    'installable': True,
    'application': True
}
