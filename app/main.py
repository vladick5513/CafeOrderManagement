from fastapi import FastAPI
from app.order.router import router as order_router

app = FastAPI()
app.include_router(order_router)
