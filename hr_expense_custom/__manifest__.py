# -*- coding: utf-8 -*-

{
    'name': "Hr Expense",
    'currency': 'EUR',
    'license': 'Other proprietary',
    'price': 0.0,
    'summary': """This module allow you to manage expense approvals.""",
    'description': """ """,
    'author': "TechUltra Solutions Pvt. Ltd.",
    'website': "https://www.everbsgroup.com/",
    'support': 'everbsgroup.com',
    'version': '1.1.9',
    'category': 'Human Resources',
    'images': [],
    'depends': ['hr_expense', 'security_rules'],
    'live_test_url': 'https://www.techultrasolutions.com/',
    'data': [
             # 'security/ir.model.access.csv',
             # 'security/ir_rule.xml',
             'views/hr_expense_settings_view.xml',
             'views/hr_expense_sheet_view.xml',
             'views/hr_expense_product_view.xml',
             'views/expense_type_view.xml',
             'views/hr_expense_view.xml'],
    'installable': True,
    'application': False,
}
