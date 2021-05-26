# -*- coding: utf-8 -*-

{
    'name': 'res_company_custom',
    'description': 'res_company_custom',
    'version': '1.0',
    'summary': 'res_company_custom',
    'license': 'OPL-1',
    'author': 'TechUltra Solutions Pvt. Ltd.',
    'website': 'https://www.techultrasolutions.com/',
    'images': [],
    'category': 'uncategorized',
    'description': """ res_company_custom""",
    'depends': ['base'],
    'data': ['views/res_company_view.xml',
             'views/res_country_view.xml',
             'reports/custom_layout.xml',
             'reports/paper_format.xml'],
    'auto_install': False,
}
