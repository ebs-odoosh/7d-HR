from odoo import models, fields, api, _


class ResBank(models.Model):
    _inherit = 'res.bank'
    arabic_bank_name = fields.Char(string="Arabic Name")

    def name_get(self):
        """
        :Author:Bhavesh Jadav TechUltra Solutions
        :Date:23/09/2020
        :Func:this method use for the add arabic name in name field
        :Return:list with english bank name and the arabic name
        """
        result = []
        for bank in self:
            name = bank.name
            if bank.arabic_bank_name:
                name = name + ' : ' + bank.arabic_bank_name
            result.append((bank.id, name))
        return result
