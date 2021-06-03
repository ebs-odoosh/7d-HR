# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime

from odoo import fields, models


class SurveyUserInput(models.Model):
    _inherit = 'survey.user_input'

    done_datetime = fields.Datetime('Interview DateTime')
    done_date = fields.Date('Interview Date')
    done_time = fields.Float('Interview Time')

    def _mark_done(self):
        """ Will add done date"""

        super(SurveyUserInput, self)._mark_done()
        for record in self:
            record.done_datetime = datetime.now()
            record.done_date = datetime.now().date()
            record.done_time = (datetime.now() -
                                datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds() / 3600
