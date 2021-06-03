# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from dateutil.relativedelta import relativedelta

from odoo import fields, models, api, _
from odoo.exceptions import UserError

Religions_list = [
    ('apostolic', 'Apostolic'),
    ('baptist', 'Baptist'),
    ('buddhist', 'Buddhist'),
    ('charismatic', 'Charismatic'),
    ('evang', 'Evang'),
    ('lutheran-church', 'Lutheran Church'),
    ('evangelical', 'Evangelical'),
    ('free-church-alzey', 'Free church Alzey'),
    ('free-religion-of-the-den', 'Free religion of the den'),
    ('french-reformed', 'French reformed'),
    ('hebrew-reg-baden', 'Hebrew reg. BADEN'),
    ('hebrew-reg-wuertbg', 'Hebrew reg. WUERTBG'),
    ('hebrew-state', 'Hebrew state'),
    ('hindu', 'Hindu'),
    ('islamic', 'Islamic'),
    ('israelite', 'Israelite'),
    ("jehovah-s-witness", "Jehovah's witness"),
    ('mennonite-church', 'Mennonite Church'),
    ('jewish', 'Jewish'),
    ('mennonite-church', 'Mennonite Church'),
    ('mormon', 'Mormon'),
    ('moravian-congregation', 'Moravian Congregation'),
    ('muslim', 'Muslim'),
    ('netherl', 'Netherl'),
    ('netherl-reformed-church', 'Netherl. Reformed Church'),
    ('new-apostolic', 'New apostolic'),
    ('no-denomination', 'No denomination'),
    ('old-catholic', 'Old Catholic'),
    ('oecumenic', 'Oecumenic'),
    ('protestant', 'Protestant'),
    ('roman-catholic', 'Roman Catholic'),
    ("shia-muslim", "Shi'a Muslim"),
    ('sunni-muslim', 'Sunni Muslim'),
    ('christian', 'Christian'),
    ('christian-reformed', 'Christian Reformed'),
]


