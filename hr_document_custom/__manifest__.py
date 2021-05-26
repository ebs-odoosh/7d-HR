# -*- coding: utf-8 -*-
{
    'name': "company Documents",

    'summary': """
        This module contains custom modifications for QSsheild
        """,

    'description': """
       This module contains custom modifications for QSsheild
    """,

    'author': "Jaafar Khansa",
    'website': "http://www.ever-bs.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.6',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'contacts',
        'hr',
        'documents',
        'hr_employee_custom',
        'custom_org_chart'
        # 'documents_hr'
    ],

    # always loaded
    'data': [
        # 'cron/document_cron_job.xml',
        'data/sequence.xml',
        'wizards/create_contact_document_wiz.xml',
        'views/contacts_view_custom.xml',
        'views/document_custom.xml',
        'views/document_folder_custom.xml',
        # 'views/document_types_view.xml',
        'views/menus.xml',
        'views/employee_views.xml',
    ]
}
