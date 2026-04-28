# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class SendAppraisalWizard(models.TransientModel):
    _name = 'send.appraisal.survey.wizard'
    _description = 'Send Appraisal Feedback Wizard'

    employee_ids = fields.Many2many(
        'hr.employee',
        'send_appraisal_wizard_employee_rel',
        'wizard_id',
        'employee_id',
        string='Employees',
        required=True,
    )
    
    manager_id = fields.Many2one(
        'res.users',
        string='Manager',
        required=True,
    )
    
    appraisal_cycle = fields.Selection([
        ('april', 'April'),
        ('october', 'October'),
    ], string='Appraisal Cycle',
        required=True,
    )
    
    cc_email_to = fields.Many2many(
        'res.users',
        'send_appraisal_wizard_cc_rel',
        'wizard_id',
        'user_id',
        string='CC Email To',
    )
    
    deadline_date = fields.Date(
        string='Deadline',
    )
    
    notes = fields.Text(
        string='Notes',
    )
    
    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if 'default_employee_ids' in self.env.context:
            res['employee_ids'] = [(6, 0, self.env.context.get('default_employee_ids', []))]
        return res
    
    @api.onchange('employee_ids')
    def _onchange_employee_ids(self):
        if self.employee_ids:
            managers = self.employee_ids.mapped('parent_id.user_id').filtered(lambda m: m)
            if managers and len(managers) == 1:
                self.manager_id = managers[0]
            # Auto-set appraisal cycle if all employees have same cycle
            cycles = self.employee_ids.mapped('appraisal_cycle')
            cycles = list(set([c for c in cycles if c]))
            if len(cycles) == 1:
                self.appraisal_cycle = cycles[0]
    
    def action_send_surveys(self):
        """Create appraisal records and send email"""
        if not self.employee_ids:
            raise UserError(_('Please select at least one employee.'))
        
        if not self.manager_id:
            raise UserError(_('Please select a manager.'))
        
        if not self.manager_id.email:
            raise UserError(_('Manager does not have an email address.'))
        
        if not self.appraisal_cycle:
            raise UserError(_('Please select an appraisal cycle.'))
        
        if not self.env['ks.question.master'].search_count([('active', '=', True)]):
            raise UserError(_('No active questions found. Please configure questions first.'))
        
        appraisals = []
        employee_data = []
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url').rstrip('/')
        
        for employee in self.employee_ids:
            try:
                # Create appraisal in draft (no lines), then use action_populate_questions
                appraisal = self.env['ks.employee.appraisal'].sudo().create({
                    'employee_id': employee.id,
                    'manager_id': self.manager_id.id,
                    'appraisal_cycle': self.appraisal_cycle,
                    'deadline_date': self.deadline_date,
                    'notes': self.notes,
                    'state': 'draft',
                })
                appraisal.action_populate_questions()
                appraisal.sudo().write({
                    'state': 'sent',
                    'sent_date': fields.Datetime.now(),
                })

                appraisals.append(appraisal)
                
                employee_data.append({
                    'name': employee.name,
                    'code': employee.employee_code if hasattr(employee, 'employee_code') else '',
                    'designation': employee.job_id.name if employee.job_id else '',
                })
                
            except Exception as e:
                _logger.error("Error creating appraisal for %s: %s", employee.name, str(e))
                continue
        
        if not employee_data:
            raise UserError(_('Failed to create appraisal records.'))
        
        # Get the client action URL for Manager Feedback
        feedback_action = self.env.ref('ks_appraisal_feedback.action_manager_feedback', raise_if_not_found=False)
        if feedback_action:
            feedback_url = f"{base_url}/web#action={feedback_action.id}"
        else:
            feedback_url = f"{base_url}/web#menu_id=&action=ks_appraisal_feedback.action_manager_feedback"
        
        # Build email - table without individual links
        table_rows = ''.join([f"""
            <tr>
                <td style="padding: 10px; border: 1px solid #ddd;">{emp['name']}</td>
                <td style="padding: 10px; border: 1px solid #ddd;">{emp['code'] or 'N/A'}</td>
                <td style="padding: 10px; border: 1px solid #ddd;">{emp['designation'] or 'N/A'}</td>
            </tr>
        """ for emp in employee_data])
        
        cycle_label = dict(self._fields['appraisal_cycle'].selection).get(self.appraisal_cycle, '')
        
        email_body = f"""
        <div style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <p>Dear {self.manager_id.name},</p>
            <p>You have been requested to provide <strong>{cycle_label}</strong> appraisal feedback for the following employees:</p>
            
            <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                <thead>
                    <tr style="background-color: #875A7B; color: white;">
                        <th style="padding: 12px; border: 1px solid #ddd; text-align: left;">Employee</th>
                        <th style="padding: 12px; border: 1px solid #ddd; text-align: left;">Code</th>
                        <th style="padding: 12px; border: 1px solid #ddd; text-align: left;">Designation</th>
                    </tr>
                </thead>
                <tbody>{table_rows}</tbody>
            </table>
            
            <p style="margin: 25px 0;">
                <a href="{feedback_url}" style="background-color: #875A7B; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; font-weight: bold; display: inline-block;">
                    Fill Feedback for All Employees
                </a>
            </p>
            
            <p><strong>Deadline:</strong> {self.deadline_date.strftime('%B %d, %Y') if self.deadline_date else 'Not specified'}</p>
            
            {f'<p><strong>Notes:</strong> {self.notes}</p>' if self.notes else ''}
            
            <p>Thank you.</p>
            <p>Best regards,<br/>{self.env.user.name}</p>
        </div>
        """
        
        cc_emails = []
        if self.cc_email_to:
            cc_emails = [u.email for u in self.cc_email_to if u.email]
        
        try:
            mail = self.env['mail.mail'].create({
                'subject': f'Appraisal Feedback Request - {cycle_label} - {len(employee_data)} Employee(s)',
                'body_html': email_body,
                'email_to': self.manager_id.email,
                'email_cc': ','.join(cc_emails) if cc_emails else False,
                'email_from': self.env.user.email_formatted or 'noreply@odoo.com',
                'auto_delete': False,
            })
            mail.send()
        except Exception as e:
            raise UserError(_('Failed to send email: %s') % str(e))
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Requests Sent'),
                'message': _('Appraisal requests sent for %d employee(s).') % len(employee_data),
                'type': 'success',
                'sticky': False,
            }
        }
