# -*- coding: utf-8 -*-

from odoo import models, fields


class ImportChildEducationLogLine(models.Model):
    _name = 'import.child.education.log.line'
    _description = 'Import Child Education Log Line'

    import_log_id = fields.Many2one('import.child.education', string='Import Child Education')
    line_no = fields.Integer(string='Line Number')
    message = fields.Char(string='Message')
