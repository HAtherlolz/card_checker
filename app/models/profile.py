from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Profile(Base):
    __tablename__ = "profiles"

    id: Mapped[int] = mapped_column(
        "id", autoincrement=True, nullable=False, unique=True, primary_key=True, index=True
    )
    email: Mapped[str] = mapped_column("email", String(55), unique=True, nullable=False, index=True)
    password: Mapped[str] = mapped_column("password", String(255), nullable=False)
