from odoo import models, fields, api, _


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        """
        @Author:Bhavesh Jadav TechUltra solutions
        @Date:25/01/2021
        @Func:This Method use for the show specific  value in the Many2one field
        @return:specific ids or result of supper call
        """
        if self._context.get('is_child_education_request_dynamic_domain'):
            if self.env.user.has_group('security_rules.group_strata_hc'):
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
