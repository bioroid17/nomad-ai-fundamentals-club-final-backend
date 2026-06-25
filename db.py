from datetime import datetime, timedelta, timezone

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):

    pass


db = SQLAlchemy(model_class=Base)


class Subject(db.Model):
    __tablename__ = "subject"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
        }


class Session(db.Model):
    __tablename__ = "session"

    id: Mapped[int] = mapped_column(primary_key=True)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subject.id"))
    duration: Mapped[int]
    created_at: Mapped[datetime] = mapped_column(
        default=datetime.now(tz=timezone(timedelta(hours=9)))
    )

    def to_dict(self):
        return {
            "id": self.id,
            "subject_id": self.subject_id,
            "duration": self.duration,
            "created_at": self.created_at,
        }


def obj_to_dict(obj):
    data = {}
    for column in obj.__mapper__.columns:
        key = column.key
        value = getattr(obj, column.key)
        if isinstance(value, datetime):
            value = value.isoformat()
        data[key] = value
    return data
