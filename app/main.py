from fastapi import FastAPI
from app.order.router import router as order_router
from app.pages.router import router as page_router

app = FastAPI()
app.include_router(order_router)
app.include_router(page_router)
