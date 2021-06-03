# -*- coding: utf-8 -*-
import base64
from datetime import date

from dateutil.relativedelta import relativedelta
from werkzeug.exceptions import NotFound

from odoo import http
from odoo.addons.website_form.controllers.main import WebsiteForm
from odoo.addons.website_hr_recruitment.controllers.main import WebsiteHrRecruitment
from odoo.exceptions import ValidationError
from odoo.http import request
from ..models import hr_applicant


class WebsiteHrRecruitmentInherit(WebsiteHrRecruitment):

    @http.route('''/jobs/apply/<model("hr.job", "[('website_id', 'in', (False, current_website_id))]"):job>''',
                type='http', auth="public", website=True)
    def jobs_apply(self, job, **kwargs):
        if not job.can_access_from_current_website():
            raise NotFound()

        error = {}
        default = {}
        if 'website_hr_recruitment_error' in request.session:
            error = request.session.pop('website_hr_recruitment_error')
            default = request.session.pop('website_hr_recruitment_default')
        states = request.env['res.country.state'].sudo().search([])
        countries = request.env['res.country'].sudo().search([])
        languages_values = request.env['hr.recruitment.language.data'].sudo().search([])
        surname_values = [('mr', 'Mr.'), ('dr', 'Dr.'), ('ms', 'Ms.'), ('mrs', 'Mrs.'), ('miss', 'Miss.')]
        religions_values = hr_applicant.Religions_list
        marital_values = [('single', 'Single'), ('married', 'Married'), ('cohabitant', 'Legal Cohabitant'),
                          ('widower', 'Widower'), ('divorced', 'Divorced')]
        language_levels = [('fluent', 'Fluent'), ('average', 'Average'), ('low', 'Low')]
        questions = request.env['hr.recruitment.questions'].sudo().search([])
        return request.render("website_hr_recruitment.apply", {
            'job': job,
            'states': states,
            'countries': countries,
            'questions': questions,
            'languages_values': languages_values,
            'language_levels': language_levels,
            'surnames': surname_values,
            'religions': religions_values,
            'marital': marital_values,
            'error': error,
            'default': default,
        })


