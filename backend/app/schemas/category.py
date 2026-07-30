import uuid

from pydantic import BaseModel, ConfigDict, Field

from app.models.category import CategoryType


class CategoryCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=100)
    emoji: str | None = None
    parent_category_id: uuid.UUID | None = None
    category_type: CategoryType
    is_shared: bool = False


class CategoryUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(default=None, min_length=1, max_length=100)
    emoji: str | None = None
    parent_category_id: uuid.UUID | None = None
    is_shared: bool | None = None


class CategorySharingUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    is_shared: bool


class CategoryPublic(BaseModel):
    id: uuid.UUID
    name: str
    emoji: str | None
    parent_category_id: uuid.UUID | None
    category_type: CategoryType
    is_shared: bool
    is_default: bool
    is_active: bool
