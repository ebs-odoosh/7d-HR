from odoo import models, fields, api, _
import datetime
from datetime import date


class EducationApprovalRejectReason(models.TransientModel):
    _name = 'education.approval.reject.reason'

    name = fields.Char('Rejection Reason', required=True)
    request_id = fields.Many2one('education.request')

    def action_done(self):
        """
        :Author:Bhavesh Jadav TechUltra solutions
        :Date:09/10/2020
        :Func : this method use for the add log for the reject
            and the write the reject reason and the cancel the activity for that approvers
        :Return: N/A
        """
        approver = self.request_id.mapped('approver_ids').filtered(
            lambda approver: approver.user_id == self.env.user
        ).filtered(
            lambda approver: approver.status != 'approved')
        if len(approver) > 0:
            approver[0].update({'reject_reason': self.name, 'status': 'refused'})
            approver[0].request_id.approval_date = datetime.datetime.now()

            msg = _('Request Rejected by ' + approver[0].user_id.name + '. Rejection Reason: ' + self.name)
            self.request_id.message_post(body=msg)
            activity = self.env.ref('child_education.mail_activity_data_education_request').id
            self.request_id.sudo()._get_user_approval_activities(user=self.env.user,
                                                                 activity_type_id=activity).action_feedback()
        for line in self.request_id.request_lines:
            for fee in line.terms_fees_line_ids:
                fee.approve_amount = 0