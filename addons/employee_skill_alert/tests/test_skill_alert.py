import pytest
from odoo.tests.common import TransactionCase


class TestSkillAlert(TransactionCase):

    def setUp(self):
        super().setUp()
        self.employee = self.env["hr.employee"].create({"name": "Test Emp"})
        skill_type = self.env["hr.skill.type"].create(
            {"name": "Python", "standard_level": 3}
        )
        skill_level = self.env["hr.skill.level"].create(
            {"name": "Beginner", "sequence": 1}
        )
        self.skill = self.env["hr.skill"].create(
            {
                "employee_id": self.employee.id,
                "skill_type_id": skill_type.id,
                "skill_id": self.env["hr.skill"].create({"name": "Odoo"}).id,
                "skill_level_id": skill_level.id,
            }
        )

    def test_alert_visibility(self):
        self.employee._compute_skill_status()
        assert self.employee.has_any_low_skill is True

    def test_alert_sends_email(self):
        self.employee.action_send_skill_alert()
        mails = self.env["mail.mail"].search([("subject", "ilike", "Skill Alert")])
        assert mails, "No email was sent."
