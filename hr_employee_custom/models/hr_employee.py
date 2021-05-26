import json
from datetime import datetime

from dateutil import relativedelta
from lxml import etree

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

Religions_list = [
    ('apostolic', 'Apostolic'),
    ('baptist', 'Baptist'),
    ('buddhist', 'Buddhist'),
    ('charismatic', 'Charismatic'),
    ('evang', 'Evang'),
    ('lutheran-church', 'Lutheran Church'),
    ('evangelical', 'Evangelical'),
    ('free-church-alzey', 'Free church Alzey'),
    ('free-religion-of-the-den', 'Free religion of the den'),
    ('french-reformed', 'French reformed'),
    ('hebrew-reg-baden', 'Hebrew reg. BADEN'),
    ('hebrew-reg-wuertbg', 'Hebrew reg. WUERTBG'),
    ('hebrew-state', 'Hebrew state'),
    ('hindu', 'Hindu'),
    ('islamic', 'Islamic'),
    ('israelite', 'Israelite'),
    ("jehovah-s-witness", "Jehovah's witness"),
    ('mennonite-church', 'Mennonite Church'),
    ('jewish', 'Jewish'),
    ('mennonite-church', 'Mennonite Church'),
    ('mormon', 'Mormon'),
    ('moravian-congregation', 'Moravian Congregation'),
    ('muslim', 'Muslim'),
    ('netherl', 'Netherl'),
    ('netherl-reformed-church', 'Netherl. Reformed Church'),
    ('new-apostolic', 'New apostolic'),
    ('no-denomination', 'No denomination'),
    ('old-catholic', 'Old Catholic'),
    ('oecumenic', 'Oecumenic'),
    ('protestant', 'Protestant'),
    ('roman-catholic', 'Roman Catholic'),
    ("shia-muslim", "Shi'a Muslim"),
    ('sunni-muslim', 'Sunni Muslim'),
    ('christian', 'Christian'),
    ('christian-reformed', 'Christian Reformed'),
]


def get_dep(dep, level):
    if not dep.id:
        return False
    dep_type = dep.type
    if dep_type == level:
        return dep.id
    else:
        return get_dep(dep.parent_id, level)


