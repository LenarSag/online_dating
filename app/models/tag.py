from sqlalchemy import (
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)
from app.models.base import Base


class Tag(Base):
    __tablename__ = 'tag'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    slug: Mapped[str] = mapped_column(String(50), unique=True)

    users: Mapped[list['User']] = relationship(
        'User', secondary='user_tag', back_populates='tags'
    )

    __table_args__ = (UniqueConstraint('name', 'slug', name='tag_name_slug'),)
