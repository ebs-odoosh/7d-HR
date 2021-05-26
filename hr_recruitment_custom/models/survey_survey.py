# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.osv import expression


class SurveySurveyExt(models.Model):
    _inherit = "survey.survey"

    # security / access
    access_mode = fields.Selection([('public', 'Anyone with the link'),
                                    ('token', 'Invited people only')], string='Access Mode', default='public'
                                   )

    is_attempts_limited = fields.Boolean('Limited number of attempts',
                                         help="Check this option if you want to limit the number of attempts per user")
    attempts_limit = fields.Integer('Number of attempts', default=1)

    '''
    Add New Method, as per v13
    '''
    def _create_answer(self, user=False, partner=False, email=False, test_entry=False, check_attempts=True, **additional_vals):
        """ Main entry point to get a token back or create a new one. This method
        does check for current user access in order to explicitely validate
        security.

          :param user: target user asking for a token; it might be void or a
                       public user in which case an email is welcomed;
          :param email: email of the person asking the token is no user exists;
        """
        self.check_access_rights('read')
        self.check_access_rule('read')

        answers = self.env['survey.user_input']
        for survey in self:
            if partner and not user and partner.user_ids:
                user = partner.user_ids[0]

            invite_token = additional_vals.pop('invite_token', False)
            survey._check_answer_creation(user, partner, email, test_entry=test_entry, check_attempts=check_attempts, invite_token=invite_token)
            answer_vals = {
                'survey_id': survey.id,
                'test_entry': test_entry,
            }
            if user and not user._is_public():
                answer_vals['partner_id'] = user.partner_id.id
                answer_vals['email'] = user.email
            elif partner:
                answer_vals['partner_id'] = partner.id
                answer_vals['email'] = partner.email
            else:
                answer_vals['email'] = email

            if invite_token:
                answer_vals['token'] = invite_token
            elif survey.is_attempts_limited and survey.access_mode != 'public':
                # attempts limited: create a new invite_token
                # exception made for 'public' access_mode since the attempts pool is global because answers are
                # created every time the user lands on '/start'
                answer_vals['invite_token'] = self.env['survey.user_input']._generate_invite_token()

            answer_vals.update(additional_vals)
            answers += answers.create(answer_vals)

        return answers

    def _check_answer_creation(self, user, partner, email, test_entry=False, check_attempts=True, invite_token=False):
        """
        Ensure conditions to create new tokens are met.
        """
        self.ensure_one()
        if test_entry:
            # the current user must have the access rights to survey
            if not user.has_group('survey.group_survey_user'):
                raise UserError(_('Creating test token is not allowed for you.'))
        else:
            if not self.active:
                raise UserError(_('Creating token for archived surveys is not allowed.'))
            elif self.stage_id.closed:
                raise UserError(_('Creating token for closed surveys is not allowed.'))
            if self.access_mode == 'authentication':
                # signup possible -> should have at least a partner to create an account
                if self.users_can_signup and not user and not partner:
                    raise UserError(
                        _('Creating token for external people is not allowed for surveys requesting authentication.'))
                # no signup possible -> should be a not public user (employee or portal users)
                if not self.users_can_signup and (not user or user._is_public()):
                    raise UserError(
                        _('Creating token for external people is not allowed for surveys requesting authentication.'))
            if self.access_mode == 'internal' and (not user or not user.has_group('base.group_user')):
                raise UserError(_('Creating token for anybody else than employees is not allowed for internal surveys.'))
            if check_attempts and not self._has_attempts_left(partner or (user and user.partner_id), email, invite_token):
                raise UserError(_('No attempts left.'))

    def _prepare_answer_questions(self):
        """ Will generate the questions for a randomized survey.
        It uses the random_questions_count of every sections of the survey to
        pick a random number of questions and returns the merged recordset """
        self.ensure_one()

        # questions = self.env['survey.question']
        questions = self.page_ids.mapped('question_ids')

        # First append questions without page
        # for question in self.question_ids:
        #     if not question.page_id:
        #         questions |= question

        # Then, questions in sections

        # for page in self.page_ids:
        #     if self.questions_selection == 'all':
        #         questions |= page.question_ids
        #     else:
        #         if page.random_questions_count > 0 and len(page.question_ids) > page.random_questions_count:
        #             questions = questions.concat(*random.sample(page.question_ids, page.random_questions_count))
        #         else:
        #             questions |= page.question_ids

        return questions

    def _has_attempts_left(self, partner, email, invite_token):
        self.ensure_one()

        if (self.access_mode != 'public' or self.auth_required) and self.is_attempts_limited:
            return self._get_number_of_attempts_lefts(partner, email, invite_token) > 0

        return True

    def _get_number_of_attempts_lefts(self, partner, email, invite_token):
        """ Returns the number of attempts left. """
        self.ensure_one()

        domain = [
            ('survey_id', '=', self.id),
            ('test_entry', '=', False),
            ('state', '=', 'done')
        ]

        if partner:
            domain = expression.AND([domain, [('partner_id', '=', partner.id)]])
        else:
            domain = expression.AND([domain, [('email', '=', email)]])

        if invite_token:
            domain = expression.AND([domain, [('invite_token', '=', invite_token)]])

        return self.attempts_limit - self.env['survey.user_input'].search_count(domain)