class HRApplicant(models.Model):
    _inherit = 'hr.applicant'

    @api.depends('date_of_birth')
    def _compute_age(self):
        for record in self:
            if record.date_of_birth:
                today = fields.Date.context_today(self)
                birth_date = record.date_of_birth

                record.age = today.year - birth_date.year - (
                        (today.month, today.day) < (birth_date.month, birth_date.day))
            else:
                record.age = 0

    @api.depends('job_id', 'partner_name')
    def _compute_name(self):
        for record in self:
            if record.partner_name and record.job_id.name:
                record.name = record.partner_name + ' is applied for ' + record.job_id.name
            elif record.partner_name:
                record.name = record.partner_name
            elif record.job_id.name:
                record.name = record.job_id.name
            else:
                record.name = 'New Application'

    name = fields.Char("Subject / Application Name", required=True, readonly=True,
                       help="Email subject for applications sent via email", compute='_compute_name')
    surname_id = fields.Many2one('res.partner.title', string='Title', required=True)
    former_name = fields.Char('Former name(s) / Maiden Name')
    partner_name = fields.Char("Applicant's Name", required=True)
    business_no = fields.Char("Business No.", size=32)
    passport_number = fields.Char("Passport Number")
    expiry_date = fields.Date("Expiry Date")
    nationality_id_no = fields.Char("National Identity Number (CPR)")
    place_of_birth = fields.Many2one('res.country', string='Place Of Birth')
    age = fields.Integer('Age', compute='_compute_age')
    spouse_name = fields.Char('Spouse Name')
    spouse_employment_status = fields.Char('Spouse\'s Employment Status')
    religion = fields.Selection(Religions_list, 'Religions')
    no_of_children = fields.Integer('No. of Children')
    next_of_kin_name = fields.Char('Next of Kin')
    next_of_kin_relationship = fields.Char('RelationShip')
    legal_beneficiary_ids = fields.One2many('legal.beneficiary', 'application_id', 'Legal Beneficiary')
    education_ids = fields.One2many('hr.recruitment.education.history', 'application_id', 'Education')
    language_ids = fields.One2many('hr.recruitment.language', 'application_id', 'Languages')
    employment_history_ids = fields.One2many('hr.recruitment.employment.history', 'application_id',
                                             'Employment History')
    answer_ids = fields.One2many('hr.recruitment.answers', 'application_id', string='Questions')
    references_ids = fields.One2many('hr.recruitment.references', 'application_id', string='References')
    employment_gap = fields.Boolean('Employment Gap')
    employment_gap_date_from = fields.Date(string='Employment Gap Date From')
    employment_gap_date_to = fields.Date(string='Employment Gap Date To')
    employment_gap_reason = fields.Text(string='Employment Gap Description')
    # Address fields
    street = fields.Char('Street')
    street2 = fields.Char('Street2')
    zip = fields.Char('Zip')
    city = fields.Char('City')
    state_id = fields.Many2one("res.country.state", string='State', domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one('res.country', string='Country')
    # Address of kin fields
    next_of_kin_street = fields.Char('Street')
    next_of_kin_street2 = fields.Char('Street2')
    next_of_kin_zip = fields.Char('Zip')
    next_of_kin_city = fields.Char('City')
    next_of_kin_state_id = fields.Many2one("res.country.state", string='State',
                                           domain="[('country_id', '=?', country_id)]")
    next_of_kin_country_id = fields.Many2one('res.country', string='Country')
    response_count = fields.Integer(compute="_get_response_count")
    availability = fields.Date("Effective Start Date",
                               help="The date at which the applicant will be available to start working",
                               default=fields.Date.context_today)

    @api.depends('response_ids')
    def _get_response_count(self):
        for record in self:
            record.response_count = len(record.response_ids)

    @api.model
    def default_get(self, fields):
        res = super(HRApplicant, self).default_get(fields)

        questions = self.env['hr.recruitment.questions'].search([])
        app_questions = [(5, 0, 0)]
        if questions:
            for question in questions:
                app_questions.append((0, 0, {
                    'question_id': question.id,
                    'answer': 'no',
                }))
        res.update({
            'answer_ids': app_questions
        })
        return res

    @api.onchange('related_children')
    def _onchange_related_children(self):
        for record in self:
            record.no_of_children = len(record.related_children)

    @api.onchange('notice_period')
    def _onchange_notice_period(self):
        for record in self:
            record.availability = fields.Date.context_today(self) + relativedelta(days=record.notice_period)

    @api.onchange('employment_history_ids')
    def _onchange_employment_history_ids(self):
        for record in self:
            record.total_years_of_exp = int(sum(record.employment_history_ids.mapped('years_of_exp')))

    def create_employee_from_applicant(self):
        """ Create an hr.employee from the hr.applicants """
        employee = False
        for applicant in self:
            contact_name = False
            if applicant.partner_id:
                address_id = applicant.partner_id.address_get(['contact'])['contact']
                contact_name = applicant.partner_id.display_name
            else:
                if not applicant.partner_name:
                    raise UserError(_('You must define a Contact Name for this applicant.'))
            if applicant.partner_name or contact_name:
                running_contract = applicant.proposed_contracts.filtered(lambda x: x.state == 'open')
                name_split = applicant.partner_name.split()
                firstname = ""
                middlename = ""
                lastname = ""
                if len(name_split) >= 3:
                    firstname = name_split[0]
                    middlename = name_split[1]
                    lastname = " ".join(x for x in name_split[2:])
                elif len(name_split) == 2:
                    firstname = name_split[0]
                    lastname = name_split[1]
                else:
                    firstname = name_split[0]
                employee = self.env['hr.employee'].create({
                    'title': applicant.surname_id.id,
                    'company_id': applicant.company_id.id,
                    'name': applicant.partner_name or contact_name,
                    'firstname': firstname,
                    'middlename': middlename,
                    'lastname': lastname,
                    'phone': applicant.partner_phone or applicant.partner_mobile,
                    'birthday': applicant.date_of_birth,
                    'country_of_birth': applicant.nationality.id,
                    'marital': applicant.marital_status,
                    'work_email': applicant.department_id and applicant.department_id.company_id
                                  and applicant.department_id.company_id.email or False,
                    'work_phone': applicant.department_id and applicant.department_id.company_id
                                  and applicant.department_id.company_id.phone or False,
                    'department_id': applicant.job_id.department_id.id,
                    'parent_id': applicant.job_id.default_manager.id,
                    'job_id': applicant.job_id.id
                })
                applicant.write({'emp_id': employee.id})
                if running_contract:
                    running_contract.write({
                        'employee_id': employee.id,
                    })
                    running_contract._assign_open_contract()
                if applicant.job_id:
                    applicant.job_id.write({'no_of_hired_employee': applicant.job_id.no_of_hired_employee + 1})
                    applicant.job_id.message_post(
                        body=_(
                            'New Employee %s Hired') % applicant.partner_name if applicant.partner_name else applicant.name,
                        subtype="hr_recruitment.mt_job_applicant_hired")
                applicant.message_post_with_view(
                    'hr_recruitment.applicant_hired_template',
                    values={'applicant': applicant},
                    subtype_id=self.env.ref("hr_recruitment.mt_applicant_hired").id)

        employee_action = self.env.ref('hr.open_view_employee_list')
        dict_act_window = employee_action.read([])[0]
        dict_act_window['context'] = {'form_view_initial_mode': 'edit'}
        dict_act_window['res_id'] = employee.id
        return dict_act_window

    def _get_contract_values(self):
        values = {
            'group': self.job_id.group.id,
            'department': self.job_id.department_id.id,
            'section': self.job_id.section.id,
            'subsection': self.job_id.subsection.id,
            'department_id': self.job_id.subsection.id if self.job_id.subsection.id else (
                self.job_id.section.id if self.job_id.section.id else (
                    self.job_id.department_id.id if self.job_id.department_id.id else (
                        self.job_id.group.id if self.job_id.group.id else False))),
            'job_id': self.job_id.id,
            'applicant_id': self.id,
            # 'wage': self.salary_expected + int(self.salary_expected_extra),
            'date_start': self.availability,
            'cost_center': self.job_id.cost_center.id or False,
            'company_id': self.company_id.id,
            'manager_id': self.job_id.default_manager.id or False,
            'employee_id': self.emp_id.id or False
        }
        return values
