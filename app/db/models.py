"""
SQLAlchemy models — the Python-class representation of our tables.

Each class here maps directly to a table. Alembic's migration
(alembic/versions/0001_...) is what actually creates these tables in
Postgres; this file is what lets our Python code read/write rows as
objects instead of hand-writing SQL everywhere.

Phase 3 scope: just `Organization` and `User`, linked by a foreign key.
No password field yet — that's Phase 4 (Authentication). No roles,
permissions, or documents yet — those come in Phases 5-7.
"""

from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Every model inherits from this. SQLAlchemy uses it to track all
    tables that exist, so Alembic can compare 'what models say' vs
    'what the database actually has' when generating migrations."""
    pass


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Lets Python code do `some_org.users` to get every User belonging
    # to it, without writing a query by hand. This is an ORM convenience,
    # not a database column.
    users: Mapped[list["User"]] = relationship(back_populates="organization")


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    # The foreign key: this column must contain a value that exists as
    # an `id` in the organizations table, or the database rejects the
    # insert (see Phase 3 lesson, checkpoint question 2).
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    organization: Mapped["Organization"] = relationship(back_populates="users")
