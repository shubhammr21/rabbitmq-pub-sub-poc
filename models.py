from typing import Type

from faker import Faker
from pydantic import BaseModel

fake = Faker()


class Person(BaseModel):
    name: str
    age: int
    email: str

    @classmethod
    def generate_random(cls: Type['Person']) -> 'Person':
        return cls(
            name=f"{fake.first_name()} {fake.last_name()}",
            age=fake.random_int(min=18, max=100),
            email=fake.email(),
        )
