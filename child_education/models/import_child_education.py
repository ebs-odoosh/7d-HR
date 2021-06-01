# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime
import base64
import logging
import csv
from io import StringIO, BytesIO

from odoo.addons import test_limits
from odoo.exceptions import Warning
from odoo.modules.module import get_module_resource

_logger = logging.getLogger(__name__)


class ImportChildEducation(models.Model):
    _name = 'import.child.education'
    _description = 'Import Child Education'

    choose_file = fields.Binary('Choose File', required=True)
    datas = fields.Binary('File')
    file_name = fields.Char('File Name')
    date = fields.Datetime('Date', default=fields.Datetime.now)
    name = fields.Char(string='Name')
    state = fields.Selection([
        ('pending', 'Pending '),
        ('done', 'Done'),
    ], string='Status', copy=False, default='pending')
    log_line_ids = fields.One2many('import.child.education.log.line', 'import_log_id', string='Log Lines')

    attachment_path = fields.Char(string="Attachment Path")

    @api.model
    def create(self, vals):
        """
        set name through sequence while creating log record
        :param vals:
        :return:
        """
        vals['name'] = self.env.ref('child_education.seq_child_education_import_log').next_by_id() or 'New'
        result = super(ImportChildEducation, self).create(vals)
        return result

    def import_child_education_data(self):
        """
        Import Data from the csv
        :return:
        """

        if not self.choose_file:
            raise Warning("File Not Found To Import")
        if self.file_name and self.file_name[-3:] != 'csv':
            raise Warning("Please Provide Only .csv File to Import !!!")

        self.write({'datas': self.choose_file})
        self._cr.commit()
        import_file = BytesIO(base64.decodestring(self.datas))
        csvf = StringIO(import_file.read().decode())
        reader = csv.DictReader(csvf, delimiter=',')
        data = []
        for line in reader:
            data.append(line)

        if data:
            keys = []
            header_data = data[0]
            for key, value in header_data.items():
                keys.append(key)

            headers = ['Employee', 'Employee No', 'Claim Number', 'Claim Date', 'Request Status', 'Request Approver',
                       'Academic Year', 'Eligibility Rule', 'Children Lines/Eligibility Amount',
                       'Children Lines/Approved Amount', 'Children Lines/Balance Amount',
                       'Children Lines/Total Claimed Amount', 'Children Lines/Child', 'Children Lines/Date Of Birth',
                       'Children Lines/Child Age', 'Children Lines/School', 'Children Lines/School Grade',
                       'Children Lines/Reference Date', 'Children Lines/Reference No', 'Children Lines/Documents',
                       'Children Lines/Check Number',
                       'Children Lines/Terms Fees/Name', 'Children Lines/Terms Fees/Terms and Fees',
                       'Children Lines/Terms Fees/Approve Amount', 'Children Lines/Terms Fees/Claimed Amount',
                       'Children Lines/Terms Fees/Paid To']
            for header in headers:
                if header not in keys:
                    raise Warning(
                        "File Header is not correct you have to give this file headers :"
                        "'Employee', 'Employee No', 'Claim Number', 'Claim Date', 'Request Status', 'Request Approver',"
                        "'Academic Year', 'Eligibility Rule', 'Children Lines/Eligibility Amount',"
                        "'Children Lines/Approved Amount', 'Children Lines/Balance Amount',"
                        "'Children Lines/Total Claimed Amount', 'Children Lines/Child', 'Children Lines/Date Of Birth',"
                        "'Children Lines/Child Age', 'Children Lines/School', 'Children Lines/School Grade',"
                        "'Children Lines/Reference Date', 'Children Lines/Reference No', 'Children Lines/Documents', 'Children Lines/Check Number',"
                        "'Children Lines/Terms Fees/Name', 'Children Lines/Terms Fees/Terms and Fees',"
                        "'Children Lines/Terms Fees/Approve Amount', 'Children Lines/Terms Fees/Claimed Amount'"
                        "Children Lines/Terms Fees/Paid To")
            self.do_import_child_education_data(data)
            education_request = self.env['education.request']
            for education in education_request:
                for request_line in education.request_lines:
                    request_line.sudo()._compute_request_approved_amount()
                    request_line.sudo()._compute_total_approved_amount()
                    request_line.sudo()._compute_request_claimed_amount()

            return {'effect': {'fadeout': 'slow',
                               'message': "Yeah %s, It's Done,"
                                          "You can check import logs for further details."
                                          % self.env.user.name,
                               'img_url': '/web/static/src/img/smile.svg', 'type': 'rainbow_man'
                               }
                    }

    def do_import_child_education_data(self, data):
        """
        Import data Child Education data"
        :param data: dict of data
        :return:
        """
        if data:
            line_no = 1
            try:
                for row in data:
                    line_no += 1
                    employee_id = row.get('Employee')
                    if employee_id != '':
                        employee_no = row.get('Employee No')
                        claim_number = row.get('Claim Number')
                        claim_date = row.get('Claim Date')
                        claim_date = self.date_replace(claim_date)
                        request_status = row.get('Request Status')
                        request_approval = row.get('Request Approver')
                        academic_year = row.get('Academic Year')
                        eligibility_rule = row.get('Eligibility Rule')
                        eligibility_amount = float(row.get('Children Lines/Eligibility Amount')) if row.get(
                            'Children Lines/Eligibility Amount') else 0.0
                        approved_amount = float(row.get('Children Lines/Approved Amount')) if row.get(
                            'Children Lines/Approved Amount') else 0.0
                        balance_amount = float(row.get('Children Lines/Balance Amount')) if row.get(
                            'Children Lines/Balance Amount') else 0.0
                        total_claimed_amount = float(row.get('Children Lines/Total Claimed Amount')) if row.get(
                            'Children Lines/Total Claimed Amount') else 0.0
                        child_name = row.get('Children Lines/Child')
                        date_of_birth = row.get('Children Lines/Date Of Birth')
                        date_of_birth = self.date_replace(date_of_birth)
                        child_age = row.get('Children Lines/Child Age')
                        school = row.get('Children Lines/School')
                        school_grade = row.get('Children Lines/School Grade')
                        reference_date = row.get('Children Lines/Reference Date')
                        reference_date = self.date_replace(reference_date)
                        reference_no = row.get('Children Lines/Reference No')
                        documents = row.get('Children Lines/Documents')
                        cheque_number = row.get('Children Lines/Check Number')
                        terms_fees_name = row.get('Children Lines/Terms Fees/Name')
                        terms_fees = row.get('Children Lines/Terms Fees/Terms and Fees')
                        fees_approved_amount = float(row.get('Children Lines/Terms Fees/Approve Amount')) if row.get(
                            'Children Lines/Terms Fees/Approve Amount') else 0.0
                        fees_claimed_amount = float(row.get('Children Lines/Terms Fees/Claimed Amount')) if row.get(
                            'Children Lines/Terms Fees/Claimed Amount') else 0.0
                        paid_to = row.get('Children Lines/Terms Fees/Paid To')

                        strata_id = self.env['hr.employee'].search([('strata_id', '=', employee_no)])
                        if not strata_id:
                            val = {
                                'import_log_id': self.id,
                                'line_no': int(line_no),
                                'message': "Strata Id %s not found for any employee" % employee_no
                            }
                            self.env['import.child.education.log.line'].create(val)
                        else:
                            if documents:
                                documents = self.get_create_attachments(self.attachment_path, documents, line_no)
                            academic_year = self.env['education.academic.year'].search(
                                [('name', '=', academic_year)], limit=1)
                            education_id = self.env['education.request'].search(
                                [('claim_date', '=', claim_date), ('academic_year', '=', academic_year.id),
                                 ('employee_id', '=', strata_id.id)], limit=1)
                            if education_id:
                                child_id = self.env['res.partner'].search(
                                    [('name', '=', child_name), ('related_employee', '=', strata_id.id)], limit=1)
                                request_line_id = self.env['education.request.line'].search(
                                    [('education_request_id', '=', education_id.id),
                                     ('employee_id', '=', strata_id.id), ('child_id', '=', child_id.id)])
                                if request_line_id:
                                    fees_terms = self.env['education.terms.fees.line'].search(
                                        [('name', '=', terms_fees_name)])
                                    if fees_terms:
                                        if fees_terms:
                                            val = {
                                                'import_log_id': self.id,
                                                'line_no': int(line_no),
                                                'message': "terms fees already available : %s, Line no %d" % (
                                                    fees_terms, line_no)
                                            }
                                            self.env['import.child.education.log.line'].create(val)
                                    else:
                                        s_terms_fees = self.env['school.terms.fees'].search(
                                            [('name', '=', terms_fees)])
                                        if not s_terms_fees:
                                            s_terms_fees = s_terms_fees.create({'name': terms_fees})
                                            val = {
                                                'import_log_id': self.id,
                                                'line_no': int(line_no),
                                                'message': "School terms fees created : %s, Line no %d" % (
                                                    terms_fees_name, line_no)
                                            }
                                            self.env['import.child.education.log.line'].create(val)
                                        if s_terms_fees:
                                            terms_fees_val = {'name': terms_fees_name or '',
                                                              'school_terms_fees': s_terms_fees.id if s_terms_fees else False,
                                                              'claimed_amount': fees_claimed_amount,
                                                              'approve_amount': fees_approved_amount,
                                                              'paid_to': self.replace_paid_to(paid_to)}
                                            fees_terms = self.env['education.terms.fees.line'].create(terms_fees_val)
                                            school = self.env['schools'].search([('name', '=', school)], limit=1)
                                            school_grade = self.env['school.grades'].search(
                                                [('code', '=', school_grade)], limit=1)
                                            request_line_id.write({'child_birthdate': date_of_birth or '',
                                                                   'child_age': int(child_age) if child_age else '',
                                                                   'school': school.id if school else False,
                                                                   'school_grade': school_grade.id if school_grade else False,
                                                                   'reference_no': reference_no or '',
                                                                   'reference_date': reference_date or '',
                                                                   'total_claimed_amount': total_claimed_amount or 0,
                                                                   'eligibility_amount': eligibility_amount or 0,
                                                                   'education_request_id': education_id.id if education_id else False,
                                                                   'total_approved_amount': approved_amount or 0,
                                                                   'balance_amount': balance_amount or 0,
                                                                   'employee_id': strata_id.id if strata_id else False,
                                                                   # 'cheque_number': cheque_number or '',
                                                                   'attachment_ids': documents if documents else False,
                                                                   'terms_fees_line_ids': fees_terms if fees_terms else False, })
                                            val = {
                                                'import_log_id': self.id,
                                                'line_no': int(line_no),
                                                'message': "Child record updated : %s, Line no %d" % (
                                                    child_name, line_no)
                                            }
                                            self.env['import.child.education.log.line'].create(val)
                                else:
                                    fees_terms = self.env['education.terms.fees.line'].search(
                                        [('name', '=', terms_fees_name)])
                                    if fees_terms:
                                        if fees_terms:
                                            val = {
                                                'import_log_id': self.id,
                                                'line_no': int(line_no),
                                                'message': "terms fees already available : %s, Line no %d" % (
                                                    fees_terms, line_no)
                                            }
                                            self.env['import.child.education.log.line'].create(val)
                                    else:
                                        s_terms_fees = self.env['school.terms.fees'].search(
                                            [('name', '=', terms_fees)])
                                        if not s_terms_fees:
                                            s_terms_fees = s_terms_fees.create({'name': terms_fees})
                                            val = {
                                                'import_log_id': self.id,
                                                'line_no': int(line_no),
                                                'message': "School terms fees created : %s, Line no %d" % (
                                                    terms_fees_name, line_no)
                                            }
                                            self.env['import.child.education.log.line'].create(val)
                                        if s_terms_fees:
                                            terms_fees_val = {'name': terms_fees_name or '',
                                                              'school_terms_fees': s_terms_fees.id if s_terms_fees else False,
                                                              'claimed_amount': fees_claimed_amount or 0,
                                                              'approve_amount': fees_approved_amount or 0,
                                                              'paid_to': self.replace_paid_to(paid_to)}
                                            fees_terms = self.env['education.terms.fees.line'].create(terms_fees_val)
                                    child_id = self.env['res.partner'].search(
                                        [('name', '=', child_name), ('related_employee', '=', strata_id.id)], limit=1)
                                    school = self.env['schools'].search([('name', '=', school)], limit=1)
                                    school_grade = self.env['school.grades'].search([('code', '=', school_grade)],
                                                                                    limit=1)
                                    request_line_val = {'child_id': child_id.id if child_id else False,
                                                        'child_birthdate': date_of_birth or '',
                                                        'child_age': int(child_age) if child_age else '',
                                                        'school': school.id if school else False,
                                                        'school_grade': school_grade.id if school_grade else False,
                                                        'reference_no': reference_no or '',
                                                        'reference_date': reference_date or '',
                                                        'total_claimed_amount': total_claimed_amount or 0,
                                                        'eligibility_amount': eligibility_amount or 0,
                                                        'education_request_id': education_id.id if education_id else False,
                                                        'total_approved_amount': approved_amount or 0,
                                                        'balance_amount': balance_amount or 0,
                                                        'employee_id': strata_id.id if strata_id else False,
                                                        # 'cheque_number': cheque_number or '',
                                                        'attachment_ids': documents if documents else False,
                                                        'terms_fees_line_ids': fees_terms if fees_terms else False,
                                                        }
                                    request_line_id = self.env['education.request.line'].create(request_line_val)
                                    if request_line_id:
                                        val = {
                                            'import_log_id': self.id,
                                            'line_no': int(line_no),
                                            'message': "Child record created : %s, Line no %d" % (
                                                child_name, line_no)
                                        }
                                        self.env['import.child.education.log.line'].create(val)
                            else:
                                s_terms_fees = self.env['school.terms.fees'].search(
                                    [('name', '=', terms_fees)])
                                if not s_terms_fees:
                                    s_terms_fees = s_terms_fees.create({'name': terms_fees})
                                    val = {
                                        'import_log_id': self.id,
                                        'line_no': int(line_no),
                                        'message': "School terms fees created : %s, Line no %d" % (
                                            terms_fees_name, line_no)
                                    }
                                    self.env['import.child.education.log.line'].create(val)
                                if s_terms_fees:
                                    terms_fees_val = {'name': terms_fees_name or '',
                                                      'school_terms_fees': s_terms_fees.id if s_terms_fees else False,
                                                      'claimed_amount': fees_claimed_amount or 0,
                                                      'approve_amount': fees_approved_amount or 0,
                                                      'paid_to': self.replace_paid_to(paid_to)}
                                    fees_terms = self.env['education.terms.fees.line'].create(terms_fees_val)
                                child_id = self.env['res.partner'].search(
                                    [('name', '=', child_name), ('related_employee', '=', strata_id.id)], limit=1)
                                school = self.env['schools'].search([('name', '=', school)], limit=1)
                                school_grade = self.env['school.grades'].search([('name', '=', school_grade)], limit=1)
                                request_line_val = {'child_id': child_id.id if child_id else False,
                                                    'child_birthdate': date_of_birth or '',
                                                    'child_age': int(child_age) if child_age else '',
                                                    'school': school.id if school else False,
                                                    'school_grade': school_grade.id if school_grade else False,
                                                    'reference_no': reference_no or '',
                                                    'reference_date': reference_date or '',
                                                    'total_claimed_amount': total_claimed_amount or 0,
                                                    'eligibility_amount': eligibility_amount or 0,
                                                    'total_approved_amount': approved_amount or 0,
                                                    'balance_amount': balance_amount or 0,
                                                    'employee_id': strata_id.id if strata_id else False,
                                                    # 'cheque_number': cheque_number or '',
                                                    'attachment_ids': documents if documents else False,
                                                    'terms_fees_line_ids': fees_terms if fees_terms else False,
                                                    }
                                request_line_id = self.env['education.request.line'].create(request_line_val)
                                # academic_year = self.env['education.academic.year'].search(
                                #     [('name', '=', academic_year)])
                                request_approval = self.env['res.users'].search([('name', '=', request_approval)],
                                                                                limit=1)
                                eligibility_rule = self.env['education.eligibility'].search(
                                    [('name', '=', eligibility_rule)], limit=1)

                                education_val = {'request_lines': request_line_id.ids if request_line_id else False,
                                                 'employee_id': strata_id.id if strata_id else False,
                                                 'employee_no': employee_no or '',
                                                 'academic_year': academic_year.id if academic_year else False,
                                                 'request_owner_id': strata_id.user_id.id if strata_id else False,
                                                 'claim_date': claim_date or '',
                                                 'claim_number': claim_number or '',
                                                 'request_status': self.replace_status(request_status) or '',
                                                 'education_eligibility_id': eligibility_rule.id if eligibility_rule else False,
                                                 'request_approver': request_approval.id if request_approval else False,
                                                 'is_hc_approved': True
                                                 }
                                if strata_id[0]:
                                    e_rec = self.env['education.request'].sudo().create(education_val)
                                    if e_rec:
                                        approver = self.env['res.users'].search([('name', '=', request_approval.name)])
                                        if approver:
                                            approver = e_rec.approver_ids.sudo().create({'user_id': approver.id,
                                                                                         'status': self.replace_status(
                                                                                             request_status) or ''})
                                            e_rec.write({'approver_ids': approver.ids})
                                            e_rec.sudo()._compute_request_status()
                                            self.compute_eligibility_rule(e_rec)
                                            # for request_line in e_rec.request_lines:
                                            #     request_line.sudo()._compute_request_approved_amount()
                                            #     request_line.sudo()._compute_total_approved_amount()
                                            #     request_line.sudo()._compute_request_claimed_amount()
                                    log_val = {
                                        'import_log_id': self.id,
                                        'line_no': int(line_no),
                                        'message': "Record Created with Strata id %s, Line no %d" % (
                                            employee_id, line_no)
                                    }
                                    self.env['import.child.education.log.line'].create(log_val)
                            if education_id:
                                approver = self.env['res.users'].search([('name', '=', request_approval)])
                                if approver:
                                    approver = education_id.approver_ids.sudo().create(
                                        {'user_id': approver.id, 'status': self.replace_status(request_status) or ''})
                                    education_id.write({'approver_ids': approver.ids, 'is_hc_approved': True})
                                    education_id.sudo()._compute_request_status()
                                    self.compute_eligibility_rule(education_id)
                                    # for request_line in education_id.request_lines:
                                    #     request_line.sudo()._compute_request_approved_amount()
                                    #     request_line.sudo()._compute_total_approved_amount()
                                    #     request_line.sudo()._compute_request_claimed_amount()
                            self.env.cr.commit()
            except Exception as e:
                log_val = {
                    'import_log_id': self.id,
                    'line_no': int(line_no),
                    'message': 'Error: %s' % e
                }
                self.env['import.child.education.log.line'].create(log_val)
                _logger.info(e)
                return False

    @api.model
    def get_create_attachments(self, attachment_path, name, line_no):
        """
        Author:Nimesh Jadav TechUltra solutions
        Date:  18th March 2021
        Func: get attachment path and create attachments
        :return: attachment else False
        """
        file_path = get_module_resource('child_education', attachment_path, name)
        if not file_path:
            val = {
                'import_log_id': self.id,
                'line_no': int(line_no),
                # 'message': 'Attachment not found in directory: %s' % attachments_id_val
                'message': 'Attachment: %s not found in directory' % file_path
            }
            self.env['import.child.education.log.line'].create(val)
        else:
            pdf_file = open(file_path, 'rb')
            pdf_file_encode = base64.b64encode(pdf_file.read())
            if pdf_file_encode:
                attachment = self.env['ir.attachment'].create({
                    'name': name,
                    'type': 'binary',
                    'datas': pdf_file_encode,
                    'res_model': 'approval.request',
                    'res_id': self.id
                })

                return attachment
            else:
                return False

    @api.model
    def replace_status(self, status):
        """
        Author:Nimesh Jadav TechUltra solutions
        Date:  18th March 2021
        Func: get status key(Selection filed)
        :return: key
        """
        if status == "SAVED (DRAFT)":
            return 'new'
        elif status == 'Submitted':
            return 'pending'
        # elif status == 'REQUEST WITHDRAWN':
        #     return 'under_approval'
        elif status == 'APPROVED':
            return 'approved'
        elif status == 'REJECTED' or status == 'REQUEST WITHDRAWN' or status == 'HC REJECTED':
            return 'refused'
        elif status == 'Cancel':
            return 'cancel'

    @api.model
    def replace_paid_to(self, status):
        """
        Author:Nimesh Jadav TechUltra solutions
        Date:  18th March 2021
        Func: get status key(Selection filed)
        :return: key
        """
        if status == "Cheque to School":
            return 'school'
        elif status == 'Cheque to Employee':
            return 'employee'

    @api.model
    def date_replace(self, date):
        """
        Replace date into the YY-MM-DD format
        :param date: date
        :return: date
        """
        date = date.replace("[", '').replace("]", '')
        date = date.replace('/', '-')
        date_time = date.split(' ')
        date = date_time[0].split('-')
        # if len(date_time) > 1:
        #     time = date_time[1]
        # else:
        #     time = ''
        if len(date[2]) != 4:
            date[2] = "20" + date[2]
        if len(date[1]) != 2:
            date[1] = "0" + date[1]
        if len(date[0]) != 2:
            date[0] = "0" + date[0]
        date = date[2] + "-" + date[1] + "-" + date[0]
        return date

    def compute_eligibility_rule(self, e_rec):
        if e_rec.employee_id and e_rec.academic_year:
            country_id = self.env['res.country'].search([('code', '=', 'AE')])
            if e_rec.employee_id.country_id == country_id:
                is_uae = True
            else:
                is_uae = False
            rule = e_rec.get_education_eligibility_rule(is_uae=is_uae, employee_id=e_rec.employee_id,
                                                        academic_year=e_rec.academic_year)
            if rule:
                e_rec.education_eligibility_id = rule[0]
