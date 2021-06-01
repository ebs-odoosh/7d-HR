from odoo import models, fields, api, _
from odoo.exceptions import Warning


class EducationEligibility(models.Model):
    _name = 'education.eligibility'
    _description = "Eligible For Education Assistance"
    _order = 'id'

    name = fields.Char(string="Name")
    is_uae_nationals = fields.Boolean(string="IS UAE Nationals", default=False)
    number_of_child = fields.Integer(string="Number of Child")
    child_min_age = fields.Integer(string="Minimum Age of Child", default=3)
    child_max_age = fields.Integer(string="Maximum Age of Child", default=18)
    per_child_amount = fields.Monetary(string="Amount Per Child", currency_field='currency_id')
    employee_ids = fields.Many2many('hr.employee', string="Employees", copy=True)
    contract_subgroup = fields.Many2many('hr.contract.subgroup', string="Subgroup", copy=True)
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda self: self.env.company.currency_id, copy=True)
    academic_year_id = fields.Many2one('education.academic.year', string="Academic Year", copy=True)
    exception = fields.Selection(selection=[('no_exception', 'No Exception'), ('exception', 'Exception'),
                                            ('specific_per_child', 'Specific Per Child')],
                                 string="Exception", default='no_exception')
    employee_id = fields.Many2one('hr.employee', string="Employee", copy=True)
    specific_child_education_eligibility_line_ids = fields.One2many('specific.child.education.eligibility',
                                                                    'education_eligibility_id',
                                                                    string="Specific Child Education Eligibility",
                                                                    copy=True)
    job_grades = fields.Many2many('job.grade', string="Job Grades", copy=True)
    note = fields.Text(string="Note")
    valid_from_date = fields.Date(strimg="Valid From")
    valid_to_date = fields.Date(strimg="Valid To")

    @api.model
    def create(self, vals):
        """
        @Author : Nimesh Jadav TechUltra Solutions
        @Date  : 10th March 2021
        @func: Add validations and Auto generated name and  Add restriction for UAEN employee
        (restriction more then 3 children)
        @return: result of supper call
        """
        vals['name'] = self.env['ir.sequence'].next_by_code('education.eligibility') or _('New')
        res = super(EducationEligibility, self).create(vals)
        for request in res:
            if request.exception == 'exception':
                for employee in request.employee_ids:
                    if employee.country_id.code == 'AE' and request.number_of_child > 3:
                        raise Warning('"%s"  should not allow more then 3 children' % employee.name)
        return res
    @api.model
    def write(self, vals):
        """
        @Author : Nimesh Jadav TechUltra Solutions
        @Date  : 10th March 2021
        @func: Add restriction for UAEN employee (restriction more then 3 children)
        @return: result of supper call
        """
        res = super(EducationEligibility, self).write(vals)
        for request in self:
            if request.exception == 'exception':
                for employee in request.employee_ids:
                    if employee.country_id.code == 'AE' and request.number_of_child > 3:
                        raise Warning('"%s"  should not allow more then 3 children' % employee.name)
        return res


class EducationAcademicYear(models.Model):
    _name = 'education.academic.year'
    _description = "Education Academic Year"
    _order = 'id'

    name = fields.Char(string="Name")
    academic_year_start_date = fields.Date(string="Academic Year Start Date")
    academic_year_end_date = fields.Date(string="Academic Year End Date")


class SpecificChildEducationEligibility(models.Model):
    _name = 'specific.child.education.eligibility'
    _description = "Specific Child Education Eligibility"
    _order = 'id'

    name = fields.Char(string="Name")
    child_id = fields.Many2one('res.partner')
    specific_amount_for_child = fields.Monetary(string="Specific Amount For Child")
    education_eligibility_id = fields.Many2one('education.eligibility')
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda self: self.env.company.currency_id)
    employee_id = fields.Many2one('hr.employee', string="Employee", compute='_compute_set_employee')

    @api.depends('education_eligibility_id.employee_id')
    def _compute_set_employee(self):
        """
        :Author:Bhavesh Jadav TechUltra Solutions
        :Date: 10/11/2020
        :Func:This method use for the set employee when the exception is specific_per_child then we need to set employee in line
        """
        for rec in self:
            if rec.education_eligibility_id.exception == 'specific_per_child':
                if rec.education_eligibility_id.employee_id:
                    rec.employee_id = rec.education_eligibility_id.employee_id
                else:
                    rec.employee_id = False
            else:
                rec.employee_id = False

    @api.model
    def create(self, vals):
        """
        @Author : Bhavesh Jadav TechUltra Solutions
        @Date  : 18/11/ 2020
        @func: Add validations and Auto generated name
        @return: result of supper call
        """
        vals['name'] = self.env['ir.sequence'].next_by_code('specific.child.education.eligibility') or _('New')
        res = super(SpecificChildEducationEligibility, self).create(vals)
        return res

    @api.onchange('employee_id')
    def onchange_child_id(self):
        """
        @Author : Bhavesh Jadav TechUltra Solutions
        @Date  : 18/11/ 2020
        @Func:this method use for the add dynamic domain because we need to show only there employee child ids
        """
        if self.education_eligibility_id.employee_id.dependents:
            contact_relation_types = self.env['contact.relation.type'].search(
                [('name', 'in', ['Son', 'Child', 'Daughter', 'SON', 'CHILD', 'DAUGHTER', 'son', 'child', 'daughter'])])
            children = self.env['res.partner']
            ids = self.education_eligibility_id and self.education_eligibility_id.specific_child_education_eligibility_line_ids and self.education_eligibility_id.specific_child_education_eligibility_line_ids.child_id.ids
            children = self.education_eligibility_id.employee_id.dependents.filtered(
                lambda x: x.contact_relation_type_id.id in contact_relation_types.ids and x.state == 'approved')
            return {'domain': {'child_id': [('id', 'in', children.ids), ('id', 'not in', ids)]}}
        else:
            return {'domain': {'child_id': [('id', '=', False)]}}
