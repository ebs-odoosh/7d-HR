from odoo import models, fields, api, _


class ResOtherEntities(models.Model):
    _name = 'res.other.entities'
    _description = "Other Entities"

    name = fields.Char(string="Name", required=True)
    arabic_name = fields.Char(string="Arabic Name")
    note = fields.Text(string='Note')

    def name_get(self):
        """
        :Author:Bhavesh Jadav TechUltra Solutions
        :Date:23/09/2020
        :Func:this method use for the add arabic name in name field
        :Return:list with english embassy name and the arabic name
        """
        result = []
        for entity in self:
            name = entity.name
            if entity.arabic_name:
                name = name + ' : ' + entity.arabic_name
            result.append((entity.id, name))
        return result
