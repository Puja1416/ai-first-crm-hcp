from datetime import date, time
from langchain_core.tools import tool
from sqlalchemy.orm import Session

from app.schemas.interaction_schema import InteractionCreate, InteractionUpdate
from app.services.interaction_service import (
    create_interaction,
    get_interaction,
    search_hcps,
    serialize_interaction,
    update_interaction,
)


def build_tools(db: Session, summarize_fn, recommend_fn):
    @tool
    def search_hcp(query: str) -> dict:
        """Search healthcare professionals by name, specialty, organization, or city."""
        results = search_hcps(db, query)
        return {
            "count": len(results),
            "hcps": [
                {
                    "id": h.id,
                    "name": h.name,
                    "specialty": h.specialty,
                    "organization": h.organization,
                    "city": h.city,
                }
                for h in results
            ],
        }

    @tool
    def summarize_interaction(notes: str) -> dict:
        """Summarize free-text HCP interaction notes into a concise CRM-ready summary."""
        return {"summary": summarize_fn(notes)}

    @tool
    def recommend_follow_up(notes: str, sentiment: str = "Neutral") -> dict:
        """Recommend practical next actions for a field representative."""
        return {"recommendation": recommend_fn(notes, sentiment)}

    @tool
    def log_interaction(
        hcp_id: int,
        interaction_type: str,
        interaction_date: str,
        interaction_time: str,
        topics_discussed: str,
        attendees: str = "",
        materials_shared: str = "",
        samples_distributed: str = "",
        sentiment: str = "Neutral",
        outcomes: str = "",
        follow_up_actions: str = "",
    ) -> dict:
        """Create a new structured HCP interaction record."""
        summary = summarize_fn(topics_discussed)
        payload = InteractionCreate(
            hcp_id=hcp_id,
            interaction_type=interaction_type,
            interaction_date=date.fromisoformat(interaction_date),
            interaction_time=time.fromisoformat(interaction_time),
            attendees=attendees,
            topics_discussed=topics_discussed,
            materials_shared=materials_shared,
            samples_distributed=samples_distributed,
            sentiment=sentiment,
            outcomes=outcomes,
            follow_up_actions=follow_up_actions,
        )
        created = create_interaction(db, payload, ai_summary=summary)
        return serialize_interaction(created)

    @tool
    def edit_interaction(
        interaction_id: int,
        field: str,
        value: str,
    ) -> dict:
        """Edit one supported field on an existing interaction."""
        allowed = {
            "interaction_type",
            "attendees",
            "topics_discussed",
            "materials_shared",
            "samples_distributed",
            "sentiment",
            "outcomes",
            "follow_up_actions",
            "ai_summary",
        }
        if field not in allowed:
            return {"error": f"Unsupported field. Allowed fields: {sorted(allowed)}"}

        interaction = get_interaction(db, interaction_id)
        if not interaction:
            return {"error": "Interaction not found"}

        updated = update_interaction(
            db,
            interaction,
            InteractionUpdate(**{field: value}),
        )
        return serialize_interaction(updated)

    return {
        "search_hcp": search_hcp,
        "summarize_interaction": summarize_interaction,
        "recommend_follow_up": recommend_follow_up,
        "log_interaction": log_interaction,
        "edit_interaction": edit_interaction,
    }
