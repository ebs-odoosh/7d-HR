from odoo import fields, models, api, _
from odoo.exceptions import Warning
from datetime import datetime


class ApprovalRequest(models.Model):
    _inherit = 'approval.request'

    can_create_bank_change = fields.Boolean('Create Bank Change', compute='_create_bank_change', default=False,
                                            store=True)
    bank_changes_request = fields.One2many('employee.bank.change', inverse_name='bank_change_approval',
                                           string='Bank Change', required=False)
    employee_name = fields.Many2one('hr.employee', string="Employee Name")
    employee_number = fields.Char(related='employee_name.strata_id', string="Strata Id")
    department_id_e_bank = fields.Many2one(related='employee_name.department_id', string="Department")
    date_of_join_e_bank = fields.Date(related='employee_name.contract_id.date_start', string="Date of joining")
    current_bank_name = fields.Many2one('res.bank', string='Current Bank Name')
    current_iban = fields.Char(string='Current IBAN', size=23)
    current_account_number = fields.Char(string='Current Account Number', size=16)
    account_number = fields.Char(string='Account Number', size=16)
    iban = fields.Char(string='IBAN', size=23)
    # effective_month_year = fields.Date(string='Effective Month/Year')
    select_bank = fields.Many2one('res.bank', string='Select Bank')
    effective_month = fields.Selection(
        [('1', 'January'), ('2', 'February'), ('3', 'March'), ('4', 'April'), ('5', 'May'), ('6', 'June'),
         ('7', 'July'), ('8', 'August'), ('9', 'September'), ('10', 'October'), ('11', 'November'),
         ('12', 'December')], string='Effective Month/Year')

    @api.onchange('employee_name')
    def onchange_name_subject(self):
        """
        :Author:Nimesh Jadav TechUltra Solutions
        :Date:27/11/2020
        :Func:this method use for the add name with with strata id
        :Return:list with name and strata id
        """
        for employee in self:
            if employee.is_bank_changes_request == 'yes':
                employee.name = str(employee.category_id.name) + " - " + str(
                    employee.employee_name.name or '') + " - " + str(employee.employee_name.strata_id or '')

    def action_approve(self, approver=None):
        res = super(ApprovalRequest, self).action_approve(approver=approver)
        if self.is_bank_changes_request == 'yes' and self.request_status == 'approved':
            self.create_bank_changes()
        return res

    @api.constrains('current_iban', 'iban')
    def constrains_check_iban(self):
        if self.current_iban or self.iban:
            if self.current_iban:
                if self.current_iban[:2] != "AE":
                    raise Warning("Make sure Current IBAN Start with the 'AE'")
            if self.iban:
                if self.iban[:2] != "AE":
                    raise Warning("Make sure IBAN Start with the 'AE'")

    @api.model
    def year_selection(self):
        year = datetime.now().year
        last_year = datetime.now().year + 10
        year_list = []
        while year != last_year:
            year_list.append((str(year), str(year)))
            year += 1
        return year_list

    effective_year = fields.Selection(year_selection, string="Year", default=str(datetime.now().year))
    current_bank_name_msg = fields.Many2one(related='current_bank_name')

    is_bank_changes_request = fields.Selection(related="category_id.is_bank_changes_request")

    # Related with Category
    has_employee_name = fields.Selection(related="category_id.has_employee_name")
    has_employee_number = fields.Selection(related="category_id.has_employee_number")
    has_department_id_e_bank = fields.Selection(related="category_id.has_department_id_e_bank")
    has_date_of_join_e_bank = fields.Selection(related="category_id.has_date_of_join_e_bank")
    has_current_bank_name = fields.Selection(related="category_id.has_current_bank_name")
    has_current_iban = fields.Selection(related="category_id.has_current_iban")
    has_current_account_number = fields.Selection(related="category_id.has_current_account_number")

    has_account_number = fields.Selection(related="category_id.has_account_number")
    has_iban = fields.Selection(related="category_id.has_iban")
    has_effective_month_year = fields.Selection(related="category_id.has_effective_month_year")
    has_select_bank = fields.Selection(related="category_id.has_select_bank")

    # limit_month_day = fields.Integer(related='category_id.has_limit_month_day')

    @api.onchange('effective_month', 'effective_year')
    def _onchange_check_month(self):
        if self.effective_month:
            month = datetime.now().month
            year = datetime.now().year
            if month > int(self.effective_month) and year == int(self.effective_year):
                raise Warning("You can't choose past month")

    @api.depends('request_status', 'is_bank_changes_request')
    def _create_bank_change(self):
        for rec in self:
            bank_rec = rec.env['employee.bank.change'].search([('bank_change_approval', '=', rec.id)])
            if rec.request_status == 'approved' and rec.is_bank_changes_request == 'yes' and not bank_rec:
                rec.can_create_bank_change = True
            else:
                rec.can_create_bank_change = False

    @api.onchange('request_owner_id')
    def onchange_employee(self):
        """
        Author:Bhavesh Jadav TechUltra solutions
        Date:  17/09/2020
        Func: for apply dynamic domain
        :return: domain
        """
        if self.env.user.employee_id:
            self.employee_name = self.env.user.employee_id.id
            return {'domain': {'employee_name': [('id', '=', self.env.user.employee_id.id)]}}
        else:
            return {'domain': {'employee_name': [('id', 'in', [-1])]}}

    @api.onchange('employee_name')
    def onchange_current_bank_details(self):
        """
            Author:Nimesh Jadav TechUltra solutions
            Date:  07/10/2020
            Func: Compute current bank details
            :return: set value to the fields
        """
        for rec in self:
            if rec.employee_name and rec.employee_name.current_bank_name:
                rec.current_bank_name = rec.employee_name.current_bank_name.id or ''
            else:
                rec.current_bank_name = ''
            rec.current_account_number = rec.employee_name and rec.employee_name.current_account_number or ''
            rec.current_iban = rec.employee_name and rec.employee_name.iban or ''

    # @api.onchange('effective_month_year')
    # def onchange_split_date(self):
    #     if self.effective_month_year:
    #         year = self.effective_month_year.strftime('%Y')
    #         self.effective_month = self.effective_month_year.strftime('%m')
    #         month = dict(self._fields['effective_month'].selection).get(self.effective_month)
    #         self.effective_date = month + "  " + year

    def create_bank_changes(self):
        employee_bank = self.env['employee.bank.change']
        # model = self._context.get('params').get('model')
        attachment = self.env['ir.attachment'].search(
            [('res_model', '=', 'approval.request'), ('res_id', '=', self.id)],
            limit=1)
        month = dict(self._fields['effective_month'].selection).get(self.effective_month)
        bank_history_val = {'employee_bank_change': self.employee_name.id or '',
                            'current_bank_name': self.select_bank.id or '',
                            'current_iban': self.iban or '',
                            'current_account_number': self.account_number or '',
                            'select_bank': self.current_bank_name.id or '',
                            'iban': self.current_iban or '',
                            'account_number': self.current_account_number or '',
                            'effective_month_year': (month or '') + "  " + (self.effective_year or ''),
                            # 'effective_date': self.effective_date or '',
                            'limit_month_day': self.category_id.has_limit_month_days,
                            'attachment': attachment.datas or '',
                            }
        bank_request = employee_bank.create(bank_history_val)
        if bank_request:
            self.bank_changes_request = bank_request

    def action_confirm(self):
        if not self.attachment_number and self.category_id.is_bank_changes_request == 'yes':
            raise Warning(_("You have to attach at least one document."))
        # if self.category_id.is_bank_changes_request == 'yes':
            # old_request = self.env['approval.request'].search(
            #     [('employee_name', '=', self.employee_name.id),
            #      ('account_number', '=', self.account_number),
            #      ('request_status', 'in', ('approved', 'pending', 'under_approval'))])

            # if len(old_request) > 0:
            #     raise Warning(_("You already have Same Request Submitted or Approved"))
        if self.is_bank_changes_request == 'yes':
            year = datetime.now().year
            month = datetime.now().month
            if self.category_id.has_limit_month_days < datetime.now().day and int(self.effective_year) == year and int(
                    self.effective_month) == month:
                raise Warning("Your limit month days is more then current month days, please choose next month")
        res = super(ApprovalRequest, self).action_confirm()
        return res

    def action_print_employee_bank_change_report(self):
        """
        :Author:Nimesh Jadav TechUltra solutions
        :Date:21/10/2020
        :Func:This method use to download Employee Bank Change request report
        :Return:Report action xml id
        """
        return self.env.ref('employee_bank_approvals.report_bank_change').report_action(self)
