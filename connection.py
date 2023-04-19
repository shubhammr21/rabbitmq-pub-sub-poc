from aio_pika import connect_robust


async def connect_to_rabbitmq():
    return await connect_robust("amqp://guest:guest@localhost/")
