# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ApproveEmployeeEvent(models.TransientModel):
    _name = 'approve.employee.event'
    _description = 'Approve Employee Events wizard'

    employee_id = fields.Many2one('hr.employee', 'Employee', required=True)
    event_type_id = fields.Many2one(comodel_name='sap.event.type', string='Event Type', required=True)
    event_reason_id = fields.Many2one(comodel_name='sap.event.type.reason', string='Event Reason', required=False)

    @api.onchange('event_type_id')
    def onchange_event_type(self):
        self.event_reason_id = False
        return {'domain': {'event_reason_id': [('event_type_id', '=', self.event_type_id.id)]}}

    def approve_employee_event(self):
        self.ensure_one()
        self.employee_id.company_employee_id = self.env['ir.sequence'].next_by_code(
            self.employee_id.contract_employment_type.related_sequence.code)
        self.employee_id.system_id = self.employee_id.contract_employment_type.code + self.employee_id.split_code(
            self.employee_id.company_employee_id)
        self.employee_id.id_generated = True
        self.employee_id.contract_id.name = self.employee_id.company_employee_id

        if not self.employee_id.contract_id:
            raise ValidationError(_(self.employee_id.name + ' must have running contract to be able to create event.'))

        event = self.env['hr.employee.event'].create({
            'name': self.event_type_id.id,
            'event_reason': self.event_reason_id.id,
            'start_date': self.employee_id.contract_id.date_start,
            'end_date': False,
            'employee_id': self.employee_id.id,
            'is_processed': False,
            'is_triggered': True,
            'is_esd': True
        })
        event.onchange_employee()
