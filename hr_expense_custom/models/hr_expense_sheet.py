from odoo import api, fields, models, _
import datetime
from datetime import date
from odoo.exceptions import UserError


class HrExpenseSheet(models.Model):
    _inherit = "hr.expense.sheet"

    expense_settings_id = fields.Many2one('hr.expense.settings', string="Expense Setting", required=True,
                                          compute='_compute_expense_settings_id', store=False)
    approval_minimum = fields.Integer(related="expense_settings_id.approval_minimum")
    approver_ids = fields.One2many('hr.expense.approver', 'expense_sheet_id', string="Approvers")

    # is_travel_expense = fields.Boolean(string="Is travel Expense", default=False)

    expense_type = fields.Many2one('expense.type', string="Expense Category", compute='_compute_expense_type',
                                   store=False)

    user_status = fields.Selection([
        ('new', 'New'),
        ('pending', 'To Approve'),
        ('approved', 'Approved'),
        ('refused', 'Refused'),
        ('cancel', 'Cancel')], compute="_compute_user_status")

    state = fields.Selection([
        ('draft', 'Draft'),
        ('submit', 'Submitted'),
        ('under_approval', 'Under Approval'),
        ('approve', 'Approved'),
        ('post', 'Posted'),
        ('done', 'Paid'),
        ('cancel', 'Refused')
    ], string='Status', readonly=True, tracking=False,
        copy=False, default='draft', index=True, store=True,
        compute_sudo=True, compute="_compute_expense_status",
        help='Expense Report State')  # tracking=True, index=True required=True,

    # total_amount = fields.Monetary('Total Amount', currency_field='currency_id', compute='_compute_amount', store=True)
    #
    # @api.depends('expense_line_ids.total_amount_company', 'expense_line_ids.amount_in_aed')
    # def _compute_amount(self):
    #     """
    #     @Author:Bhavesh Jadav TechUltra Solution
    #     @Date:19/01/2020
    #     @Func:This method over ride for the change calculation of the total amount
    #     """
    #     for sheet in self:
    #         sheet.total_amount = sum(sheet.expense_line_ids.mapped('amount_in_aed'))

    @api.depends('expense_line_ids')
    def _compute_expense_type(self):
        """
        """
        for rec in self:
            if rec.expense_line_ids:
                product_ids = rec.expense_line_ids.mapped('product_id')
                expense_type_list = []
                for product_id in product_ids:
                    expense_type_list += product_id.expense_type.ids
                if expense_type_list:
                    most_frequent_expense_type = max(set(expense_type_list), key=expense_type_list.count)
                    expense_type_id = self.env['expense.type'].browse(most_frequent_expense_type)
                    rec.expense_type = expense_type_id
                else:
                    rec.expense_type = False
            else:
                rec.expense_type = False
        # return True

    @api.depends('expense_type')
    def _compute_expense_settings_id(self):
        for rec in self:
            if rec.expense_type:
                expense_settings = self.env['hr.expense.settings'].search([])
                expense_settings_with_expense_type = self.env['hr.expense.settings']
                for expense_setting in expense_settings:
                    if rec.expense_type.id in expense_setting.expense_type.ids:
                        expense_settings_with_expense_type += expense_setting
                if expense_settings_with_expense_type:
                    rec.expense_settings_id = expense_settings_with_expense_type[0]
                else:
                    rec.expense_settings_id = self.env['hr.expense.settings']
            else:
                rec.expense_settings_id = self.env['hr.expense.settings']

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

    @api.depends('approver_ids.status')
    def _compute_expense_status(self):
        for expense in self:
            status_lst = expense.mapped('approver_ids.status')
            if status_lst:
                if status_lst.count('cancel') or status_lst.count('refused'):
                    status = 'cancel'
                elif status_lst.count('new') and not status_lst.count('pending') and not status_lst.count('approved'):
                    status = 'draft'
                elif 0 < status_lst.count('approved') < len(status_lst):
                    status = 'under_approval'
                elif status_lst.count('approved') == len(status_lst):
                    status = 'approve'
                else:
                    status = 'submit'
            else:
                status = 'draft'
            expense.state = status

    def create_approver_line(self, user_list, last_sequence, current_users, user_category={},
                             is_manager_approval=False):
        counter = 0
        for user in user_list:
            if user.id not in current_users:
                counter += 1
                last_sequence += 10
                approver_ids_vals = {'sequence': last_sequence,
                                     'user_id': user.id,
                                     'expense_sheet_id': self.id,
                                     'status': 'new'}
                approver_ids_vals.update({'approval_category': user_category.get(user.id) or ''})
                # if is_manager_approval:
                #     approver_ids_vals.update({'approval_category': 'LM' + '-' + str(counter)})
                # else:
                #     approver_ids_vals.update({'approval_category': user_category.get(user.id) or ''})

                self.approver_ids += self.env['hr.expense.approver'].new(approver_ids_vals)

    @api.onchange('expense_settings_id', 'employee_id')
    def _onchange_expense_settings_id(self):
        if self.expense_settings_id and self.employee_id:
            if self.employee_id:
                self.approver_ids = self.env['hr.expense.approver']
            current_users = []
            if self.expense_settings_id:
                new_approvals_ordered = self.expense_settings_id.approval_sequence.sorted(lambda x: x.sequence)
            else:
                new_approvals_ordered = self.env['res.users']

            # manager_approver = []
            # if self.expense_settings_id.is_manager_approver:
            #     if self.employee_id.parent_id:
            #         manager_approver.append(self.employee_id.parent_id.user_id)
            #         if self.expense_settings_id.is_higher_manager_approver:
            #             if self.employee_id.parent_id.parent_id:
            #                 manager_approver.append(self.employee_id.parent_id.parent_id.user_id)
            #     if manager_approver:
            #         if self.approver_ids:
            #             approver_ids = self.approver_ids.sorted(lambda x: x.sequence)
            #             last_sequence = approver_ids[-1].sequence
            #         else:
            #             last_sequence = 0
            #
            #         self.create_approver_line(user_list=manager_approver, last_sequence=last_sequence,
            #                                   current_users=current_users, is_manager_approval=True)
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

    def _get_responsible_for_approval(self):
        res = super(HrExpenseSheet, self)._get_responsible_for_approval()
        expense_approver_record = self.mapped('approver_ids').filtered(lambda approver: approver.status == 'new')
        if expense_approver_record:
            sorted_expense_approver_record = expense_approver_record.sorted('sequence')
            if sorted_expense_approver_record:
                return sorted_expense_approver_record[0].user_id
        return self.env['res.users']

    def approve_expense_sheets(self):
        approver = self.mapped('approver_ids').filtered(
            lambda approver: approver.user_id == self.env.user
        ).filtered(
            lambda approver: approver.status != 'approved').sorted(lambda x: x.sequence)
        if len(approver) > 0:
            approver[0].write({'status': 'approved', 'approval_date': datetime.datetime.now()})
        activity = self.env.ref('hr_expense.mail_act_expense_approval').id
        self.sudo()._get_user_approval_activities(user=self.env.user, activity_type_id=activity).action_feedback()
        approvers = self.mapped('approver_ids').filtered(lambda approver: approver[0].status == 'new').sorted(
            'sequence')
        if len(approvers) > 0:
            approvers[0]._create_activity()
            approvers[0].write({'status': 'pending'})
        return True

    def _get_user_approval_activities(self, user, activity_type_id):
        domain = [
            ('res_model', '=', 'hr.expense.sheet'),
            ('res_id', 'in', self.ids),
            ('activity_type_id', '=', activity_type_id),
            ('user_id', '=', user.id)
        ]
        activities = self.env['mail.activity'].search(domain)
        return activities

    def action_submit_sheet(self):
        res = super(HrExpenseSheet, self).action_submit_sheet()
        expense_approver_record = \
            self.mapped('approver_ids').filtered(lambda approver: approver.status == 'new').sorted('sequence')[
                0]
        if expense_approver_record:
            expense_approver_record.write({'status': 'pending'})
        return res

    def refuse_expense(self, reason):
        res = super(HrExpenseSheet, self).refuse_expense(reason)
        return res

    def refuse_sheet(self, reason):
        self.write({'state': 'cancel'})
        for sheet in self:
            sheet.message_post_with_view('hr_expense.hr_expense_template_refuse_reason',
                                         values={'reason': reason, 'is_sheet': True, 'name': self.name})
        self.activity_update()
        approver = self.mapped('approver_ids').filtered(
            lambda approver: approver.user_id == self.env.user
        ).filtered(
            lambda approver: approver.status != 'approved')
        if len(approver) > 0:
            approver[0].update({'reject_reason': self.name, 'status': 'refused'})
            # activity = self.env.ref('hr_expense.mail_act_expense_approval').id
            # self.sudo()._get_user_approval_activities(user=self.env.user,
            #                                           activity_type_id=activity).action_feedback()

# def approve_expense_sheets(self):
#     if not self.user_has_groups('hr_expense.group_hr_expense_team_approver'):
#         raise UserError(_("Only Managers and HR Officers can approve expenses"))
#     elif not self.user_has_groups('hr_expense.group_hr_expense_manager'):
#         current_managers = self.employee_id.expense_manager_id | self.employee_id.parent_id.user_id | self.employee_id.department_id.manager_id.user_id
#
#         if self.employee_id.user_id == self.env.user:
#             raise UserError(_("You cannot approve your own expenses"))
#
#         if not self.env.user in current_managers and not self.user_has_groups(
#                 'hr_expense.group_hr_expense_user') and self.employee_id.expense_manager_id != self.env.user:
#             raise UserError(_("You can only approve your department expenses"))
#
#     responsible_id = self.user_id.id or self.env.user.id
#     self.write({'state': 'approve', 'user_id': responsible_id})
#     self.activity_update()
