/** @odoo-module **/

import { Component, useState, onWillStart, useRef } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { rpc } from "@web/core/network/rpc";
import { _t } from "@web/core/l10n/translation";

/**
 * ManagerFeedbackMatrix Component
 * Displays a matrix of employees (rows) x questions (columns) for feedback
 * - Employee column is frozen/sticky on the left
 * - Questions scroll horizontally as columns
 */
export class ManagerFeedbackMatrix extends Component {
    static template = "ks_appraisal_feedback.ManagerFeedbackMatrix";
    static props = {};

    setup() {
        this.notification = useService("notification");
        this.action = useService("action");

        this.state = useState({
            loading: true,
            saving: false,
            submitting: false,
            cycleInfo: "",
            managerName: "",
            categories: [],
            employees: [],
            activeCategory: null,
            answers: {},
            hasChanges: false,
            showValidationPopup: false,
            validationMessage: "",
        });

        this.matrixScrollRef = useRef("matrixScroll");

        onWillStart(async () => {
            await this.loadFeedbackData();
        });
    }

    async loadFeedbackData() {
        this.state.loading = true;
        try {
            const data = await rpc("/ks_appraisal_feedback/get_feedback_data", {});
            
            this.state.cycleInfo = data.cycle_info || "Annual Appraisal";
            this.state.managerName = data.manager_name || "";
            this.state.categories = data.categories || [];
            this.state.employees = data.employees || [];
            
            if (this.state.categories.length > 0 && !this.state.activeCategory) {
                this.state.activeCategory = this.state.categories[0].id;
            }
            
            this.initializeAnswers();
        } catch (error) {
            console.error("Error loading feedback data:", error);
            this.notification.add(_t("Error loading feedback data"), { type: "danger" });
        } finally {
            this.state.loading = false;
        }
    }

    initializeAnswers() {
        const answers = {};
        for (const employee of this.state.employees) {
            answers[employee.appraisal_id] = { ...employee.answers };
        }
        this.state.answers = answers;
    }

    get activeQuestions() {
        if (!this.state.activeCategory) return [];
        const category = this.state.categories.find(c => c.id === this.state.activeCategory);
        return category ? category.questions : [];
    }

    get hasEmployees() {
        return this.state.employees.length > 0;
    }

    get hasCategories() {
        return this.state.categories.length > 0;
    }

    selectCategory(categoryId) {
        this.state.activeCategory = categoryId;
    }

    isCategoryActive(categoryId) {
        return this.state.activeCategory === categoryId;
    }

    getAnswer(appraisalId, questionId) {
        const appraisalAnswers = this.state.answers[appraisalId];
        if (!appraisalAnswers) return "";
        return appraisalAnswers[questionId] ?? "";
    }

    setAnswer(appraisalId, questionId, value) {
        if (!this.state.answers[appraisalId]) {
            this.state.answers[appraisalId] = {};
        }
        this.state.answers[appraisalId][questionId] = value;
        this.state.hasChanges = true;
    }

    onInputChange(ev, appraisalId, questionId) {
        const value = ev.target.value;
        this.setAnswer(appraisalId, questionId, value);
    }

    onRatingChange(appraisalId, questionId, rating) {
        this.setAnswer(appraisalId, questionId, String(rating));
    }

    onBooleanChange(appraisalId, questionId, value) {
        this.setAnswer(appraisalId, questionId, value ? "Yes" : "No");
    }

    onOptionSelect(appraisalId, questionId, optionName) {
        this.setAnswer(appraisalId, questionId, optionName);
    }

    getRatingValue(appraisalId, questionId) {
        const answer = this.getAnswer(appraisalId, questionId);
        return parseInt(answer) || 0;
    }

    getBooleanValue(appraisalId, questionId) {
        const answer = this.getAnswer(appraisalId, questionId);
        return answer === "Yes";
    }

    renderStars(rating) {
        const stars = [];
        for (let i = 1; i <= 5; i++) {
            stars.push(i <= rating ? "★" : "☆");
        }
        return stars.join("");
    }

