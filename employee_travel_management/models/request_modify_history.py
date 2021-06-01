from odoo import models, fields, api, _


class RequestModifyHistory(models.Model):
    _name = 'request.modify.history'
    _description = 'Request Modify History'
    _order = 'id desc'

    name = fields.Char(string="Name")

    request_modify_user = fields.Many2one('res.users', string="Request Modify User")
    modify_fields = fields.Char(string="modify_fields")

