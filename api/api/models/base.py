from datetime import datetime

from sqlmodel import SQLModel, Field
from sqlalchemy.inspection import inspect
from sqlalchemy import event
from sqlalchemy.orm import DeclarativeBase


class Base(SQLModel):
    __exclude__ = ()

    def to_dict(self):
        instance = inspect(self)
        mapper = instance.mapper
        cols = mapper.column_attrs
        d = {c.key: getattr(self, c.key) for c in cols if c not in self.__exclude__}
        for key in mapper.relationships.keys():
            if key not in instance.unloaded:
                relation = getattr(self, key)
                if isinstance(relation, list):
                    d[key] = [r.to_dict() for r in relation]
                elif isinstance(relation, DeclarativeBase):
                    d[key] = relation.to_dict()
        return d


class TimestempMixin:
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    def __init_subclass__(cls):
        @event.listens_for(cls, "before_update")
        def update_updated_at(_mapper, connection, instance):
            instance.updated_at = datetime.now()
