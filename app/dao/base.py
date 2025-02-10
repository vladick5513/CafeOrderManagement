from sqlalchemy import select, update as sqlalchemy_update, delete as sqlalchemy_delete, func
from sqlalchemy.exc import SQLAlchemyError
from app.database import async_session_factory

class BaseDAO:
    model = None

    @classmethod
    async def find_one_or_none_by_id(cls, data_id: int):
        """Поиск записи по ID"""
        async with async_session_factory() as session:
            query = select(cls.model).filter_by(id=data_id)
            result = await session.execute(query)
            order = result.scalar_one_or_none()
            if order:
                return order.to_dict()  # Используем to_dict
            return None


    @classmethod
    async def find_all(cls, **filter_by):
        """Поиск всех записей с возможностью фильтрации"""
        async with async_session_factory() as session:
            query = select(cls.model).filter_by(**filter_by)
            result = await session.execute(query)
            orders = result.scalars().all()
            return [order.to_dict() for order in orders]  # Используем to_dict


    @classmethod
    async def add(cls, **values):
        """
        Добавление новой записи
        Для заказов: автоматически вычисляет общую стоимость и устанавливает статус "в ожидании"
        """
        async with async_session_factory() as session:
            if cls.model.__tablename__ == 'orders':
                # Вычисляем общую стоимость для заказов
                if 'items' in values:
                    values['total_price'] = sum(item['price'] for item in values['items'])
                values['status'] = 'в ожидании'  # Устанавливаем начальный статус

            new_instance = cls.model(**values)
            session.add(new_instance)
            try:
                await session.commit()
                # Получаем свежие данные из базы
                await session.refresh(new_instance)
                # Преобразуем SQLAlchemy модель в словарь
                return {
                    "id": new_instance.id,
                    "table_number": new_instance.table_number,
                    "items": new_instance.items,
                    "total_price": new_instance.total_price,
                    "status": new_instance.status
                }
            except SQLAlchemyError as e:
                await session.rollback()
                raise e



    @classmethod
    async def update(cls, filter_by, **values):
        """
        Обновление записи
        Для заказов: позволяет обновить статус и другие поля
        """
        async with async_session_factory() as session:
            async with session.begin():
                if cls.model.__tablename__ == 'orders':
                    # Проверяем корректность статуса при обновлении
                    if 'status' in values:
                        if values['status'] not in ['в ожидании', 'готово', 'оплачено']:
                            raise ValueError("Недопустимый статус заказа")

                    # Если обновляются позиции заказа, пересчитываем стоимость
                    if 'items' in values:
                        values['total_price'] = sum(item['price'] for item in values['items'])

                query = (
                    sqlalchemy_update(cls.model)
                    .where(*[getattr(cls.model, k) == v for k, v in filter_by.items()])
                    .values(**values)
                    .execution_options(synchronize_session="fetch")
                )
                result = await session.execute(query)
                try:
                    await session.commit()
                except SQLAlchemyError as e:
                    await session.rollback()
                    raise e
                return result.rowcount

    @classmethod
    async def delete(cls, delete_all: bool = False, **filter_by):
        """Удаление записи(ей)"""
        if delete_all is False:
            if not filter_by:
                raise ValueError("Необходимо указать хотя бы один параметр для удаления.")
        async with async_session_factory() as session:
            async with session.begin():
                query = sqlalchemy_delete(cls.model).filter_by(**filter_by)
                result = await session.execute(query)
                try:
                    await session.commit()
                except SQLAlchemyError as e:
                    await session.rollback()
                    raise e
                return result.rowcount

    @classmethod
    async def find_by_table_number(cls, table_number: int):
        """Поиск заказов по номеру стола"""
        async with async_session_factory() as session:
            query = select(cls.model).filter_by(table_number=table_number)
            result = await session.execute(query)
            orders = result.scalars().all()
            return [order.to_dict() for order in orders]  # Используем to_dict



    @classmethod
    async def find_by_status(cls, status: str):
        """Поиск заказов по статусу"""
        async with async_session_factory() as session:
            query = select(cls.model).filter_by(status=status)
            result = await session.execute(query)
            orders = result.scalars().all()
            return [order.to_dict() for order in orders]  # Используем to_dict


    @classmethod
    async def update_status(cls, order_id: int, new_status: str):
        """Обновление статуса заказа"""
        if new_status not in ['в ожидании', 'готово', 'оплачено']:
            raise ValueError("Недопустимый статус заказа")
        return await cls.update({"id": order_id}, status=new_status)

    @classmethod
    async def get_all_orders(cls):
        """Получение всех заказов для отображения в таблице"""
        async with async_session_factory() as session:
            query = select(cls.model).order_by(cls.model.id)
            result = await session.execute(query)
            orders = result.scalars().all()
            return [order.to_dict() for order in orders]  # Используем to_dict


    @classmethod
    async def calculate_revenue(cls):
        """
        Расчет общей выручки по оплаченным заказам
        Returns:
            float: Общая сумма выручки по оплаченным заказам
        """
        async with async_session_factory() as session:
            try:
                # Выбираем все заказы со статусом "оплачено" и суммируем их total_price
                query = (
                    select(func.sum(cls.model.total_price))
                    .where(cls.model.status == "оплачено")
                )
                result = await session.execute(query)
                total_revenue = result.scalar() or 0.0  # Если нет заказов, возвращаем 0
                return total_revenue
            except SQLAlchemyError as e:
                raise e