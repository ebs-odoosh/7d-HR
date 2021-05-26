# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class Survey(models.Model):
    _inherit = 'survey.survey'

    category = fields.Selection([('default', 'Generic Survey'),
                                 ('hr_recruitment', 'Recruitment')], string='Category', default='default',
                                help='Category is used to know in which context the survey is used. Various apps may '
                                     'define their own categories when they use survey like jobs recruitment or '
                                     'employee appraisal surveys.')
