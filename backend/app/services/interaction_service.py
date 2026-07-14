from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.hcp import HCP
from app.models.interaction import Interaction
from app.schemas.interaction_schema import InteractionCreate, InteractionUpdate


def seed_hcps(db: Session) -> None:
    exists = db.scalar(select(HCP.id).limit(1))
    if exists:
        return

    db.add_all(
        [
            HCP(name="Dr. Ananya Sharma", specialty="Cardiology", organization="City Heart Hospital", city="Pune"),
            HCP(name="Dr. Rohan Mehta", specialty="Endocrinology", organization="Metro Care Clinic", city="Mumbai"),
            HCP(name="Dr. Priya Nair", specialty="Oncology", organization="LifeSpring Hospital", city="Bengaluru"),
            HCP(name="Dr. Vivek Patil", specialty="General Medicine", organization="Sahyadri Clinic", city="Nashik"),
        ]
    )
    db.commit()


def search_hcps(db: Session, query: str) -> list[HCP]:
    pattern = f"%{query.strip()}%"
    statement = (
        select(HCP)
        .where(
            or_(
                HCP.name.ilike(pattern),
                HCP.specialty.ilike(pattern),
                HCP.organization.ilike(pattern),
                HCP.city.ilike(pattern),
            )
        )
        .order_by(HCP.name)
        .limit(20)
    )
    return list(db.scalars(statement).all())


def list_hcps(db: Session) -> list[HCP]:
    return list(db.scalars(select(HCP).order_by(HCP.name)).all())


def get_hcp(db: Session, hcp_id: int) -> HCP | None:
    return db.get(HCP, hcp_id)


def create_interaction(db: Session, payload: InteractionCreate, ai_summary: str = "") -> Interaction:
    interaction = Interaction(**payload.model_dump(), ai_summary=ai_summary)
    db.add(interaction)
    db.commit()
    db.refresh(interaction)
    return interaction


def get_interaction(db: Session, interaction_id: int) -> Interaction | None:
    return db.get(Interaction, interaction_id)


def list_interactions(db: Session) -> list[Interaction]:
    statement = select(Interaction).order_by(Interaction.created_at.desc())
    return list(db.scalars(statement).all())


def update_interaction(
    db: Session,
    interaction: Interaction,
    payload: InteractionUpdate,
) -> Interaction:
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(interaction, key, value)
    db.add(interaction)
    db.commit()
    db.refresh(interaction)
    return interaction


def serialize_interaction(interaction: Interaction) -> dict:
    return {
        "id": interaction.id,
        "hcp_id": interaction.hcp_id,
        "hcp_name": interaction.hcp.name if interaction.hcp else "",
        "interaction_type": interaction.interaction_type,
        "interaction_date": interaction.interaction_date.isoformat(),
        "interaction_time": interaction.interaction_time.isoformat(),
        "attendees": interaction.attendees,
        "topics_discussed": interaction.topics_discussed,
        "materials_shared": interaction.materials_shared,
        "samples_distributed": interaction.samples_distributed,
        "sentiment": interaction.sentiment,
        "outcomes": interaction.outcomes,
        "follow_up_actions": interaction.follow_up_actions,
        "ai_summary": interaction.ai_summary,
        "created_at": interaction.created_at.isoformat(),
        "updated_at": interaction.updated_at.isoformat(),
    }
