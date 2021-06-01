from odoo import api, fields, models, _


class HrExpense(models.Model):
    _inherit = 'hr.expense'

    @api.model
    def default_get(self, fields):
        """
        @Author:Bhavesh Jadav TechUltra solutions
        @Date: 21/01/2020
        @Func: this method use for the set employee_id
        @return: result of teh supper call
        """
        res = super(HrExpense, self).default_get(fields)
        if self._context.get('employee_id') and 'employee_id' in fields:
            res.update({'employee_id': self._context.get('employee_id')})
        return res

    travel_request_id = fields.Many2one('employee.travel.request', string="Travel Request")
    document = fields.Binary(string="Document")
    document_name = fields.Char(string="File Name")
    is_per_diem_expense = fields.Boolean(string="is Per Diem Expense", compute="compute_is_per_diem_expense")

    def compute_is_per_diem_expense(self):
        """
        @Author:Bhavesh Jadav TechUltra solutions
        @Date: 21/01/2020
        @Func: this method use for the set is_per_diem_expense in hr expense record
        @return: result of teh supper call
        """
        for rec in self:
            if rec.product_id.is_per_diem_product:
                rec.is_per_diem_expense = True
            else:
                rec.is_per_diem_expense = False

    @api.model
    def create(self, vals):
        """
        :Author: Bhavesh Jadav TechUltra solutions
        :Date: 15/10/2020
        :Func:for the set employee and the paid by in expense recoded
         when its create from the tra el requests and also create the ir.attachment for te expense
         record
        """
        attachment = False
        if vals.get('travel_request_id'):
            travel_request_id = self.env['employee.travel.request'].browse(vals.get('travel_request_id'))
            vals.update({'employee_id': travel_request_id.employee_id.id})
            if travel_request_id.accommodation_type == 'by_company':
                vals.update({'payment_mode': 'company_account'})
            elif travel_request_id.accommodation_type == 'by_self':
                vals.update({'payment_mode': 'own_account'})
            if vals.get('document_name') and vals.get('document'):
                attachment_val = {'type': 'binary',
                                  'name': vals.get('document_name'),
                                  'datas': vals.get('document'),
                                  'res_model': 'hr.expense'}
                attachment = self.env['ir.attachment'].create(attachment_val)
        res = super(HrExpense, self).create(vals)
        if attachment:
            attachment.write({'res_id': res.id})
        return res
