from pydantic import BaseModel, ConfigDict


class LocationBase(BaseModel):
    latitude: float
    longitude: float

    model_config = ConfigDict(from_attributes=True)
