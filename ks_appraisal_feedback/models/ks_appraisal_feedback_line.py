# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class KsAppraisalFeedbackLine(models.Model):
    _name = 'ks.appraisal.feedback.line'
    _description = 'Appraisal Feedback Line'
    _order = 'sequence, id'

    appraisal_id = fields.Many2one(
        'ks.employee.appraisal',
        string='Employee Appraisal',
        required=True,
        ondelete='cascade',
        index=True,
    )
    sequence = fields.Integer(
        string='Sequence',
        default=10,
    )
    display_type = fields.Selection([
        ('line_section', 'Section'),
        ('line_note', 'Note'),
    ], string='Display Type',
        default=False,
    )
    name = fields.Text(
        string='Description',
    )
    question_id = fields.Many2one(
        'ks.question.master',
        string='Question',
        ondelete='restrict',
    )
    category_id = fields.Many2one(
        'ks.appraisal.question.category',
        string='Category',
        related='question_id.category_id',
        store=True,
        readonly=True,
    )
    question_type = fields.Selection(
        related='question_id.question_type',
        string='Question Type',
        readonly=True,
    )
    is_required = fields.Boolean(
        related='question_id.is_required',
        string='Required',
        readonly=True,
    )
    
    # Answer fields
    answer_text = fields.Text(string='Answer (Text)')
    answer_number = fields.Float(string='Answer (Number)', digits=(16, 2))
    answer_date = fields.Date(string='Answer (Date)')
    answer_selection = fields.Char(string='Answer (Selection)')
    answer_rating = fields.Selection([
        ('0', 'Not Rated'),
        ('1', '1 Star'),
        ('2', '2 Stars'),
        ('3', '3 Stars'),
        ('4', '4 Stars'),
        ('5', '5 Stars'),
    ], string='Answer (Rating)', default='0')
    
    answer_display = fields.Char(
        string='Answer',
        compute='_compute_answer_display',
        store=True,
    )
    
    @api.depends('answer_text', 'answer_number', 'answer_date', 'answer_selection', 'answer_rating', 'question_type')
    def _compute_answer_display(self):
        for line in self:
            if line.display_type:
                line.answer_display = ''
            elif line.question_type in ('text', 'textarea'):
                line.answer_display = line.answer_text or ''
            elif line.question_type == 'number':
                line.answer_display = str(line.answer_number) if line.answer_number else ''
            elif line.question_type == 'date':
                line.answer_display = str(line.answer_date) if line.answer_date else ''
            elif line.question_type in ('selection', 'multiple_choice'):
                line.answer_display = line.answer_selection or ''
            elif line.question_type == 'rating':
                line.answer_display = f"{line.answer_rating} Star(s)" if line.answer_rating and line.answer_rating != '0' else ''
            else:
                line.answer_display = line.answer_text or ''
