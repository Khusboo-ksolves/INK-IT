# Employee Appraisal Feedback Module - Flow Documentation

## Quick Start Testing Guide

### Step 1: Clean Up Old Data (IMPORTANT)

Before testing, run these SQL commands in your PostgreSQL database to remove old cached views:

```sql
-- Delete old views
DELETE FROM ir_ui_view WHERE model = 'appraisal.feedback';
DELETE FROM ir_ui_view WHERE model = 'send.appraisal.survey.wizard';

-- Clean stale references
DELETE FROM ir_model_data WHERE module = 'ks_appraisal_feedback' AND model = 'ir.ui.view';
```

Then upgrade the module:
```bash
./odoo-bin -d <database> -u ks_appraisal_feedback --stop-after-init
```

Clear browser cache (Ctrl+Shift+R) and restart Odoo.

---

### Step 2: Configure Question Categories

**Navigate to**: Feedbacks > Configuration > Question Categories

Create categories (editable list):

| Sequence | Name | Description |
|----------|------|-------------|
| 10 | Technical Skills | Questions about technical competencies |
| 20 | Soft Skills | Communication and teamwork |
| 30 | Performance | Work performance and goals |
| 40 | Overall Assessment | Final evaluation |

---

### Step 3: Create Questions in Question Master

**Navigate to**: Feedbacks > Configuration > Question Master

Add questions:

| Question | Category | Type | Required |
|----------|----------|------|----------|
| Rate coding skills | Technical Skills | Rating | Yes |
| Technical strengths | Technical Skills | Text Area | No |
| Rate communication | Soft Skills | Rating | Yes |
| Team collaboration | Soft Skills | Text | No |
| Goals achieved? | Performance | Selection | Yes |
| Overall rating | Overall Assessment | Rating | Yes |
| Additional comments | Overall Assessment | Text Area | No |

---

### Step 4: Send Appraisal Requests (Bulk Method)

**Navigate to**: Feedbacks > Employee Appraisals > Send Appraisal Request

Fill the wizard:
- **Employees**: Select employees
- **Manager**: Select manager who will provide feedback
- **Appraisal Cycle**: Select April or October
- **Deadline**: Optional deadline date
- **CC Email To**: Optional CC recipients
- **Notes**: Optional notes

Click **Send Appraisal Requests**

**What happens**:
- Creates `ks.employee.appraisal` record for each employee
- Each record contains questions organized by category sections
- Sends email to manager with employee table and links

---

### Step 5: Fill Feedback (as Manager)

**Navigate to**: Feedbacks > Employee Appraisals

Open an appraisal (status: Sent):

1. View questions organized by category sections
2. Click **Start Filling** to mark as "In Progress"
3. Fill answers for each question
4. Click **Mark Completed** when done

---

### Step 6: Export Results

Select multiple records in list view → **Action > Export to Excel**

---

## Data Models

### ks.employee.appraisal

| Field | Type | Description |
|-------|------|-------------|
| name | Char | Auto-generated reference (APR/2024/0001) |
| employee_id | Many2one | Employee being evaluated |
| employee_code | Char | Related employee code |
| manager_id | Many2one | Manager providing feedback |
| date | Date | Appraisal date |
| appraisal_cycle | Selection | April / October |
| designation | Char | Employee's job title |
| department_id | Many2one | Employee's department |
| state | Selection | draft/sent/in_progress/completed/cancelled |
| feedback_line_ids | One2many | Feedback lines |
| deadline_date | Date | Deadline |
| sent_date | Datetime | When request sent |
| completed_date | Datetime | When completed |

### ks.appraisal.feedback.line

| Field | Type | Description |
|-------|------|-------------|
| appraisal_id | Many2one | Parent appraisal |
| sequence | Integer | Order |
| display_type | Selection | line_section (category header) or False (question) |
| name | Text | Section name or question text |
| question_id | Many2one | Link to question master |
| question_type | Selection | text/textarea/number/date/selection/rating |
| is_required | Boolean | Is answer required |
| answer_text | Text | Text answer |
| answer_number | Float | Number answer |
| answer_date | Date | Date answer |
| answer_selection | Char | Selection answer |
| answer_rating | Integer | Rating (1-5) |
| answer_display | Char | Computed display |

### ks.appraisal.question.category

| Field | Type | Description |
|-------|------|-------------|
| name | Char | Category name (unique) |
| sequence | Integer | Display order |
| description | Text | Description |
| active | Boolean | Is active |

### ks.question.master

| Field | Type | Description |
|-------|------|-------------|
| name | Char | Question text |
| sequence | Integer | Order within category |
| category_id | Many2one | Category |
| question_type | Selection | text/textarea/number/date/selection/multiple_choice/rating |
| is_required | Boolean | Is mandatory |
| description | Text | Help text |
| active | Boolean | Is active |

---

## Menu Structure

```
Feedbacks
├── Employees
├── Employee Appraisals
│   └── Send Appraisal Request
└── Configuration
    ├── Question Categories
    └── Question Master
```

---

## Status Flow

```
Draft → Sent → In Progress → Completed
                    ↓
               Cancelled
```

---

## Troubleshooting

### Error: "field is undefined"

Old cached views in database. Run SQL cleanup commands above.

### No questions appearing

Check Question Master has active questions with categories assigned.

### Email not sending

Verify manager has email address and mail server is configured.
