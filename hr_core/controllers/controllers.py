# -*- coding: utf-8 -*-
from odoo import http

# class HrCore(http.Controller):
#     @http.route('/hr_core/hr_core/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/hr_core/hr_core/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('hr_core.listing', {
#             'root': '/hr_core/hr_core',
#             'objects': http.request.env['hr_core.hr_core'].search([]),
#         })

#     @http.route('/hr_core/hr_core/objects/<model("hr_core.hr_core"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('hr_core.object', {
#             'object': obj
#         })