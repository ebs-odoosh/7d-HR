from odoo import models, fields, api, _


class RequestModifyReason(models.TransientModel):
    _name = 'request.modify.reason'

    name = fields.Char(string="Name")
    request_id = fields.Many2one('employee.travel.request')

    def action_done(self):
        vals = {'name': self.name,
                'request_id': self._context.get('request_id')}
        self.env['request.modify.history'].create(vals)
        return True
