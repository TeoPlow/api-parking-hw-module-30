import pytest
import os
from flask_sqlalchemy import SQLAlchemy
from app import create_app
from models import db


@pytest.fixture(scope='module')
def app():
    app = create_app()
    app.config['TESTING'] = True
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope='function')
def client(app):
    with app.test_client() as test_client:
        yield test_client


@pytest.fixture(scope='module')
def test_db():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']  or "sqlite:///test.db"
    test_db = SQLAlchemy(app)
    with app.app_context():
        test_db.create_all()
        yield test_db
        test_db.session.remove()
        test_db.drop_all()


from test_factory import ClientFactory, ParkingFactory

@pytest.fixture(scope='module')
def client_factory():
    return ClientFactory

@pytest.fixture(scope='module')
def parking_factory():
    return ParkingFactory


@pytest.mark.parametrize("endpoint", [
    '/clients',
    '/clients/1'
])
def test_get_methods(client, endpoint):
    client.post('/clients', json={
        'name': 'Chel',
        'surname': 'Chelov',
        'credit_card': '2200150511111111',
        'car_number': 'A667ГД'
    })
    response = client.get(endpoint)
    assert response.status_code == 200


@pytest.mark.create
def test_create_client(client):
    response = client.post('/clients', json={
        'name': 'Pchel',
        'surname': 'chelov',
        'credit_card': '2200150511111112',
        'car_number': 'Д365CГ'
    })
    assert response.status_code == 201
    assert response.json['name'] == 'Pchel'
    assert response.json['surname'] == 'chelov'


@pytest.mark.create
def test_create_parking(client):
    response = client.post('/parkings', json={
        'address': 'ул.Ленина, 1',
        'count_places': 10,
        'count_available_places': 10,
        'opened': True
    })
    assert response.status_code == 201
    assert response.json['address'] == 'ул.Ленина, 1'


@pytest.mark.parking
def test_client_parking(client):
    # Создание нового клиента
    response = client.post('/clients', json={
        'name': 'Pchel',
        'surname': 'chelov',
        'credit_card': '2200150511111112',
        'car_number': 'Д365CГ'
    })
    assert response.status_code == 201
    assert response.json['id'] == 4

    # Создание парковки
    response = client.post('/parkings', json={
        'address': 'ул.Ленина, 1',
        'count_places': 2,
        'count_available_places': 1,
        'opened': True
    })
    assert response.status_code == 201
    assert response.json['id'] == 2

    # Назначение нового клиента на парковку
    response = client.post('/client_parkings', json={
        'client_id': 4,
        'parking_id': 2
    })
    assert response.status_code == 201
    assert response.json['client_id'] == 4
    assert response.json['parking_id'] == 2

    # Проверка, что количество доступных мест уменьшилось
    response = client.get('/parkings/2')
    assert response.status_code == 200
    assert response.json['count_available_places'] == 0

    # Создание второго нового клиента
    response = client.post('/clients', json={
        'name': 'Pchel2',
        'surname': 'chelov2',
        'credit_card': '2230150511111112',
        'car_number': 'H365CT'
    })
    assert response.status_code == 201
    assert response.json['id'] == 5

    # Попытка назначить второго клиента на ту же парковку
    response = client.post('/client_parkings', json={
        'client_id': 5,
        'parking_id': 2
    })
    assert response.status_code == 400
    assert response.json['error'] == 'На парковке нет мест.'

    # Создание третьего нового клиента
    response = client.post('/clients', json={
        'name': 'Pchel3',
        'surname': 'chelov3',
        'credit_card': '2330150511111112',
        'car_number': 'Д363CT'
    })
    assert response.status_code == 201
    assert response.json['id'] == 6

    # Создание закрытой парковки
    response = client.post('/parkings', json={
        'address': 'ул.Пушкина, 2',
        'count_places': 11,
        'count_available_places': 13,
        'opened': False
    })
    assert response.status_code == 201
    assert response.json['id'] == 3

    # Попытка назначить третьего клиента на закрытую парковку
    response = client.post('/client_parkings', json={
        'client_id': 6,
        'parking_id': 3
    })
    assert response.status_code == 400
    assert response.json['error'] == 'Парковка закрыта.'

    # Кредитная карта не привязана
    response = client.post('/clients', json={
        'name': 'Pchel4',
        'surname': 'chelov4',
        'credit_card': '',
        'car_number': 'Д363CT'
    })
    assert response.status_code == 201
    
    response = client.post('/client_parkings', json={
        'client_id': 7,
        'parking_id': 2
    })
    assert response.status_code == 400
    assert response.json['error'] == 'Кредитная карта не привязана.'


@pytest.mark.parking
def test_delete_client_parking(client):
    client.post('/clients', json={
        'name': 'Pchel',
        'surname': 'chelov',
        'credit_card': '2200150511111112',
        'car_number': 'Д365CГ'
    })
    client.post('/parkings', json={
        'address': 'ул.Ленина, 1',
        'count_places': 10,
        'count_available_places': 10,
        # 'opened': True
    })
    client.post('/client_parkings', json={
        'client_id': 1,
        'parking_id': 1
    })
    response = client.delete('/client_parkings', json={
        'client_id': 1,
        'parking_id': 1
    })
    assert response.status_code == 200

@pytest.mark.create
def test_create_client_2(client):
    client_factory = ClientFactory()
    response = client.post('/clients', json={
        'name': client_factory.name,
        'surname': client_factory.surname,
        'credit_card': client_factory.credit_card,
        'car_number': client_factory.car_number
    })
    assert response.status_code == 201
    assert response.json['name'] == client_factory.name
    assert response.json['surname'] == client_factory.surname


@pytest.mark.create
def test_create_parking_2(client):
    parking_factory = ParkingFactory()
    response = client.post('/parkings', json={
        'address': parking_factory.address,
        'count_places': parking_factory.count_places,
        'count_available_places': parking_factory.count_available_places,
        'opened': parking_factory.opened
    })
    assert response.status_code == 201
    assert response.json['address'] == parking_factory.address
