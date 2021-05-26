# # -*- coding: utf-8 -*-
# 
# from odoo import models, fields, api
# 
# 
# class SAPSettings(models.TransientModel):
#     _inherit = 'res.config.settings'
#     sap_folder_path = fields.Char(
#         string='SAP Output Folder',
#         required=False)
#     sap_log_folder_path = fields.Char(
#         string='SAP Log Folder',
#         required=False)
# 
#     def set_values(self):
#         super(SAPSettings, self).set_values()
#         select_type = self.env['ir.config_parameter'].sudo()
#         if self.sap_folder_path:
#             select_type.set_param('res.config.settings.sap_folder_path', self.sap_folder_path)
#         else:
#             select_type.set_param('res.config.settings.sap_folder_path', False)
# 
#         if self.sap_log_folder_path:
#             select_type.set_param('res.config.settings.sap_log_folder_path', self.sap_log_folder_path)
#         else:
#             select_type.set_param('res.config.settings.sap_log_folder_path', False)
# 
#     @api.model
#     def get_values(self):
#         res = super(SAPSettings, self).get_values()
#         select_type = self.env['ir.config_parameter'].sudo()
#         sap_folder_path = select_type.get_param('res.config.settings.sap_folder_path')
#         if sap_folder_path:
#             res.update({'sap_folder_path': sap_folder_path})
# 
#         sap_log_folder_path = select_type.get_param('res.config.settings.sap_log_folder_path')
#         if sap_log_folder_path:
#             res.update({'sap_log_folder_path': sap_log_folder_path})
# 
#         return res
