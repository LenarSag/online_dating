from datetime import date, datetime
from enum import Enum as PyEnum
import re
import uuid

from sqlalchemy import (
    Column,
    Date,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    func,
    String,
    Table,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from app.models.base import Base


user_tag = Table(
    'user_tag',
    Base.metadata,
    Column('user_id', ForeignKey('user.id', ondelete='CASCADE'), primary_key=True),
    Column('tag_id', ForeignKey('tag.id', ondelete='CASCADE'), primary_key=True),
)


class UserSex(PyEnum):
    MALE = 'male'
    FEMALE = 'female'


class User(Base):
    __tablename__ = 'user'

    id: Mapped[PG_UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(
        String(150), unique=True, nullable=False, index=True
    )
    password: Mapped[str] = mapped_column(nullable=False)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    sex: Mapped[UserSex] = mapped_column(
        Enum(UserSex, values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
    )
    birth_date: Mapped[date] = mapped_column(Date, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    last_online: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    location: Mapped['Location'] = relationship(
        back_populates='user', cascade='all, delete-orphan'
    )
    tags: Mapped[list['Tag']] = relationship(
        'Tag', secondary=user_tag, back_populates='users'
    )

    @validates('email')
    def validate_email(self, key, email):
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not re.match(email_regex, email):
            raise ValueError('Invalid email format')
        return email

    @validates('first_name')
    def validate_first_name(self, key, first_name):
        username_regex = r'^[\w.@+-]+$'
        if not re.match(username_regex, first_name):
            raise ValueError('First name is invalid')
        return first_name

    @validates('last_name')
    def validate_last_name(self, key, last_name):
        username_regex = r'^[\w.@+-]+$'
        if not re.match(username_regex, last_name):
            raise ValueError('Last name is invalid')
        return last_name

    @validates('birth_date')
    def validate_birth_date(self, key, birth_date):
        today = date.today()
        age = (
            today.year
            - birth_date.year
            - ((today.month, today.day) < (birth_date.month, birth_date.day))
        )

        if age < 18:
            raise ValueError('Age must be at least 18 years old.')
        elif age > 100:
            raise ValueError('Age must not be older than 100 years.')
        return birth_date

    def __str__(self) -> str:
        return self.email


class Location(Base):
    __tablename__ = 'location'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id', ondelete='CASCADE'))
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)

    user: Mapped['User'] = relationship(back_populates='location')

    __table_args__ = (UniqueConstraint('user_id', name='location_user_id'),)

    @validates('latitude')
    def validate_latitude(self, key, latitude):
        if latitude < -90 or latitude > 90:
            raise ValueError('Latitude must be between -90 and 90.')
        return latitude

    @validates('longitude')
    def validate_longitude(self, key, longitude):
        if longitude < -180 or longitude > 180:
            raise ValueError('Longitude must be between -180 and 180.')
        return longitude


class Tag(Base):
    __tablename__ = 'tag'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    slug: Mapped[str] = mapped_column(String(50), unique=True)

    users: Mapped[list['User']] = relationship(
        'User', secondary=user_tag, back_populates='tags'
    )

    __table_args__ = (UniqueConstraint('name', 'slug', name='tag_name_slug'),)
