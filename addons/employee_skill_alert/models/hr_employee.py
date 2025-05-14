from odoo import models, fields, api
from odoo.exceptions import UserError


class Employee(models.Model):
    _inherit = "hr.employee"

    skill_below_standard = fields.Boolean(
        string="Skill Below Standard", compute="_compute_skill_status"
    )
    has_any_low_skill = fields.Boolean(
        string="Has Any Low Skill", compute="_compute_skill_status"
    )

    @api.depends("skill_ids")
    def _compute_skill_status(self):
        for emp in self:
            below_standard = emp.skill_ids.filtered(
                lambda s: s.skill_level_id.sequence < s.skill_type_id.standard_level
            )
            emp.skill_below_standard = all(
                s.skill_level_id.sequence >= s.skill_type_id.standard_level
                for s in emp.skill_ids
            )
            emp.has_any_low_skill = bool(below_standard)

    def action_send_skill_alert(self):
        for emp in self:
            low_skills = emp.skill_ids.filtered(
                lambda s: s.skill_level_id.sequence < s.skill_type_id.standard_level
            )
            if not low_skills:
                raise UserError("No low-level skills to alert.")
            template = self.env.ref("employee_skill_alert.email_template_skill_alert")
            self.env["mail.mail"].create(
                {
                    "subject": f"Skill Alert for {emp.name}",
                    "email_to": emp.department_id.manager_id.work_email
                    or "hr@example.com",
                    "body_html": template._render_template(
                        template.body_html, "hr.employee", emp.id
                    ),
                }
            ).send()
