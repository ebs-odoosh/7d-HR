from odoo import models, fields, api, _


class ResEmbassy(models.Model):
    _name = 'res.embassy'
    _description = "Embassy of Country"

    name = fields.Char(string="Name", required=True)
    arabic_name = fields.Char(string="Arabic Name")
    country_id = fields.Many2one(string="Country", comodel_name='res.country')

    def name_get(self):
        """
        :Author:Bhavesh Jadav TechUltra Solutions
        :Date:23/09/2020
        :Func:this method use for the add arabic name in name field
        :Return:list with english embassy name and the arabic name
        """
        result = []
        for embassy in self:
            name = embassy.name
            if embassy.arabic_name:
                name = name + ' : ' + embassy.arabic_name
            result.append((embassy.id, name))
        return result
