# -*- coding: utf-8 -*-
from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    appraisal_cycle = fields.Selection([
           ('april', 'April'),
           ('october', 'October')
      ], string='Appraisal Cycle', default='april')
