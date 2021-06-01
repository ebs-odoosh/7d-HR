from odoo import models, fields, api, _
from odoo.exceptions import Warning


class EmployeeTravelRequest(models.Model):
    _name = 'travel.request.quotation'
    _description = 'Travel Request quotation'
    _order = 'id desc'

    @api.model
    def default_get(self, fields):
        """
        :Author:Bhavesh Jadav TechUltra solutions
        :Date:25/11/2020
        :Func:For set class_of_travel when open form view
        """
        res = super(EmployeeTravelRequest, self).default_get(fields)
        if self._context.get('perdiem_rule') and 'class_of_travel' in fields:
            rule = self.env['travel.perdiem.rule'].browse(self._context.get('perdiem_rule'))
            res.update({'class_of_travel': rule.class_of_travel})
        return res

    name = fields.Char(string="Name")
    travel_request_id = fields.Many2one('employee.travel.request', string="Travel Request")
    travel_agency_id = fields.Many2one('res.partner', string="Agency")
    flight_no = fields.Char(string="Flight No.")
    boarding_time = fields.Datetime(string="Boarding Time")
    value_cost = fields.Monetary(string="Value Cost", currency_field='currency_id')
    markup_amount = fields.Monetary(string="Markup Amount", currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda self: self.env.company.currency_id)
    car_rental_days = fields.Float(string='Car Rental Days', required=False)
    car_rental_amount = fields.Monetary(string="Car Rental Amount", currency_field='currency_id')
    hotel_accommodation_days = fields.Float(string='Hotel Accommodation Days', required=False)
    hotel_accommodation_amount = fields.Monetary(string="Hotel Accommodation Amount", currency_field='currency_id')
    class_of_travel = fields.Selection(
        selection=[('economy_class', 'Economy Class'), ('premium_economy_class', 'Premium Economy Class'),
                   ('business_class', 'Business Class')])

    attachment_ids = fields.Many2many(comodel_name="ir.attachment",
                                      relation="quotation_ir_attachment_document",
                                      column1="quotation_id",
                                      column2="attachment_id",
                                      string="Attachments",
                                      required=True
                                      )
    comment = fields.Char(string='Comment')
    note = fields.Text('Note')
    total_amount = fields.Float(string="Total Amount", compute='_get_quotation_total_amount')

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        """
        @Author:Bhavesh Jadav TechUltra solutions
        @Date:22/01/2021
        @Func:This Method use for the show specific  value in the Many2one field
        @return:specific ids or result of supper call
        """
        if self._context.get('is_dynamic_domain') and self._context.get('current_id'):
            travel_request = self._context.get('current_id')
            # we are using  query for avoid the recursion error
            query = """ Select array_agg(id) as quotation_id from  travel_request_quotation where travel_request_id= {} """.format(
                travel_request)
            self.env.cr.execute(query)
            query_result = self.env.cr.dictfetchall()
            res = query_result and query_result[0].get('quotation_id', [])
            return res
        return super(EmployeeTravelRequest, self)._search(args, offset=0, limit=None, order=None, count=False,
                                                          access_rights_uid=None)

    @api.depends('value_cost', 'markup_amount', 'car_rental_amount', 'hotel_accommodation_amount')
    def _get_quotation_total_amount(self):
        """
        @Author:Bhavesh Jadav  TechUltra solutions
        @Date:18/01/2021
        @Func:this method use for the get sum of all of the expenses in the quotation
        @Return:N/A
        """
        for rec in self:
            total_amount = 0.0
            if rec.value_cost:
                total_amount += rec.value_cost
            if rec.markup_amount:
                total_amount += rec.markup_amount
            if rec.car_rental_amount:
                total_amount += rec.car_rental_amount
            if rec.hotel_accommodation_amount:
                total_amount += rec.car_rental_amount
            rec.total_amount = total_amount

    @api.onchange('travel_request_id')
    def onchange_travel_agency(self):
        """
        Author:Bhavesh Jadav TechUltra solutions
        Date:  17/09/2020
        Func: for apply dynamic domain
        :return: domain
        """
        travel_agency_list = self.travel_request_id.travel_settings_id.travel_agency_ids.ids
        return {'domain': {'travel_agency_id': [('id', 'in', travel_agency_list)]}}

    @api.model
    def create(self, vals):
        """
        :Author: Bhavesh Jadav TechUltra Solutions
        :Date: 12/10/2020
        :Func: inherit for the add name of the quotation
        :Return : Result of the supper call
        """
        name = self.env['ir.sequence'].next_by_code('travel.request.quotation') or _('New')
        vals['name'] = name
        res = super(EmployeeTravelRequest, self).create(vals)
        if res:
            if not res.attachment_ids:
                raise Warning('Please Add Attachment for the Quotation')
        return res

    @api.model
    def write(self, vals):
        """
        :Author: Nimesh Jadav TechUltra Solutions
        :Date: 17th May 2021
        :Func: inherit for the check attachment
        :Return : Result of the supper call
        """
        res = super(EmployeeTravelRequest, self).write(vals)
        if res:
            if not self.attachment_ids:
                raise Warning('Please Add Attachment for the Quotation')
        return res
