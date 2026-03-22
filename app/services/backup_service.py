from __future__ import annotations

import json
import shutil
from pathlib import Path

from app.db.models import Answer, Recommendation
from app.repositories.answers import AnswerRepository
from app.repositories.executive import ExecutiveRepository
from app.repositories.recommendations import RecommendationRepository
from app.services.auth import require_role


class BackupService:
    def __init__(self, session):
        self.session = session
        self.answer_repo = AnswerRepository(session)
        self.executive_repo = ExecutiveRepository(session)
        self.recommendation_repo = RecommendationRepository(session)

    def export_assessment_json(self, actor, company, assessment) -> bytes:
        require_role(actor, "viewer")

        answers = self.answer_repo.list_for_assessment(assessment.id)
        executive = self.executive_repo.get_by_assessment_id(assessment.id)
        recommendations = self.recommendation_repo.list_for_assessment(assessment.id)

        payload = {
            "company": {
                "name": getattr(company, "name", None),
                "industry": getattr(company, "industry", None),
                "country": getattr(company, "country", None),
                "size": getattr(company, "size", None),
            },
            "assessment": {
                "name": getattr(assessment, "name", None),
                "framework_code": getattr(assessment, "framework_code", None),
                "framework_name": getattr(assessment, "framework_name", None),
                "framework_version": getattr(assessment, "framework_version", "1.0"),
                "status": getattr(assessment, "status", "draft"),
            },
            "answers": [
                {
                    "question_code": a.question_code,
                    "question_text": a.question_text,
                    "domain_code": a.domain_code,
                    "domain_name": a.domain_name,
                    "selected_value": a.selected_value,
                    "score": a.score,
                    "max_score": a.max_score,
                    "weight": a.weight,
                    "comment": a.comment,
                    "evidence": a.evidence,
                    "status": a.status,
                }
                for a in answers
            ],
            "executive_summary": {
                "summary_text": getattr(executive, "summary_text", None) if executive else None,
                "strengths_text": getattr(executive, "strengths_text", None) if executive else None,
                "gaps_text": getattr(executive, "gaps_text", None) if executive else None,
                "recommendations_text": getattr(executive, "recommendations_text", None) if executive else None,
            },
            "recommendations": [
                {
                    "domain_code": r.domain_code,
                    "domain_name": r.domain_name,
                    "question_code": r.question_code,
                    "title": r.title,
                    "description": r.description,
                    "priority": r.priority,
                    "status": r.status,
                    "source": r.source,
                    "score": r.score,
                }
                for r in recommendations
            ],
        }

        return json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")

    def import_assessment_json(self, actor, *, company, assessment, json_bytes: bytes):
        require_role(actor, "auditor")

        payload = json.loads(json_bytes.decode("utf-8"))

        answers = payload.get("answers", [])
        executive_payload = payload.get("executive_summary", {})
        recommendations_payload = payload.get("recommendations", [])

        self.session.query(Answer).filter(
            Answer.assessment_id == assessment.id
        ).delete(synchronize_session=False)

        self.session.query(Recommendation).filter(
            Recommendation.assessment_id == assessment.id
        ).delete(synchronize_session=False)

        for item in answers:
            self.answer_repo.upsert(
                assessment_id=assessment.id,
                question_code=item.get("question_code"),
                question_text=item.get("question_text"),
                domain_code=item.get("domain_code"),
                domain_name=item.get("domain_name"),
                selected_value=item.get("selected_value"),
                score=item.get("score"),
                max_score=item.get("max_score"),
                weight=item.get("weight", 1.0),
                comment=item.get("comment"),
                evidence=item.get("evidence"),
                answered_by=getattr(actor, "id", None),
                answered_at=None,
            )

        executive = self.executive_repo.upsert(
            assessment_id=assessment.id,
            summary_text=executive_payload.get("summary_text"),
            strengths_text=executive_payload.get("strengths_text"),
            gaps_text=executive_payload.get("gaps_text"),
            recommendations_text=executive_payload.get("recommendations_text"),
            updated_by=getattr(actor, "id", None),
        )

        for item in recommendations_payload:
            self.recommendation_repo.create(
                assessment_id=assessment.id,
                domain_code=item.get("domain_code"),
                domain_name=item.get("domain_name"),
                question_code=item.get("question_code"),
                title=item.get("title"),
                description=item.get("description"),
                priority=item.get("priority", "medium"),
                status=item.get("status", "open"),
                source=item.get("source", "import"),
                score=item.get("score"),
                updated_by=getattr(actor, "id", None),
            )

        self.session.commit()
        return executive

    def export_sqlite_db(self, actor) -> bytes:
        require_role(actor, "admin")

        db_path = Path("assessment.db")
        if not db_path.exists():
            raise FileNotFoundError("assessment.db nu exista.")

        return db_path.read_bytes()

    def import_sqlite_db(self, actor, db_bytes: bytes):
        require_role(actor, "admin")

        db_path = Path("assessment.db")
        backup_path = Path("assessment.db.bak")

        if db_path.exists():
            shutil.copy2(db_path, backup_path)

        db_path.write_bytes(db_bytes)
        return str(db_path)
