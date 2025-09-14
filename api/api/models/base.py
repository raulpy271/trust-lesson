from functools import cache
from datetime import datetime

from sqlmodel import SQLModel, Field
from sqlalchemy.inspection import inspect
from sqlalchemy import event
from sqlalchemy.orm import RelationshipDirection, selectinload
from sqlalchemy.ext.asyncio import AsyncAttrs
from pydantic import create_model
from pydantic_core import PydanticUndefined

from api.utils import set_dict_to_tuple


class Base(AsyncAttrs, SQLModel):
    __exclude__ = ()

    """
    Creates a response model to use on `response_model` route parameter.

    This method is usefull because it creates a model excluding undesired fields and
    including relationship fields.

    Besides, the returned model is cached to avoid creating different models for
    responses with same fields and relationships.
    """

    @classmethod
    def response_model(
        cls, relationships: set[str] | dict[str, dict | set[str]] = set()
    ):
        relationships_tuple = set_dict_to_tuple(relationships)
        return cls._cached_response_model(relationships_tuple)

    """
    Create a Load object to include a set of relationships of a given model inside
    a query using the parameter `options`.

    Example:
    session.get(Model, model_id,
        options=Model.selectload({"model_relation_a", "model_relation_b"})
    )

    The statement above will load the model entity and his relationships
    `model_relation_a` and `model_relation_b`.

    This method is usefull because it also accept a nested structure of relationships.
    """

    @classmethod
    def selectload(cls, relationships: set[str] | dict[str, dict | set[str]] = set()):
        if isinstance(relationships, set):
            relationships = {r: {} for r in relationships}
        mapper = inspect(cls).mapper
        subloads = []
        for rel, subrel in relationships.items():
            if rel in mapper.relationships:
                entity = mapper.relationships[rel].entity.entity
                opts = entity.selectload(subrel)
                if opts:
                    load = selectinload(getattr(cls, rel)).options(*opts)
                else:
                    load = selectinload(getattr(cls, rel))
                subloads.append(load)
            else:
                raise ValueError(f"Relation {rel} doesn't exist")
        return tuple(subloads)

    @classmethod
    @cache
    def _cached_response_model(cls, relationships: tuple = tuple()):
        fields = cls._model_fields_response()
        relationships = tuple(
            (rel, ()) if isinstance(rel, str) else rel for rel in relationships
        )
        name: str = cls.__name__ + "Out"
        if relationships:
            name += " with: " + ", ".join(map(lambda r: r[0], relationships))
        mapper = inspect(cls).mapper
        for rel, subrel in relationships:
            if rel in mapper.relationships:
                entity = mapper.relationships[rel].entity.entity
                res = entity._cached_response_model(subrel)
                if (
                    mapper.relationships[rel].direction
                    == RelationshipDirection.MANYTOONE
                ):
                    fields[rel] = res
                else:
                    fields[rel] = list[res]
            else:
                raise ValueError(f"Relation {rel} doesn't exist")
        return create_model(name, **fields)

    @classmethod
    def _model_fields_response(cls) -> dict:
        fields = {}
        for key, info in cls.model_fields.items():
            if key in cls.__exclude__:
                continue
            if info.default is not PydanticUndefined:
                fields[key] = (info.annotation, info.default)
            else:
                fields[key] = info.annotation
        for key, info in cls.model_computed_fields.items():
            fields[key] = info.return_type
        return fields


class TimestempMixin:
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    def __init_subclass__(cls):
        @event.listens_for(cls, "before_update")
        def update_updated_at(_mapper, connection, instance):
            instance.updated_at = datetime.now()
