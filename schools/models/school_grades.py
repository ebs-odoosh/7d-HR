# -*- coding: utf-8 -*-

from odoo import models, fields


class SchoolGrades(models.Model):
    _name = 'school.grades'
    _description = 'School Grades'
    _rec_name = 'code'

    code = fields.Char(string="Grade", required=1)
    name = fields.Char(string="Grade Name")
