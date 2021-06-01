from odoo import models, fields, api, _
from odoo.exceptions import UserError
import datetime
from datetime import date
from dateutil import tz
import pytz


class EmployeeTravelRequest(models.Model):
    _name = 'employee.travel.request'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = 'Employee Travel Request'
    _rec_name = 'name'
    _order = 'id desc'

    @api.model
    def _read_group_request_status(self, stages, domain, order):
        request_status_list = dict(self._fields['request_status'].selection).keys()
        return request_status_list

    name = fields.Char(string="Name")
    reference = fields.Char(string="Reference", track_visibility='onchange')
    employee_id = fields.Many2one('hr.employee', track_visibility='onchange')
    request_owner_id = fields.Many2one('res.users', string="Request Owner", default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company)
    travel_purpose = fields.Char(string="Travel Purpose", track_visibility='onchange')
    travel_type = fields.Selection([('business_trip', 'Business Trip'), ('training_trip', 'Training Trip')],
                                   string="Travel Type", track_visibility='onchange', default='business_trip')
    travel_start_date = fields.Datetime(strig='start Date', default=fields.Datetime.now)
    travel_end_date = fields.Datetime('Return Date')
    accommodation_type = fields.Selection(
        [('by_company', 'Company'), ('by_self', 'Self')],
        string="Accommodation Type", track_visibility='onchange', default='by_company')
    travel_comment = fields.Text(string="Comment", track_visibility='onchange')
    quotation_comment = fields.Text(string="Justification", track_visibility='onchange')
    employee_contact_number = fields.Char(string="Contact Number")
    employee_email = fields.Char(string="Email")

    travel_cost_center_lines = fields.One2many('travel.cost.center.line', 'travel_request_id',
                                               string="Travel Cost Center Line", track_visibility='onchange',
                                               required=True)
    travel_request_quotation_lines = fields.One2many('travel.request.quotation', 'travel_request_id',
                                                     string="Quotation lines", track_visibility='onchange')

    travel_request_quotation_line = fields.Many2one('travel.request.quotation', string="Select Quotation",
                                                    track_visibility='onchange')
    set_default_quotation = fields.Boolean(string="Set Default Quotation", default=False)
    request_submit_date = fields.Datetime(string="Submission Date")
    approval_date = fields.Datetime(string='Approval Date')

    from_city = fields.Char(string="From City")
    from_state_id = fields.Many2one("res.country.state", string='From State')
    from_zip = fields.Char(string='From zip')
    from_country_id = fields.Many2one('res.country', string='From Country')

    to_city = fields.Char(string="To City")
    to_state_id = fields.Many2one("res.country.state", string='To State')
    to_zip = fields.Char(string='To zip')
    to_country_id = fields.Many2one('res.country', string='To Country')

    # base fields
    travel_settings_id = fields.Many2one('travel.request.settings', string="Travel Setting", required=True,
                                         compute='_compute_travel_settings_id')
    approval_minimum = fields.Integer(related="travel_settings_id.approval_minimum")

    approver_ids = fields.One2many('travel.request.approver', 'request_id', string="Approvers")
    user_status = fields.Selection([
        ('new', 'New'),
        ('pending', 'To Approve'),
        ('approved', 'Approved'),
        ('refused', 'Refused'),
        ('cancel', 'Cancel')], compute="_compute_user_status")

    request_status = fields.Selection([
        ('new', 'NEW'),
        ('wait_for_quotations', 'Wait For Quotations'),
        ('select_quotation', 'Select Quotation'),
        ('pending', 'Submitted'),
        ('under_approval', 'Under Approval'),
        ('approved', 'Approved'),
        ('returned', 'Add Expenses'),
        ('expenses_added', 'Expenses Added'),
        ('refused', 'Refused'),
        ('cancel', 'Cancel')], default="new", compute="_compute_request_status", store=True, compute_sudo=True,
        group_expand='_read_group_request_status')
    note = fields.Text(string="Note")
    has_access_travel_quotation = fields.Boolean(string="Has Access travel_quotation",
                                                 compute="_compute_has_access_travel_quotation")
    hr_expense_ids = fields.One2many("hr.expense", 'travel_request_id', string="Expense Line")
    is_return_employee = fields.Boolean(string="Is Return Employee")
    is_expense_report_created = fields.Boolean(string="Is Expense Report Created",
                                               compute='_compute_expense_report_created',
                                               default=False)
    expense_sheet_ids = fields.Many2many('hr.expense.sheet',
                                         string='Created Expense Sheet', readonly=True,
                                         copy=False)
    trip_days = fields.Integer(string="Total Trip Days", compute="_compute_trip_days", store=True)
    project_id = fields.Many2one('project.project', 'Project')
    expense_count = fields.Integer(compute='_compute_expense_count', string='Number of Generated Expense')
    perdiem_rule = fields.Many2one('travel.perdiem.rule', string="Perdiem Rule")
    class_of_travel_str = fields.Char(string="Class Of Travel",
                                      help="This field use only to get selection value for using  the send mail to "
                                           "travel agency ")

    read_only_user = fields.Boolean(default=False, compute='_get_user_group')

    @api.depends('company_id')
    def _get_user_group(self):
        user = self.env.user
        for rec in self:
            rec.read_only_user = True
            if user.has_group('security_rules.group_travel_quotation_employee'):
                rec.read_only_user = False

    def _compute_expense_count(self):
        for rec in self:
            rec.expense_count = len(rec.expense_sheet_ids)
        return True

    @api.depends('expense_sheet_ids')
    def _compute_expense_report_created(self):
        for rec in self:
            expense_sheet_id = rec.expense_sheet_ids.filtered(
                lambda expense_sheet_id: expense_sheet_id.state == 'draft')
            if expense_sheet_id:
                rec.is_expense_report_created = True
            elif not expense_sheet_id:
                rec.is_expense_report_created = False

    def _compute_has_access_travel_quotation(self):
        if self.env.user.has_group('employee_travel_management.group_travel_quotation_employee'):
            self.has_access_travel_quotation = True
        else:
            self.has_access_travel_quotation = False
            return True

    @api.depends('travel_start_date', 'travel_end_date', 'from_country_id', 'to_country_id')
    def _compute_trip_days(self):
        for rec in self:
            if rec.travel_start_date and rec.travel_end_date and rec.from_country_id and rec.to_country_id:
                # total_nights = 0
                # total_days = 0
                # user_tz = pytz.timezone(self.env.context.get('tz') or self.env.user.tz)
                # travel_start_date_in_local = pytz.utc.localize(rec.travel_start_date).astimezone(user_tz)
                # travel_end_date_in_local = pytz.utc.localize(rec.travel_end_date).astimezone(user_tz)
                # days = datetime.datetime.strptime(str(rec.travel_end_date), "%Y-%m-%d") - datetime.datetime.strptime(
                #     str(rec.travel_start_date),
                #     "%Y-%m-%d")
                if rec.from_country_id.code == 'AE' and rec.to_country_id.code == 'AE':
                    travel_end_date = rec.travel_end_date
                    travel_end_date = travel_end_date.replace(hour=13, minute=00, second=00)
                    days = (travel_end_date - rec.travel_start_date).days
                    if rec.from_country_id.id != rec.to_country_id.id:
                        hours, remainder = divmod((travel_end_date - rec.travel_start_date).seconds, 3600)
                        if hours > 12:
                            days += 1
                    rec.trip_days = days
                else:
                    travel_end_date = rec.travel_end_date.replace(hour=13, minute=00, second=00)
                    days = (travel_end_date - rec.travel_start_date).days
                    rec.trip_days = days + 1
            else:
                rec.trip_days = False

        return True

    @api.onchange('from_country_id')
    def _onchange_from_country_id(self):
        res = {'domain': {'from_state_id': []}}
        if self.from_country_id:
            res['domain']['from_state_id'] = [('country_id', '=', self.from_country_id.id)]
        return res

    @api.onchange('to_country_id')
    def _onchange_to_country_id(self):
        res = {'domain': {'to_state_id': []}}
        if self.to_country_id:
            res['domain']['to_state_id'] = [('country_id', '=', self.to_country_id.id)]
        return res

    @api.onchange('travel_request_quotation_line')
    def _onchange_travel_quotation(self):
        """
        Author:Bhavesh Jadav TechUltra solutions
        Date:  17/09/2020
        Func: for apply dynamic domain
        :return: domain
        """
        travel_request_quotation_lines = self.travel_request_quotation_lines and self.travel_request_quotation_lines.ids or []
        return {'domain': {'travel_request_quotation_line': [('id', 'in', travel_request_quotation_lines)]}}

    def _compute_has_access_to_request(self):
        is_approval_user = self.env.user.has_group('approvals.group_approval_user')
        for request in self:
            request.has_access_to_request = request.request_owner_id == self.env.user and is_approval_user

    @api.depends('request_owner_id')
    def _compute_travel_settings_id(self):
        travel_settings_id = self.env['travel.request.settings'].search([], limit=1)
        for rec in self:
            rec.travel_settings_id = travel_settings_id

    @api.depends('approver_ids.status', 'is_return_employee', 'is_expense_report_created')
    def _compute_request_status(self):
        for request in self:
            status_lst = request.mapped('approver_ids.status')
            # minimal_approver = request.approval_minimum if len(status_lst) >= request.approval_minimum else len(
            #     status_lst)
            if status_lst:
                if status_lst.count('cancel'):
                    status = 'cancel'
                elif status_lst.count('refused'):
                    status = 'refused'
                elif status_lst.count('new') and not status_lst.count('pending') and not status_lst.count('approved'):
                    status = 'new'
                elif 0 < status_lst.count('approved') < len(status_lst):
                    status = 'under_approval'
                elif status_lst.count('approved') == len(status_lst):
                    if request.is_return_employee and not request.is_expense_report_created:
                        status = 'returned'
                    elif request.is_expense_report_created:
                        status = 'expenses_added'
                    else:
                        status = 'approved'
                else:
                    status = 'pending'
            else:
                status = 'new'
            request.request_status = status

    def action_cancel(self):
        activity = self.env.ref('employee_travel_management.mail_activity_data_travel_request').id
        self.sudo()._get_user_approval_activities(user=self.env.user, activity_type_id=activity).unlink()
        activity = self.env.ref('employee_travel_management.mail_activity_data_travel_employee').id
        self.sudo()._get_user_approval_activities(user=self.env.user, activity_type_id=activity).unlink()
        self.mapped('approver_ids').write({'status': 'cancel'})

    @api.depends('approver_ids.status')
    def _compute_user_status(self):
        for approval in self:
            approvers = approval.approver_ids.filtered(
                lambda approver: approver.user_id == self.env.user).filtered(
                lambda approver: approver.status != 'approved').sorted(lambda x: x.sequence)
            if len(approvers) > 0:
                approval.user_status = approvers[0].status
            else:
                approval.user_status = False

    def _get_user_approval_activities(self, user, activity_type_id):
        domain = [
            ('res_model', '=', 'employee.travel.request'),
            ('res_id', 'in', self.ids),
            ('activity_type_id', '=', activity_type_id),
            ('user_id', '=', user.id)
        ]
        activities = self.env['mail.activity'].search(domain)
        return activities

    def action_wait_for_quotations(self):
        if len(self.approver_ids) < self.approval_minimum:
            raise UserError(
                _("You have to add at least {} approvers to confirm your request.".format(self.approval_minimum)))
        self.write({'request_submit_date': fields.Datetime.now(),
                    'request_status': 'wait_for_quotations'})
        rule = self.travel_settings_id.perdiem_rule_lines.filtered(
            lambda
                rule: rule.min_days <= self.trip_days <= rule.max_days and self.employee_id.contract_id.job_grade.id in rule.job_grade_ids.ids)
        if rule and len(rule) == 1:
            class_of_travel = dict(rule._fields['class_of_travel'].selection).get(
                rule.class_of_travel) or ''
            self.write({'perdiem_rule': rule.id,
                        'class_of_travel_str': class_of_travel})
            self.mail_sent_travel_agency()

    def mail_sent_travel_agency(self):
        if self.travel_settings_id.travel_agency_ids:
            mail_obj = self.env['mail.mail']
            email_template = self.env.ref('employee_travel_management.mail_template_travel_agency_quotation', False)
            mail_id = email_template.send_mail(self.id)
            mail = mail_obj.browse(mail_id)
            mail.recipient_ids = self.travel_settings_id.travel_agency_ids
            mail.email_from = self.travel_settings_id.email_from
            mail.reply_to = self.travel_settings_id.reply_to
            mail.send()
        return True

    def action_quotation_submit(self):
        if not self.travel_request_quotation_lines:
            raise UserError(_('Please Add Travel Quotations '))
        self.write({'request_status': 'select_quotation'})
        if self.employee_id.user_id:
            self.activity_schedule('employee_travel_management.mail_activity_data_travel_employee',
                                   user_id=self.employee_id.user_id.id)

    def action_submit_request(self):
        if not self.travel_request_quotation_line:
            raise UserError(_('Before proceeding you need to select a travel quotation\n'
                              'Please mark TRUE in  (Set Quotation) checkbox and select your Quotation'))
        requests = \
            self.mapped('approver_ids').filtered(lambda approver: approver.status == 'new').sorted('sequence')[
                0]
        requests._create_activity()
        requests.write({'status': 'pending'})
        activity = self.env.ref('employee_travel_management.mail_activity_data_travel_employee').id
        self.sudo()._get_user_approval_activities(user=self.env.user, activity_type_id=activity).action_feedback()

    def add_admin_approver(self):
        request_approver = self.env['travel.request.approver']
        if self.approver_ids.filtered(
                lambda
                        id: id.user_id == self.env.user) and self.request_owner_id == self.env.user and self.request_owner_id != self.travel_settings_id.default_approver and not self.approver_ids.filtered(
            lambda approver_id: approver_id.user_id == self.travel_settings_id.default_approver):
            vals = {'user_id': self.travel_settings_id.default_approver and self.travel_settings_id.default_approver.id,
                    'status': 'new',
                    'request_id': self.id,
                    'sequence': self.approver_ids.mapped('sequence')[-1] + 1}
            request_approver = request_approver.create(vals)
        return request_approver

    def action_approve(self, approver=None):
        if not isinstance(approver, models.BaseModel):
            approver = self.mapped('approver_ids').filtered(
                lambda approver: approver.user_id == self.env.user
            ).filtered(
                lambda approver: approver.status != 'approved').sorted(lambda x: x.sequence)
        if len(approver) > 0:
            approver[0].write({'status': 'approved', 'approval_date': datetime.datetime.now()})
        activity = self.env.ref('employee_travel_management.mail_activity_data_travel_request').id
        self.sudo()._get_user_approval_activities(user=self.env.user, activity_type_id=activity).action_feedback()
        approvers = self.mapped('approver_ids').filtered(lambda approver: approver[0].status == 'new').sorted(
            'sequence')
        if not approvers:
            admin_approver = self.add_admin_approver()
            approvers = self.mapped('approver_ids').filtered(lambda approver: approver[0].status == 'new').sorted(
                'sequence')

        if len(approvers) > 0:
            approvers[0]._create_activity()
            approvers[0].write({'status': 'pending'})
        else:
            self.approval_date = datetime.datetime.now()

    def action_refuse(self, approver=None):
        if not isinstance(approver, models.BaseModel):
            approver = self.mapped('approver_ids').filtered(
                lambda approver: approver.user_id == self.env.user
            )
        approver.write({'status': 'refused'})
        activity = self.env.ref('employee_travel_management.mail_activity_data_travel_request').id
        self.sudo()._get_user_approval_activities(user=self.env.user, activity_type_id=activity).action_feedback()

    def print_ticket_request(self):
        return self.env.ref('employee_travel_management.travel_request_ticket_print').report_action(self)

    def print_ticket_request_with_perdiem(self):
        return self.env.ref('employee_travel_management.travel_request_ticket_print_with_per_diem').report_action(self)

    def action_return(self):
        self.write({'is_return_employee': True})
        rule = self.travel_settings_id.perdiem_rule_lines.filtered(
            lambda
                rule: rule.min_days <= self.trip_days <= rule.max_days and self.employee_id.contract_id.job_grade.id in rule.job_grade_ids.ids)
        if rule and len(rule) == 1:
            if self.from_country_id != self.to_country_id:
                trip_days = self.trip_days + 1
            else:
                trip_days = self.trip_days
            self.create_perdiem_expense_line(trip_days=trip_days, rule=rule,
                                             perdiem_expense_product=self.travel_settings_id.perdiem_expense_product)
        elif not rule:
            raise UserError(
                _("Per Diam Rule not found please create Per Diam Rule in Travel Settings"))
        return True

    def create_perdiem_expense_line(self, trip_days, rule, perdiem_expense_product):
        vals = {'name': perdiem_expense_product.display_name,
                'product_id': perdiem_expense_product.id,
                'employee_id': self.employee_id.id,
                'date': date.today(),
                'quantity': trip_days,
                'payment_mode': 'company_account',
                'state': 'draft',
                'travel_request_id': self.id}
        if self.accommodation_type == 'by_company':
            vals.update({'unit_amount': rule.amount / 100 * rule.accommodation_by_company_percentage})
        elif self.accommodation_type == 'by_self':
            vals.update({'unit_amount': rule.amount / 100 * rule.accommodation_by_self_percentage})
        expense_obj = self.env['hr.expense']
        perdiem_expense_line = expense_obj.create(vals)
        if perdiem_expense_line:
            msg = "Per Diam expense line added with rule : {} ".format(rule.name)
            self.message_post(body=msg)
        return True

    def action_create_expense_sheet(self):
        if not self.employee_id.contract_id.job_grade:
            raise UserError(_("Employee has not running contract and the job grade"))
        expense_sheet_obj = self.env['hr.expense.sheet']
        if not self.hr_expense_ids:
            raise UserError(_("Please Add Expense Line"))
        # self.is_expense_report_created = True
        # rule = self.travel_settings_id.perdiem_rule_lines.filtered(
        #     lambda
        #         rule: rule.min_days <= self.trip_days <= rule.max_days and self.employee_id.contract_id.job_grade.id in rule.job_grade_ids.ids)
        # if rule and len(rule) == 1:
        #     if self.from_country_id != self.to_country_id:
        #         trip_days = self.trip_days + 1
        #     else:
        #         trip_days = self.trip_days
        #     self.create_perdiem_expense_line(trip_days=trip_days, rule=rule,
        #                                      perdiem_expense_product=self.travel_settings_id.perdiem_expense_product)
        # elif not rule:
        #     raise UserError(
        #         _("Per Diam Rule not found please create Per Diam Rule in Travel Settings"))
        hr_expense_ids = self.hr_expense_ids.filtered(lambda hr_expense_id: hr_expense_id.state == 'draft')
        if not hr_expense_ids:
            raise UserError(
                _("Please add a new expense line for the new  expense report"))
        expense_sheet_vals = {
            'name': self.name,
            'employee_id': self.employee_id.id,
            'company_id': self.company_id.id,
            'state': 'draft',
            # 'is_travel_expense': True,
            'expense_line_ids': [(6, 0, hr_expense_ids.ids)],
        }
        expense_sheet_id = expense_sheet_obj.create(expense_sheet_vals)
        if expense_sheet_id:
            # her we need to call manually onchange for the add approval_ids
            expense_sheet_id._onchange_expense_settings_id()
            self.expense_sheet_ids += expense_sheet_id
            # print(self.expense_sheet_ids)
        return True

    def action_view_expense_sheet(self):
        expenses = self.mapped('expense_sheet_ids')
        action = self.env.ref('hr_expense.action_hr_expense_sheet_my_all').read()[0]
        if len(expenses) > 1:
            action['domain'] = [('id', 'in', expenses.ids)]
        elif len(expenses) == 1:
            action['views'] = [(self.env.ref('hr_expense.view_hr_expense_sheet_form').id, 'form')]
            action['res_id'] = expenses.ids[0]
        else:
            action = {'type': 'ir.actions.act_window'}
        return action

    @api.onchange('request_owner_id')
    def onchange_employee(self):
        """
        Author:Bhavesh Jadav TechUltra solutions
        Date:  17/09/2020
        Func: for apply dynamic domain
        :return: domain
        """
        if self.env.user.has_group('security_rules.group_travel_quotation_employee'):
            employees = self.env['hr.employee'].search([])
            return {'domain': {'employee_id': [('id', 'in', employees.ids)]}}

        elif self.env.user.has_group('security_rules.group_travel_quotation_employee'):
            if self.env.user.employee_id:
                return {'domain': {'employee_id': [('id', '=', self.env.user.employee_id.id)]}}
            else:
                # if the login user are not employee and the is in employee group then its blank
                return {'domain': {'employee_id': [('id', 'in', [-1])]}}
        else:
            return {'domain': {'employee_id': [('id', 'in', [-1])]}}

    @api.onchange('employee_id')
    def onchange_employee_info(self):
        for rec in self:
            if rec.employee_id:
                rec.employee_contact_number = rec.employee_id.mobile_phone
                rec.employee_email = rec.employee_id.work_email
                employee_cost_center = rec.employee_id.contract_id.cost_center
                rec.travel_cost_center_lines = False
                if employee_cost_center:
                    new_cc_line = [(0, 0, {
                        'cost_center_id': employee_cost_center,
                        'share_percentage': 100})]
                    rec.travel_cost_center_lines = new_cc_line

    @api.onchange('company_id')
    def onchange_company_id(self):
        for rec in self:
            current_employee = self.env['hr.employee'].search([('user_id', '=',
                                                                self.env.user.id)],
                                                              limit=1)
            if current_employee:
                rec.employee_id = current_employee
                rec.onchange_employee_info()
                rec._onchange_travel_settings_id()
                children = current_employee.child_ids
                if not self.env.user.has_group('security_rules.group_travel_quotation_employee'):
                    return {'domain': {
                        'employee_id': ['|', ('id', 'in', children.ids), ('id', '=', current_employee.id)]
                    }}

    @api.model
    def create(self, vals):
        if not vals.get('travel_cost_center_lines'):
            raise UserError(
                _("Please add Cost Center line"))
        name = self.env['ir.sequence'].next_by_code('employee.travel.request') or _('New')
        vals['name'] = name + ' - ' + self.env['hr.employee'].browse(vals.get('employee_id')).name
        res = super(EmployeeTravelRequest, self).create(vals)
        return res

    #
    # def create_default_cost_center(self):
    #     if self.employee_id.contract_id and self.employee_id.contract_id.cost_center:
    #         vals = {'cost_center_id': self.employee_id.contract_id.cost_center.id,
    #                 'share_percentage': 100,
    #                 ''}
    #     return True

    @api.onchange('travel_settings_id', 'employee_id')
    def _onchange_travel_settings_id(self):
        if self.employee_id:
            self.approver_ids = self.env['travel.request.approver']
            current_users = []  # self.approver_ids.mapped('user_id')
            if self.travel_settings_id:
                new_approvals_ordered = self.travel_settings_id.approval_sequence.sorted(lambda x: x.sequence)
            else:
                new_approvals_ordered = self.env['res.users']
            # manager_approver = []
            # if self.travel_settings_id.is_manager_approver:
            #     if self.employee_id.parent_id:
            #         manager_approver.append(self.employee_id.parent_id.user_id)
            #         if self.travel_settings_id.is_higher_manager_approver:
            #             if self.employee_id.parent_id.parent_id:
            #                 manager_approver.append(self.employee_id.parent_id.parent_id.user_id)
            # if manager_approver:
            #     if self.approver_ids:
            #         approver_ids = self.approver_ids.sorted(lambda x: x.sequence)
            #         last_sequence = approver_ids[-1].sequence
            #     else:
            #         last_sequence = 0
            #         ##### code here ################################3
            #
            #     self.create_approver_line(user_list=manager_approver, last_sequence=last_sequence,
            #                               current_users=current_users, is_manager_approval=True)
            new_users = []
            user_category = {}
            for approval in new_approvals_ordered:
                if approval.user_id:
                    new_users.append(approval.user_id)
                    key = approval.user_id.id
                    value = approval.approval_category
                    user_category[key] = value
                if not approval.user_id:
                    if approval.is_manager_approver and self.employee_id.parent_id:
                        new_users.append(self.employee_id.parent_id.user_id)
                        key = self.employee_id.parent_id.user_id.id
                        value = approval.approval_category
                        user_category[key] = value
                    if approval.is_higher_manager_approver and self.employee_id.parent_id and self.employee_id.parent_id.parent_id:
                        new_users.append(self.employee_id.parent_id.parent_id.user_id)
                        key = self.employee_id.parent_id.parent_id.user_id.id
                        value = approval.approval_category
                        user_category[key] = value
            if self.approver_ids:
                approver_ids = self.approver_ids.sorted(lambda x: x.sequence)
                last_sequence = approver_ids[-1].sequence
            else:
                last_sequence = 0
            self.create_approver_line(user_list=new_users, last_sequence=last_sequence,
                                      current_users=current_users, user_category=user_category)

    def create_approver_line(self, user_list, last_sequence, current_users, user_category={},
                             is_manager_approval=False):
        counter = 0
        for user in user_list:
            if user.id not in current_users:
                counter += 1
                last_sequence += 10
                approver_ids_vals = {'sequence': last_sequence,
                                     'user_id': user.id,
                                     'request_id': self.id,
                                     'status': 'new'}
                approver_ids_vals.update({'approval_category': user_category.get(user.id) or ''})
                # if is_manager_approval:
                #     approver_ids_vals.update({'approval_category': 'LM' + '-' + str(counter)})
                # else:
                #     approver_ids_vals.update({'approval_category': user_category.get(user.id) or ''})

                self.approver_ids += self.env['travel.request.approver'].new(approver_ids_vals)

    def maximum_accommodation_rate(self):
        maximum_accommodation_rate = 0.0
        unit_amount = 0.0
        rule = self.travel_settings_id.perdiem_rule_lines.filtered(
            lambda
                rule: rule.min_days <= self.trip_days <= rule.max_days and self.employee_id.contract_id.job_grade.id in rule.job_grade_ids.ids)
        if rule and len(rule) == 1:
            # if self.from_country_id != self.to_country_id:
            #     trip_days = self.trip_days + 1
            # else:
            #     trip_days = self.trip_days
            if self.accommodation_type == 'by_company':
                unit_amount = rule.amount / 100 * rule.accommodation_by_company_percentage or 0.0
            elif self.accommodation_type == 'by_self':
                unit_amount = rule.amount / 100 * rule.accommodation_by_self_percentage
            if unit_amount:
                # maximum_accommodation_rate = unit_amount * trip_days
                maximum_accommodation_rate = unit_amount / 100 * 75
        return maximum_accommodation_rate

    # def write(self, vals):
    #     print(vals)
    #     if vals.get('hr_expense_ids'):
    #         for hr_expense_id_list in vals.get('hr_expense_ids'):
    #
    #     res = super(EmployeeTravelRequest, self).write(vals)
    #     return res


