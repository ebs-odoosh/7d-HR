# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import uuid


class SurveyUserInputExt(models.Model):
    _inherit = "survey.user_input"

    @api.model
    def _generate_invite_token(self):
        return str(uuid.uuid4())