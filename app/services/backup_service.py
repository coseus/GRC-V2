from __future__ import annotations

import json
import shutil
from io import BytesIO
from pathlib import Path

from app.db.models import Assessment, Company
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

    def import_assessment_json(self, actor, *, company, assessment, json_bytes: bytes):
        require_role(actor, "auditor")

        from app.db.models import Answer, Recommendation

        payload = json.loads(json_bytes.decode("utf-8"))

        answers = payload.get("answers", [])
        executive_payload = payload.get("executive_summary", {})
        recommendations_payload = payload.get("recommendations", [])

        self.session.query(Answer).filter(Answer.assessment_id == assessment.id).delete(synchronize_session=False)
        self.session.query(Recommendation).filter(Recommendation.assessment_id == assessment.id).delete(synchronize_session=False)

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

        return json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")

    def import_assessment_json(self, actor, *, company, assessment, json_bytes: bytes):
        require_role(actor, "auditor")

        payload = json.loads(json_bytes.decode("utf-8"))

        answers = payload.get("answers", [])
        executive_payload = payload.get("executive_summary", {})
        recommendations_payload = payload.get("recommendations", [])

        # answers
        self.session.query(type(self.answer_repo.list_for_assessment(assessment.id)[0]) if self.answer_repo.list_for_assessment(assessment.id) else None)
        existing_answers = self.answer_repo.list_for_assessment(assessment.id)
        for a in existing_answers:
            self.session.delete(a)

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

        self.recommendation_repo.delete_for_assessment(assessment.id)
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
