from datetime import datetime

from sqlalchemy.inspection import inspect
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
)


class Base(DeclarativeBase):
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
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.now, onupdate=datetime.now
    )
