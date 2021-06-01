from odoo import fields, models, api
import csv
from datetime import datetime, timedelta

full_datetime_format = '%d.%m.%Y'
full_date_format = '%Y%m%d'
full_date_format_time = '%Y%m%d%H%M%S'


class EmploymentCustom(models.Model):
    _inherit = 'hr.employee'

    def write_company_csv_file(self):
        select_type = self.env['ir.config_parameter'].sudo()
        sap_folder_path = select_type.get_param('res.config.settings.sap_folder_path')
        today = datetime.today().strftime(full_date_format_time)

        if sap_folder_path:
            path = ''
            if sap_folder_path.endswith('\\') or sap_folder_path.endswith('/'):
                path = sap_folder_path
            else:
                separator = ''
                if '\\' in sap_folder_path:
                    separator = '\\'
                elif '/' in sap_folder_path:
                    separator = '/'
                path = sap_folder_path + separator

            with open(path + 'OMD_' + today + '.csv', 'w', newline='') as file:
                fieldnames = ['Object ID', 'Object Type', 'Start Date', 'End Date', 'Object Description', 'Parent ID']
                writer = csv.writer(file)
                departments = self.env['hr.department'].search(
                    [('write_date', '>=', datetime.now() - timedelta(days=1))])
                jobs = self.env['hr.job'].search(
                    [('write_date', '>=', datetime.now() - timedelta(days=1))])
                # writer.writeheader()
                writer.writerow(fieldnames)
                for department in departments:
                    department_code = department.code if department.code else ''
                    department_type = department.type if department.type else ''
                    start_date = department.start_date.strftime(full_datetime_format) if department.start_date else ''
                    end_date = department.end_date.strftime(full_datetime_format) if department.end_date else ''
                    department_name = department.name if department.name else ''
                    parent = department.parent_id.code if department.parent_id else ''
                    writer.writerow(
                        [department_code, department_type, start_date, end_date, department_name, parent])
                for job in jobs:
                    job_code = job.name if job.name else ''
                    job_type = 'P'
                    start_date = job.create_date.strftime(full_datetime_format) if job.create_date else ''
                    end_date = ''
                    job_name = job.description if job.description else ''
                    parent = job.subsection.code if job.subsection else (job.section.code if job.section else (
                        job.department_id.code if job.department_id else (job.group.code if job.group else '')))
                    writer.writerow(
                        [
                            job_code, job_type, start_date, end_date, job_code, parent
                        ]
                    )

            with open(path + 'EMD_' + today + '.csv', 'w', newline='') as file:
                fieldnames = ['Employee ID', 'Event Type', 'Event Reason', 'Start Date', 'End Date', 'Org Unit',
                              'Line Manager Employee Id', 'Position Code', 'Cost Center', 'Employee Group',
                              'Employee subgroup', 'Payroll area', 'Contract type', 'Probation end date',
                              'Confirmation date', 'Salutation', 'First name',
                              'Middle name', 'Last name', 'Birth date', 'Gender', 'Nationality', 'Birth Country',
                              'Shift type', 'OT eligibility', 'System Id', 'Email id', 'Pay scale group',
                              'Payscale Level']
                writer = csv.writer(file)
                events = self.env['hr.employee.event'].search([('is_processed', '=', False)])
                writer.writerow(fieldnames)
                for event in events:
                    employee_id = event.company_employee_id if event.company_employee_id else ''
                    event_type = event.name.name
                    event_reason = event.event_reason.name if event.event_reason.name else ''
                    start_date = event.start_date.strftime(full_datetime_format) if event.start_date else ''
                    end_date = event.end_date.strftime(full_datetime_format) if event.end_date else ''
                    org_unit = event.org_unit_fkey.code if event.org_unit_fkey.code else ''
                    line_manager_id = event.line_manager_id_fkey.company_employee_id if event.line_manager_id_fkey.company_employee_id else ''
                    position_code = event.position_code_fkey.name if event.position_code_fkey.name else ''
                    cost_center = event.cost_center_fkey.code if event.cost_center_fkey.code else ''
                    employee_group = event.employee_group_fkey.code if event.employee_group_fkey.code else ''
                    employee_sub_group = event.employee_sub_group_fkey.code if event.employee_sub_group_fkey.code else ''
                    payroll_area = event.payroll_area_fkey.code if event.payroll_area_fkey.code else ''
                    contract_type = event.contract_type_fkey.code if event.contract_type_fkey.code else ''
                    probation_end_date = event.probation_end_date.strftime(
                        full_datetime_format) if event.probation_end_date else ''
                    confirmation_date = event.confirmation_date.strftime(
                        full_datetime_format) if event.confirmation_date else ''
                    salutation = event.salutation_fkey.shortcut if event.salutation_fkey.shortcut else ''
                    first_name = event.first_name if event.first_name else ''
                    middle_name = event.middle_name if event.middle_name else ''
                    last_name = event.last_name if event.last_name else ''
                    birth_date = event.birth_date.strftime(full_datetime_format) if event.birth_date else ''
                    gender = event.gender_fkey if event.gender_fkey else ''
                    if gender == 'male':
                        gender = 'M'
                    elif gender == 'female':
                        gender = 'F'
                    else:
                        gender = ''
                    nationality = event.nationality_fkey.code if event.nationality_fkey.code else ''
                    birth_country = event.birth_country_fkey.code if event.birth_country_fkey.code else ''
                    shift_type = event.shift_type_fkey.code if event.shift_type_fkey.code else ''
                    ot_eligibility = event.ot_eligibility
                    system_id = event.system_id if event.system_id else ''
                    email_id = event.email_id if event.email_id else ''
                    payscale_group = event.payscale_group_fkey.code if event.payscale_group_fkey.code else ''
                    payscale_level = event.payscale_level_fkey.code if event.payscale_level_fkey.code else ''
                    writer.writerow([
                        employee_id, event_type, event_reason, start_date, end_date, org_unit, line_manager_id,
                        position_code,
                        cost_center, employee_group, employee_sub_group, payroll_area,
                        contract_type, probation_end_date, confirmation_date, salutation, first_name,
                        middle_name, last_name, birth_date, gender, nationality, birth_country, shift_type,
                        ot_eligibility, system_id,
                        email_id, payscale_group, payscale_level])

            with open(path + 'ESD_' + today + '.csv', 'w', newline='') as file:
                fieldnames = ['Employee ID', 'Start Date', 'End Date', 'Pay Component Type', 'Pay Amount', 'Currency',
                              'Event Type']
                writer = csv.writer(file)
                events = self.env['event.compensation'].search(
                    [('is_sap_processed', '=', False), ('state', '=', 'active')])
                writer.writerow(fieldnames)
                for event in events:
                    is_hire = event.related_event.name.is_new_hire
                    if is_hire:
                        employee_id = event.related_event.employee_id.company_employee_id if event.related_event.employee_id.company_employee_id else ''
                        start_date = event.from_date.strftime(full_datetime_format) if event.from_date else ''
                        end_date = event.to_date.strftime(full_datetime_format) if event.to_date else ''
                        pay_component_type = event.name.name if event.name.name else ''
                        pay_amount = event.amount if event.amount else ''
                        currency = event.currency.name if event.currency.name else ''
                        event_type = event.related_event.name.name
                        writer.writerow(
                            [employee_id, start_date, end_date, pay_component_type, pay_amount, currency, event_type])
                    else:
                        if event.is_new:
                            employee_id = event.related_event.employee_id.company_employee_id if event.related_event.employee_id.company_employee_id else ''
                            start_date = event.from_date.strftime(full_datetime_format) if event.from_date else ''
                            end_date = event.to_date.strftime(full_datetime_format) if event.to_date else ''
                            pay_component_type = event.name.name if event.name.name else ''
                            pay_amount = event.amount if event.amount else ''
                            currency = event.currency.name if event.currency.name else ''
                            event_type = event.related_event.name.name
                            writer.writerow(
                                [employee_id, start_date, end_date, pay_component_type, pay_amount, currency,
                                 event_type])
