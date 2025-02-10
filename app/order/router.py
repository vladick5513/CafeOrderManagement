from fastapi import APIRouter, HTTPException
from app.order.dao import OrderDAO
from app.order.schemas import SOrderAdd, SOrderUpdate, SOrderStatus, SOrderResponse, SOrder
from typing import Optional

router = APIRouter(
    prefix="/orders",
    tags=["Управление заказами"]
)


@router.post("/add/", response_model=SOrderResponse)
async def add_order(order: SOrderAdd) -> SOrderResponse:
    """
    Добавление нового заказа
    - Принимает номер стола и список блюд с ценами
    - Автоматически рассчитывает общую стоимость
    - Устанавливает начальный статус "в ожидании"
    """
    try:
        new_order = await OrderDAO.add(**order.model_dump())
        return SOrderResponse(
            message="Заказ успешно создан!",
            order=SOrder(**new_order)  # Создаем Pydantic модель из словаря
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка при создании заказа: {str(e)}")


@router.get("/all/")
async def get_all_orders() -> SOrderResponse | dict:
    """
    Получение списка всех заказов
    Возвращает таблицу со всеми заказами
    """
    try:
        orders = await OrderDAO.find_all()
        return {
            "message": "Список заказов успешно получен",
            "orders": orders
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка при получении списка заказов: {str(e)}")


@router.get("/search/")
async def search_orders(
        table_number: Optional[int] = None,
        status: Optional[str] = None
) -> SOrderResponse | dict:
    """
    Поиск заказов по номеру стола или статусу.
    """
    try:
        if table_number is not None:
            orders = await OrderDAO.find_by_table_number(table_number)
            if not orders:
                raise HTTPException(status_code=404, detail=f"Заказов с номером стола {table_number} не найдено.")
        elif status is not None:
            orders = await OrderDAO.find_by_status(status)
            if not orders:
                raise HTTPException(status_code=404, detail=f"Заказов со статусом '{status}' не найдено.")
        else:
            orders = await OrderDAO.find_all()

        return {
            "message": "Поиск выполнен успешно",
            "orders": orders
        }
    except HTTPException:
        raise  # Пропускаем явно обработанные ошибки
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка при поиске заказов: {str(e)}")



@router.get("/{order_id}")
async def get_order(order_id: int) -> SOrderResponse | dict:
    """
    Получение информации о конкретном заказе по ID
    """
    order = await OrderDAO.find_one_or_none_by_id(order_id)
    if not order:
        raise HTTPException(status_code=404, detail=f"Заказ с ID {order_id} не найден")
    return {
        "message": "Заказ найден",
        "order": order
    }


@router.put("/update_status/{order_id}")
async def update_order_status(order_id: int, status_update: SOrderStatus) -> dict:
    """
    Обновление статуса заказа
    Допустимые статусы: "в ожидании", "готово", "оплачено"
    """
    try:
        check = await OrderDAO.update_status(order_id, status_update.status)
        if check:
            return {
                "message": f"Статус заказа {order_id} успешно обновлен!",
                "new_status": status_update.status
            }
        else:
            raise HTTPException(status_code=404, detail=f"Заказ с ID {order_id} не найден")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка при обновлении статуса: {str(e)}")


@router.put("/update/{order_id}")
async def update_order(order_id: int, order: SOrderUpdate) -> dict:
    """
    Обновление информации о заказе
    """
    try:
        check = await OrderDAO.update({"id": order_id}, **order.model_dump(exclude_unset=True))
        if check:
            return {
                "message": f"Заказ {order_id} успешно обновлен!",
                "updated_data": order
            }
        else:
            raise HTTPException(status_code=404, detail=f"Заказ с ID {order_id} не найден")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка при обновлении заказа: {str(e)}")


@router.delete("/delete/{order_id}")
async def delete_order(order_id: int) -> dict:
    """
    Удаление заказа по ID
    """
    try:
        check = await OrderDAO.delete(id=order_id)
        if check:
            return {"message": f"Заказ с ID {order_id} успешно удален!"}
        else:
            raise HTTPException(status_code=404, detail=f"Заказ с ID {order_id} не найден")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка при удалении заказа: {str(e)}")


@router.get("/revenue/total/")
async def get_total_revenue() -> dict:
    """
    Получение общей выручки по оплаченным заказам
    """
    try:
        revenue = await OrderDAO.calculate_revenue()
        return {
            "message": "Выручка успешно рассчитана",
            "total_revenue": revenue
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка при расчете выручки: {str(e)}")