class EmployeeEvent(models.Model):
    _name = 'hr.employee.event'

    name = fields.Many2one(
        comodel_name='sap.event.type',
        string='Event Type',
        required=True)
    event_reason = fields.Many2one(
        comodel_name='sap.event.type.reason',
        string='Event Reason',
        required=False)
    start_date = fields.Datetime(
        string='Effective Date',
        required=True)
    end_date = fields.Datetime(
        string='End Date',
        required=False)
    employee_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Employee',
        required=True, ondelete='cascade')
    is_processed = fields.Boolean(
        string='Is SAP Processed',
        required=True, default=False)
    is_triggered = fields.Boolean(
        string='Is Schedule Processed',
        required=True, default=False)
    update_info = fields.Boolean(
        string='Update Employee Information',
        required=True, default=True)

    old_active_salary = fields.Float(
        string='Old Active Salary',
        required=False)
    new_active_salary = fields.Float(
        string='New Active Salary',
        required=False)

    # related_requisition = fields.Many2one('approval.request', string='Related Requisition')

    company_employee_id = fields.Char(string='Company Employee ID', required=False)

    org_unit = fields.Char(string='Org Unit', required=False)
    org_unit_fkey = fields.Many2one(comodel_name='hr.department', string='Org Unit', required=False)

    line_manager_id = fields.Char(string='Line Manager', required=False)
    line_manager_id_fkey = fields.Many2one(comodel_name='hr.employee', string='Line Manager', required=False)

    position_code = fields.Char(string='Position', required=False)
    position_code_fkey = fields.Many2one(comodel_name='hr.job', string='Position', required=False)

    job_title_fkey = fields.Many2one(comodel_name='job.title', string='Job Title', required=False)

    cost_center = fields.Char(string='Cost Center', required=False)
    cost_center_fkey = fields.Many2one(comodel_name='hr.cost.center', string='Cost Center', required=False)

    employee_group = fields.Char(string='Employee Group', required=False)
    employee_group_fkey = fields.Many2one(comodel_name='hr.contract.group', string='Employee Group', required=False)

    employee_sub_group = fields.Char(string='Employee SubGroup', required=False)
    employee_sub_group_fkey = fields.Many2one(comodel_name='hr.contract.subgroup', string='Employee SubGroup',
                                              required=False)

    payroll_area = fields.Char(string='Payroll Area', required=False)
    payroll_area_fkey = fields.Many2one(comodel_name='hr.payroll.area', string='Payroll Area', required=False)

    contract_type = fields.Char(string='Contract Type', required=False)
    contract_type_fkey = fields.Many2one(comodel_name='hr.contract.type', string='Contract Type', required=False)

    probation_end_date = fields.Datetime(string='Probation End Date', required=False)
    confirmation_date = fields.Datetime(string='Confirmation Date', required=False)

    salutation = fields.Char(string='Salutation', required=False)
    salutation_fkey = fields.Many2one(comodel_name='res.partner.title', string='Salutation', required=False)

    first_name = fields.Char(string='First Name', required=False)
    middle_name = fields.Char(string='Middle Name', required=False)
    last_name = fields.Char(string='Last Name', required=False)
    birth_date = fields.Datetime(string='Birth Date', required=False)

    gender = fields.Char(string='Gender', required=False)
    gender_fkey = fields.Selection(
        string='Gender',
        selection=[('male', 'Male'),
                   ('female', 'Female'), ('other', 'Other')],
        required=False)

    nationality = fields.Char(string='Nationality', required=False)
    nationality_fkey = fields.Many2one(comodel_name='res.country', string='Nationality', required=False)

    birth_country = fields.Char(string='Birth Country', required=False)
    birth_country_fkey = fields.Many2one(comodel_name='res.country', string='Birth Country', required=False)

    shift_type = fields.Char(string='Shift Type', required=False)
    shift_type_fkey = fields.Many2one(comodel_name='resource.calendar', string='Shift Type', required=False)

    ot_eligibility = fields.Boolean(string='Overtime Eligibility', required=False)
    system_id = fields.Char(string='System ID', required=False)
    email_id = fields.Char(string='Email', required=False)

    payscale_group = fields.Char(string='Payscale Group', required=False)
    payscale_group_fkey = fields.Many2one(comodel_name='hr.payscale.group', string='Payscale Group', required=False)

    payscale_level = fields.Char(string='Payroll Level', required=False)
    payscale_level_fkey = fields.Many2one(comodel_name='hr.payscale.level', string='Payroll Level', required=False)

    related_compensations = fields.One2many(related='employee_id.contract_id.related_compensation', readonly=False)
    related_inactive_compensations = fields.One2many(related='employee_id.contract_id.inactive_related_compensation',
                                                     readonly=False)
    related_compensation = fields.One2many('event.compensation', 'related_event', string='Related Compensation')
    inactive_related_compensation = fields.One2many('event.compensation', 'related_event',
                                                    domain=[('state', '=', 'inactive')],
                                                    string='Inactive Salary Compensation')
    is_esd = fields.Boolean(string='Change To Contract Salary Components', required=True, default=False)

    @api.onchange('name')
    def onchange_event_type(self):
        self.event_reason = False
        return {'domain': {'event_reason': [('event_type_id', '=', self.name.id)]}}

    @api.onchange('is_esd')
    def onchange_esd(self):
        for rec in self:
            # rec.old_active_salary = 0
            # rec.new_active_salary = 0
            # for comp in rec.related_compensation:
            # if comp.state == 'active':
            basic_salary = sum(
                rec.related_compensation.filtered(
                    lambda x: x.name.component_type == 'basic_pay' and x.state == 'active').mapped(
                    'amount'))
            percentage = sum(rec.related_compensation.filtered(
                lambda x: x.is_payroll and x.amount_type == 'percentage' and x.state == 'active').mapped(
                'amount')) / 100.0
            active_salary = sum(
                rec.related_compensation.filtered(
                    lambda x: x.is_payroll and x.amount_type == 'amount' and x.state == 'active').mapped(
                    'amount')) + (basic_salary * percentage)

            rec.old_active_salary = active_salary
            rec.new_active_salary = active_salary

    @api.onchange('related_compensation')
    def onchange_comp(self):
        for rec in self:
            # rec.new_active_salary = 0
            # for comp in rec.related_compensation:
            basic_salary = sum(
                rec.related_compensation.filtered(
                    lambda x: x.name.component_type == 'basic_pay' and x.state == 'active').mapped(
                    'amount'))
            percentage = sum(rec.related_compensation.filtered(
                lambda x: x.is_payroll and x.amount_type == 'percentage' and x.state == 'active').mapped(
                'amount')) / 100.0
            rec.new_active_salary = sum(
                rec.related_compensation.filtered(
                    lambda x: x.is_payroll and x.amount_type == 'amount' and x.state == 'active').mapped(
                    'amount')) + (basic_salary * percentage)

    @api.onchange('payscale_group_fkey')
    def onchange_payscale_group(self):
        if self.payscale_level_fkey.related_group.id != self.payscale_group_fkey.id:
            self.payscale_level_fkey = False
        return {'domain': {'payscale_level_fkey': [('related_group', '=', self.payscale_group_fkey.id)]}}

    @api.onchange('position_code_fkey')
    def onchange_position(self):
        self.job_title_fkey = self.position_code_fkey.job_title.id

    @api.onchange('employee_id')
    def onchange_employee(self):
        employee = self.employee_id

        company_employee_id = employee.company_employee_id

        real_employee = self.env['hr.employee'].search([('company_employee_id', '=', company_employee_id)], limit=1)
        if not str(self.id).startswith('<NewId'):
            # events = self.search([('employee_id', '=', real_employee.id), ('id', '!=', self.id)],
            #                      order="start_date desc")
            events = self.search([('employee_id', '=', real_employee.id)],order="start_date desc")
        else:
            events = self.search([('employee_id', '=', real_employee.id)], order="start_date desc")

        if len(events) == 0:
            self.company_employee_id = employee.company_employee_id if employee.company_employee_id else ''
            self.org_unit_fkey = employee.department_id.id
            self.line_manager_id_fkey = employee.parent_id.id
            self.position_code_fkey = employee.job_id.id
            self.job_title_fkey = employee.contract_id.job_title.id
            self.cost_center_fkey = employee.contract_id.cost_center.id
            self.employee_group_fkey = employee.contract_id.contract_group.id
            self.employee_sub_group_fkey = employee.contract_id.contract_subgroup.id
            self.payroll_area_fkey = employee.contract_id.pay_type_id.id
            self.contract_type_fkey = employee.contract_id.contract_type.id
            self.probation_end_date = str(employee.contract_id.trial_date_end) if employee.contract_id.trial_date_end else False
            self.confirmation_date = employee.contract_id.confirmation_date
            self.salutation_fkey = employee.title.id
            self.first_name = employee.firstname if employee.firstname else ''
            self.middle_name = employee.middlename if employee.middlename else ''
            self.last_name = employee.lastname if employee.lastname else ''
            self.birth_date = str(employee.birthday) if employee.birthday else False
            self.gender_fkey = employee.gender
            self.nationality_fkey = employee.country_id.id
            self.birth_country_fkey = employee.country_of_birth.id
            self.shift_type_fkey = employee.resource_calendar_id.id
            self.ot_eligibility = employee.contract_id.overtime_eligibility
            self.system_id = employee.system_id if employee.system_id else ''
            self.email_id = employee.work_email if employee.work_email else ''
            self.payscale_group_fkey = employee.contract_id.payscale_group.id
            self.payscale_level_fkey = employee.contract_id.payscale_level.id

            self.related_compensation = [(0, 0, {
                'name': comp.name.id,
                'from_date': comp.from_date,
                'to_date': comp.to_date,
                'amount': comp.amount,
                'currency': comp.currency.id,
                'frequency': comp.frequency,
                'is_payroll': comp.is_payroll,
                'value': comp.value,
                'period': comp.period,
                'active': comp.active,
                'state': comp.state,
                'amount_type': comp.amount_type,
                'related_compensation': comp.id,
                'is_new': False,
            }) for comp in employee.contract_id.related_compensation]
        else:
            latest_event = events[0]
            self.company_employee_id = latest_event.company_employee_id if latest_event.company_employee_id else ''
            self.org_unit_fkey = latest_event.org_unit_fkey.id
            self.line_manager_id_fkey = latest_event.line_manager_id_fkey.id
            self.position_code_fkey = latest_event.position_code_fkey.id
            self.job_title_fkey = latest_event.job_title_fkey.id
            self.cost_center_fkey = latest_event.cost_center_fkey.id
            self.employee_group_fkey = latest_event.employee_group_fkey.id
            self.employee_sub_group_fkey = latest_event.employee_sub_group_fkey.id
            self.payroll_area_fkey = latest_event.payroll_area_fkey.id
            self.contract_type_fkey = latest_event.contract_type_fkey.id
            self.probation_end_date = latest_event.probation_end_date
            self.confirmation_date = latest_event.confirmation_date
            self.salutation_fkey = latest_event.salutation_fkey.id
            self.first_name = latest_event.first_name if latest_event.first_name else ''
            self.middle_name = latest_event.middle_name if latest_event.middle_name else ''
            self.last_name = latest_event.last_name if latest_event.last_name else ''
            self.birth_date = latest_event.birth_date
            self.gender_fkey = latest_event.gender_fkey
            self.nationality_fkey = latest_event.nationality_fkey.id
            self.birth_country_fkey = latest_event.birth_country_fkey.id
            self.shift_type_fkey = latest_event.shift_type_fkey.id
            self.ot_eligibility = latest_event.ot_eligibility
            self.system_id = latest_event.system_id if latest_event.system_id else ''
            self.email_id = latest_event.email_id if latest_event.email_id else ''
            self.payscale_group_fkey = latest_event.payscale_group_fkey.id
            self.payscale_level_fkey = latest_event.payscale_level_fkey.id

            for comp in latest_event.related_compensation.filtered(lambda x: x.state == 'active'):
                self.related_compensation = [(0, 0, {
                    'name': comp.name.id,
                    'from_date': comp.from_date,
                    'to_date': comp.to_date,
                    'amount': comp.amount,
                    'currency': comp.currency.id,
                    'frequency': comp.frequency,
                    'is_payroll': comp.is_payroll,
                    'value': comp.value,
                    'period': comp.period,
                    'active': comp.active,
                    'state': comp.state,
                    'amount_type': comp.amount_type,
                    'related_compensation': comp.related_compensation.id,
                    'related_event_compensation': comp.id,
                    'is_new': False,
                })]
            # self.related_compensation = [(0, 0, {
            #     'name': comp.name.id,
            #     'from_date': comp.from_date,
            #     'to_date': comp.to_date,
            #     'amount': comp.amount,
            #     'currency': comp.currency.id,
            #     'frequency': comp.frequency,
            #     'is_payroll': comp.is_payroll,
            #     'value': comp.value,
            #     'period': comp.period,
            #     'active': comp.active,
            #     'state': comp.state,
            #     'related_compensation': comp.related_compensation.id,
            #     'is_new': False,
            # }) for comp in latest_event.related_compensation.filtered(lambda x: x.state == 'active')]

    def run_employee_events_scheduler(self):
        not_processed_events = self.search([('is_triggered', '=', False), ('update_info', '=', True)])
        for event in not_processed_events:
            effective_date = event.start_date
            if effective_date.date() <= datetime.today().date():
                try:
                    self.do_changes(event)
                except Exception:
                    print('Employee: ' + event.employee_id.name + ', Event Type: ' + event.name.name + ' ERROR')

    def do_changes(self, event):
        employee = event.employee_id
        # check company id
        is_changed_company_id = is_changed(employee.company_employee_id, event.company_employee_id)
        if is_changed_company_id:
            employee.company_employee_id = event.company_employee_id
        # check org
        is_changed_org_id = is_changed(employee.department_id.id, event.org_unit_fkey.id)
        if is_changed_org_id:
            employee.contract_id.group = get_dep(event.org_unit_fkey, 'BU')
            employee.contract_id.department = get_dep(event.org_unit_fkey, 'BD')
            employee.contract_id.section = get_dep(event.org_unit_fkey, 'BS')
            employee.contract_id.subsection = get_dep(event.org_unit_fkey, 'SS')
            employee.contract_id.department_id = event.org_unit_fkey.id
            employee.department_id = event.org_unit_fkey.id
        # check manager
        is_changed_manager_id = is_changed(employee.parent_id.id, event.line_manager_id_fkey.id)
        if is_changed_manager_id:
            employee.contract_id.manager_id = event.line_manager_id_fkey.id
            employee.parent_id = event.line_manager_id_fkey.id
        # check position
        is_changed_position_id = is_changed(employee.job_id.id, event.position_code_fkey.id)
        if is_changed_position_id:
            employee.contract_id.job_id = event.position_code_fkey.id
            employee.job_id = event.position_code_fkey.id
        # check job title
        is_changed_job_title_id = is_changed(employee.contract_id.job_title.id, event.job_title_fkey.id)
        if is_changed_job_title_id:
            employee.contract_id.job_title = event.job_title_fkey.id
        # check cost center
        is_changed_cost_center_id = is_changed(employee.contract_id.cost_center.id, event.cost_center_fkey.id)
        if is_changed_cost_center_id:
            employee.contract_id.cost_center = event.cost_center_fkey.id
        # check contract group
        is_changed_group_id = is_changed(employee.contract_id.contract_group.id, event.employee_group_fkey.id)
        if is_changed_group_id:
            employee.contract_id.contract_group = event.employee_group_fkey.id
        # check contract subgroup
        is_changed_subgroup_id = is_changed(employee.contract_id.contract_subgroup.id,
                                            event.employee_sub_group_fkey.id)
        if is_changed_subgroup_id:
            employee.contract_id.contract_subgroup = event.employee_sub_group_fkey.id
        # check payroll area
        is_changed_payroll_area_id = is_changed(employee.contract_id.pay_type_id.id, event.payroll_area_fkey.id)
        if is_changed_payroll_area_id:
            employee.contract_id.pay_type_id = event.payroll_area_fkey.id
        # check contract type
        is_changed_contract_type_id = is_changed(employee.contract_id.contract_type.id,
                                                 event.contract_type_fkey.id)
        if is_changed_contract_type_id:
            employee.contract_id.contract_type = event.contract_type_fkey.id
        # check probation date
        is_changed_prob_date_id = is_changed(employee.contract_id.trial_date_end, event.probation_end_date)
        if is_changed_prob_date_id:
            employee.contract_id.trial_date_end = event.probation_end_date
        # check confirmation datetime
        is_changed_conf_date_id = is_changed(employee.contract_id.confirmation_date, event.confirmation_date)
        if is_changed_conf_date_id:
            employee.contract_id.confirmation_date = event.confirmation_date
        # check salutation
        is_changed_salutation_id = is_changed(employee.title.id, event.salutation_fkey.id)
        if is_changed_salutation_id:
            employee.title = event.salutation_fkey.id
        # check first name
        is_changed_first_name_id = is_changed(employee.firstname, event.first_name)
        if is_changed_first_name_id:
            employee.firstname = event.first_name
        # check middle name
        is_changed_middle_name_id = is_changed(employee.middlename, event.middle_name)
        if is_changed_middle_name_id:
            employee.middlename = event.middle_name
        # check last name
        is_changed_last_name_id = is_changed(employee.lastname, event.last_name)
        if is_changed_last_name_id:
            employee.lastname = event.last_name
        # if any name is changed
        if is_changed_first_name_id or is_changed_middle_name_id or is_changed_last_name_id:
            employee.name = (employee.firstname or '') + ' ' + (employee.middlename or '') + ' ' + (employee.lastname or '')
        # check birth date
        is_changed_birthday_id = is_changed(employee.birthday, event.birth_date)
        if is_changed_birthday_id:
            employee.birthday = event.birth_date
        # check gender
        is_changed_gender_id = is_changed(employee.gender, event.gender_fkey)
        if is_changed_gender_id:
            employee.gender = event.gender_fkey
        # check country
        is_changed_country_id = is_changed(employee.country_id.id, event.nationality_fkey.id)
        if is_changed_country_id:
            employee.country_id = event.nationality_fkey.id
        # check country birth
        is_changed_birth_country_id = is_changed(employee.country_of_birth.id, event.birth_country_fkey.id)
        if is_changed_birth_country_id:
            employee.country_of_birth = event.birth_country_fkey.id
        # check shift type
        is_changed_shift_type_id = is_changed(employee.contract_id.resource_calendar_id.id,
                                              event.shift_type_fkey.id)
        if is_changed_shift_type_id:
            employee.contract_id.resource_calendar_id = event.shift_type_fkey.id
            employee.resource_calendar_id = event.shift_type_fkey.id
        # check overtime eligibility
        is_changed_ot_eligibility_id = is_changed(employee.contract_id.overtime_eligibility, event.ot_eligibility)
        if is_changed_ot_eligibility_id:
            employee.contract_id.overtime_eligibility = event.ot_eligibility
        # check system id
        is_changed_system_id = is_changed(employee.system_id, event.system_id)
        if is_changed_system_id:
            employee.system_id = event.system_id
        # check mail
        is_changed_mail_id = is_changed(employee.work_email, event.email_id)
        if is_changed_mail_id:
            employee.work_email = event.email_id
        # check payscale group
        is_changed_payscale_group_id = is_changed(employee.contract_id.payscale_group.id,
                                                  event.payscale_group_fkey.id)
        if is_changed_payscale_group_id:
            employee.contract_id.payscale_group = event.payscale_group_fkey.id
        # check payscale level
        is_changed_payscale_level_id = is_changed(employee.contract_id.payscale_level.id,
                                                  event.payscale_level_fkey.id)
        if is_changed_payscale_level_id:
            employee.contract_id.payscale_level = event.payscale_level_fkey.id

        # check compensations
        is_changed_compensations = event.is_esd
        if is_changed_compensations:
            for comp in event.related_compensation:
                pay_component = comp.name
                contract = employee.contract_id

                contract_comp_line = get_contract_comp_line(contract, pay_component)

                if contract_comp_line and contract_comp_line.id == comp.related_compensation.id and \
                        (
                                contract_comp_line.name.id != comp.name.id or
                                contract_comp_line.amount != comp.amount or
                                contract_comp_line.currency.id != comp.currency.id or
                                contract_comp_line.frequency != comp.frequency or
                                contract_comp_line.is_payroll != comp.is_payroll or
                                contract_comp_line.amount_type != comp.amount_type or
                                contract_comp_line.value != comp.value or
                                contract_comp_line.period != comp.period
                        ):
                    compensation_date_to = comp.to_date
                    contract_comp_line.write({
                        'state': 'inactive',
                        'to_date': fields.Date.context_today(self)
                    })
                    self.env['hr.compensation'].create({
                        'name': comp.name.id,
                        'from_date': fields.Date.context_today(self),
                        'to_date': compensation_date_to,
                        'amount': comp.amount,
                        'currency': comp.currency.id,
                        'frequency': comp.frequency,
                        'is_payroll': comp.is_payroll,
                        'amount_type': comp.amount_type,
                        'value': comp.value,
                        'period': comp.period,
                        'active': True,
                        'state': 'active',
                        'related_contract': employee.contract_id.id,
                        'compensation_id': comp.related_compensation.compensation_id.id,
                    })
                elif contract_comp_line and contract_comp_line.id != comp.related_compensation.id:
                    self.env['hr.compensation'].create({
                        'name': comp.name.id,
                        'from_date': comp.from_date,
                        'to_date': comp.to_date,
                        'amount': comp.amount,
                        'currency': comp.currency.id,
                        'frequency': comp.frequency,
                        'is_payroll': comp.is_payroll,
                        'amount_type': comp.amount_type,
                        'value': comp.value,
                        'period': comp.period,
                        'active': comp.active,
                        'state': comp.state,
                        'related_contract': employee.contract_id.id,
                        'compensation_id': comp.related_compensation.id,
                    })

            # for comp in event.related_compensation.filtered(lambda x: x.related_compensation.id):
            # event_comp_ids = []
            # for event_comp in event.related_compensation:
            #     if event_comp.related_compensation.id:
            #         event_comp_ids.append(event_comp.related_compensation.id)
            # deleted_comp = self.env['hr.compensation'].search(
            #     [('related_contract', '=', employee.contract_id.id), ('id', 'not in', event_comp_ids)])
            # for deleted in deleted_comp:
            #     deleted.state = 'inactive'
            #     deleted.from_date = comp.from_date
            #     deleted.to_date = comp.to_date
            # comp.related_compensation.write({'name': comp.name.id,
            #                                  'from_date': comp.from_date,
            #                                  'to_date': comp.to_date,
            #                                  'amount': comp.amount,
            #                                  'currency': comp.currency.id,
            #                                  'frequency': comp.frequency,
            #                                  'is_payroll': comp.is_payroll,
            #                                  'value': comp.value,
            #                                  'period': comp.period,
            #                                  'active': comp.active,
            #                                  'state': comp.state})
            # for comp in event.related_compensation.filtered(lambda x: x.related_event_compensation.id):
            #     event_comp_ids = []
            #     for event_comp in event.related_compensation:
            #         if event_comp.related_compensation.id:
            #             event_comp_ids.append(event_comp.related_compensation.id)
            #     deleted_comp = self.env['hr.compensation'].search(
            #         [('related_contract', '=', employee.contract_id.id), ('id', 'not in', event_comp_ids)])
            #     for deleted in deleted_comp:
            #         deleted.state = 'inactive'
            #         deleted.from_date = comp.from_date
            #         deleted.to_date = comp.to_date
            #     comp.related_compensation.write({'name': comp.name.id,
            #                                      'from_date': comp.from_date,
            #                                      'to_date': comp.to_date,
            #                                      'amount': comp.amount,
            #                                      'currency': comp.currency.id,
            #                                      'frequency': comp.frequency,
            #                                      'is_payroll': comp.is_payroll,
            #                                      'value': comp.value,
            #                                      'period': comp.period,
            #                                      'active': comp.active,
            #                                      'state': comp.state})
            # for comp in event.related_compensation.filtered(lambda x: not x.related_compensation.id).filtered(
            #         lambda x: not x.related_event_compensation.id):
            #     self.env['hr.compensation'].create({'name': comp.name.id,
            #                                         'from_date': comp.from_date,
            #                                         'to_date': comp.to_date,
            #                                         'amount': comp.amount,
            #                                         'currency': comp.currency.id,
            #                                         'frequency': comp.frequency,
            #                                         'is_payroll': comp.is_payroll,
            #                                         'value': comp.value,
            #                                         'period': comp.period,
            #                                         'active': comp.active,
            #                                         'state': comp.state,
            #                                         'related_contract': employee.contract_id.id})

        event.is_triggered = True


