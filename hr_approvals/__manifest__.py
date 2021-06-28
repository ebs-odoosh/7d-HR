# -*- coding: utf-8 -*-
{
    'name': "hr_approvals",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'HR',
    'version': '0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'security_groups', 'hr_core', 'hr_contract_custom', 'hr_employee_custom', 'mail', 'approvals'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/approval_security.xml',
        'views/views.xml',
        'views/templates.xml',
        'views/resignation_reasons.xml',
        'views/create_transfer_event_wiz.xml',
        'views/employee_event_type_custom.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}