class TravelRequestApprover(models.Model):
    _name = 'travel.request.approver'
    _description = 'Travel Request Approver'

    user_id = fields.Many2one('res.users', string="User", required=True)
    status = fields.Selection([
        ('new', 'New'),
        ('pending', 'To Approve'),
        ('approved', 'Approved'),
        ('refused', 'Refused'),
        ('cancel', 'Cancel')], string="Status", default="new")
    request_id = fields.Many2one('employee.travel.request', string="Request", ondelete='cascade')
    reject_reason = fields.Char('Rejection Reason')
    sequence = fields.Integer('Sequence', default=10)
    approval_date = fields.Datetime(
        string='Approval Date',
        required=False, readonly=True)

    approval_category = fields.Char(string="Category")

    # approval_type = fields.Selection([('static', 'Static'), ('dynamic', 'Dynamic')], default="static")

    @api.onchange('user_id')
    def _onchange_approver_ids(self):
        return {'domain': {'user_id': [('id', 'not in', self.request_id.approver_ids.mapped(
            'user_id').ids + self.request_id.request_owner_id.ids)]}}

    def _create_activity(self):
        for approver in self:
            approver.request_id.activity_schedule(
                'employee_travel_management.mail_activity_data_travel_request',
                user_id=approver.user_id.id)

    def unlink(self):
        activity = self.env.ref('employee_travel_management.mail_activity_data_travel_request').id
        activities = self._get_user_approval_activities(user=self.user_id, res_ids=self.request_id.ids,
                                                        activity_type_id=activity)
        activities.unlink()
        # next_approvers = self.request_id.approver_ids - self
        # if not next_approvers.filtered(lambda approver: approver.status == 'pending'):
        #     next_approver = next_approvers.filtered(lambda approver: approver.status == 'new').sorted(
        #         'sequence')
        #     if next_approver:
        #         next_approver[0]._create_activity()
        #         next_approver[0].status = 'pending'
        res = super(TravelRequestApprover, self).unlink()
        return res

    def _get_user_approval_activities(self, user, res_ids, activity_type_id):
        domain = [
            ('res_model', '=', 'employee.travel.request'),
            ('res_id', 'in', res_ids),
            ('activity_type_id', '=', activity_type_id),
            ('user_id', '=', user.id)
        ]
        activities = self.env['mail.activity'].search(domain)
        return activities

    @api.model
    def create(self, vals):
        res = super(TravelRequestApprover, self).create(vals)
        if len(res.request_id.approver_ids.filtered(
                lambda approver: approver.status == 'pending')) > 1:
            raise UserError(_("You Can not add Multiple approve with 'To Approve' Status."))
        next_approvers = self.env['employee.travel.request'].browse(vals['request_id']).approver_ids
        # if not next_approvers.filtered(lambda approver: approver.status == 'pending'):
        next_approver = next_approvers.filtered(lambda approver: approver.status == 'pending').sorted(
            'sequence')
        if next_approver:
            next_approver[0]._create_activity()
            # next_approver[0].status = 'pending'
        return res
    # extra  method for the day time and night time calculations
    # total_day = fields.Float(string="Total Days", compute='_day_night_cal')
    #
    # @api.depends('travel_start_date', 'travel_end_date')
    # def _day_night_cal(self):
    #     for rec in self:
    #         if rec.travel_start_date and rec.travel_end_date:
    #             to_zone = tz.gettz('Asia/Kolkata')
    #             travel_start_date_with_time_zone = rec.travel_start_date.astimezone(to_zone)
    #             travel_end_date_with_time_zone = rec.travel_end_date.astimezone(to_zone)
    #             days = (rec.travel_end_date - rec.travel_start_date).days
    #             hours, remainder = divmod((rec.travel_end_date - rec.travel_start_date).seconds, 3600)
    #             minutes, seconds = divmod(remainder, 60)
    #             extra_day_hours = 0
    #             extra_night_hours = 0
    #             start_extra_day_hours = 0
    #             start_extra_night_hours = 0
    #             if int(travel_end_date_with_time_zone.strftime('%H')) < 12:
    #                 extra_night_hours = int(travel_end_date_with_time_zone.strftime('%H'))
    #             else:
    #                 extra_day_hours = 24 - int(travel_end_date_with_time_zone.strftime('%H'))
    #             if int(travel_start_date_with_time_zone.strftime('%H')) < 12:
    #                 start_extra_night_hours = int(travel_start_date_with_time_zone.strftime('%H'))
    #             else:
    #                 start_extra_day_hours = 24 - int(travel_start_date_with_time_zone.strftime('%H'))
    #             print(days)
    #             print(extra_day_hours)
    #             print(extra_night_hours)
    #             print(start_extra_day_hours)
    #             print(start_extra_night_hours)
    #
    #     self.total_day = 0.0
    #     self.total_night = 0.0
    #     return True
