# -*- coding: utf-8 -*-
from odoo import http

# class HrApprovals(http.Controller):
#     @http.route('/hr_approvals/hr_approvals/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/hr_approvals/hr_approvals/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('hr_approvals.listing', {
#             'root': '/hr_approvals/hr_approvals',
#             'objects': http.request.env['hr_approvals.hr_approvals'].search([]),
#         })

#     @http.route('/hr_approvals/hr_approvals/objects/<model("hr_approvals.hr_approvals"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('hr_approvals.object', {
#             'object': obj
#         })