# -*- coding: utf-8 -*-
{
    'name': "EBS HR Applicant",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'HR',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'hr_approvals',
        'hr_recruitment_custom',
        'res_company_custom'
    ],

    # always loaded
    'data': [
        # 'views/hr_department.xml',
        'views/hr_recruitment_questions.xml',
        'views/hr_recruitment_employment_history_views.xml',
        'views/hr_recruitment_views.xml',
        # 'views/website_hr_recruitment_templates.xml',
        # 'views/templates.xml',
        # 'views/hr_applicant_survey.xml',
        # 'views/approval_request.xml',
        'views/hr_employee.xml',
    ]
}
