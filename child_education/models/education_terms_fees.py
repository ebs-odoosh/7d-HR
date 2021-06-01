from odoo import models, fields, api, _


class EducationTermsFeesLine(models.Model):
    _name = 'education.terms.fees.line'
    _description = 'Education Terms Fees Line'

    @api.model
    def default_get(self, fields):
        """
        :Author:Bhavesh Jadav TechUltra Solutions
        :Date: 25/11/2020
        :Func:This method use for the set is_readonly_approve_amount true or false base on group
        :Return: result of the supper call
        """
        res = super(EducationTermsFeesLine, self).default_get(fields)
        if not self.env.user.has_group('security_rules.group_strata_hc') and 'is_readonly_approve_amount' in fields:
            res.update({'is_readonly_approve_amount': True})
        return res

    name = fields.Char(string="Name")

    school_terms_fees = fields.Many2one('school.terms.fees', string="Terms and Fees")
    claimed_amount = fields.Monetary(string="Claimed Amount")
    approve_amount = fields.Monetary(string="Approve Amount")
    request_line_id = fields.Many2one('education.request.line', 'Request Line', ondelete='cascade')
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda self: self.env.company.currency_id)
    is_readonly_approve_amount = fields.Boolean(string="Is Readonly Approve Amount",
                                                compute='_is_readonly_approve_amount',
                                                help="This field use for the readonly some field for the "
                                                     "requester")
    is_readonly_claim_amount = fields.Boolean(string="Is Readonly Claim Amount",
                                              compute='_is_readonly_claim_amount',
                                              help="This field use for the readonly some field for the "
                                                   "requester")
    paid_to = fields.Selection([
        ('school', 'School'),
        ('employee', 'Employee')], string="Paid To", default="employee", required=True)

    @api.onchange('name')
    def _is_readonly_approve_amount(self):
        """
        @Author:Bhavesh Jadav TechUltra Solutions
        @Date: 25/11/2020
        @Func: This method use for the set is_readonly_approve_amount boolean true or false base on the group
        """
        education_settings = self.request_line_id.education_request_id.education_settings_id or False
        approvers_ids = self.request_line_id.education_request_id.approver_ids.mapped('user_id') or False
        for rec in self:
            if self.env.user.has_group(
                    'security_rules.group_strata_hc') or (self.env.user not in approvers_ids if approvers_ids else []):
                rec.is_readonly_approve_amount = True
            else:
                rec.is_readonly_approve_amount = False

    @api.onchange('school_terms_fees')
    def _is_readonly_claim_amount(self):
        """
        @Author:Nimesh Jadav TechUltra Solutions
        @Date: 10th march 2021
        @Func: This method use for the set is_readonly_claim_amount boolean true or false base on the group
        """
        for rec in self:
            if rec.request_line_id.employee_id and rec.request_line_id.employee_id.user_id \
                    and self.env.user != rec.request_line_id.employee_id.user_id:
                rec.is_readonly_claim_amount = True
            else:
                rec.is_readonly_claim_amount = False

    @api.model
    def create(self, vals):
        """
        @Author:Bhavesh Jadav TechUltra Solutions
        @Date:24/11/2020
        @Func:This method inherit for add name of the record
        @Return: res result of the supper call
        """
        vals['name'] = self.env['ir.sequence'].next_by_code('education.terms.fees.line') or _('New')
        res = super(EducationTermsFeesLine, self).create(vals)
        return res

    # Report Methods
    def terms_and_fees_name(self):
        terms_and_fees_name_list = self.school_terms_fees.mapped('name')
        name = ','.join(map(str, terms_and_fees_name_list))
        return name
