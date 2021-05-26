# -*- coding: utf-8 -*-
{
    'name': "Custom Org Chart",

    'summary': """
        Custom App for Org Chart""",

    'description': """
        
    """,

    'author': "EBS",
    'website': "http://www.ever-bs.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'OrgChart',
    'version': '0.3',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr_contract_custom'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        # 'views/views.xml',
        'views/templates.xml',
        'views/job_position_custom.xml',
        'views/contract_custom.xml',
        'views/contact_signatures.xml',
#         'views/sap_settings_view.xml',
#         'data/cron_jobs.xml',
        # 'views/employment_type_custom.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
