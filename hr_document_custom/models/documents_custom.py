# -*- coding: utf-8 -*-

from datetime import datetime

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class DocumentsCustom(models.Model):
    _inherit = 'ir.attachment'
    _order = 'issue_date desc'

    issue_date = fields.Date(
        string='Date of Issue',
        required=False)

    related_employee = fields.Many2one(
        comodel_name='hr.employee',
        string='Related Employee')
    company_employee_id = fields.Char(related='related_employee.company_employee_id')
    dependent_relationship = fields.Many2one(
        comodel_name='contact.relation.type',
        string='Dependent Relationship',
        required=False)
    relation_type = fields.Many2one(related='partner_id.contact_relation_type_id')

    def log_and_reject(self):
        self = self.sudo()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Reject Reason',
            'res_model': 'log.note.reject.wizard',
            'view_mode': 'form',
            'target': 'new',
            'view_id': self.env.ref('hr_employee_custom.log_note_reject_wizard_view_form').id,
            'context': {
                'related_name': self._name,
            }
        }

    def state_reject(self):
        if self.reject_reason:
            self.write({'state': 'reject'})
            msg = _('Document ' + self.document_number + ' Rejected. Rejection Reason: ' + self.reject_reason)
            self.related_employee.message_post(body=msg)
        else:
            raise ValidationError('Must add reject reason!')

    # @api.constrains('document_number')
    # def _check_document_number(self):
    #     for rec in self:
    #         if len(self.env['ir.attachment'].search(
    #                 [('document_number', '=', rec.document_number),
    #                  ('active', '=', True),
    #                  ('id', '!=', rec.id)])) != 0 \
    #                 and rec.document_number:
    #             raise ValidationError(_("Document Number and Document Type Combination must be unique !"))

    # def name_get(self):
    #     result = []
    #     for rec in self:
    #         rec_name = ""
    #         if rec.document_number:
    #             rec_name = rec.document_number
    #         else:
    #             rec_name = rec.name
    #         result.append((rec.id, rec_name))
    #     return result

    def write(self, vals):
        # if vals.get('expiry_date', False):
        #     expiry_date = datetime.strptime(vals['expiry_date'], "%Y-%m-%d").today().date()
        #     if expiry_date > datetime.today().date():
        #         vals['status'] = 'active'
        #     else:
        #         vals['status'] = 'expired'
        res = super(DocumentsCustom, self).write(vals)
        if self.expiry_date and self.issue_date:
            if self.expiry_date < self.issue_date:
                raise ValidationError(_("Expiry date is before issue date."))
        if vals.get('attachment_name', '') != '' and self.state == 'reject':
            self.state = 'pending'
        return res

    def check_document_expiry_date(self):
        for doc in self.env['ir.attachment'].search([('status', '=', 'active')]):
            if doc.expiry_date:
                if doc.expiry_date < datetime.today().date():
                    doc.status = 'expired'

    @api.model
    def create(self, vals):
        if vals.get('expiry_date', False):
            expiry_date = datetime.strptime(vals['expiry_date'], "%Y-%m-%d").date()
            if expiry_date > datetime.today().date():
                vals['status'] = 'active'
            else:
                vals['status'] = 'expired'
        else:
            vals['status'] = 'na'
        vals['document_number'] = self.env['ir.sequence'].next_by_code('company.documents.code')
        res = super(DocumentsCustom, self).create(vals)
        if res.expiry_date and res.issue_date:
            if res.expiry_date < res.issue_date:
                raise ValidationError(_("Expiry date is before issue date."))
        return res

    def preview_document(self):
        self.ensure_one()
        action = {
            'type': "ir.actions.act_url",
            'target': "_blank",
            'url': '/documents/content/preview/%s' % self.id
        }
        return action

    def access_content(self):
        return super(DocumentsCustom, self).access_content()


class DocumentsFolderCustom(models.Model):
    _inherit = 'documents.folder'
    is_default_folder = fields.Boolean(
        string='Is Default Folder',
        required=False
    )
