# -*- coding: utf-8 -*-
{
    'name': "hr_core",

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
    'version': '0.4',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr', 'web','security_groups'],

    # always loaded
    'data': [

        'security/ir.model.access.csv',
        'views/hr_core_views.xml',
        'data/data_sequence.xml',
        'views/templates.xml',
    ],
    'qweb': [
        'views/templates-qweb.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
