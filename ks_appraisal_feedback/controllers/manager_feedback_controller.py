# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
from datetime import date
import json


class ManagerFeedbackController(http.Controller):
    """Controller for Manager Feedback Matrix Screen"""

    @http.route('/ks_appraisal_feedback/get_feedback_data', type='json', auth='user')
    def get_feedback_data(self):
        """
        Fetch all data needed for the feedback matrix screen.
        Returns categories, questions, employees (appraisals) for the logged-in manager.
        Only shows appraisals where deadline has not passed (deadline >= today or no deadline set).
        """
        user = request.env.user
        today = date.today()
        
        # Get all appraisals where current user is the manager
        # Filter: deadline not passed (deadline >= today OR deadline is not set)
        appraisals = request.env['ks.employee.appraisal'].search([
            ('manager_id', '=', user.id),
            ('state', 'in', ['draft', 'sent', 'in_progress']),
            '|',
            ('deadline_date', '=', False),
            ('deadline_date', '>=', today),
        ], order='employee_id')
        
        # Get all categories
        categories = request.env['ks.appraisal.question.category'].search([], order='sequence, name')
        
        # Get all active questions grouped by category
        questions = request.env['ks.question.master'].search([
            ('active', '=', True)
        ], order='category_id, sequence, name')
        
        # Build category data with questions
        categories_data = []
        for category in categories:
            category_questions = questions.filtered(lambda q: q.category_id.id == category.id)
            if category_questions:
                categories_data.append({
                    'id': category.id,
                    'name': category.name,
                    'sequence': category.sequence,
                    'questions': [{
                        'id': q.id,
                        'name': q.name,
                        'question_type': q.question_type,
                        'is_required': q.is_required,
                        'description': q.description or '',
                        'options': [{
                            'id': opt.id,
                            'name': opt.name,
                            'is_default': opt.is_default,
                        } for opt in q.option_ids.sorted('sequence')] if q.question_type in ('selection', 'multiple_choice') else [],
                    } for q in category_questions]
                })
        
        # Build employees (appraisals) data
        employees_data = []
        for appraisal in appraisals:
            employee = appraisal.employee_id
            
            # Build answers dictionary {question_id: answer_value}
            answers = {}
            for line in appraisal.feedback_line_ids.filtered(lambda l: not l.display_type and l.question_id):
                answer_value = None
                if line.question_type in ('text', 'textarea'):
                    answer_value = line.answer_text or ''
                elif line.question_type == 'number':
                    answer_value = line.answer_number or 0
                elif line.question_type == 'date':
                    answer_value = str(line.answer_date) if line.answer_date else ''
                elif line.question_type in ('selection', 'multiple_choice'):
                    answer_value = line.answer_selection or ''
                elif line.question_type == 'rating':
                    answer_value = line.answer_rating or '0'
                answers[line.question_id.id] = answer_value
            
            employees_data.append({
                'appraisal_id': appraisal.id,
                'employee_id': employee.id,
                'employee_name': employee.name,
                'employee_code': appraisal.employee_code or '',
                'designation': appraisal.job_id.name if appraisal.job_id else '',
                'department': appraisal.department_id.name if appraisal.department_id else '',
                'appraisal_cycle': appraisal.appraisal_cycle,
                'state': appraisal.state,
                'answers': answers,
            })
        
        # Get current appraisal cycle info from the appraisals
        cycle_info = ''
        if appraisals:
            # Get the cycle from the first appraisal (they should all be the same cycle)
            cycle = appraisals[0].appraisal_cycle
            cycle_label = dict(appraisals[0]._fields['appraisal_cycle'].selection).get(cycle, '')
            cycle_info = cycle_label if cycle_label else ""
        else:
            cycle_info = ""
        
        return {
            'cycle_info': cycle_info,
            'manager_name': user.name,
            'categories': categories_data,
            'employees': employees_data,
        }

    @http.route('/ks_appraisal_feedback/save_answer', type='json', auth='user')
    def save_answer(self, appraisal_id, question_id, answer_value):
        """
        Save a single answer for a specific appraisal and question.
        Creates the feedback line if it doesn't exist.
        """
        user = request.env.user
        
        # Verify the appraisal belongs to this manager
        appraisal = request.env['ks.employee.appraisal'].browse(appraisal_id)
        if not appraisal.exists() or appraisal.manager_id.id != user.id:
            return {'success': False, 'error': 'Unauthorized access'}
        
        if appraisal.state == 'completed':
            return {'success': False, 'error': 'Appraisal is already completed'}
        
        # Get the question
        question = request.env['ks.question.master'].browse(question_id)
        if not question.exists():
            return {'success': False, 'error': 'Question not found'}
        
        # Find or create the feedback line
        feedback_line = appraisal.feedback_line_ids.filtered(
            lambda l: l.question_id.id == question_id and not l.display_type
        )
        
        # Prepare answer values based on question type
        answer_vals = {
            'answer_text': False,
            'answer_number': 0,
            'answer_date': False,
            'answer_selection': False,
            'answer_rating': '0',
        }
        
        if question.question_type in ('text', 'textarea'):
            answer_vals['answer_text'] = answer_value or ''
        elif question.question_type == 'number':
            try:
                answer_vals['answer_number'] = float(answer_value) if answer_value else 0
            except (ValueError, TypeError):
                answer_vals['answer_number'] = 0
        elif question.question_type == 'date':
            answer_vals['answer_date'] = answer_value if answer_value else False
        elif question.question_type in ('selection', 'multiple_choice'):
            answer_vals['answer_selection'] = answer_value or ''
        elif question.question_type == 'rating':
            answer_vals['answer_rating'] = str(answer_value) if answer_value else '0'
        
        if feedback_line:
            feedback_line.write(answer_vals)
        else:
            # Create new feedback line
            max_sequence = max(appraisal.feedback_line_ids.mapped('sequence') or [0])
            request.env['ks.appraisal.feedback.line'].create({
                'appraisal_id': appraisal_id,
                'question_id': question_id,
                'name': question.name,
                'sequence': max_sequence + 10,
                **answer_vals,
            })
        
        # Update appraisal state to in_progress if it was sent
        if appraisal.state == 'sent':
            appraisal.write({'state': 'in_progress'})
        
        return {'success': True}

    @http.route('/ks_appraisal_feedback/save_all_answers', type='json', auth='user')
    def save_all_answers(self, answers_data):
        """
        Bulk save all answers.
        answers_data: list of {appraisal_id, question_id, answer_value}
        """
        user = request.env.user
        errors = []
        
        for answer in answers_data:
            appraisal_id = answer.get('appraisal_id')
            question_id = answer.get('question_id')
            answer_value = answer.get('answer_value')
            
            result = self.save_answer(appraisal_id, question_id, answer_value)
            if not result.get('success'):
                errors.append({
                    'appraisal_id': appraisal_id,
                    'question_id': question_id,
                    'error': result.get('error'),
                })
        
        return {
            'success': len(errors) == 0,
            'errors': errors,
            'saved_count': len(answers_data) - len(errors),
        }

    @http.route('/ks_appraisal_feedback/submit_feedback', type='json', auth='user')
    def submit_feedback(self, appraisal_ids):
        """
        Submit/complete the feedback for specified appraisals.
        Validates required questions before marking as completed.
        """
        user = request.env.user
        results = []
        
        for appraisal_id in appraisal_ids:
            appraisal = request.env['ks.employee.appraisal'].browse(appraisal_id)
            
            if not appraisal.exists() or appraisal.manager_id.id != user.id:
                results.append({
                    'appraisal_id': appraisal_id,
                    'success': False,
                    'error': 'Unauthorized access',
                })
                continue
            
            if appraisal.state == 'completed':
                results.append({
                    'appraisal_id': appraisal_id,
                    'success': True,
                    'message': 'Already completed',
                })
                continue
            
            # Check required questions
            required_lines = appraisal.feedback_line_ids.filtered(
                lambda l: not l.display_type and l.is_required and not l.answer_display
            )
            
            if required_lines:
                results.append({
                    'appraisal_id': appraisal_id,
                    'success': False,
                    'error': f"Missing required answers: {', '.join(required_lines.mapped('question_id.name'))}",
                })
                continue
            
            try:
                appraisal.action_mark_completed()
                results.append({
                    'appraisal_id': appraisal_id,
                    'success': True,
                })
            except Exception as e:
                results.append({
                    'appraisal_id': appraisal_id,
                    'success': False,
                    'error': str(e),
                })
        
        return {
            'success': all(r.get('success') for r in results),
            'results': results,
        }

    @http.route('/ks_appraisal_feedback/populate_questions_for_appraisals', type='json', auth='user')
    def populate_questions_for_appraisals(self, appraisal_ids=None):
        """
        Populate questions for appraisals that don't have feedback lines yet.
        If appraisal_ids is None, populate for all draft appraisals of the manager.
        """
        user = request.env.user
        
        domain = [
            ('manager_id', '=', user.id),
            ('state', '=', 'draft'),
        ]
        if appraisal_ids:
            domain.append(('id', 'in', appraisal_ids))
        
        appraisals = request.env['ks.employee.appraisal'].search(domain)
        
        populated_count = 0
        for appraisal in appraisals:
            if not appraisal.feedback_line_ids:
                appraisal.action_populate_questions()
                populated_count += 1
        
        return {
            'success': True,
            'populated_count': populated_count,
        }
