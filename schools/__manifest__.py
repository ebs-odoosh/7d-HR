# -*- coding: utf-8 -*-
{
    'name': "school",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Schools information
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '1.0.3',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr_payroll', 'security_rules'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/schools_views.xml',
        'views/school_terms_and_fees_view.xml'
    ],
}
