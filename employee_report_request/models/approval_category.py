from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ApprovalCategory(models.Model):
    _inherit = 'approval.category'

    is_letter_request = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')], string="Is Letter Request", default="no", required=True)

    def create_request(self):
        """
        :Author:Bhavesh Jadav TechUltra Solutions
        :Date:14/10/2020
        :Func:id is letter request then we need to return action of the  report_request
        :Return: Action or res
        """
        if self.env.user.employee_ids.contract_id.contract_subgroup.id not in self.contract_subgroups.ids:
            raise ValidationError(_('You are not allowed to submit this type of request'))
        if self.is_letter_request == 'yes':
            action = self.env.ref('employee_report_request.report_request_act_window')
            result = action.read()[0]
            return result
        res = super(ApprovalCategory, self).create_request()
        return res

    # def call_to_review_action(self):
    #     """
    #     :Author:Bhavesh Jadav TechUltra Solutions
    #     :Date:14/10/2020
    #     :Func:if is letter request then we need to return action of the  report_request
    #     :Return:  report request Action or approvals action
    #     """
    #     if self.is_letter_request == 'yes':
    #         action = self.env.ref('employee_report_request.report_request_act_window')
    #         result = action.read()[0]
    #         return result
    #     res = super(ApprovalCategory, self).call_to_review_action()
    #     return res
