from odoo import models, fields, api, _


class ApprovalCategory(models.Model):
    _inherit = 'approval.category'

    is_travel_request = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')], string="Is Travel Request", default="no", required=True)

    travel_request_to_validate_count = fields.Integer("Number of requests to validate",
                                                      compute="_compute_travel_request_to_validate_count")

    def _compute_travel_request_to_validate_count(self):
        """
        :Author : Bhavesh Jadav TechUltra solution
        :Date: 15/10/2020
        :Func:this method  use for the add counts of the request to validate for tha kan ban button
        :return : True
        """
        request_to_validate = []
        domain = [('request_status', 'in', ['pending', 'under_approval']),
                  ('approver_ids.user_id', '=', self.env.user.id)]
        requests = self.env['employee.travel.request'].search(domain)
        for request in requests:
            approver_id = request.approver_ids.filtered(
                lambda approver_id: approver_id.status in ['pending'] and approver_id.user_id.id == self.env.user.id)
            if approver_id:
                request_to_validate.append(approver_id.request_id.id)
        for category in self:
            category.travel_request_to_validate_count = len(request_to_validate)
        return True

    def create_request(self):
        """
        :Author:Bhavesh Jadav TechUltra Solutions
        :Date:14/10/2020
        :Func:is travel request then we need to return action of the  travel_request
        :Return: Action or res
        """
        if self.is_travel_request == 'yes':
            action = self.env.ref('employee_travel_management.employee_travel_request_act_window')
            result = action.read()[0]
            return result
        res = super(ApprovalCategory, self).create_request()
        return res

    def call_to_review_action(self):
        """
        :Author:Bhavesh Jadav TechUltra Solutions
        :Date:14/10/2020
        :Func:if is travel request then we need to return action of the  travel_request
        :Return:  travel  request to review  Action or approvals action
        """
        if self.is_travel_request == 'yes':
            action = self.env.ref('employee_travel_management.travel_request_action_to_review')
            result = action.read()[0]
            return result
        res = super(ApprovalCategory, self).call_to_review_action()
        return res
