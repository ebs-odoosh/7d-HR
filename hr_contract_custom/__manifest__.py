# -*- coding: utf-8 -*-
{
    'name': "hr_contract",

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
    'version': '0.3',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr_contract', 'security_groups', 'hr_recruitment_custom', 'hr_core', 'survey', 'resource'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'report/job_offer_report.xml',
        'report/probation_assessment_report.xml',
        'report/probation_confirmation_letter_report.xml',
        'report/probation_extension_letter_report.xml',
        'report/resignation_report.xml',
        'data/mail_template.xml',
        'data/data_sequence.xml',
        'wizard/job_offer_send_views.xml',
        'views/views.xml',
        'views/templates.xml',
        'views/contract_custom.xml',
        'views/contract_compensation.xml',
        'views/view_survey_survey.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],

}
