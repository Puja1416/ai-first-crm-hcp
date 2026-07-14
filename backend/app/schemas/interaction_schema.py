from datetime import date, datetime, time
from pydantic import BaseModel, ConfigDict, Field


class InteractionCreate(BaseModel):
    hcp_id: int
    interaction_type: str = "Meeting"
    interaction_date: date
    interaction_time: time
    attendees: str = ""
    topics_discussed: str = Field(min_length=3)
    materials_shared: str = ""
    samples_distributed: str = ""
    sentiment: str = "Neutral"
    outcomes: str = ""
    follow_up_actions: str = ""


class InteractionUpdate(BaseModel):
    interaction_type: str | None = None
    interaction_date: date | None = None
    interaction_time: time | None = None
    attendees: str | None = None
    topics_discussed: str | None = None
    materials_shared: str | None = None
    samples_distributed: str | None = None
    sentiment: str | None = None
    outcomes: str | None = None
    follow_up_actions: str | None = None
    ai_summary: str | None = None


class InteractionResponse(InteractionCreate):
    id: int
    ai_summary: str
    created_at: datetime
    updated_at: datetime
    hcp_name: str = ""

    model_config = ConfigDict(from_attributes=True)


class ChatRequest(BaseModel):
    message: str = Field(min_length=2)


class ChatResponse(BaseModel):
    action: str
    message: str
    data: dict | list | None = None
