# -*- coding: utf-8 -*-

from odoo import api, fields, models, SUPERUSER_ID


class HrJobExt(models.Model):
    _inherit = "hr.job"

    @api.model
    def create(self, vals):
        default_signatures = self.env['hr.job.default.signature'].search([])

        signatures_vals = []
        for signature in default_signatures:
            signatures_vals.append((0, 0, {'sequence': signature.sequence, 'name': signature.name.id}))

        if signatures_vals:
            vals.update({'required_signatures': signatures_vals})

        return super(HrJobExt, self).create(vals)
