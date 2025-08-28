from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(nullable=True)
    image: Mapped[str | None] = mapped_column(String(500), nullable=True)
    layout: Mapped[str] = mapped_column(String(20), default="products")
    is_active: Mapped[bool] = mapped_column(default=True)

    parent = relationship("Category", remote_side="Category.id") 