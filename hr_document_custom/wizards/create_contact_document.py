# -*- coding: utf-8 -*-

import re

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class CreateContactDocument(models.TransientModel):
    _name = 'contact.document'
    _description = 'Create documents for contacts wizard'

    document_number = fields.Char(
        string='Document Number',
        required=False)

    issue_date = fields.Date(
        string='Date of Issue',
        required=False)
    expiry_date = fields.Date(
        string='Date of Expiry',
        required=False)
    contact_id = fields.Many2one(
        comodel_name='res.partner',
        string='Contact',
        required=False)

    attachment_ids = fields.Many2many(comodel_name="ir.attachment",
                                      relation="ebs_mod_m2m_ir_contact_document",
                                      column1="m2m_id",
                                      column2="attachment_id",
                                      string="File"
                                      )
    desc = fields.Text(
        string="Description",
        required=False)

    document_type_id = fields.Many2one(
        comodel_name='document.types',
        string='Document Type',
        required=True)

    tags = fields.Many2many(
        comodel_name='documents.tag',
        relation="ebs_mod_m2m_ir_contact_document_tags",
        column1="m2m_id",
        column2="tag_id",
        string='Tags')

    related_employee = fields.Many2one(
        comodel_name='hr.employee',
        string='Related Employee')

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
        required=False)
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
    dependent_relationship = fields.Many2one(
        comodel_name='contact.relation.type',
        string='Dependent Relationship',
        required=False)

    @api.onchange('contact_id')
    def onchange_contact_id(self):
        for record in self:
            if record.contact_id.id:
                req_list = self.env['required.document'].search([('required_model', '=', 'dependent')])
                result = []
                for req in req_list:
                    result.append(req.name.id)
            else:
                req_list = self.env['required.document'].search([('required_model', '=', 'employee')])
                result = []
                for req in req_list:
                    result.append(req.name.id)

            return {'domain': {'document_type_id': [('id', 'in', result)]}}

    def get_count_existing_document_by_employee_and_type(self, employee, document_type):
        existing_docs = self.env['ir.attachment'].search(
            [('related_employee', '=', employee.id), ('document_type_id', '=', document_type.id),
             ('status', '=', 'active')])
        result = len(existing_docs)
        return result

    def create_document(self):
        folder = self.env['documents.folder'].search([('is_default_folder', '=', True)], limit=1)
        if not folder:
            raise ValidationError(
                'Please go to Workspaces menu from Documents menu and check one of workspace as default folder')
        if len(self.attachment_ids) == 0 or len(self.attachment_ids) > 1:
            raise ValidationError(_("Select 1 File"))

        docs_count = self.get_count_existing_document_by_employee_and_type(self.related_employee, self.document_type_id)

        if docs_count > 0:
            raise ValidationError(_('You can not submit a document of this type at this stage'))

        emirates_id_pattern = re.compile("^[1234567890]{3}-[1234567890]{4}-[1234567890]{7}-[1234567890]{1}$")
        if self.document_type_name == 'Emirates ID' and not emirates_id_pattern.match(self.emirates_id):
            raise ValidationError(_("Emirates ID does not meet the specified format: ###-####-#######-#"))
        attachment = self.attachment_ids[0]
        # attachment.write({'res_model':})
        attachment.write(
            {'res_model': self._context.get('active_model'), 'res_id': self._context.get('active_id')})

        vals = {
            'document_type_id': self.document_type_id.id,
            'document_number': self.document_number,
            'issue_date': self.issue_date.strftime("%Y-%m-%d"),
            'desc': self.desc,
            'tag_ids': self.tags,
            'related_employee': self.related_employee.id,
            'passport_unified_no': self.passport_unified_no,
            'passport_no': self.passport_no,
            'passport_country_issue': self.passport_country_issue.id,
            'passport_place_issue': self.passport_place_issue,
            'family_book': self.family_book,
            'town_no': self.town_no,
            'visa_job_title': self.visa_job_title,
            'visa_job_title_arabic': self.visa_job_title_arabic,
            'visa_sponsor': self.visa_sponsor,
            'visa_place_issue': self.visa_place_issue,
            'visa_file_no': self.visa_file_no,
            'visa_unified_no': self.visa_unified_no,
            'emirates_id': self.emirates_id,
            'type': 'binary',
            'folder_id': folder.id
        }
        if self.env.context.get('upload_contact', False):
            vals['partner_id'] = self.contact_id.id

        if self.expiry_date:
            vals['expiry_date'] = self.expiry_date.strftime("%Y-%m-%d")
        doc = self.env['ir.attachment'].search([('id', '=', attachment.id)])
        if doc:
            doc.write(vals)
        else:
            self.env['ir.attachment'].create(vals)
        self.env.cr.commit()
