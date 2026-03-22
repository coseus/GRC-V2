from __future__ import annotations

from app.audit.service import audit_log
from app.repositories.recommendations import RecommendationRepository
from app.services.auth import require_role


class RecommendationService:
    def __init__(self, session):
        self.session = session
        self.repo = RecommendationRepository(session)

    def list_for_assessment(self, actor, assessment_id: int):
        require_role(actor, "viewer")
        return self.repo.list_for_assessment(assessment_id)

    def create_manual(
        self,
        actor,
        *,
        assessment_id: int,
        title: str,
        description: str | None = None,
        priority: str = "medium",
        domain_code: str | None = None,
        domain_name: str | None = None,
        question_code: str | None = None,
        score: float | None = None,
    ):
        require_role(actor, "auditor")

        title = (title or "").strip()
        if not title:
            raise ValueError("Titlul recomandarii este obligatoriu.")

        priority = (priority or "medium").strip().lower()
        if priority not in {"high", "medium", "low"}:
            raise ValueError("Prioritate invalida.")

        obj = self.repo.create(
            assessment_id=assessment_id,
            domain_code=domain_code,
            domain_name=domain_name,
            question_code=question_code,
            title=title,
            description=(description or "").strip() or None,
            priority=priority,
            status="open",
            source="manual",
            score=score,
            updated_by=getattr(actor, "id", None),
        )

        audit_log(
            self.session,
            getattr(actor, "id", None),
            "create",
            "recommendation",
            obj.id,
            {
                "assessment_id": assessment_id,
                "title": title,
                "priority": priority,
            },
        )
        self.session.commit()
        return obj

    def regenerate_from_scores(self, actor, assessment_id: int, domain_scores: dict):
        require_role(actor, "auditor")

        self.repo.delete_for_assessment(assessment_id)

        created = []

        if not domain_scores:
            obj = self.repo.create(
                assessment_id=assessment_id,
                domain_code=None,
                domain_name="General",
                question_code=None,
                title="Complete the assessment",
                description="There are not enough scored answers yet. Complete more questions to generate targeted recommendations.",
                priority="medium",
                status="open",
                source="auto",
                score=None,
                updated_by=getattr(actor, "id", None),
            )
            created.append(obj)
        else:
            for domain_name, score in (domain_scores or {}).items():
                if score is None:
                    continue

                numeric_score = float(score)

                if numeric_score >= 70:
                    continue

                if numeric_score < 40:
                    priority = "high"
                elif numeric_score < 60:
                    priority = "medium"
                else:
                    priority = "low"

                title = f"Improve controls for {domain_name}"
                description = (
                    f"The current score for '{domain_name}' is {numeric_score:.1f}. "
                    f"Review missing controls, add evidence, and define remediation actions."
                )

                obj = self.repo.create(
                    assessment_id=assessment_id,
                    domain_code=None,
                    domain_name=domain_name,
                    question_code=None,
                    title=title,
                    description=description,
                    priority=priority,
                    status="open",
                    source="auto",
                    score=numeric_score,
                    updated_by=getattr(actor, "id", None),
                )
                created.append(obj)

            if not created:
                obj = self.repo.create(
                    assessment_id=assessment_id,
                    domain_code=None,
                    domain_name="General",
                    question_code=None,
                    title="Maintain current control posture",
                    description="Current scores are relatively good. Review evidence quality and define continuous improvement actions.",
                    priority="low",
                    status="open",
                    source="auto",
                    score=None,
                    updated_by=getattr(actor, "id", None),
                )
                created.append(obj)

        audit_log(
            self.session,
            getattr(actor, "id", None),
            "regenerate",
            "recommendation",
            None,
            {
                "assessment_id": assessment_id,
                "count": len(created),
            },
        )
        self.session.commit()
        return created