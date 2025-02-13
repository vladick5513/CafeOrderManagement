from fastapi import APIRouter, Request, Query
from fastapi.params import Depends
from fastapi.templating import Jinja2Templates
from typing import Optional

from app.order.router import (
    get_all_orders,
    search_orders,
    get_total_revenue
)


router = APIRouter(
    prefix="/pages",
    tags=["Фронтенд"]
)

templates = Jinja2Templates(directory="app/templates")

@router.get("/")
async def get_main_page(
    request: Request,
    orders_response = Depends(get_all_orders)
):
    """Главная страница со списком всех заказов"""
    print("Orders response:", orders_response)
    orders = orders_response.get("orders", [])
    return templates.TemplateResponse(
        "main.html",
        {
            "request": request,
            "orders": orders
        }
    )

@router.get("/add")
async def get_add_order_page(request: Request):
    """Страница добавления нового заказа"""
    return templates.TemplateResponse(
        "add_order.html",
        {"request": request}
    )


@router.get("/search")
async def get_search_page(
        request: Request,
        table_number: Optional[int] = Query(default=None),
        status: Optional[str] = Query(default=None),
        search_results=Depends(search_orders)
):
    """
    Страница поиска заказов

    Parameters:
    - table_number: Optional[int] - номер стола (может быть пустым)
    - status: Optional[str] - статус заказа (может быть пустым)
    """
    # Debug output to see what values we're receiving
    print(f"Search params - table_number: {table_number}, status: {status}")

    # Get orders from the search results
    orders = search_results.get("orders", [])

    return templates.TemplateResponse(
        "search.html",
        {
            "request": request,
            "orders": orders,
            "table_number": table_number,
            "status": status,
            "error_message": None
        }
    )

@router.get("/revenue")
async def get_revenue_page(
    request: Request,
    revenue = Depends(get_total_revenue)
):
    """Страница с информацией о выручке"""
    return templates.TemplateResponse(
        "revenue.html",
        {"request": request, "revenue": revenue.get("total_revenue", 0)}
    )