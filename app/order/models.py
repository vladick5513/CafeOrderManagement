from sqlalchemy import Column, String, Integer, JSON, Float
from enum import Enum as PyEnum
from app.database import Base

class OrderStatus(str, PyEnum):
    PENDING = "в ожидании"
    READY = "готово"
    PAID = "оплачено"

class Order(Base):
    id = Column(Integer, primary_key=True, index=True)
    table_number = Column(Integer, nullable=False)
    items = Column(JSON, nullable=False)  # Список блюд с ценами
    total_price = Column(Float, nullable=False)
    status = Column(String, nullable=False, default=OrderStatus.PENDING)

    def to_dict(self):
        """Преобразует SQLAlchemy модель в словарь."""
        return {
            "id": self.id,
            "table_number": self.table_number,
            "items": self.items,
            "total_price": self.total_price,
            "status": self.status
        }