def get_contract_comp_line(contract, pay_component):
    result = False
    for contract_line in contract.related_compensation:
        contract_pay_component = contract_line.name
        if pay_component.id == contract_pay_component.id:
            result = contract_line
    return result


def is_changed(original_value, event_value):
    result = False
    if original_value != event_value:
        result = True
    return result


class EventCompensation(models.Model):
    _name = 'event.compensation'

    name = fields.Many2one('hr.compensation.pay.component', 'Pay Component')
    code = fields.Char(related='name.code', string='Code')
    from_date = fields.Date('From Date')
    to_date = fields.Date('To Date')
    amount = fields.Float('Amount', default=0.0)
    currency = fields.Many2one('res.currency', default=lambda self: self.env.user.company_id.currency_id)
    frequency = fields.Integer('Frequency')
    is_payroll = fields.Boolean('Is Payroll Element')
    value = fields.Char('Value (If not Payroll)')
    period = fields.Selection([('daily', 'Daily'), ('monthly', 'Monthly'), ('yearly', 'Yearly')], 'Period')
    related_event = fields.Many2one('hr.employee.event', 'Related Event', ondelete='cascade')
    related_compensation = fields.Many2one('hr.compensation', 'Related Compensation')
    related_event_compensation = fields.Many2one('event.compensation', 'Related Event Compensation')
    component_description = fields.Char(
        string='Component Description',
        related='name.description')
    active = fields.Boolean(default=True)
    state = fields.Selection([('active', 'Active'), ('inactive', 'Inactive')], default='active', string="State",
                             required=True)
    amount_type = fields.Selection([('amount', 'Amount'), ('percentage', 'Percentage')], string='Amount Type')
    is_sap_processed = fields.Boolean(default=False)
    is_new = fields.Boolean(default=True)

    @api.constrains('related_event', 'name')
    def _check_paycomponents_contract(self):
        for rec in self:
            if rec.name and rec.related_event:
                prev_compensations = self.env['event.compensation'].search(
                    [('related_event', '=', rec.related_event.id),
                     ('name', '=', rec.name.id), ('id', '!=', rec.id), ('state', '=', 'active')])
                if len(prev_compensations) > 0 and rec.state == 'active':
                    raise ValidationError(_("Pay Component must be unique per Event!"))

    @api.onchange('amount')
    def _onchange_amount(self):

        result = {}
        message = False
        if self.related_compensation:
            if self.related_compensation.compensation_id.min_amount > self.amount:
                message = _(' (' + str(self.amount) + ') is smaller than min (' + str(
                        self.related_compensation.compensation_id.min_amount) + ')')

            if self.related_compensation.compensation_id.max_amount < self.amount:
                message = _(' (' + str(self.amount) + ') is greater than max (' + str(
                    self.related_compensation.compensation_id.max_amount) + ')')

        if message:
            if self.name.name:
                message = self.name.name + message

            result['warning'] = {
                'title': _("Warning"),
                'message': message
            }
        return result
    # @api.model
    # def create(self, vals):
    #     employee_id = vals.get('employee_id', '')
    #     employee = self.env['hr.employee'].browse(employee_id)
    #     if employee.id:
    #         vals['company_employee_id'] = employee.company_employee_id if employee.company_employee_id else ''
    #         vals['org_unit'] = employee.department_id.code if employee.department_id.code else ''
    #         vals['line_manager_id'] = employee.parent_id.company_employee_id if employee.parent_id.company_employee_id else ''
    #         vals['position_code'] = employee.job_id.name if employee.job_id.name else ''
    #         vals['cost_center'] = employee.contract_id.cost_center.code if employee.contract_id.cost_center.code else ''
    #         vals[
    #             'employee_group'] = employee.contract_id.contract_group.code if employee.contract_id.contract_group.code else ''
    #         vals[
    #             'employee_sub_group'] = employee.contract_id.contract_subgroup.code if employee.contract_id.contract_subgroup.code else ''
    #         vals[
    #             'payroll_area'] = employee.contract_id.pay_type_id.code if employee.contract_id.pay_type_id.code else ''
    #         vals[
    #             'contract_type'] = employee.contract_id.contract_type.code if employee.contract_id.contract_type.code else ''
    #         vals['probation_end_date'] = employee.contract_id.trial_date_end
    #         vals['confirmation_date'] = employee.contract_id.confirmation_date
    #         vals['salutation'] = employee.title.shortcut if employee.title.shortcut else ''
    #         vals['first_name'] = employee.firstname if employee.firstname else ''
    #         vals['middle_name'] = employee.middlename if employee.middlename else ''
    #         vals['last_name'] = employee.lastname if employee.lastname else ''
    #         vals['birth_date'] = employee.birthday
    #         vals['gender'] = employee.gender if employee.gender else ''
    #         vals['nationality'] = employee.country_id.code if employee.country_id.code else ''
    #         vals['birth_country'] = employee.country_of_birth.code if employee.country_of_birth.code else ''
    #         vals['shift_type'] = employee.resource_calendar_id.name if employee.resource_calendar_id.name else ''
    #         vals[
    #             'ot_eligibility'] = employee.contract_id.overtime_eligibility if employee.contract_id.overtime_eligibility else ''
    #         vals['system_id'] = employee.system_id if employee.system_id else ''
    #         vals['email_id'] = employee.work_email if employee.work_email else ''
    #         vals[
    #             'payscale_group'] = employee.contract_id.payscale_group.code if employee.contract_id.payscale_group.code else ''
    #         vals[
    #             'payscale_level'] = employee.contract_id.payscale_level.code if employee.contract_id.payscale_level.code else ''
    #     return super(EmployeeEvent, self).create(vals)


