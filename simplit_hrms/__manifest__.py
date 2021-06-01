# -*- coding: utf-8 -*-
{
    'name': "simplit_hrms",
    'summary': """ """,
    'description': """ """,
    'author': "Simplit",
    'website': "http://www.simplit.me",
    'category': 'HRMS',
    'version': '12.0.1',
    'depends': ['base','hr','hr_contract'],
    'data': [
        'security/ir.model.access.csv',
        'views/data.xml',
        'views/menuitem_update.xml',
        'views/res_company_view.xml',
        'views/res_bank_view.xml',
        'views/employee_documents_view.xml',
        'views/service_provider.xml',
        'views/hr_contract.xml',
        'views/hr_employee_view.xml',
    ],
    'demo': [],
}