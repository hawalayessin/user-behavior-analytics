from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Iterable, Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.analyst_note import AnalystNote
from app.models.campaigns import Campaign
from app.models.platform_users import PlatformUser
from app.models.services import Service
from app.schemas.analyst_notes import AnalystNoteCreate, AnalystNoteUpdate, AnalystNoteResponse


class NoteAccessError(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized access to analyst notes.",
        )


def _note_query(db: Session):
    return (
        db.query(
            AnalystNote,
            PlatformUser.full_name.label("analyst_name"),
            Service.name.label("service_name"),
            Campaign.name.label("campaign_name"),
        )
        .join(PlatformUser, PlatformUser.id == AnalystNote.analyst_id)
        .outerjoin(Service, Service.id == AnalystNote.service_id)
        .outerjoin(Campaign, Campaign.id == AnalystNote.campaign_id)
    )


def _to_response(row) -> AnalystNoteResponse:
    note, analyst_name, service_name, campaign_name = row
    return AnalystNoteResponse(
        id=note.id,
        analyst_id=note.analyst_id,
        analyst_name=analyst_name,
        service_id=note.service_id,
        service_name=service_name,
        campaign_id=note.campaign_id,
        campaign_name=campaign_name,
        metric=note.metric,
        period_start=note.period_start,
        period_end=note.period_end,
        content=note.content,
        created_at=note.created_at,
        updated_at=note.updated_at,
    )


def create_note(
    db: Session,
    *,
    user: PlatformUser,
    payload: AnalystNoteCreate,
) -> AnalystNoteResponse:
    note = AnalystNote(
        analyst_id=user.id,
        service_id=payload.service_id,
        campaign_id=payload.campaign_id,
        metric=payload.metric,
        period_start=payload.period_start,
        period_end=payload.period_end,
        content=payload.content,
    )
    db.add(note)
    db.commit()
    return get_note(db, note_id=note.id, user=user)


def list_notes(
    db: Session,
    *,
    user: PlatformUser,
    service_id: Optional[UUID] = None,
    metric: Optional[str] = None,
    period_start: Optional[date] = None,
    period_end: Optional[date] = None,
    analyst_id: Optional[UUID] = None,
) -> list[AnalystNoteResponse]:
    query = _note_query(db)

    if user.role == "analyst":
        query = query.filter(AnalystNote.analyst_id == user.id)
    elif analyst_id:
        query = query.filter(AnalystNote.analyst_id == analyst_id)

    if service_id:
        query = query.filter(AnalystNote.service_id == service_id)

    if metric:
        query = query.filter(AnalystNote.metric == metric)

    if period_start:
        query = query.filter(
            or_(AnalystNote.period_end.is_(None), AnalystNote.period_end >= period_start)
        )
    if period_end:
        query = query.filter(
            or_(AnalystNote.period_start.is_(None), AnalystNote.period_start <= period_end)
        )

    rows = query.order_by(AnalystNote.created_at.desc()).all()
    return [_to_response(row) for row in rows]


def get_note(
    db: Session,
    *,
    note_id: UUID,
    user: PlatformUser,
) -> AnalystNoteResponse:
    row = _note_query(db).filter(AnalystNote.id == note_id).first()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")

    note = row[0]
    if user.role == "analyst" and note.analyst_id != user.id:
        raise NoteAccessError()

    return _to_response(row)


def update_note(
    db: Session,
    *,
    note_id: UUID,
    user: PlatformUser,
    payload: AnalystNoteUpdate,
) -> AnalystNoteResponse:
    note = db.query(AnalystNote).filter(AnalystNote.id == note_id).first()
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")

    if user.role == "analyst" and note.analyst_id != user.id:
        raise NoteAccessError()

    if payload.service_id is not None:
        note.service_id = payload.service_id
    if payload.campaign_id is not None:
        note.campaign_id = payload.campaign_id
    if payload.metric is not None:
        note.metric = payload.metric
    if payload.period_start is not None:
        note.period_start = payload.period_start
    if payload.period_end is not None:
        note.period_end = payload.period_end
    if payload.content is not None:
        note.content = payload.content

    note.updated_at = datetime.now(timezone.utc)
    db.commit()
    return get_note(db, note_id=note.id, user=user)


def delete_note(
    db: Session,
    *,
    note_id: UUID,
    user: PlatformUser,
) -> None:
    note = db.query(AnalystNote).filter(AnalystNote.id == note_id).first()
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")

    if user.role == "analyst" and note.analyst_id != user.id:
        raise NoteAccessError()

    db.delete(note)
    db.commit()


def get_context_notes(
    db: Session,
    *,
    user: PlatformUser,
    service_id: Optional[UUID],
    period_start: Optional[date],
    period_end: Optional[date],
) -> list[AnalystNoteResponse]:
    query = _note_query(db)

    if user.role == "analyst":
        query = query.filter(AnalystNote.analyst_id == user.id)

    if service_id:
        query = query.filter(AnalystNote.service_id == service_id)

    if period_start:
        query = query.filter(
            or_(AnalystNote.period_end.is_(None), AnalystNote.period_end >= period_start)
        )
    if period_end:
        query = query.filter(
            or_(AnalystNote.period_start.is_(None), AnalystNote.period_start <= period_end)
        )

    rows = query.order_by(AnalystNote.created_at.desc()).all()
    return [_to_response(row) for row in rows]
