import uuid
from typing import TypeVar

from sqlalchemy import Column, Integer, String, ForeignKey, Numeric
from sqlalchemy.orm import relationship

from src.database.database import Base

ConcreteTable = TypeVar("ConcreteTable", bound=Base)


class UserSession(Base):
    __tablename__ = 'user_sessions'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    session_id = Column(String, index=True, unique=True)

    orders = relationship('Order', back_populates='user_session')


class Order(Base):
    __tablename__ = 'orders'
    __table_args__ = {'extend_existing': True}

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    name = Column(String)
    weight = Column(Numeric(precision=10, scale=3))
    cost = Column(Numeric(precision=10, scale=2))
    delivery_cost = Column(String, default='Не рассчитана')

    session_uuid = Column(String, ForeignKey('user_sessions.session_id'))
    user_session = relationship('UserSession', back_populates='orders')

    order_type_name = Column(String, ForeignKey(
        'order_types.name'))  # Здесь используется имя типа заказа в качестве ключа
    order_type = relationship('OrderType')

    celery_task_id = Column(String, unique=True, nullable=True, default=None)


class OrderType(Base):
    __tablename__ = 'order_types'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    name = Column(String, primary_key=True, index=True, unique=True)