class ContractEmploymentType(models.Model):
    _name = 'hr.contract.employment.type'

    name = fields.Char('Type')
    code = fields.Char('Prefix')
    related_sequence = fields.Many2one('ir.sequence', 'Related Sequence')


class HrEmployeePrivate(models.Model):
    _inherit = 'hr.employee'

    title = fields.Many2one('res.partner.title')
    lang = fields.Many2one('res.lang', string='Native Language',
                           domain="['|',('active','=',True),('active','=',False)]")
    contract_employment_type = fields.Many2one('hr.contract.employment.type', 'Employment Type')
    id_generated = fields.Boolean('ID generated')
    company_employee_id = fields.Char('Company Employee ID')
    system_id = fields.Char('System ID')
    firstname = fields.Char('Firstname')
    middlename = fields.Char('Middlename')
    lastname = fields.Char('Lastname')
    arabic_name = fields.Char('Arabic Name')
    mothers_name = fields.Char("Mother's name")
    arabic_mothers_name = fields.Char("Arabic Mother's name")
    religion = fields.Selection(Religions_list, 'Religions')
    street = fields.Char('Street')
    po_box = fields.Char('PO-Box')
    city = fields.Char('City')
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict',
                               domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')

    parent_id = fields.Many2one(related='contract_id.manager_id', string='Manager', store=True, readonly=False)
    job_id = fields.Many2one(related='contract_id.job_id', store=True, string='Job Position')
    job_title = fields.Char(related='job_id.job_title.name', string='Job Title')
    department_id = fields.Many2one(related='contract_id.department_id', store=True, string="OC Path")

    dependents = fields.One2many('res.partner', 'related_employee', 'Dependents')

    notice_ids = fields.One2many('hr.notice', 'related_employee', 'Notices')

    state = fields.Selection([('pending', 'Pending Approval'), ('approved', 'Approved'), ('reject', 'Reject')],
                             default='pending',
                             string="Approval State")

    housing_ids = fields.One2many(
        comodel_name='hr.housing',
        inverse_name='employee_id',
        string='Housings',
        required=False)
    employee_event_ids = fields.One2many(
        comodel_name='hr.employee.event',
        inverse_name='employee_id',
        string='Events',
        required=False)
    reject_reason = fields.Text('Reject Reason')

    read_only_user_role = fields.Boolean(compute='_get_user_group', default=False)
    all_model_read_only = fields.Boolean(compute='_get_user_group', default=False)
    invisible_user_role = fields.Boolean(compute='_get_user_group', default=False)

    time_hired = fields.Char(
        string='Tenure of Experience',
        required=False, compute='_calculate_time_hired')

    private_email = fields.Char(string="Private Email", stored=True, related=False)

    def _calculate_time_hired(self):
        # self = self.sudo()
        for rec in self:
            now = datetime.now()
            contract_start_date = rec.contract_id.date_start

            diff = relativedelta.relativedelta(now, contract_start_date)

            old_contracts = self.env['hr.contract'].search(
                [('employee_id', '=', rec.id), ('id', '!=', rec.contract_id.id)])

            for old_contract in old_contracts:
                diff += relativedelta.relativedelta(old_contract.date_end, old_contract.date_start)

            years = diff.years
            months = diff.months
            days = diff.days

            rec.time_hired = ('{} years {} months {} days'.format(years, months, days))

    def open_employee_view(self):
        return {
            'name': _("Employees"),
            'type': 'ir.actions.act_window',
            'res_model': 'hr.employee',
            'view_mode': 'kanban,tree,form,activity',
            'search_view_id': self.env.ref('hr.view_employee_filter').id,
            'domain': ['|', ('user_id', '=', self.env.uid),
                       ('id', 'child_of', [employee.id for employee in self.env.user.employee_ids])],
            'context': {},
            'target': 'current',
        }

    @api.multi
    def write(self, vals):
        res = super(HrEmployeePrivate, self).write(vals)
        # if vals.get('parent_id') != None:
        #     self.env['approval.category'].search([]).check_if_subordinates()
        return res

    # @api.depends('read_only_user_role', 'invisible_user_role', 'all_model_read_only')
    def _get_user_group(self):
        for rec in self:
            user = self.env.user
            if user.has_group('base.user_admin'):
                rec.invisible_user_role = False
                rec.read_only_user_role = False
                rec.all_model_read_only = False

            elif user.has_group('security_groups.group_hr_employee'):
                if rec.id in user.employee_ids.ids:
                    rec.read_only_user_role = True
                    rec.invisible_user_role = False
                    rec.all_model_read_only = False
                else:
                    rec.read_only_user_role = True
                    rec.invisible_user_role = True
                    rec.all_model_read_only = True

            else:
                rec.all_model_read_only = False
                rec.read_only_user_role = False
                rec.invisible_user_role = False

    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(HrEmployeePrivate, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
                                                             submenu=submenu)
        if view_type == "form":
            doc = etree.XML(res['arch'])
            for field in res['fields']:
                for node in doc.xpath("//field[@name='%s']" % field):
                    node.set("readonly", "[('all_model_read_only','=',True)]")
                    modifiers = json.loads(node.get("modifiers"))
                    # if modifiers.get('readonly') and modifiers.get('readonly') != True:
                    # modifiers.get('readonly').append(['all_model_read_only', '=', True])
                    if not modifiers.get('readonly'):
                        modifiers['readonly'] = "[('all_model_read_only','=',True)]"
                    node.set("modifiers", json.dumps(modifiers))

            res['arch'] = etree.tostring(doc, encoding='unicode')
        return res

    def split_code(self, code):
        res = code.split(self.contract_employment_type.related_sequence.prefix, 1)
        return res[1] if 1 < len(res) else res[0]

    def generate_id(self):
        for rec in self:
            # if not rec.private_email:
            #     raise ValidationError('Please fill Personal Email before Generating ID!')
            if not rec.country_id:
                raise ValidationError('Please fill Country before Generating ID!')
            # if not rec.state_id:
            #     raise ValidationError('Please fill City before Generating ID!')
            # if not rec.po_box:
            #     raise ValidationError('Please fill PO-Box before Generating ID!')
            if not rec.gender:
                raise ValidationError('Please fill Gender before Generating ID!')
            if not rec.religion:
                raise ValidationError('Please fill Religions before Generating ID!')
            if not rec.birthday:
                raise ValidationError('Please fill Date of Birth before Generating ID!')
            if not rec.place_of_birth:
                raise ValidationError('Please fill Place of Birth before Generating ID!')
            if not rec.country_of_birth:
                raise ValidationError('Please fill Country of Birth before Generating ID!')
            if not rec.marital:
                raise ValidationError('Please fill Marital Status before Generating ID!')
            # if not rec.emergency_contact:
            #     raise ValidationError('Please fill Emergency Contact before Generating ID!')

            if rec.contract_employment_type.related_sequence:
                rec.company_employee_id = self.env['ir.sequence'].next_by_code(rec.contract_employment_type.related_sequence.code)
                rec.system_id = rec.contract_employment_type.code + self.split_code(rec.company_employee_id)
                rec.id_generated = True
            else:
                raise ValidationError('Select Employee Type Before!')

    @api.onchange('contract_employment_type')
    def onchange_contract_employment_type(self):
        for rec in self:
            rec.id_generated = False

    def open_approve_employee_wizard(self):
        if not self.country_id:
            raise ValidationError('Please fill Country before Generating ID!')
        # if not rec.state_id:
        #     raise ValidationError('Please fill City before Generating ID!')
        # if not rec.po_box:
        #     raise ValidationError('Please fill PO-Box before Generating ID!')
        if not self.gender:
            raise ValidationError('Please fill Gender before Generating ID!')
        if not self.religion:
            raise ValidationError('Please fill Religions before Generating ID!')
        if not self.birthday:
            raise ValidationError('Please fill Date of Birth before Generating ID!')
        if not self.place_of_birth:
            raise ValidationError('Please fill Place of Birth before Generating ID!')
        if not self.country_of_birth:
            raise ValidationError('Please fill Country of Birth before Generating ID!')
        if not self.marital:
            raise ValidationError('Please fill Marital Status before Generating ID!')
        if not self.contract_employment_type.related_sequence:
            raise ValidationError('Select Employee Type Before!')

        default_event_type = self.env['sap.event.type'].search([('is_new_hire', '=', True)], limit=1)
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'approve.employee.event',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_employee_id': self.id,
                'default_event_type_id': default_event_type.id if default_event_type else False,
            }
        }

    def state_approve(self):
        self.reject_reason = ""
        if not self.id_generated:
            raise ValidationError('Generate ID before Approving!')
        else:
            self.write({'state': 'approved'})
            msg = _('Employee Approved')
            self.message_post(body=msg)

    def state_pending(self):
        self.write({'state': 'pending'})

    def log_and_reject(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Reject Reason',
            'res_model': 'log.note.reject.wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'view_id': self.env.ref('hr_employee_custom.log_note_reject_wizard_view_form').id,
            'context': {
                'related_name': self._name,
            }
        }

    def state_reject(self):
        if self.reject_reason:
            self.write({'state': 'reject'})
            msg = _('Employee Rejected. Rejection Reason: ' + self.reject_reason)
            self.message_post(body=msg)
        else:
            raise ValidationError('Must add reject reason!')

    @api.onchange('firstname', 'middlename', 'lastname')
    def _onchange_name(self):
        for rec in self:
            if rec.firstname and rec.middlename and rec.lastname:
                rec.name = (rec.firstname or '') + ' ' + (rec.middlename or '') + ' ' + (rec.lastname or '')