class WebsiteFormInherit(WebsiteForm):
    # Extract all data sent by the form and sort its on several properties
    def extract_data(self, model, values):
        if model.sudo().model == 'hr.applicant':
            dest_model = request.env[model.sudo().model]

            data = {
                'record': {},  # Values to create record
                'attachments': [],  # Attached files
                'custom': '',  # Custom fields values
                'meta': '',  # Add metadata if enabled
            }

            authorized_fields = model.sudo()._get_form_writable_fields()
            error_fields = []
            custom_fields = []

            legal_beneficiary_ids = False
            legal_beneficiary_ids_1 = {}
            legal_beneficiary_ids_2 = {}

            education_ids = False
            education_ids_school = {}
            education_ids_university = {}
            education_ids_training = {}

            language_ids = False
            language_ids_1 = {}
            language_ids_2 = {}
            language_ids_3 = {}
            language_ids_4 = {}

            employment_history_ids = False
            employment_history_ids_1 = {}
            employment_history_ids_2 = {}
            employment_history_ids_3 = {}

            answers_ids = []

            references_ids = False
            references_ids_1 = {}
            references_ids_2 = {}
            for field_name, field_value in values.items():
                if 'notice_period' in field_name:
                    data['record']['availability'] = date.today() + relativedelta(days=int(field_value))

                # If the value of the field if a file
                if hasattr(field_value, 'filename'):
                    # Undo file upload field name indexing
                    field_name = field_name.split('[', 1)[0]

                    # If it's an actual binary field, convert the input file
                    # If it's not, we'll use attachments instead
                    if field_name in authorized_fields and authorized_fields[field_name]['type'] == 'binary':
                        data['record'][field_name] = base64.b64encode(field_value.read())
                        field_value.stream.seek(0)  # do not consume value forever
                        if authorized_fields[field_name]['manual'] and field_name + "_filename" in dest_model:
                            data['record'][field_name + "_filename"] = field_value.filename
                    else:
                        field_value.field_name = field_name
                        data['attachments'].append(field_value)

                # If it's a known field
                elif field_name in authorized_fields:
                    try:
                        input_filter = self._input_filters[authorized_fields[field_name]['type']]
                        data['record'][field_name] = input_filter(self, field_name, field_value)
                    except ValueError:
                        error_fields.append(field_name)
                elif 'surname_id' in field_name:
                    title_obj = request.env['res.partner.title']
                    surname = title_obj.search([('shortcut', '=', field_value)], limit=1)
                    if not surname:
                        surname = title_obj.create({'shortcut': field_value, 'name': field_value})
                    data['record']['surname_id'] = surname.id

                elif 'legal_beneficiary_ids' in field_name:
                    if not legal_beneficiary_ids:
                        legal_beneficiary_ids = True

                    if 'name' in field_name and '0' in field_name:
                        legal_beneficiary_ids_1['name'] = field_value
                    elif 'name' in field_name and '1' in field_name:
                        legal_beneficiary_ids_2['name'] = field_value
                    elif 'relationship' in field_name and '0' in field_name:
                        legal_beneficiary_ids_1['relationship'] = field_value
                    elif 'relationship' in field_name and '1' in field_name:
                        legal_beneficiary_ids_2['relationship'] = field_value
                    elif 'details' in field_name and '0' in field_name:
                        legal_beneficiary_ids_1['details'] = field_value
                    elif 'details' in field_name and '1' in field_name:
                        legal_beneficiary_ids_2['details'] = field_value
                elif 'education_ids' in field_name:
                    if not education_ids:
                        education_ids = True
                    # name
                    if 'name' in field_name and '1' in field_name:
                        education_ids_school['education_place_name'] = field_value
                        education_ids_school['type'] = 'school'
                    elif 'name' in field_name and '2' in field_name:
                        education_ids_university['education_place_name'] = field_value
                        education_ids_university['type'] = 'university'
                    elif 'name' in field_name and '3' in field_name:
                        education_ids_training['education_place_name'] = field_value
                        education_ids_training['type'] = 'training'
                        # date_from
                    elif 'from' in field_name and '1' in field_name:
                        education_ids_school['date_from'] = field_value
                    elif 'from' in field_name and '2' in field_name:
                        education_ids_university['date_from'] = field_value
                    elif 'from' in field_name and '3' in field_name:
                        education_ids_training['date_from'] = field_value
                        # date_to
                    elif 'to' in field_name and '1' in field_name:
                        education_ids_school['date_to'] = field_value
                    elif 'to' in field_name and '2' in field_name:
                        education_ids_university['date_to'] = field_value
                    elif 'to' in field_name and '3' in field_name:
                        education_ids_training['date_to'] = field_value
                elif 'language_ids' in field_name:
                    if not language_ids:
                        language_ids = True
                    # name
                    if 'name' in field_name and '1' in field_name:
                        language_ids_1['language_id'] = int(field_value)
                    elif 'name' in field_name and '2' in field_name:
                        language_ids_2['language_id'] = int(field_value)
                    elif 'name' in field_name and '3' in field_name:
                        language_ids_3['language_id'] = int(field_value)
                    elif 'name' in field_name and '4' in field_name:
                        language_ids_4['language_id'] = int(field_value)
                        # reading
                    elif 'reading' in field_name and '1' in field_name and language_ids_1.get('language_id', False):
                        language_ids_1['reading'] = field_value
                    elif 'reading' in field_name and '2' in field_name and language_ids_2.get('language_id', False):
                        language_ids_2['reading'] = field_value
                    elif 'reading' in field_name and '3' in field_name and language_ids_3.get('language_id', False):
                        language_ids_3['reading'] = field_value
                    elif 'reading' in field_name and '4' in field_name and language_ids_4.get('language_id', False):
                        language_ids_4['reading'] = field_value
                        # writing
                    elif 'writing' in field_name and '1' in field_name and language_ids_1.get('language_id', False):
                        language_ids_1['writing'] = field_value
                    elif 'writing' in field_name and '2' in field_name and language_ids_2.get('language_id', False):
                        language_ids_2['writing'] = field_value
                    elif 'writing' in field_name and '3' in field_name and language_ids_3.get('language_id', False):
                        language_ids_3['writing'] = field_value
                    elif 'writing' in field_name and '4' in field_name and language_ids_4.get('language_id', False):
                        language_ids_4['writing'] = field_value
                        # spoken
                    elif 'spoken' in field_name and '1' in field_name and language_ids_1.get('language_id', False):
                        language_ids_1['spoken'] = field_value
                    elif 'spoken' in field_name and '2' in field_name and language_ids_2.get('language_id', False):
                        language_ids_2['spoken'] = field_value
                    elif 'spoken' in field_name and '3' in field_name and language_ids_3.get('language_id', False):
                        language_ids_3['spoken'] = field_value
                    elif 'spoken' in field_name and '4' in field_name and language_ids_4.get('language_id', False):
                        language_ids_4['spoken'] = field_value
                elif 'employment_history_ids' in field_name:
                    if not employment_history_ids:
                        employment_history_ids = True
                    # company_name
                    if 'company_name' in field_name and '1' in field_name:
                        employment_history_ids_1['company_name'] = field_value
                        employment_history_ids_1['current_job'] = True
                    elif 'company_name' in field_name and '2' in field_name:
                        employment_history_ids_2['company_name'] = field_value
                    elif 'company_name' in field_name and '3' in field_name:
                        employment_history_ids_3['company_name'] = field_value
                        # date_from
                    elif 'from' in field_name and '1' in field_name \
                            and employment_history_ids_1.get('company_name', False):
                        employment_history_ids_1['date_from'] = field_value
                    elif 'from' in field_name and '2' in field_name \
                            and employment_history_ids_2.get('company_name', False):
                        employment_history_ids_2['date_from'] = field_value
                    elif 'from' in field_name and '3' in field_name \
                            and employment_history_ids_3.get('company_name', False):
                        employment_history_ids_3['date_from'] = field_value
                        # date_to
                    elif "['to']" in field_name and '2' in field_name \
                            and employment_history_ids_2.get('company_name', False):
                        employment_history_ids_2['date_to'] = field_value
                    elif "['to']" in field_name and '3' in field_name \
                            and employment_history_ids_3.get('company_name', False):
                        employment_history_ids_3['date_to'] = field_value
                        # type_of_job
                    elif 'type_of_job' in field_name and '1' in field_name \
                            and employment_history_ids_1.get('company_name', False):
                        employment_history_ids_1['type_of_job'] = field_value
                    elif 'type_of_job' in field_name and '2' in field_name \
                            and employment_history_ids_2.get('company_name', False):
                        employment_history_ids_2['type_of_job'] = field_value
                    elif 'type_of_job' in field_name and '3' in field_name \
                            and employment_history_ids_3.get('company_name', False):
                        employment_history_ids_3['type_of_job'] = field_value
                        # reason_for_leaving
                    elif 'reason_for_leaving' in field_name and '1' in field_name \
                            and employment_history_ids_1.get('company_name', False):
                        employment_history_ids_1['reason_for_leaving'] = field_value
                    elif 'reason_for_leaving' in field_name and '2' in field_name \
                            and employment_history_ids_2.get('company_name', False):
                        employment_history_ids_2['reason_for_leaving'] = field_value
                    elif 'reason_for_leaving' in field_name and '3' in field_name \
                            and employment_history_ids_3.get('company_name', False):
                        employment_history_ids_3['reason_for_leaving'] = field_value
                        # street
                    elif 'street' in field_name and '1' in field_name \
                            and employment_history_ids_1.get('company_name', False):
                        employment_history_ids_1['street'] = field_value
                    elif 'street' in field_name and '2' in field_name \
                            and employment_history_ids_2.get('company_name', False):
                        employment_history_ids_2['street'] = field_value
                    elif 'street' in field_name and '3' in field_name \
                            and employment_history_ids_3.get('company_name', False):
                        employment_history_ids_3['street'] = field_value
                        # street2
                    elif 'street2' in field_name and '1' in field_name \
                            and employment_history_ids_1.get('company_name', False):
                        employment_history_ids_1['street2'] = field_value
                    elif 'street2' in field_name and '2' in field_name \
                            and employment_history_ids_2.get('company_name', False):
                        employment_history_ids_2['street2'] = field_value
                    elif 'street2' in field_name and '3' in field_name \
                            and employment_history_ids_3.get('company_name', False):
                        employment_history_ids_3['street2'] = field_value
                        # zip
                    elif 'zip' in field_name and '1' in field_name \
                            and employment_history_ids_1.get('company_name', False):
                        employment_history_ids_1['zip'] = field_value
                    elif 'zip' in field_name and '2' in field_name \
                            and employment_history_ids_2.get('company_name', False):
                        employment_history_ids_2['zip'] = field_value
                    elif 'zip' in field_name and '3' in field_name \
                            and employment_history_ids_3.get('company_name', False):
                        employment_history_ids_3['zip'] = field_value
                        # city
                    elif 'city' in field_name and '1' in field_name \
                            and employment_history_ids_1.get('company_name', False):
                        employment_history_ids_1['city'] = field_value
                    elif 'city' in field_name and '2' in field_name \
                            and employment_history_ids_2.get('company_name', False):
                        employment_history_ids_2['city'] = field_value
                    elif 'city' in field_name and '3' in field_name \
                            and employment_history_ids_3.get('company_name', False):
                        employment_history_ids_3['city'] = field_value
                        # state_id
                    elif 'state_id' in field_name and '1' in field_name \
                            and employment_history_ids_1.get('company_name', False):
                        employment_history_ids_1['state_id'] = field_value
                    elif 'state_id' in field_name and '2' in field_name \
                            and employment_history_ids_2.get('company_name', False):
                        employment_history_ids_2['state_id'] = field_value
                    elif 'state_id' in field_name and '3' in field_name \
                            and employment_history_ids_3.get('company_name', False):
                        employment_history_ids_3['state_id'] = field_value
                        # country_id
                    elif 'country_id' in field_name and '1' in field_name \
                            and employment_history_ids_1.get('company_name', False):
                        employment_history_ids_1['country_id'] = field_value
                    elif 'country_id' in field_name and '2' in field_name \
                            and employment_history_ids_2.get('company_name', False):
                        employment_history_ids_2['country_id'] = field_value
                    elif 'country_id' in field_name and '3' in field_name \
                            and employment_history_ids_3.get('company_name', False):
                        employment_history_ids_3['country_id'] = field_value
                elif 'answer_ids' in field_name:
                    if 'yes_no' in field_name:
                        q_id = int(field_name.replace('answer_ids[', '').replace('][\'yes_no\']', ''))
                        value_name_details = 'answer_ids[' + str(q_id) + '][\'details\']'
                        answers_ids.append((0, 0,
                                            {'question_id': q_id,
                                             'answer': field_value,
                                             'details': values.get(value_name_details, '')}))
                elif 'references_ids' in field_name:
                    if not references_ids:
                        references_ids = True

                    if 'name' in field_name and '1' in field_name:
                        references_ids_1['name'] = field_value
                    elif 'name' in field_name and '2' in field_name:
                        references_ids_2['name'] = field_value

                    if 'position' in field_name and '1' in field_name:
                        references_ids_1['position_held'] = field_value
                    elif 'position' in field_name and '2' in field_name:
                        references_ids_2['position_held'] = field_value

                    if 'email' in field_name and '1' in field_name:
                        references_ids_1['email'] = field_value
                    elif 'email' in field_name and '2' in field_name:
                        references_ids_2['email'] = field_value

                    if 'phone' in field_name and '1' in field_name:
                        references_ids_1['phone'] = field_value
                    elif 'phone' in field_name and '2' in field_name:
                        references_ids_2['phone'] = field_value

                    if 'no_of_years_known' in field_name and '1' in field_name:
                        references_ids_1['no_of_years_known'] = field_value
                        if field_value > 0:
                            references_ids_1['previous_work_exp'] = True
                    elif 'no_of_years_known' in field_name and '2' in field_name:
                        references_ids_2['no_of_years_known'] = field_value
                        if field_value > 0:
                            references_ids_2['previous_work_exp'] = True

                    if 'street' in field_name and '1' in field_name:
                        references_ids_1['street'] = field_value
                    elif 'street' in field_name and '2' in field_name:
                        references_ids_2['street'] = field_value

                    if 'street2' in field_name and '1' in field_name:
                        references_ids_1['street2'] = field_value
                    elif 'street2' in field_name and '2' in field_name:
                        references_ids_2['street2'] = field_value

                    if 'zip' in field_name and '1' in field_name:
                        references_ids_1['zip'] = field_value
                    elif 'zip' in field_name and '2' in field_name:
                        references_ids_2['zip'] = field_value

                    if 'city' in field_name and '1' in field_name:
                        references_ids_1['city'] = field_value
                    elif 'city' in field_name and '2' in field_name:
                        references_ids_2['city'] = field_value

                    if 'state_id' in field_name and '1' in field_name:
                        references_ids_1['state_id'] = field_value
                    elif 'state_id' in field_name and '2' in field_name:
                        references_ids_2['state_id'] = field_value

                    if 'country_id' in field_name and '1' in field_name and references_ids_1.get('name', False):
                        references_ids_1['country_id'] = field_value
                    elif 'country_id' in field_name and '2' in field_name and references_ids_2.get('name', False):
                        references_ids_2['country_id'] = field_value

                    # If it's a custom field
                elif field_name != 'context':
                    custom_fields.append((field_name, field_value))
            if legal_beneficiary_ids:
                data['record']['legal_beneficiary_ids'] = []
                if legal_beneficiary_ids_1:
                    data['record']['legal_beneficiary_ids'].append((0, 0, legal_beneficiary_ids_1))
                if legal_beneficiary_ids_2:
                    data['record']['legal_beneficiary_ids'].append((0, 0, legal_beneficiary_ids_2))
            if education_ids:
                data['record']['education_ids'] = []
                if education_ids_school:
                    data['record']['education_ids'].append((0, 0, education_ids_school))
                if education_ids_university:
                    data['record']['education_ids'].append((0, 0, education_ids_university))
                if education_ids_training:
                    data['record']['education_ids'].append((0, 0, education_ids_training))
            if language_ids:
                data['record']['language_ids'] = []
                if language_ids_1:
                    data['record']['language_ids'].append((0, 0, language_ids_1))
                if language_ids_2:
                    data['record']['language_ids'].append((0, 0, language_ids_2))
                if language_ids_3:
                    data['record']['language_ids'].append((0, 0, language_ids_3))
                if language_ids_4:
                    data['record']['language_ids'].append((0, 0, language_ids_4))
            if employment_history_ids:
                data['record']['employment_history_ids'] = []
                if employment_history_ids_1:
                    data['record']['employment_history_ids'].append((0, 0, employment_history_ids_1))
                if employment_history_ids_2:
                    data['record']['employment_history_ids'].append((0, 0, employment_history_ids_2))
                if employment_history_ids_3:
                    data['record']['employment_history_ids'].append((0, 0, employment_history_ids_3))

            if data['record'].get('employment_gap_date_from'):
                data['record']['employment_gap'] = True

            if answers_ids:
                data['record']['answer_ids'] = answers_ids

            if references_ids:
                data['record']['references_ids'] = []
                if references_ids_1:
                    data['record']['references_ids'].append((0, 0, references_ids_1))
                if references_ids_2:
                    data['record']['references_ids'].append((0, 0, references_ids_2))

            data['custom'] = "\n".join([u"%s : %s" % v for v in custom_fields])

            # Add metadata if enabled
            environ = request.httprequest.headers.environ
            if (request.website.website_form_enable_metadata):
                data['meta'] += "%s : %s\n%s : %s\n%s : %s\n%s : %s\n" % (
                    "IP", environ.get("REMOTE_ADDR"),
                    "USER_AGENT", environ.get("HTTP_USER_AGENT"),
                    "ACCEPT_LANGUAGE", environ.get("HTTP_ACCEPT_LANGUAGE"),
                    "REFERER", environ.get("HTTP_REFERER")
                )

            # This function can be defined on any model to provide
            # a model-specific filtering of the record values
            # Example:
            # def website_form_input_filter(self, values):
            #     values['name'] = '%s\'s Application' % values['partner_name']
            #     return values
            if hasattr(dest_model, "website_form_input_filter"):
                data['record'] = dest_model.website_form_input_filter(request, data['record'])

            missing_required_fields = [label for label, field in authorized_fields.items() if
                                       field['required'] and not label in data['record']]
            if any(error_fields):
                raise ValidationError(error_fields + missing_required_fields)
        else:
            data = super(WebsiteHrRecruitmentInherit).extract_data(model, values)

        return data

    # @http.route('/website_form/<string:model_name>', type='http', auth="public", methods=['POST'], website=True,
    #             csrf=False)
    # def website_form(self, model_name, **kwargs):
    #     # Partial CSRF check, only performed when session is authenticated, as there
    #     # is no real risk for unauthenticated sessions here. It's a common case for
    #     # embedded forms now: SameSite policy rejects the cookies, so the session
    #     # is lost, and the CSRF check fails, breaking the post for no good reason.
    #     csrf_token = request.params.pop('csrf_token', None)
    #     if request.session.uid and not request.validate_csrf(csrf_token):
    #         raise BadRequest('Session expired (invalid CSRF token)')
    #
    #     model_record = request.env['ir.model'].sudo().search(
    #         [('model', '=', model_name), ('website_form_access', '=', True)])
    #     if not model_record:
    #         return json.dumps(False)
    #
    #     try:
    #         data = self.extract_data(model_record, request.params)
    #     # If we encounter an issue while extracting data
    #     except ValidationError as e:
    #         # I couldn't find a cleaner way to pass data to an exception
    #         return json.dumps({'error_fields': e.args[0]})
    #
    #     try:
    #         id_record = self.insert_record(request, model_record, data['record'], data['custom'], data.get('meta'))
    #         if id_record:
    #             self.insert_attachment(model_record, id_record, data['attachments'])
    #             # in case of an email, we want to send it immediately instead of waiting
    #             # for the email queue to process
    #             if model_name == 'mail.mail':
    #                 request.env[model_name].sudo().browse(id_record).send()
    #
    #     # Some fields have additional SQL constraints that we can't check generically
    #     # Ex: crm.lead.probability which is a float between 0 and 1
    #     # TODO: How to get the name of the erroneous field ?
    #     except IntegrityError:
    #         return json.dumps(False)
    #
    #     request.session['form_builder_model_model'] = model_record.model
    #     request.session['form_builder_model'] = model_record.name
    #     request.session['form_builder_id'] = id_record
    #
    #     return json.dumps({'id': id_record})
