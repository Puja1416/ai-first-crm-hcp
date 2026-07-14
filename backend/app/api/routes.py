from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.agents.langgraph_agent import run_agent
from app.database.db import get_db
from app.schemas.hcp_schema import HCPResponse
from app.schemas.interaction_schema import (
    ChatRequest,
    ChatResponse,
    InteractionCreate,
    InteractionResponse,
    InteractionUpdate,
)
from app.services.interaction_service import (
    create_interaction,
    get_interaction,
    list_hcps,
    list_interactions,
    search_hcps,
    serialize_interaction,
    update_interaction,
)

router = APIRouter(prefix="/api")


@router.get("/hcps", response_model=list[HCPResponse])
def get_hcps(
    q: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    return search_hcps(db, q) if q else list_hcps(db)


@router.get("/interactions")
def get_interactions(db: Session = Depends(get_db)):
    return [serialize_interaction(item) for item in list_interactions(db)]


@router.post("/interactions", status_code=201)
def post_interaction(payload: InteractionCreate, db: Session = Depends(get_db)):
    item = create_interaction(db, payload)
    return serialize_interaction(item)


@router.patch("/interactions/{interaction_id}")
def patch_interaction(
    interaction_id: int,
    payload: InteractionUpdate,
    db: Session = Depends(get_db),
):
    item = get_interaction(db, interaction_id)
    if not item:
        raise HTTPException(status_code=404, detail="Interaction not found")
    return serialize_interaction(update_interaction(db, item, payload))


@router.post("/agent/chat", response_model=ChatResponse)
def agent_chat(payload: ChatRequest, db: Session = Depends(get_db)):
    try:
        return run_agent(db, payload.message)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
