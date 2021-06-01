# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    responsible_report_person_id = fields.Many2one('responsible.report.person', string='Responsible Person')

    def set_values(self):
        """
        :Author:Bhavesh Jadav TechUltra Solutions
        :Date:23/09/2020
        :Func:This method use for the set values of the responsible_report_person_id in res.config.settings
        :Return:N/A
        """
        super(ResConfigSettings, self).set_values()
        select_type = self.env['ir.config_parameter'].sudo()
        if self.responsible_report_person_id:
            select_type.set_param('res.config.settings.responsible_report_person_id',
                                  self.responsible_report_person_id.id)
        else:
            select_type.set_param('res.config.settings.responsible_report_person_id', False)

    @api.model
    def get_values(self):
        """
        :Author:Bhavesh Jadav TechUltra Solutions
        :Date:23/09/2020
        :Func:This method use for the get values of the responsible_report_person_id from res.config.settings
        :Return:res of supper call
        """
        res = super(ResConfigSettings, self).get_values()
        select_type = self.env['ir.config_parameter'].sudo()
        responsible_report_person_id = select_type.get_param('res.config.settings.responsible_report_person_id')
        if responsible_report_person_id:
            if self.env['responsible.report.person'].search([('id', '=', int(responsible_report_person_id))]):
                res.update({'responsible_report_person_id': int(responsible_report_person_id)})
        return res
