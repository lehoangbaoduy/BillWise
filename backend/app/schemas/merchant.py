import uuid

from pydantic import BaseModel, ConfigDict, Field


class MerchantCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=200)
    type: str | None = Field(default=None, max_length=100)
    city: str | None = Field(default=None, max_length=100)
    state: str | None = Field(default=None, max_length=100)
    notes: str | None = Field(default=None, max_length=1000)


class MerchantUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(default=None, min_length=1, max_length=200)
    type: str | None = Field(default=None, max_length=100)
    city: str | None = Field(default=None, max_length=100)
    state: str | None = Field(default=None, max_length=100)
    notes: str | None = Field(default=None, max_length=1000)


class MerchantSharingUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    is_shared: bool


class MerchantPublic(BaseModel):
    id: uuid.UUID
    name: str
    type: str | None
    city: str | None
    state: str | None
    notes: str | None
    is_shared: bool
    is_active: bool