    async onSaveDraft() {
        if (this.state.saving) return;
        
        this.state.saving = true;
        try {
            const answersData = [];
            
            for (const [appraisalIdStr, questions] of Object.entries(this.state.answers)) {
                const appraisalId = parseInt(appraisalIdStr);
                for (const [questionIdStr, answerValue] of Object.entries(questions)) {
                    const questionId = parseInt(questionIdStr);
                    if (answerValue !== undefined && answerValue !== null && answerValue !== "") {
                        answersData.push({
                            appraisal_id: appraisalId,
                            question_id: questionId,
                            answer_value: answerValue,
                        });
                    }
                }
            }
            
            if (answersData.length === 0) {
                this.notification.add(_t("No answers to save"), { type: "warning" });
                return;
            }
            
            const result = await rpc("/ks_appraisal_feedback/save_all_answers", {
                answers_data: answersData,
            });
            
            if (result.success) {
                this.notification.add(
                    _t("Draft saved successfully! %s answers saved.", result.saved_count),
                    { type: "success" }
                );
                this.state.hasChanges = false;
            } else {
                this.notification.add(
                    _t("Some answers could not be saved"),
                    { type: "warning" }
                );
            }
        } catch (error) {
            console.error("Error saving draft:", error);
            this.notification.add(_t("Error saving draft"), { type: "danger" });
        } finally {
            this.state.saving = false;
        }
    }

    /**
     * Get all required questions from all categories
     */
    getAllRequiredQuestions() {
        const requiredQuestions = [];
        for (const category of this.state.categories) {
            for (const question of category.questions) {
                if (question.is_required) {
                    requiredQuestions.push(question);
                }
            }
        }
        return requiredQuestions;
    }

    /**
     * Validate that all required questions are answered for all employees
     * Returns { valid: boolean, missingCount: number }
     */
    validateRequiredAnswers() {
        const requiredQuestions = this.getAllRequiredQuestions();
        let missingCount = 0;
        
        for (const employee of this.state.employees) {
            const appraisalId = employee.appraisal_id;
            const employeeAnswers = this.state.answers[appraisalId] || {};
            
            for (const question of requiredQuestions) {
                const answer = employeeAnswers[question.id];
                const isEmpty = answer === undefined || answer === null || answer === "" || answer === "0";
                if (isEmpty) {
                    missingCount++;
                }
            }
        }
        
        return {
            valid: missingCount === 0,
            missingCount: missingCount,
        };
    }

    /**
     * Show validation popup
     */
    showValidationError() {
        this.state.showValidationPopup = true;
    }

    /**
     * Close validation popup
     */
    closeValidationPopup() {
        this.state.showValidationPopup = false;
    }

    async onSubmit() {
        if (this.state.submitting) return;
        
        // Save draft first if there are changes
        if (this.state.hasChanges) {
            await this.onSaveDraft();
        }
        
        // Validate required answers on client side
        const validation = this.validateRequiredAnswers();
        if (!validation.valid) {
            this.showValidationError();
            return;
        }
        
        this.state.submitting = true;
        try {
            const appraisalIds = this.state.employees.map(e => e.appraisal_id);
            
            const result = await rpc("/ks_appraisal_feedback/submit_feedback", {
                appraisal_ids: appraisalIds,
            });
            
            if (result.success) {
                this.notification.add(
                    _t("Feedback submitted successfully!"),
                    { type: "success" }
                );
                await this.loadFeedbackData();
            } else {
                // Check if it's a required fields error
                const hasRequiredError = result.results.some(r => 
                    !r.success && r.error && r.error.includes("Missing required")
                );
                
                if (hasRequiredError) {
                    this.showValidationError();
                } else {
                    const failedCount = result.results.filter(r => !r.success).length;
                    this.notification.add(
                        _t("Could not submit %s appraisal(s). Please try again.", failedCount),
                        { type: "warning" }
                    );
                }
            }
        } catch (error) {
            console.error("Error submitting feedback:", error);
            this.notification.add(_t("Error submitting feedback"), { type: "danger" });
        } finally {
            this.state.submitting = false;
        }
    }

    getQuestionNumber(index) {
        return `Q${index + 1}`;
    }

    getDesignationShort(designation) {
        if (!designation) return "";
        const words = designation.split(" ");
        if (words.length >= 2) {
            return words.map(w => w[0]).join("").toUpperCase();
        }
        return designation.substring(0, 3).toUpperCase();
    }
}
