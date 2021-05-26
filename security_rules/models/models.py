# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class security_rules(models.Model):
#     _name = 'security_rules.security_rules'
#     _description = 'security_rules.security_rules'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
