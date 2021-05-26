from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError


class ContractCustom(models.Model):
    _inherit = 'hr.contract'

    required_signatures = fields.One2many('hr.contract.signature', 'hr_contract_id', string='Required Signatures',
                                          ondelete='cascade')

    def name_get(self):
        return [
            (contract.id, contract.name + ((" - " + contract.employee_id.name) if contract.employee_id else ''))
            for contract in self]

    @api.model
    def create(self, vals):
        applicant_id = vals.get('applicant_id', '')
        if applicant_id != '':
            applicantt = self.env['hr.applicant'].browse(applicant_id)
            if not applicantt.stage_id.generate_contract:
                raise ValidationError(_("You can't create a contract at this stage"))

        result = super(ContractCustom, self).create(vals)
        applicant = result.applicant_id
        job = applicant.job_id
        required_signatures = job.required_signatures

        fill_values = [(0, 0, {'name': required_signature.name.id, 'sequence': required_signature.sequence}) for
                       required_signature in required_signatures]
        result.required_signatures = fill_values

        if (len(required_signatures) > 0):
            first_signature = min(required_signatures, key=lambda x: x.sequence)
            first_user = first_signature.name if first_signature else None

            msg = _(
                'A signature is required by ') + ': <a href=# data-oe-model=res.users data-oe-id=%d>%s</a>' % (
                      first_user.id, first_user.name)
            # for rec in self:
            result.message_post(body=msg)

        return result

    def write(self, vals):
        applicant_id = vals.get('applicant_id', '')
        if applicant_id != '':
            applicantt = self.env['hr.applicant'].browse(applicant_id)
            if not applicantt.stage_id.generate_contract:
                raise ValidationError(_("You can't create a contract at this stage"))

        if self.applicant_id.id != vals.get('applicant_id', ''):
            if vals.get('applicant_id', '') != '':
                applicant = self.env['hr.applicant'].browse(vals.get('applicant_id', ''))
                job = applicant.job_id
                required_signatures = job.required_signatures

                fill_values = [(0, 0, {'name': required_signature.name.id, 'sequence': required_signature.sequence}) for
                               required_signature in required_signatures]
                vals['required_signatures'] = fill_values

        return super(ContractCustom, self).write(vals)
