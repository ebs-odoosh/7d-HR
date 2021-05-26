# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
from odoo import api, exceptions, fields, models, _
from odoo.exceptions import UserError, ValidationError

# sh. Effect  object
class ShEffect(models.Model):
    _name = 'sh.effect.model'
    
    name = fields.Char(string='Name',required=True)

