# from odoo import fields, models, api
# import csv
# from datetime import datetime, timedelta
# 
# full_datetime_format = '%d.%m.%Y'
# full_date_format = '%Y%m%d'
# full_date_format_dotted = '%Y%m%d'
# 
# 
# class EmploymentCustom(models.Model):
#     _inherit = 'hr.employee'
# 
#     def read_company_csv_file(self):
#         select_type = self.env['ir.config_parameter'].sudo()
#         sap_folder_path = select_type.get_param('res.config.settings.sap_log_folder_path')
#         today = datetime.today().strftime(full_date_format)
# 
#         if sap_folder_path:
#             path = ''
#             if sap_folder_path.endswith('\\') or sap_folder_path.endswith('/'):
#                 path = sap_folder_path
#             else:
#                 separator = ''
#                 if '\\' in sap_folder_path:
#                     separator = '\\'
#                 elif '/' in sap_folder_path:
#                     separator = '/'
#                 path = sap_folder_path + separator
# 
#             try:
#                 with open(path + 'EMD_Log_' + today + '.CSV', 'r', newline='') as file:
#                     csv_reader = csv.reader(file, delimiter=',')
#                     line_count = 0
#                     for row in csv_reader:
#                         if line_count == 0:
#                             print(f'Column names are {", ".join(row)}')
#                             line_count += 1
#                         else:
#                             object_id = row[0]
#                             action_code = row[1]
#                             reason_code = row[2]
#                             start_date = row[3]
#                             log_type = row[4]
# 
#                             if log_type == 'Success':
# 
#                                 event_type = self.env['sap.event.type'].search([('name', '=', action_code)])
#                                 event_reason = self.env['sap.event.type.reason'].search(
#                                     [('name', '=', reason_code.zfill(2)), ('event_type_id', '=', event_type.id)])
# 
#                                 event = self.env['hr.employee.event'].search(
#                                     [('company_employee_id', '=', object_id), ('name', '=', event_type.id),
#                                      ('is_processed', '=', False),
#                                      ('event_reason', '=', event_reason.id)])
# 
#                                 for ev in event:
#                                     ev.is_processed = True
# 
#                             line_count += 1
#             except FileNotFoundError:
#                 print('EMD not found')
# 
#             try:
#                 with open(path + 'ESD_Log_' + today + '.CSV', 'r', newline='') as file:
#                     csv_reader = csv.reader(file, delimiter=',')
#                     line_count = 0
#                     for row in csv_reader:
#                         if line_count == 0:
#                             print(f'Column names are {", ".join(row)}')
#                             line_count += 1
#                         else:
#                             employee_id = row[0]
#                             start_date = row[1]
#                             log_type = row[2]
# 
#                             if log_type == 'Success':
#                                 event = self.env['event.compensation'].search([('is_sap_processed', '=', False)])
# 
#                                 for ev in event:
#                                     if start_date == ev.from_date.strftime(
#                                             full_date_format_dotted) and employee_id == ev.related_event.employee_id.company_employee_id:
#                                         ev.is_sap_processed = True
# 
#                             line_count += 1
#             except FileNotFoundError:
#                 print('ESD not found')
