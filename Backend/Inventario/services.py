from abc import ABC, abstractmethod
from typing import List

from contracts import Order, OrderCreate, SalesTicket, SalesTicketCreate


class SalesOrderService(ABC):
    @abstractmethod
    def list_tickets(self) -> List[SalesTicket]:
        raise NotImplementedError

    @abstractmethod
    def create_ticket(self, payload: SalesTicketCreate) -> SalesTicket:
        raise NotImplementedError

    @abstractmethod
    def list_orders(self) -> List[Order]:
        raise NotImplementedError

    @abstractmethod
    def create_order(self, payload: OrderCreate) -> Order:
        raise NotImplementedError


class InMemorySalesOrderService(SalesOrderService):
    def __init__(self) -> None:
        self._tickets: List[SalesTicket] = []
        self._orders: List[Order] = []

    def list_tickets(self) -> List[SalesTicket]:
        return self._tickets

    def create_ticket(self, payload: SalesTicketCreate) -> SalesTicket:
        total = sum(line.quantity * line.unit_price for line in payload.lines)
        ticket = SalesTicket(
            id=len(self._tickets) + 1,
            payment_method=payload.payment_method,
            lines=payload.lines,
            total_amount=round(total, 2),
            notes=payload.notes,
        )
        self._tickets.append(ticket)
        return ticket

    def list_orders(self) -> List[Order]:
        return self._orders

    def create_order(self, payload: OrderCreate) -> Order:
        order = Order(
            id=len(self._orders) + 1,
            customer_name=payload.customer_name,
            customer_phone=payload.customer_phone,
            channel=payload.channel,
            lines=payload.lines,
            notes=payload.notes,
        )
        self._orders.append(order)
        return order
