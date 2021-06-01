# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

CATEGORY_SELECTION = [
    ('required', 'Required'),
    ('optional', 'Optional'),
    ('no', 'None')]


class ApprovalSequence(models.Model):
    _name = 'approval.sequence'

    sequence = fields.Integer('Sequence', default=1)
    user_id = fields.Many2one('res.users', 'Approver')
    is_head_department_approver = fields.Boolean('Head of Department Approver')
    is_manager_approver = fields.Boolean('Manager Approver')
    related_category = fields.Many2one('approval.category', 'Related Category')
    approver_category = fields.Char(
        string='Approver Category',
        required=False)


class ApprovalCategory(models.Model):
    _inherit = 'approval.category'

    requirer_document = fields.Selection(selection_add=[('no', "None")], string="Documents", default="no",
                                         required=True)
    has_vacancy_type = fields.Selection(CATEGORY_SELECTION, string="Vacancy Type", default="no", required=True)
    is_requisition_request = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')], string="Is Requisition Request", default="no", required=True)
    is_termination_request = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')], string="Is Termination Request", default="no", required=True)
    is_termination_extend_request = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')], string="Is Extend Termination Request", default="no", required=True)
    is_internal_transfer_request = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')], string="Is Internal Transfer Request", default="no", required=True)
    has_job_title = fields.Selection(CATEGORY_SELECTION, string="Job Title", default="no", required=True)
    has_group = fields.Selection(CATEGORY_SELECTION, string="Group", default="no", required=True)
    has_department = fields.Selection(CATEGORY_SELECTION, string="Department", default="no", required=True)
    has_section = fields.Selection(CATEGORY_SELECTION, string="Section", default="no", required=True)
    has_subsection = fields.Selection(CATEGORY_SELECTION, string="Subsection", default="no", required=True)
    has_related_employee_id = fields.Selection(CATEGORY_SELECTION, string="Employee", default="no", required=True)
    has_related_contract = fields.Selection(CATEGORY_SELECTION, string="Contract", default="no", required=True)
    has_grade = fields.Selection(CATEGORY_SELECTION, string="Grade", default="no", required=True)
    has_related_manager = fields.Selection(CATEGORY_SELECTION, string="Related Manager", default="no", required=True)
    has_related_oc = fields.Selection(CATEGORY_SELECTION, string="Related OC", default="no", required=True)
    has_eligible_rehire = fields.Selection(CATEGORY_SELECTION, string="Eligible for Rehire", default="no",
                                           required=True)
    has_eligible_rehire_comment = fields.Selection(CATEGORY_SELECTION, string="Comment", default="no", required=True)
    has_related_time_hired = fields.Selection(CATEGORY_SELECTION, string="Related Tenure of Experience", default="no",
                                              required=True)
    has_related_warnings = fields.Selection(CATEGORY_SELECTION, string="Related Warnings", default="no", required=True)
    has_notice_period = fields.Selection(CATEGORY_SELECTION, string="Notice Period", default="no", required=True)
    has_job_position = fields.Selection(CATEGORY_SELECTION, string="Job Position", default="no", required=True)
    has_job_desc = fields.Selection(CATEGORY_SELECTION, string="Job Desc", default="no", required=True)
    has_replacement_employee_id = fields.Selection(CATEGORY_SELECTION, string="Replacement Report", default="no",
                                                   required=True)
    has_resignation_date = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')], string="Resignation Date", default="no", required=True)
    has_contract_type = fields.Selection(CATEGORY_SELECTION, string="Contract Type", default="no", required=True)
    has_requisition_type = fields.Selection(CATEGORY_SELECTION, string="Requisition Type", default="no", required=True)
    managers_only = fields.Boolean('Managers only')
    is_head_department_approver = fields.Boolean(
        string="Employee's Head Of Department",
        help="Automatically add the Head Of Department as approver on the request.")

    approval_sequence = fields.One2many('approval.sequence', 'related_category', 'Approval Sequence')

    has_cost_center = fields.Selection(CATEGORY_SELECTION, string="Cost Center", default="no", required=True)
    has_personal_phone_no = fields.Selection(CATEGORY_SELECTION, string="Personal Phone No", default="no",
                                             required=True)
    has_personal_email = fields.Selection(CATEGORY_SELECTION, string="Personal Email", default="no", required=True)
    has_replacement_position = fields.Selection(CATEGORY_SELECTION, string="Replacement of the Position", default="no",
                                                required=True)
    has_resignation_reason = fields.Selection(CATEGORY_SELECTION, string="Resignation Reason", default="no",
                                              required=True)
    has_resignation_extension_reason = fields.Selection(CATEGORY_SELECTION, string="Resignation Extension Reason",
                                                        default="no",
                                                        required=True)
    can_see = fields.Boolean(store=True)
    can_see_false = fields.Boolean(compute='check_if_subordinates')

    # internal transfer fields

    has_employee_transferred = fields.Selection(CATEGORY_SELECTION, string="Employee Transferred", default="no",
                                                required=True)

    # has_employee_company = fields.Selection(CATEGORY_SELECTION, string="Company Employee ID", default="no",
    #                                            required=True)
    has_company_employee_id = fields.Selection(CATEGORY_SELECTION, string="Company Employee ID", default="no",
                                            required = True)
    has_transfer_type = fields.Selection(CATEGORY_SELECTION, string="Transfer Type", default="no", required=True)
    has_transfer_reason = fields.Selection(CATEGORY_SELECTION, string="Transfer Reason", default="no", required=True)

    has_employee_type_source = fields.Selection(CATEGORY_SELECTION, string="Employee Type (Source)", default="no",
                                                required=True)
    has_employee_type_destination = fields.Selection(CATEGORY_SELECTION, string="Employee Type (Destination)",
                                                     default="no", required=True)

    has_cost_center_source = fields.Selection(CATEGORY_SELECTION, string="Cost Center (Source)", default="no",
                                              required=True)
    has_cost_center_destination = fields.Selection(CATEGORY_SELECTION, string="Cost Center (Destination)",
                                                   default="no", required=True)

    has_sap_source = fields.Selection(CATEGORY_SELECTION, string="SAP Account (Source)", default="no", required=True)
    has_sap_destination = fields.Selection(CATEGORY_SELECTION, string="SAP Account (Destination)", default="no",
                                           required=True)

    has_3dx_source = fields.Selection(CATEGORY_SELECTION, string="3DX Account (Source)", default="no", required=True)
    has_3dx_destination = fields.Selection(CATEGORY_SELECTION, string="3DX Account (Destination)", default="no",
                                           required=True)

    has_shared_folder_source = fields.Selection(CATEGORY_SELECTION, string="Shared Folder Path(Source)", default="no",
                                                required=True)
    has_shared_folder_destination = fields.Selection(CATEGORY_SELECTION, string="Shared Folder Path (Destination)",
                                                     default="no", required=True)

    has_shared_folder_status_source = fields.Selection(CATEGORY_SELECTION, string="Shared Folder Status (Source)",
                                                       default="no",
                                                       required=True)
    has_shared_folder_status_destination = fields.Selection(CATEGORY_SELECTION,
                                                            string="Shared Folder Status(Destination)",
                                                            default="no", required=True)

    has_other_source = fields.Selection(CATEGORY_SELECTION, string="Other (Source)", default="no", required=True)
    has_other_destination = fields.Selection(CATEGORY_SELECTION, string="Other (Destination)", default="no",
                                             required=True)

    has_job_title_source = fields.Selection(CATEGORY_SELECTION, string="Job Title (Source)", default="no",
                                            required=True)
    has_job_title_destination = fields.Selection(CATEGORY_SELECTION, string="Job Title (Destination)",
                                                 default="no", required=True)

    has_line_manager_source = fields.Selection(CATEGORY_SELECTION, string="Line Manager (Source)", default="no",
                                               required=True)
    has_line_manager_destination = fields.Selection(CATEGORY_SELECTION, string="Line Manager (Destination)",
                                                    default="no", required=True)

    has_group_source = fields.Selection(CATEGORY_SELECTION, string="Group (Source)", default="no", required=True)
    has_group_destination = fields.Selection(CATEGORY_SELECTION, string="Group (Destination)", default="no",
                                             required=True)

    has_department_source = fields.Selection(CATEGORY_SELECTION, string="Department (Source)", default="no",
                                             required=True)
    has_department_destination = fields.Selection(CATEGORY_SELECTION, string="Department (Destination)", default="no",
                                                  required=True)

    has_section_source = fields.Selection(CATEGORY_SELECTION, string="Section (Source)", default="no",
                                          required=True)
    has_section_destination = fields.Selection(CATEGORY_SELECTION, string="Section (Destination)", default="no",
                                               required=True)

    has_subsection_source = fields.Selection(CATEGORY_SELECTION, string="SubSection (Source)", default="no",
                                             required=True)
    has_subsection_destination = fields.Selection(CATEGORY_SELECTION, string="SubSection (Destination)",
                                                  default="no", required=True)

    has_job_grade_source = fields.Selection(CATEGORY_SELECTION, string="Job Grade (Source)", default="no",
                                            required=True)
    has_job_grade_destination = fields.Selection(CATEGORY_SELECTION, string="Job Grade (Destination)",
                                                 default="no", required=True)

    has_working_shift_source = fields.Selection(CATEGORY_SELECTION, string="Working Shift (Source)", default="no",
                                                required=True)
    has_working_shift_destination = fields.Selection(CATEGORY_SELECTION, string="Working Shift (Destination)",
                                                     default="no", required=True)

    contract_subgroups = fields.Many2many(
        comodel_name='hr.contract.subgroup',
        string='Allowed Contract Subgroups')

    def check_if_subordinates(self):
        self = self.sudo()
        for rec in self:
            if self.env.user.has_group('security_groups.group_hc_employee') or (
                    self.env.user.employee_ids and self.env.user.employee_ids.subordinate_ids and rec.managers_only) or not rec.managers_only:
                # if self.env.user.employee_ids.contract_id.contract_subgroup.id in rec.contract_subgroups.ids:
                rec.can_see = True
                rec.can_see_false = True
            else:
                rec.can_see = False
                rec.can_see_false = False
            # print(rec.name)
            # print(rec.can_see)

    # def create_request(self):
    #     if self.env.user.employee_ids.contract_id.contract_subgroup.id not in self.contract_subgroups.ids:
    #         raise ValidationError(_('You are not allowed to submit this type of request'))
    #     res = super(ApprovalCategory, self).create_request()
    #     return res

    @api.onchange('is_head_department_approver', 'is_manager_approver', 'user_ids')
    def _approvers_onchange(self):
        for rec in self:
            c = 0
            results = [(5, 0, 0)]
            if rec.is_head_department_approver:
                c += 1
                results.append((0, 0, {'sequence': c, 'is_head_department_approver': True}))
            if rec.is_manager_approver:
                c += 1
                results.append((0, 0, {'sequence': c, 'is_manager_approver': True}))
            if rec.user_ids:
                for user in rec.user_ids:
                    c += 1
                    results.append((0, 0, {'sequence': c, 'user_id': user.id.origin if user.id.origin else user.id}))
            rec.approval_sequence = results

    def call_to_review_action(self):
        """
        :Author:Bhavesh Jadav TechUltra Solutions
        :Date:14/10/2020
        :Func:we need to change button type action to object for the control for the python control
        :Return: approvals action
        """
        action = self.env.ref('approvals.approval_request_action_to_review_category')
        result = action.read()[0]
        return result
