# -*- coding: utf-8 -*-
# from odoo import http


# class CustomOrgChart(http.Controller):
#     @http.route('/custom_org_chart/custom_org_chart/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/custom_org_chart/custom_org_chart/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('custom_org_chart.listing', {
#             'root': '/custom_org_chart/custom_org_chart',
#             'objects': http.request.env['custom_org_chart.custom_org_chart'].search([]),
#         })

#     @http.route('/custom_org_chart/custom_org_chart/objects/<model("custom_org_chart.custom_org_chart"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('custom_org_chart.object', {
#             'object': obj
#         })
