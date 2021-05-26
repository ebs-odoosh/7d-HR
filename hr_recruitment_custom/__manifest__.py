# -*- coding: utf-8 -*-
{
    'name': "hr_recruitment",

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
    'depends': ['base','hr_recruitment','hr_recruitment_survey','hr_core','website_hr_recruitment'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'data/config_data.xml',
        'views/templates.xml',
        'views/job_custom.xml',
        'views/position_default_signatures.xml',
        'report/applicant_photo.xml',
        'views/view_survey_survey.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}