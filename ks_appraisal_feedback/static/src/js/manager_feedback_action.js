/** @odoo-module **/

import { Component, useState, onWillStart, onMounted } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";
import { ManagerFeedbackMatrix } from "@ks_appraisal_feedback/js/components/manager_feedback/manager_feedback_matrix";

/**
 * ManagerFeedbackAction - Main Client Action Component
 * Manages the Manager Feedback Matrix screen
 */
export class ManagerFeedbackAction extends Component {
    static template = "ks_appraisal_feedback.ManagerFeedbackAction";
    static components = { ManagerFeedbackMatrix };
    static props = ["*"];

    setup() {
        this.actionService = useService("action");
    }
}

registry.category("actions").add("ks_manager_feedback_action", ManagerFeedbackAction);
