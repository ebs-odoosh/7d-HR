# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ContactCustom(models.Model):
    _inherit = 'res.partner'

    gender = fields.Selection(
        string='Gender',
        selection=[('male', 'Male'),
                   ('female', 'Female'), ],
        required=False, )

    nationality = fields.Many2one(
        comodel_name='res.country',
        string='Nationality',
        required=False)

    country_id = fields.Many2one(
        comodel_name='res.country',
        string='Country of Birth',
        required=False)

    # passport_doc = fields.Many2one(
    #     comodel_name='ir.attachment',
    #     string='Passport Document',
    #     required=False
    # )
    #
    # passport_exp_date = fields.Date(
    #     related='passport_doc.expiry_date',
    #     string='Passport Expiry Date',
    #     required=False)

    document_o2m = fields.One2many(
        comodel_name='ir.attachment',
        inverse_name='partner_id',
        string='Related Documents',
        required=False)

    # missing_documents = fields.Many2many('required.document', string='Missing/Expired Documents',
    #                                      compute='get_missing_documents')

    # @api.depends('document_o2m')
    # def get_missing_documents(self):
    #     for rec in self:
    #         group = rec.related_employee.contract_id.contract_group
    #         required_doc = self.env['required.document'].search(
    #             [('required_model', '=', 'dependent'), ('mandatory', '=', True)])
    #         results = self.env['required.document']
    #         for line in required_doc:
    #             if group.id == line.contract_group.id or not line.contract_group.id:
    #                 doc = rec.document_o2m.filtered(
    #                     lambda x: x.document_type_id.id == line.name.id and x.status in (
    #                         'active', 'na') and x.state == 'approved')
    #                 if not doc:
    #                     results |= line
    #         rec.missing_documents = results.ids
    #         return results

    def state_approve(self):
        # if self.missing_documents:
        #     raise ValidationError('Missing/Expired Required Documents!')
        return super(ContactCustom, self).state_approve()

    def contact_archive_onchange(self, active):
        self.contact_document_archive(active)
        related_contacts_list = self.env['res.partner'].search(
            [('parent_id', '=', self.id), ('active', '=', (not active))])
        for rec in related_contacts_list:
            rec.active = active

    def contact_document_archive(self, active):
        document_list = self.env['ir.attachment'].search(
            [('partner_id', '=', self.id), ('active', '=', (not active))])
        for rec in document_list:
            rec.active = active

    def unlink(self):
        for rec in self:
            for doc in rec.document_o2m:
                doc.unlink()
            super(ContactCustom, rec).unlink()

    def action_see_documents(self):
        self.ensure_one()
        return {
            'name': _('Documents'),
            'res_model': 'ir.attachment',
            'type': 'ir.actions.act_window',
            'views': [(False, 'kanban'), (False, 'tree'), (False, 'form')],
            'view_mode': 'kanban',
            'context': {
                "search_default_partner_id": self.id,
                "default_partner_id": self.id,
                "searchpanel_default_folder_id": False,
                "hide_contact": True,
                "hide_service": True
            },
        }
