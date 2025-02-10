from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional

from app.order.models import OrderStatus


class SOrderItem(BaseModel):
    name: str = Field(..., description="Название блюда")
    price: float = Field(..., ge=0, description="Цена блюда")

class SOrderAdd(BaseModel):
    table_number: int = Field(..., gt=0, description="Номер стола")
    items: List[SOrderItem] = Field(..., description="Список заказанных блюд")

class SOrderUpdate(BaseModel):
    table_number: Optional[int] = Field(None, gt=0, description="Номер стола")
    items: Optional[List[SOrderItem]] = Field(None, description="Список заказанных блюд")

class SOrderStatus(BaseModel):
    status: str = Field(..., description="Статус заказа", choices=["в ожидании", "готово", "оплачено"])

class SOrder(BaseModel):
    id: int
    table_number: int
    items: List[SOrderItem]
    total_price: float
    status: OrderStatus

    class Config:
        from_attributes = True  # Это позволит конвертировать SQLAlchemy модель в Pydantic

class SOrderResponse(BaseModel):
    message: str
    order: SOrder
