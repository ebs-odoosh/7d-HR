# -*- coding: utf-8 -*-

from datetime import datetime

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class RequiredDocument(models.Model):
    _name = 'required.document'

    name = fields.Many2one('document.types', 'Document Required')
    required_model = fields.Selection([('employee', 'Employee'), ('dependent', 'Dependent')], 'Required By')
    color = fields.Integer(string='Color Index', default=1)
    mandatory = fields.Boolean(
        string='Mandatory',
        required=True, default=True)
    contract_group = fields.Many2one(
        comodel_name='hr.contract.group',
        string='Contract Group',
        required=False)


class DocumentsCustom(models.Model):
    _inherit = 'ir.attachment'
    _order = 'issue_date desc'

    desc = fields.Text(
        string="Description",
        required=False)
    issue_date = fields.Date(
        string='Date of Issue',
        required=False)
    expiry_date = fields.Date(
        string='Date of Expiry',
        required=False)

    document_number = fields.Char(
        string='Document Number',
        required=False)
    document_type_id = fields.Many2one(
        comodel_name='document.types',
        string='Document Type',
        required=False)

    status = fields.Selection(
        string='Status',
        selection=[('na', 'N/A'),
                   ('active', 'Active'), ('expired', 'Expired')],
        default='na',
        required=False, )

    related_employee = fields.Many2one(
        comodel_name='hr.employee',
        string='Related Employee')

    # company_employee_id = fields.Char(related='related_employee.company_employee_id')

    state = fields.Selection([('pending', 'Pending Approval'), ('approved', 'Approved'), ('reject', 'Rejected')],
                             default='pending',
                             string="Approval State")

    reject_reason = fields.Text('Reject Reason')

    document_type_name = fields.Char(
        string='Document Type Name',
        required=False,
        related='document_type_id.name')
    passport_unified_no = fields.Char(
        string='Passport Unified No',
        required=False)

    passport_no = fields.Char(
        string='Passport No',
        required=False)
    start_date = fields.Date(
        string='Start Date',
        required=True)
    passport_place_issue = fields.Char(
        string='Passport Place of Issue',
        required=False)
    passport_country_issue = fields.Many2one(
        comodel_name='res.country',
        string='Passport Country of Issue',
        required=False)

    family_book = fields.Char(
        string='Family No',
        required=False)
    town_no = fields.Char(
        string='Town No',
        required=False)

    visa_job_title = fields.Char(
        string='Visa Job Title',
        required=False)
    visa_job_title_arabic = fields.Char(
        string='Visa Job Title (Arabic)',
        required=False)
    visa_sponsor = fields.Char(
        string='Visa Sponsor',
        required=False)
    visa_place_issue = fields.Char(
        string='Visa Place of Issue',
        required=False)
    visa_file_no = fields.Char(
        string='Visa No',
        required=False)
    visa_unified_no = fields.Char(
        string='Visa Unified No',
        required=False)

    emirates_id = fields.Char(
        string='Emirates ID No',
        required=False)

    first_name = fields.Char(
        string='First Name',
        required=False)
    last_name = fields.Char(
        string='Last Name',
        required=False)
    # dependent_relationship = fields.Many2one(
    #     comodel_name='contact.relation.type',
    #     string='Dependent Relationship',
    #     required=False)
    # relation_type = fields.Many2one(related='partner_id.contact_relation_type_id')

    # def _audit_logs(self, vals):
    #     for rec in self:
    #         log = "Following Fields Changed:<br/>"
    #         # message_post(body=_(u'Shipment N° %s has been cancelled' % picking.carrier_tracking_ref))
    #         for val in vals:
    #             log = log + "   - " + self._fields[val].string + " <br/>"
    #         rec.message_post(body=log)

    # def write(self, vals):
    #     self._audit_logs(vals)
    #     if vals and len(vals) > 1 or not vals.get('state'):
    #         vals.update({'state': 'pending'})
    #     res = super(DocumentsCustom, self).write(vals)
    #
    #     return res

    def state_approve(self):
        self.reject_reason = ""
        self.write({'state': 'approved'})
        msg = _('Document ' + self.document_number if self.document_number else ''+ ' Approved')
        self.related_employee.message_post(body=msg)

    def state_pending(self):
        self.write({'state': 'pending'})

    # def log_and_reject(self):
    #     self = self.sudo()
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': 'Reject Reason',
    #         'res_model': 'log.note.reject.wizard',
    #         'view_mode': 'form',
    #         'target': 'new',
    #         'view_id': self.env.ref('hr_employee_custom.log_note_reject_wizard_view_form').id,
    #         'context': {
    #             'related_name': self._name,
    #         }
    #     }

    def state_reject(self):
        if self.reject_reason:
            self.write({'state': 'reject'})
            msg = _('Document ' + self.document_number + ' Rejected. Rejection Reason: ' + self.reject_reason)
            self.related_employee.message_post(body=msg)
        else:
            raise ValidationError('Must add reject reason!')

    @api.constrains('document_number')
    def _check_document_number(self):
        for rec in self:
            if len(self.env['ir.attachment'].search(
                    [('document_number', '=', rec.document_number),
                     ('active', '=', True),
                     ('id', '!=', rec.id)])) != 0 \
                    and rec.document_number:
                raise ValidationError(_("Document Number and Document Type Combination must be unique !"))

    def name_get(self):
        result = []
        for rec in self:
            rec_name = ""
            if rec.document_number:
                rec_name = rec.document_number
            else:
                rec_name = rec.name
            result.append((rec.id, rec_name))
        return result

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
