from datetime import datetime, timedelta, timezone

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):

    pass


db = SQLAlchemy(model_class=Base)


class Subject(db.Model):
    __tablename__ = "subject"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)


class Session(db.Model):
    __tablename__ = "session"

    id: Mapped[int] = mapped_column(primary_key=True)
    subject_id: Mapped[int] = mapped_column(
        ForeignKey("subject.id", ondelete="CASCADE")
    )
    duration: Mapped[int]
    created_at: Mapped[datetime] = mapped_column(
        default=datetime.now(tz=timezone(timedelta(hours=9))),
    )


def obj_to_dict(obj):
    data = {}
    for column in obj.__mapper__.columns:
        key = column.key
        value = getattr(obj, column.key)
        if isinstance(value, datetime):
            value = value.isoformat()
        data[key] = value
    return data
