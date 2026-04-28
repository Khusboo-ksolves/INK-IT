# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class KsQuestionMaster(models.Model):
    _name = 'ks.question.master'
    _description = 'Question Master'
    _order = 'category_id, sequence, name'

    name = fields.Char(
        string='Question',
        required=True,
        help='The question text'
    )
    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help='Sequence for ordering questions'
    )
    category_id = fields.Many2one(
        'ks.appraisal.question.category',
        string='Category',
        required=True,
        ondelete='restrict',
        help='Category of the question'
    )
    question_type = fields.Selection([
        ('text', 'Text'),
        ('textarea', 'Text Area'),
        ('number', 'Number'),
        ('date', 'Date'),
        ('selection', 'Selection'),
        ('multiple_choice', 'Multiple Choice'),
        ('rating', 'Rating'),
    ], string='Question Type',
        default='text',
        required=True,
        help='Type of the question'
    )
    is_required = fields.Boolean(
        string='Required',
        default=False,
        help='If checked, the question is mandatory'
    )
    description = fields.Text(
        string='Description/Help Text',
        help='Additional description or help text for the question'
    )
    active = fields.Boolean(
        string='Active',
        default=True,
        help='If unchecked, the question will be hidden and not available for selection'
    )
    
    # Options for Selection and Multiple Choice question types
    option_ids = fields.One2many(
        'ks.question.option',
        'question_id',
        string='Options',
        help='Options for selection or multiple choice questions'
    )
    option_count = fields.Integer(
        string='Option Count',
        compute='_compute_option_count',
    )

    _sql_constraints = [
        ('name_category_uniq', 'unique(name, category_id)', 'Question must be unique within a category!'),
    ]
    
    @api.depends('option_ids')
    def _compute_option_count(self):
        for record in self:
            record.option_count = len(record.option_ids)
    
    @api.constrains('question_type', 'option_ids')
    def _check_options_for_selection_types(self):
        for record in self:
            if record.question_type in ('selection', 'multiple_choice') and not record.option_ids:
                raise ValidationError(
                    _('Please add at least one option for Selection or Multiple Choice questions.')
                )
