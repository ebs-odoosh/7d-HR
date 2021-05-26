# -*- coding: utf-8 -*-
{
    'name': "hr_employee_custom",

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
    'version': '0.7',

    # any module necessary for this one to work correctly
    'depends': ['base', 'contacts','security_groups', 'hr_core', 'hr_contract_custom', 'hr_recruitment_custom', 'hr_org_chart_overview', 'mail'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/contact_relation_type_view.xml',
        'views/views.xml',
        'views/employee_custom.xml',
        'data/sequence.xml',
        'views/templates.xml',
        'views/event_type.xml',
        'views/employee_event.xml',
        'views/employee_color_combo.xml',
        'wizards/log_note_wizard_view.xml',
        'report/employee_applicant_photo.xml',
        'data/cron_jobs.xml',
        'views/housing_settings_view.xml',
        'views/approve_employee_wiz.xml',
        # 'views/probation_wizard_custom.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
