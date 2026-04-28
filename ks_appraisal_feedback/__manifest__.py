# -*- coding: utf-8 -*-
{
    'name': 'Appraisal Feedback',
    'version': '19.0.1.0.0',
    'category': 'Human Resources',
    'summary': 'Employee Appraisal Feedback with Question Master',
    'description': """
        Appraisal Feedback Module
        =========================
        
        Features:
        * Employee Appraisal management
        * Question Categories and Question Master
        * Section-based feedback forms
        * Manager Feedback Matrix Screen
        * Bulk appraisal request sending
        * Progress tracking
        * Excel export
    """,
    'author': 'Ksolves India Pvt. Ltd.',
    'website': 'https://www.ksolves.com',
    'depends': [
        'base',
        'web',
        'hr',
        'mail',
        'ks_crm_team_hierarchy',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/appraisal_feedback_security.xml',
        'data/appraisal_feedback_cron.xml',
        'data/appraisal_feedback_server_action.xml',
        'views/ks_appraisal_question_category_views.xml',
        'views/ks_question_master_views.xml',
        'views/ks_employee_appraisal_views.xml',
        'views/send_appraisal_survey_wizard_views.xml',
        'views/manager_feedback_views.xml',
        'views/menu_items.xml',
        'views/hr_employee_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'ks_appraisal_feedback/static/src/js/components/**/*.js',
            'ks_appraisal_feedback/static/src/js/components/**/*.xml',
            'ks_appraisal_feedback/static/src/js/components/**/*.scss',
            'ks_appraisal_feedback/static/src/js/manager_feedback_action.js',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
