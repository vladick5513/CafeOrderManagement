from app.dao.base import BaseDAO
from app.order.models import Order


class OrderDAO(BaseDAO):
    model = Order