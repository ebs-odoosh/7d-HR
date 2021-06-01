from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class TravelCostCenterLine(models.Model):
    _name = 'travel.cost.center.line'
    _description = 'Travel Request Cost Center line'
    _order = 'id desc'

    @api.model
    def default_get(self, fields):
        """
        :Author :Bhavesh Jadav TechUltra solutions
        :Date: 14/10/2020
        :Func: this method use for the set default employee cost center when form open
        :Return : result of supper call
        """
        res = super(TravelCostCenterLine, self).default_get(fields)
        if self._context.get('employee_id') and 'cost_center_id' in fields:
            employee_id = self.env['hr.employee'].browse(self._context.get('employee_id'))
            if employee_id and employee_id.contract_id and employee_id.contract_id.cost_center:
                res.update({'cost_center_id': employee_id.contract_id.cost_center.id})
        return res

    cost_center_id = fields.Many2one('hr.cost.center', string="Cost Center")
    share_percentage = fields.Float(string="Share Percentage", default=100)
    description = fields.Char(string="Description")
    travel_request_id = fields.Many2one('employee.travel.request', string="Travel Request")

    @api.model
    def create(self, vals):
        """
        :Author:Bhavesh Jadav TechUltra solution
        :Date: 12/10/2020
        :Func: This method inherit for the raise UserError when the cost center line was not created
        """
        if vals.get('share_percentage') and float(vals.get('share_percentage')) > 100:
            raise UserError(_("Please add proper percentage you can not add more then 100%"))
        res = super(TravelCostCenterLine, self).create(vals)
        return res
