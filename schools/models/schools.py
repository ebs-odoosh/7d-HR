# -*- coding: utf-8 -*-

from odoo import models, fields


class Schools(models.Model):
    _name = 'schools'
    _description = 'Schools'

    name = fields.Char(string="School")
