import factory
import random
from models import Client, Parking, db


class ClientFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Client
        sqlalchemy_session = db.session

    name = factory.Faker("first_name")
    surname = factory.Faker("last_name")
    credit_card = factory.LazyAttribute(
        lambda x: random.choice(["2200150511111111", ""])
    )
    car_number = factory.LazyAttribute(lambda o: "%sA123BC")


class ParkingFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Parking
        sqlalchemy_session = db.session

    address = factory.Faker("address")
    opened = factory.Faker("boolean", chance_of_getting_true=80)
    count_places = factory.LazyAttribute(lambda x: random.randrange(0, 100))
    count_available_places = factory.SelfAttribute("count_places")
