from odoo import models, fields, api, _


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    # iban = fields.Char(string="IBAN NO.")
    current_account_number = fields.Char(string='Current Account Number', compute='_compute_bank_details',
                                         readonly=True)
    current_bank_name = fields.Many2one('res.bank', string='Current Bank Name', readonly=True,
                                        compute='_compute_bank_details')
    iban = fields.Char(string="IBAN NO.", compute='_compute_bank_details')

    def _compute_bank_details(self):
        for rec in self:
            details = rec.bank_history_ids
            if details:
                if len(details) == 1:
                    rec.current_bank_name = details.current_bank_name.id or ''
                    rec.iban = details.current_iban or ''
                    rec.current_account_number = details.current_account_number or ''
                elif len(details) > 1:
                    last_rec = (len(details) - 1)
                    rec.current_bank_name = details[last_rec].current_bank_name.id or ''
                    rec.iban = details[last_rec].current_iban or ''
                    rec.current_account_number = details[last_rec].current_account_number or ''
            else:
                rec.current_account_number = ''
                rec.iban = ''
                rec.current_bank_name = False
                return

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        """
        @Author:Bhavesh Jadav TechUltra solutions
        @Date:25/01/2021
        @Func:This Method use for the show specific  value in the Many2one field
        @return:specific ids or result of supper call
        """
        if self._context.get('is_report_request_dynamic_domain'):
            if self.env.user.has_group('security_rules.group_hc_employee'):
                res = super(HrEmployee, self)._search(args, offset, limit, order, count, access_rights_uid)
            elif self.env.user.has_group('security_rules.group_strata_employee'):
                if self.env.user.employee_id:
                    res = self.env.user.employee_id.ids
                    return res
                else:
                    return []
            else:
                return []
        res = super(HrEmployee, self)._search(args, offset, limit, order, count, access_rights_uid)
        return res