class Partner(models.Model):
    _inherit = 'res.partner'

    related_employee = fields.Many2one('hr.employee', 'Related Employee')

    state = fields.Selection([('pending', 'Pending Approval'), ('approved', 'Approved'), ('reject', 'Reject')],
                             default='pending',
                             string="Approval State")

    reject_reason = fields.Text('Reject Reason')

    contact_relation_type_id = fields.Many2one(
        comodel_name='contact.relation.type',
        string='Relation Type',
        required=False)

    gender = fields.Selection(
        string='Gender',
        selection=[('male', 'Male'),
                   ('female', 'Female'), ],
        required=False, )

    nationality = fields.Many2one(
        comodel_name='res.country',
        string='Nationality',
        required=False)

    country_id = fields.Many2one(
        comodel_name='res.country',
        string='Country of Birth',
        required=False)

    # passport_doc = fields.Many2one(
    #     comodel_name='documents.document',
    #     string='Passport Document',
    #     required=False
    # )
    #
    # passport_exp_date = fields.Date(
    #     related='passport_doc.expiry_date',
    #     string='Passport Expiry Date',
    #     required=False)

    # document_o2m = fields.One2many(
    #     comodel_name='documents.document',
    #     inverse_name='partner_id',
    #     string='Related Documents',
    #     required=False)

    # missing_documents = fields.Many2many('required.document', string='Missing/Expired Documents',
    #                                      compute='get_missing_documents')

    # @api.depends('document_o2m')
    # def get_missing_documents(self):
    #     for rec in self:
    #         group = rec.related_employee.contract_id.contract_group
    #         required_doc = self.env['required.document'].search(
    #             [('required_model', '=', 'dependent'), ('mandatory', '=', True)])
    #         results = self.env['required.document']
    #         for line in required_doc:
    #             if group.id == line.contract_group.id or not line.contract_group.id:
    #                 doc = rec.document_o2m.filtered(
    #                     lambda x: x.document_type_id.id == line.name.id and x.status in (
    #                         'active', 'na') and x.state == 'approved')
    #                 if not doc:
    #                     results |= line
    #         rec.missing_documents = results.ids
    #         return results

    def state_approve(self):
        # if self.missing_documents:
        #     raise ValidationError('Missing/Expired Required Documents!')
        super(Partner, self).state_approve()

    def contact_archive_onchange(self, active):
        self.contact_document_archive(active)
        related_contacts_list = self.env['res.partner'].search(
            [('parent_id', '=', self.id), ('active', '=', (not active))])
        for rec in related_contacts_list:
            rec.active = active

    def contact_document_archive(self, active):
        pass
        # document_list = self.env['documents.document'].search(
        #     [('partner_id', '=', self.id), ('active', '=', (not active))])
        # for rec in document_list:
        #     rec.active = active

    # def unlink(self):
    #     for rec in self:
    #         for doc in rec.document_o2m:
    #             doc.unlink()
    #         super(Partner, rec).unlink()

    def action_see_documents(self):
        self.ensure_one()
        # return {
        #     'name': _('Documents'),
        #     'res_model': 'documents.document',
        #     'type': 'ir.actions.act_window',
        #     'views': [(False, 'kanban'), (False, 'tree'), (False, 'form')],
        #     'view_mode': 'kanban',
        #     'context': {
        #         "search_default_partner_id": self.id,
        #         "default_partner_id": self.id,
        #         "searchpanel_default_folder_id": False,
        #         "hide_contact": True,
        #         "hide_service": True
        #     },
        # }

    # def _audit_logs(self, vals):
    #     for rec in self:
    #         log = "Following Fields Changed:<br/>"
    #         # message_post(body=_(u'Shipment N° %s has been cancelled' % picking.carrier_tracking_ref))
    #         for val in vals:
    #             log = log + "   - " + self._fields[val].string + " <br/>"
    #         rec.message_post(body=log)

    # def write(self, vals):
    #     # self._audit_logs(vals)
    #     # if vals and len(vals) > 1 or not vals.get('state'):
    #     #     vals.update({'state': 'pending'})
    #     # res = super(Partner, self).write(vals)
    #
    #     return res

    def state_approve(self):
        self.reject_reason = ""
        self.write({'state': 'approved'})
        msg = _('Dependent ' + self.name + ' Approved')
        self.related_employee.message_post(body=msg)

    def state_pending(self):
        self.write({'state': 'pending'})

    def log_and_reject(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Reject Reason',
            'res_model': 'log.note.reject.wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'view_id': self.env.ref('hr_employee_custom.log_note_reject_wizard_view_form').id,
            'context': {
                'related_name': self._name,
            }
        }

    def state_reject(self):
        if self.reject_reason:
            self.write({'state': 'reject'})
            msg = _('Dependent ' + self.name + ' Rejected. Rejection Reason: ' + self.reject_reason)
            self.related_employee.message_post(body=msg)
        else:
            raise ValidationError('Must add reject reason!')
