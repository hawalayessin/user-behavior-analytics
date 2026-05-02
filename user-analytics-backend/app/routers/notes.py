from datetime import date
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.analyst_notes import AnalystNoteCreate, AnalystNoteResponse, AnalystNoteUpdate
from app.services import note_service


router = APIRouter(prefix="/notes", tags=["Analyst Notes"])


@router.post("", response_model=AnalystNoteResponse)
def create_note(
    payload: AnalystNoteCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    return note_service.create_note(db, user=user, payload=payload)


@router.get("", response_model=list[AnalystNoteResponse])
def list_notes(
    service_id: Optional[UUID] = Query(default=None),
    metric: Optional[str] = Query(default=None),
    period_start: Optional[date] = Query(default=None),
    period_end: Optional[date] = Query(default=None),
    analyst_id: Optional[UUID] = Query(default=None),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    return note_service.list_notes(
        db,
        user=user,
        service_id=service_id,
        metric=metric,
        period_start=period_start,
        period_end=period_end,
        analyst_id=analyst_id,
    )


@router.get("/{note_id}", response_model=AnalystNoteResponse)
def get_note(
    note_id: UUID,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    return note_service.get_note(db, note_id=note_id, user=user)


@router.put("/{note_id}", response_model=AnalystNoteResponse)
def update_note(
    note_id: UUID,
    payload: AnalystNoteUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    return note_service.update_note(db, note_id=note_id, user=user, payload=payload)


@router.delete("/{note_id}")
def delete_note(
    note_id: UUID,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    note_service.delete_note(db, note_id=note_id, user=user)
    return {"message": "Note deleted"}


@router.get("/context", response_model=list[AnalystNoteResponse])
def get_context_notes(
    service_id: Optional[UUID] = Query(default=None),
    period_start: Optional[date] = Query(default=None),
    period_end: Optional[date] = Query(default=None),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    return note_service.get_context_notes(
        db,
        user=user,
        service_id=service_id,
        period_start=period_start,
        period_end=period_end,
    )
