# -*- coding: utf-8 -*-
# from odoo import http


# class SecurityRules(http.Controller):
#     @http.route('/security_groups/security_groups/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/security_groups/security_groups/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('security_rules.listing', {
#             'root': '/security_rules/security_rules',
#             'objects': http.request.env['security_rules.security_rules'].search([]),
#         })

#     @http.route('/security_rules/security_rules/objects/<model("security_rules.security_rules"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('security_rules.object', {
#             'object': obj
#         })
