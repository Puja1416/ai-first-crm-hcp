from pydantic import BaseModel, ConfigDict


class HCPResponse(BaseModel):
    id: int
    name: str
    specialty: str
    organization: str
    city: str

    model_config = ConfigDict(from_attributes=True)
