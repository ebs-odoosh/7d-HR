# -*- coding: utf-8 -*-

from odoo import models, _
from odoo.exceptions import ValidationError


class ApproveEmployeeEvent(models.TransientModel):
    _inherit = 'approve.employee.event'
    _description = 'Approve Employee Events wizard'

    def approve_employee_event(self):
        if not self.employee_id.contract_id:
            raise ValidationError(
                _(self.employee_id.name + ' must have no running contract to be able to create event.'))

        employee_code = self.env['ir.sequence'].next_by_code('hr.employee',
                                                             sequence_date=self.employee_id.contract_id.date_start)
        self.employee_id.company_employee_id = employee_code
        self.employee_id.system_id = employee_code
        self.employee_id.id_generated = True
        self.employee_id.contract_id.name = self.employee_id.company_employee_id

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
