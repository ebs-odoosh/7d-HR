# -*- coding: utf-8 -*-
{
    'name': "security_rules",

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
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr','website','hr_appraisal','hr_contract', 'security_groups', 'hr_employee_custom','hr_recruitment','documents','survey','hr_org_chart_overview'],

    # always loaded
    'data': [
        # 'views/user_roles.xml',
        'views/user_rules.xml',
        'views/menu_items.xml',
        'views/res_user_view.xml',
        'security/ir.model.access.csv',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
