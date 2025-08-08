from typing import Dict

from faker import Faker


def get_creation_data() -> Dict:
    faker = Faker()
    data = {
        'username': faker.user_name(),
        'email': faker.email(),
        'password': faker.password(length=10)
    }
    return data
