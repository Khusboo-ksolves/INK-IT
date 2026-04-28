# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class KsQuestionOption(models.Model):
    _name = 'ks.question.option'
    _description = 'Question Option'
    _order = 'sequence, id'

    name = fields.Char(
        string='Option',
        required=True,
        help='The option text'
    )
    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help='Sequence for ordering options'
    )
    question_id = fields.Many2one(
        'ks.question.master',
        string='Question',
        required=True,
        ondelete='cascade',
        index=True,
    )
    is_default = fields.Boolean(
        string='Default',
        default=False,
        help='If checked, this option will be pre-selected'
    )

    _sql_constraints = [
        ('name_question_uniq', 'unique(name, question_id)', 'Option must be unique within a question!'),
    ]
