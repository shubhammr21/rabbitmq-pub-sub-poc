import asyncio
from typing import Any, Callable

import aio_pika
from structlog import get_logger

from models import Person

logger = get_logger()


class BasePubSub:
    def __init__(self, connect_func: Callable[..., Any]) -> None:
        self._connect_func = connect_func

    async def _connect(self) -> None:
        self.connection = await self._connect_func()
        self.channel = await self.connection.channel()
        await self.channel.declare_queue("person_queue", auto_delete=True)

    async def ensure_connection(self) -> None:
        if not hasattr(self, "connection"):
            await self._connect()


class Publisher(BasePubSub):
    async def publish(self, message: Any) -> None:
        await self.ensure_connection()
        await self.channel.default_exchange.publish(
            aio_pika.Message(body=message.encode()),
            routing_key="person_queue",
        )

    async def generate_data(self, rate: int = 100) -> None:
        while True:
            person = Person.generate_random()
            await self.publish(person.json())
            await asyncio.sleep(1 / rate)


class Consumer(BasePubSub):
    async def _consume(self, rate: int = 20) -> None:
        await self.ensure_connection()
        self.queue = await self.channel.declare_queue("person_queue", auto_delete=True)

        async with self.queue.iterator() as queue_iter:
            while True:
                async for message in queue_iter:
                    person = Person.parse_raw(message.body.decode())
                    print(f"Consumed: {person}")
                    await asyncio.sleep(1 / rate)
                    await message.ack()  # Manually send the acknowledgement after the sleep

    async def start_consuming(self, rate: int = 20) -> None:
        await self._consume(rate)
