from odoo import models, fields, api, _


class EducationRequestApprover(models.Model):
    _name = 'education.request.approver'
    _description = 'education request approver'

    user_id = fields.Many2one('res.users', string="User", required=True)

    status = fields.Selection([
        ('new', 'New'),
        ('pending', 'To Approve'),
        ('approved', 'Approved'),
        ('refused', 'Refused'),
        ('cancel', 'Cancel')], string="Status", default="new")

    request_id = fields.Many2one('education.request', string="Request", ondelete='cascade')

    reject_reason = fields.Char('Rejection Reason')
    sequence = fields.Integer('Sequence', default=10)
    approval_date = fields.Datetime(
        string='Approval Date',
        required=False, readonly=True)
    approval_category = fields.Char(string="Category")
    is_hc_admin = fields.Boolean('HC Admin')

    @api.onchange('user_id')
    def _onchange_approver_ids(self):
        """
        :Author:Bhavesh Jadav TechUltra Solutions
        :Date:18/11/2020
        :Func: for apply dynamic domain
        :return: domain dict
        """
        return {'domain': {'user_id': [('id', 'not in', self.request_id.approver_ids.mapped(
            'user_id').ids + self.request_id.request_owner_id.ids)]}}

    def _create_activity(self):
        """
        :Author:Bhavesh Jadav TechUltra Solutions
        :Date: 18/11/2020
        :Func: this method use for the create schedule activity
        :Return: N/A
        """
        for approver in self:
            approver.request_id.activity_schedule(
                'child_education.mail_activity_data_education_request',
                user_id=approver.user_id.id)

    def _get_user_approval_activities(self, user, res_ids, activity_type_id):
        """
        :Author:Bhavesh Jadav TechUltra Solutions
        :Date: 18/11/2020
        :Func: this method use for the  find activities
        :Return: activities
        """
        domain = [
            ('res_model', '=', 'education.request'),
            ('res_id', 'in', res_ids),
            ('activity_type_id', '=', activity_type_id),
            ('user_id', '=', user.id)
        ]
        activities = self.env['mail.activity'].search(domain)
        return activities