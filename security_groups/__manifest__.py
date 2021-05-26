# -*- coding: utf-8 -*-
{
    'name': "Security Groups",

    'summary': """
        This Module contains Security Groups Used in All Modules""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Everteam Business Solution",
    'website': "https://www.everteam.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'hr',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr','hr_contract','hr_appraisal','hr_recruitment','documents','survey'],

    # always loaded
    'data': [
        'views/security_groups.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
