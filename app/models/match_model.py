from sqlalchemy import Date, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from app.models.base import Base


class Match(Base):
    __tablename__ = 'match'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[PG_UUID] = mapped_column(ForeignKey('user.id', ondelete='CASCADE'))
    matched_user_id: Mapped[PG_UUID] = mapped_column(
        ForeignKey('user.id', ondelete='CASCADE')
    )
    is_mutual: Mapped[bool] = mapped_column(default=False)
    matched_at: Mapped[Date] = mapped_column(Date, default=func.current_date())

    user = relationship(
        'User', foreign_keys=[user_id], back_populates='initiated_matches'
    )
    matched_user = relationship(
        'User', foreign_keys=[matched_user_id], back_populates='received_matches'
    )
