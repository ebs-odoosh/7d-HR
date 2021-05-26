# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
{
    "name": "Employee Complain Management",
    
    "author": "Softhealer Technologies",
    
    "website": "https://www.softhealer.com",
        
    "support": "support@softhealer.com",   

    "version": "12.0.1",
    
    "category": "Extra Tools",
    
    "summary": "Manage Complains Module, Handle Worker Complain, Complain Management App, Employee Complain Management, Manage Complains With Types, Maintain Complains Odoo",
    
    "description": """"Complain Management" helps to evaluate complains systematically. You can manage, handle & solve employees complains. This module is useful to track employee complain records easily. Admin has to create a complain category accordingly to the organization and allocate the responsible person & department. Employees can create and post their complains with categories. After that posted complains go to responsible persons and they can resolve, refuse, or close. Responsible persons get an email for complains and the employee gets an email for complains resolved, refused, or closed. They can give ratings and comment about the decision. You can print the complain report.Complain Management System Odoo, Manage Complains Module, Complain Management, Employee Complain Management, Manage Complains With Types, Maintain Complains Odoo,Manage Complains Module, Complain Management App, Employee Complain Management, Manage Complains With Types, Maintain Complains Odoo""",
    
    "depends": [
        
            'hr',
        ],
    
    "data": [
            
            'security/ir.model.access.csv',
            'security/sh_complain_security.xml',
            'data/sh_complain_sequence.xml',
            'data/new_complain_mail.xml',
            'views/sh_complain.xml',
            'wizard/sh_complain_resolve_wizard.xml',
            'wizard/sh_complain_refuse_wizard.xml',
            'views/sh_effect.xml',
            'views/sh_complain_categories.xml',
            'report/complain_report.xml',
            

        ],
    "images": ["static/description/background.png", ],
    "installable": True,
    "auto_install": False,
    "application": True,
    "price": "25",
    "currency": "EUR"
}
