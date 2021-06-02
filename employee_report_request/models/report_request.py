# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import UserError


class ReportRequest(models.Model):
    _name = 'report.request'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _description = "Employee Report Request"

    # def _get_default_employee(self):
    #     """
    #     :Author:Bhavesh Jadav Tech Ultra
    #     :Date: 23/09/2020
    #     :Func:this method use for the set default employee
    #     :return: employee id or False
    #     """
    #     if self.env.user.employee_id:
    #         return self.env.user.employee_id
    #     else:
    #         return False

    name = fields.Char(string="Name")
    employee_id = fields.Many2one('hr.employee')  # default=_get_default_employee
    # employee_id = fields.Many2one('hr.employee', compute='compute_employee_id', store=True)
    # employee_selection = fields.Selection(selection=lambda self: self.get_employee())
    request_owner_id = fields.Many2one('res.users', string="Request Owner")
    letter_type = fields.Selection(string='Letter Type', selection=lambda self: self.get_letter_type(), copy=False,
                                   store=True,
                                   default='bank_letter')
    letter_lang = fields.Selection([('english', 'English'),
                                    ('arabic', 'Arabic')],
                                   string='Letter Language',
                                   copy=False,
                                   default='english')

    whom_this_letter_issue = fields.Selection([('bank', 'Bank'),
                                               ('embassy', 'Embassy'),
                                               ('other', 'Other Entities')],
                                              string='to whom this letter is issue?',
                                              copy=False,
                                              default='bank')
    bank_id = fields.Many2one('res.bank')
    embassy_id = fields.Many2one('res.embassy')
    other_entities_id = fields.Many2one('res.other.entities')
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company)
    submit_date = fields.Datetime('Date')
    state = fields.Selection([('new', 'New'), ('submitted', 'Submitted')],
                             string='Status', readonly=False, required=True, tracking=True, copy=False, default='new')
    auto_unique_num = fields.Integer(string="Auto Generate NO.", readonly=1)
    reference = fields.Char(string="Reference")

    def get_letter_type(self):
        """
        :Author :Bhavesh Jadav TechUltra solutions
        :Date:17/09/2020
        :Func:This method use for the hide Immigration Letter option if user group_strata_hc
        """
        if self.env.user.has_group('security_rules.group_hc_employee'):
            return [('bank_letter', 'Bank Letter'), ('to_whom_it_may_concern', ' To Whom it May Concern'),
                    ('employment_letter', 'Employment Letter'), ('immigration_letter', 'Immigration Letter')]
        else:
            return [('bank_letter', 'Bank Letter'), ('to_whom_it_may_concern', ' To Whom it May Concern'),
                    ('employment_letter', 'Employment Letter')]

    @api.onchange('company_id')
    def onchange_employee(self):
        """
        Author:Bhavesh Jadav TechUltra solutions
        Date:  17/09/2020
        Func: for apply dynamic domain
        :return: domain
        """
        self.employee_id = self.env.user.employee_id.id
        self.bank_id = self.env.user.employee_id.current_bank_name.id
        if self.env.user.has_group('security_rules.group_hc_employee'):
            employees = self.env['hr.employee'].search([])
            self.employee_id = self.env.user.employee_id.id
            self.bank_id = self.env.user.employee_id.current_bank_name.id
            return {'domain': {'employee_id': [('id', 'in', employees.ids)]}}

        elif self.env.user.has_group('security_rules.group_strata_employee'):
            if self.env.user.employee_id:
                self.employee_id = self.env.user.employee_id.id
                self.bank_id = self.env.user.employee_id.current_bank_name.id
                return {'domain': {'employee_id': [('id', '=', self.env.user.employee_id.id)]}}
            else:
                # if the login user are not employee and the is in employee group then its blank
                return {'domain': {'employee_id': [('id', 'in', [-1])]}}
        else:
            return {'domain': {'employee_id': [('id', 'in', [-1])]}}

    @api.onchange('employee_id')
    def onchange_employee2(self):
        for rec in self:
            rec.bank_id = rec.employee_id.current_bank_name.id

    @api.onchange('letter_type')
    def _onchange_lan(self):
        """
        Author:Bhavesh Jadav TechUltra solutions
        Date:15/09/2020
        Func: set language based on the report type
        :return:
        """
        if self.letter_type == 'bank_letter':
            self.letter_lang = 'english'
            self.whom_this_letter_issue = 'bank'
        if self.letter_type == 'immigration_letter':
            self.letter_lang = 'arabic'
            self.whom_this_letter_issue = 'embassy'

    @api.model
    def create(self, vals):
        """
        Author:Bhavesh Jadav TechUltra Solutions
        Func: Add auto generate sequence for the request.report
        :param vals: request. report vals
        :return: result
        """
        vals['name'] = self.env['ir.sequence'].next_by_code('report.request') or _('New')
        vals['auto_unique_num'] = self.env['ir.sequence'].next_by_code('auto.generate.num')
        vals['request_owner_id'] = self.env.user.id
        res = super(ReportRequest, self).create(vals)
        return res

    def action_print_report(self):
        """
        :Author: Bhavesh Jadav TechUltra solutions
        :Date:14/08/2020
        :Func:this method use for the print the specific report from the print letters button
        :return: Report Action
        """
        if self.letter_type == "bank_letter":
            return self.env.ref('employee_report_request.report_bank_letter_eng').report_action(self)
        if self.letter_type == "to_whom_it_may_concern" and self.letter_lang == 'english':
            return self.env.ref('employee_report_request.report_whom_it_may_concern_letter_eng').report_action(self)
        if self.letter_type == "to_whom_it_may_concern" and self.letter_lang == 'arabic':
            return self.env.ref('employee_report_request.report_whom_it_may_concern_letter_arabic').report_action(self)
        if self.letter_type == "employment_letter" and self.letter_lang == 'english':
            return self.env.ref('employee_report_request.report_employment_letter_eng').report_action(self)
        if self.letter_type == "employment_letter" and self.letter_lang == 'arabic':
            return self.env.ref('employee_report_request.report_employment_letter_arabic').report_action(self)
        if self.letter_type == "immigration_letter":
            return self.env.ref('employee_report_request.report_immigration_letter_arabic').report_action(self)

    def action_submit(self):
        """
        :Author: Bhavesh Jadav TechUltra solutions
        :Date:14/08/2020
        :Func:this method use for the change the state submit the report request
        :Return:True
        """
        # employee_id = self.env.user.employee_id
        if self.employee_id and self.employee_id.contract_id and self.employee_id.contract_id.related_resign_request and self.employee_id.contract_id.related_resign_request.filtered(
                lambda r: r.state != 'cancel'):
            raise UserError(_(
                'The selected employee is not authorized to request these letters because the employee has resigned '
                'request please contact your higher authority.'))

        missing_docs = self.employee_id.missing_documents.filtered(lambda x: not x.exclude_in_letter)

        if self.employee_id and missing_docs:
            # doc_name = ','.join(employee_id.missing_documents.mapped('name').mapped('name'))
            raise UserError(_(
                "You had some expired and missing documents "
                "we can not allowed proceed with expired and missing documents please contact your higher authority."
                "\n Employee Name: {} \n Expired and Missing Documents:\n {}".format(
                    self.employee_id.name,
                    '\n '.join(self.employee_id.missing_documents.mapped('name').mapped('name')))))
        self.write({'state': 'submitted',
                    'submit_date': datetime.now()})
        reference = self.reference_generator()
        if reference:
            self.write({'reference': reference})
        return True

    # ------- Report Methods --------
    def reference_generator(self):
        """
        Author: Bhavesh Jadav TechUltra solutions
        Date:14/08/2020
        Func:this method use for the generate reference for the report based on the report type
        :return: reference
        """
        ref = ''
        submit_date = self.submit_date.strftime('%Y%m%d') if self.submit_date else datetime.now().strftime('%Y%m%d')
        system_id = self.employee_id.system_id
        if self.letter_type == 'bank_letter':
            ref = 'GS' + submit_date + 'BL' + system_id + str(self.auto_unique_num)
        if self.letter_type == 'to_whom_it_may_concern':
            ref = 'GS' + submit_date + 'TWL' + system_id + str(self.auto_unique_num)
        if self.letter_type == 'employment_letter':
            ref = 'GS' + submit_date + 'EL' + system_id + str(self.auto_unique_num)
        if self.letter_type == 'immigration_letter':
            ref = 'GS' + submit_date + 'IL' + system_id + str(self.auto_unique_num)
        return ref

    def date_format(self, arabic=False):
        """
        Author:Bhavesh Jadav TechUltra solutions
        Date: 14/09/2020
        :return:print date with proper format
        """
        if arabic:
            return datetime.today().strftime("%d/%m/%Y")
        return datetime.today().strftime("%d %B, %Y")

    def emp_passport_num(self):
        """
        Author:Bhavesh Jadav TechUltra Solutions
        Date: 14/09/2020
        Func: get newest pass port number
        :return:passport_no
        """
        # we need to search because of domain we can not use employee_id.own_document_o2m
        document_type_passport = self.env['document.types'].search([('name', '=', 'Passport')], limit=1)
        if document_type_passport:
            passport_id = self.env['documents.document'].search(
                [('res_id', '=', self.employee_id.id), ('status', '=', 'active'), ('res_model', '=', 'hr.employee'),
                 ('document_type_id', '=', document_type_passport.id)], limit=1, order='desc')

            return passport_id.passport_no
        else:
            return '    '

    def emp_salary_monthly(self):
        """
        Author:Bhavesh Jadav TechUltra Solutions
        Date: 14/09/2020
        Func: get monthly salary with currency code
        :return: monthly salary with currency code string
        """
        try:
            salary_monthly = self.employee_id.contract_id.wage
        except:
            salary_monthly = 0.0
        return str("{:,}".format(round(salary_monthly, 2))) + ' ' + str(self.company_id.currency_id.name)

    def contract_wage(self):
        """
        :Author:Bhavesh Jadav TechUltra Solutions
        :Date: 23/09/2020
        :Func: for the english currency name
        :return:str: contract wage + currency in english
        """
        return str("{:,}".format(round(self.employee_id.contract_id.wage, 2))) + ' ' + str(
            self.company_id.currency_id.name)

    def get_entities_name(self):
        """
        :Author: Bhavesh Jadav TechUltra Solutions
        :Date:23/09/2020
        :Func: this method use for the add bank,embassy,other entities name in english and the arabic base on the letter_lang
        :return:str:bank,embassy,other entities name in english and arabic
        """
        if self.letter_type == 'employment_letter':
            if self.whom_this_letter_issue == 'bank':
                if self.letter_lang == 'english':
                    return str(self.bank_id.name)
                elif self.letter_lang == 'arabic':
                    return str(self.bank_id.arabic_bank_name)
            elif self.whom_this_letter_issue == 'embassy':
                if self.letter_lang == 'english':
                    return str(self.embassy_id.name)
                elif self.letter_lang == 'arabic':
                    return str(self.embassy_id.arabic_name)
            elif self.whom_this_letter_issue == 'other':
                if self.letter_lang == 'english':
                    return str(self.other_entities_id.name)
                elif self.letter_lang == 'arabic':
                    return str(self.other_entities_id.arabic_name)

    def get_responsible_info(self, name=False, position=False, english=False, arabic=False, signature=False):
        """
        :Author: Bhavesh Jadav TechUltra Solutions
        :Date:23/09/2020
        :Func:This method use for the return responsible person info
        :return responsible person info
        """
        select_type = self.env['ir.config_parameter'].sudo()
        responsible_person = select_type.get_param('res.config.settings.responsible_report_person_id')
        if responsible_person and self.env['responsible.report.person'].search(
                [('id', '=', int(responsible_person))]):
            responsible_person = self.env['responsible.report.person'].browse(int(responsible_person))
            if name and english:
                return responsible_person.person_name_eng and str(responsible_person.person_name_eng) or ''
            if name and arabic:
                return responsible_person.person_name_arab and str(responsible_person.person_name_arab) or ''
            if position and english:
                return responsible_person.person_position_eng and str(responsible_person.person_position_eng) or ''
            if position and arabic:
                return responsible_person.person_position_arab and str(responsible_person.person_position_arab) or ''
            if signature:
                return responsible_person.person_signature or False

        # ------------- extra methods -------------
    def get_employee(self):
        """
        Author:Bhavesh Jadav TechUltra Solutions
        Date:10/09/2020
        Func:prepare list of tuple for the dynamic selection field for the employee
        :return: list: for selection combinations with the employees id and the employee name
        """
        data = []
        employees = []
        employee_id = self.env.user.employee_id
        if employee_id and self.env.user.has_group('security_rules.group_strata_employee'):
            data.append((str(employee_id.id), str(employee_id.name)))
            return data
            # employees = list(set(self.get_child_of_employee(employee_id)))
            # employees = employee_id.browse(employees)
        if employees:
            for employee in employees:
                data.append((str(employee.id), str(employee.name)))
        return data

    # def get_child_of_employee(self, child_ids):
    #     """
    #     Author:Bhavesh Jadav TechUltra Solutions
    #     Date: 10/09/2020
    #     Func: this method get child ids using recursion
    #     :param child_ids:use for the child id of the employee
    #     :return: data list of the all child id
    #     """
    #     data = []
    #     for employee in child_ids:
    #         if employee.child_ids:
    #             result = self.get_child_of_employee(employee.child_ids) + [employee.id]
    #             data += result
    #         else:
    #             data.append(employee.id)
    #     return data

    # def get_embassy(self):
    #     data = []
    #     embassy_ids = self.env['res.embassy'].search_read(domain=[],
    #                                                       fields=['id', 'name', 'arabic_name'])
    #     for embassy_id in embassy_ids:
    #         data.append(
    #             (str(embassy_id.get('id')), str(embassy_id.get('name') + ' : ' + embassy_id.get('arabic_name'))))
    #     return data

    # def get_bank(self):
    #     data = []
    #     bank_ids = self.env['res.bank'].search_read(domain=[], fields=['id', 'name', 'arabic_bank_name'])
    #     for bank_id in bank_ids:
    #         data.append((str(bank_id.get('id')), str(bank_id.get('name') + ' : ' + bank_id.get('arabic_bank_name'))))
    #     return data

    # @api.depends('employee_selection')
    # def compute_employee_id(self):
    #     """
    #     Author: Bhavesh Jadav TechUltra solutions
    #
    #     :return:
    #     """
    #     for rec in self:
    #         rec.employee_id = self.env['hr.employee'].browse(int(rec.employee_selection) or [])
