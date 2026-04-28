# Appraisal Feedback Module

## Overview

The Appraisal Feedback module enables HR teams to collect structured feedback from managers about their employees using a Question Master system with categories.

## Features

- **Question Categories** - Organize questions into logical groups
- **Question Master** - Central repository of all feedback questions  
- **Section-based Feedback Forms** - Questions displayed with category headers (like sale order lines)
- **Bulk Feedback Requests** - Send feedback requests to multiple employees at once
- **Progress Tracking** - Track completion percentage and answered questions
- **Excel Export** - Export feedback data for reporting

## Installation

1. Install required dependencies:
   - `base`
   - `hr`
   - `mail`
   - `ks_crm_team_hierarchy`

2. Install the module from Apps menu or via command line:
   ```bash
   ./odoo-bin -d <database> -i ks_appraisal_feedback
   ```

## Upgrade Instructions

If upgrading from a previous version, run:
```bash
./odoo-bin -d <database> -u ks_appraisal_feedback --stop-after-init
```

After upgrade, clear your browser cache and refresh the page.

## Quick Start

### 1. Configure Question Categories

Navigate to **Feedbacks > Configuration > Question Categories**

Create categories like:
- Technical Skills
- Soft Skills
- Performance
- Overall Assessment

### 2. Create Questions

Navigate to **Feedbacks > Configuration > Question Master**

Add questions with:
- Question text
- Category assignment
- Question type (Text, Rating, Number, etc.)
- Required flag

### 3. Send Feedback Requests

Navigate to **Feedbacks > Appraisal Feedback > Send Survey**

- Select employees
- Select manager
- Set deadline (optional)
- Click "Send Feedback Requests"

### 4. Fill Feedback

Manager opens the feedback form and:
- Fills answers for each question
- Clicks "Mark Completed" when done

## Menu Structure

```
Feedbacks (Root)
├── Employees
├── Appraisal Feedback
│   └── Send Survey
└── Configuration
    ├── Question Categories
    └── Question Master
```

## Models

| Model | Description |
|-------|-------------|
| `ks.appraisal.question.category` | Question categories |
| `ks.question.master` | Question definitions |
| `appraisal.feedback` | Main feedback record |
| `ks.appraisal.feedback.line` | Feedback lines (questions/answers) |
| `send.appraisal.survey.wizard` | Bulk send wizard |

## Documentation

For detailed flow documentation, see [FLOW_DOCUMENTATION.md](FLOW_DOCUMENTATION.md)

## License

LGPL-3
