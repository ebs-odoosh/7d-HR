from odoo import fields, models, api
from odoo.exceptions import ValidationError


class HrEmployeePrivate(models.Model):
    _inherit = 'hr.employee'

    own_document_o2m = fields.One2many('ir.attachment', 'related_employee', string="Own Related Document")
                                       # domain=lambda self: [('res_id', '=', self.id), ('res_model', '=', self._name)])
    document_o2m = fields.One2many('ir.attachment', 'related_employee', string="Related Document")

    # missing_documents = fields.Many2many('required.document', string='Missing/Expired Documents',
    #                                      compute='get_missing_documents')

    # @api.depends('own_document_o2m')
    # def get_missing_documents(self):
    #     for rec in self:
    #         group = rec.contract_id.contract_group
    #         required_doc = self.env['required.document'].search(
    #             [('required_model', '=', 'employee'), ('mandatory', '=', True)])
    #         results = self.env['required.document']
    #         for line in required_doc:
    #             if group.id == line.contract_group.id or not line.contract_group.id:
    #                 doc = rec.own_document_o2m.filtered(
    #                     lambda x: x.document_type_id.id == line.name.id and x.status in (
    #                         'active', 'na') and x.state == 'approved')
    #                 if not doc:
    #                     results |= line
    #         rec.missing_documents = results.ids
    #         return results

    # def state_approve(self):
    #     if self.missing_documents:
    #         raise ValidationError('Missing/Expired Required Documents!')
    #     super(HrEmployeePrivate, self).state_approve()

    def _get_document_vals(self, attachment):
        """
        Return values used to create a `ir.attachment`
        """
        self.ensure_one()
        document_vals = super(HrEmployeePrivate, self)._get_document_vals(attachment)
        if self._check_create_documents():
            document_vals.update({'related_employee': self.id,
                                  'issue_date': fields.Date.today()})
        return document_vals

    def write(self, vals):
        self = self.sudo()
        res = super(HrEmployeePrivate, self).write(vals)
        for rec in self:
            if not rec.active and rec.user_id and rec.user_id.active:
                rec.user_id.active = False
            if rec.active and rec.user_id and not rec.user_id.active:
                rec.user_id.active = True
        return res
