# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class KsAppraisalQuestionCategory(models.Model):
    _name = 'ks.appraisal.question.category'
    _description = 'Appraisal Question Category'
    _order = 'sequence, name'

    name = fields.Char(
        string='Category Name',
        required=True,
        help='Name of the question category'
    )
    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help='Sequence for ordering categories'
    )
    description = fields.Text(
        string='Description',
        help='Description of the category'
    )

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Category name must be unique!'),
    ]
