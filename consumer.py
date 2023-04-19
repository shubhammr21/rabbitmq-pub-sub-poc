import asyncio
from typing import Any, Callable

import aio_pika
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from connection import connect_to_rabbitmq
from models import Person

console = Console()


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
        console.log(f"[cyan]Published:[/cyan] {message}")

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
                    console.log(f"[green]Consumed:[/green] {person}")
                    await asyncio.sleep(1 / rate)
                    await message.ack()

    async def start_consuming(self, rate: int = 20) -> None:
        await self._consume(rate)


class VM:
    def __init__(
        self,
        vm_name: str,
        publisher: 'Publisher',
        consumers: int,
        connect_func: Callable[..., Any],
    ) -> None:
        self.vm_name = vm_name
        self.publisher = publisher
        self.consumers = [Consumer(connect_func) for _ in range(consumers)]

    async def run(self) -> None:
        console.print(Panel(f"[bold]{self.vm_name}[/bold]", expand=False))
        tasks = [self.publisher.generate_data()]
        tasks.extend([c.start_consuming() for c in self.consumers])
        await asyncio.gather(*tasks)

    def __str__(self) -> str:
        return f"VM {self.vm_name}"


def create_vm_table(vm: VM) -> Table:
    table = Table(title=str(vm))
    table.add_column("Activity", justify="center", style="cyan", no_wrap=True)
    table.add_column("Person", justify="left", style="white")

    for consumer in vm.consumers:
        table.add_row("Consume", f"{consumer}")

    return table


if __name__ == "__main__":
    publisher = Publisher(connect_to_rabbitmq)
    vm = VM("VM 1", publisher, consumers=5, connect_func=connect_to_rabbitmq)

    vm_table = create_vm_table(vm)
    console.print(Panel(vm_table))

    try:
        asyncio.run(vm.run())
    except KeyboardInterrupt:
        console.print("Shutting down...")
