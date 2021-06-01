from odoo import models, fields, api, _


class ResponsibleReportPerson(models.Model):
    _name = 'responsible.report.person'
    _description = "Responsible Person For letters "

    person_name_eng = fields.Char(string="Responsible Person English")
    person_name_arab = fields.Char(string="Responsible Person Arabic")
    person_position_eng = fields.Char(string="Position English")
    person_position_arab = fields.Char(string="Position Arabic")
    person_signature = fields.Binary("Signature")
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)

    def name_get(self):
        """
        :Author:Bhavesh Jadav TechUltra Solutions
        :Date:23/09/2020
        :Func:this method use for the add person_name_eng name in name field
        :Return:list with name
        """
        result = []
        for responsible_person in self:
            name = responsible_person.person_name_eng
            # + ' : ' + responsible_person.person_name_arab
            result.append((responsible_person.id, name))
        return result
