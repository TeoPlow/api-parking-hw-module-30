import os
from flask import Flask, request, jsonify
from models import db, Client, Parking, ClientParking
from http import HTTPStatus
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv('DATABASE_URL') or "sqlite:///test.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    with app.app_context():
        db.create_all()

    @app.route('/')
    def main_page():
        return "Parking API is running!"


    @app.route('/clients', methods=['GET'])
    def get_clients():
        clients = Client.query.all()
        return jsonify([{'id': client.id, 
                         'name': client.name, 
                         'surname': client.surname} for client in clients])


    @app.route('/clients/<int:client_id>', methods=['GET'])
    def get_client_by_id(client_id):
        client = Client.query.get_or_404(client_id)
        return jsonify({'id': client.id, 
                        'name': client.name, 
                        'surname': client.surname, 
                        'credit_card': client.credit_card, 
                        'car_number': client.car_number})


    @app.route('/clients', methods=['POST'])
    def create_client():
        data = request.get_json()
        new_client = Client(name=data['name'], 
                            surname=data['surname'], 
                            credit_card=data.get('credit_card'), 
                            car_number=data.get('car_number'))
        db.session.add(new_client)
        db.session.commit()
        return jsonify({'id': new_client.id, 
                        'name': new_client.name, 
                        'surname': new_client.surname}), HTTPStatus.CREATED


    @app.route('/parkings', methods=['POST'])
    def create_parking():
        data = request.get_json()
        try:
            new_parking = Parking(address=data['address'], 
                              count_places=data['count_places'], 
                              count_available_places=data['count_available_places'],
                              opened=data['opened'])
        except:
            new_parking = Parking(address=data['address'], 
                              count_places=data['count_places'], 
                              count_available_places=data['count_available_places'])
        
        db.session.add(new_parking)
        db.session.commit()
        return jsonify({'id': new_parking.id, 
                        'address': new_parking.address}), HTTPStatus.CREATED

    @app.route('/parkings/<int:parking_id>', methods=['GET'])
    def get_parking_by_id(parking_id):
        parking = Parking.query.get_or_404(parking_id)
        return jsonify({
            'id': parking.id,
            'address': parking.address,
            'opened': parking.opened,
            'count_places': parking.count_places,
            'count_available_places': parking.count_available_places
        })

    @app.route('/client_parkings', methods=['POST'])
    def assign_client_to_parking():
        data = request.get_json()
        
        client_parking = ClientParking(client_id = data['client_id'],
                                       parking_id = data['parking_id'])
        
        client: Client = Client.query.get(data['client_id'])
        parking: Parking = Parking.query.get(data['parking_id'])

        if client.credit_card is None or client.credit_card == '':
            return jsonify({'error': 'Кредитная карта не привязана.'}), HTTPStatus.BAD_REQUEST

        if not client or not parking:
            return jsonify({'error': 'Клиент или Паркинг не существуют.'}), HTTPStatus.BAD_REQUEST
        
        if parking.opened == False:
            return jsonify({'error': 'Парковка закрыта.'}), HTTPStatus.BAD_REQUEST

        if parking.count_available_places <= 0:
            return jsonify({'error': 'На парковке нет мест.'}), HTTPStatus.BAD_REQUEST

        parking.count_available_places -= 1
        db.session.add(parking)
        db.session.commit()

        db.session.add(client_parking)
        db.session.commit()
        return jsonify({'client_id': client_parking.client_id,
                        'parking_id': client_parking.parking_id}), HTTPStatus.CREATED


    @app.route('/client_parkings', methods=['DELETE'])
    def delete_client_parking():
        data = request.get_json()
        client_id = data['client_id']
        parking_id = data['parking_id']

        client_parking: ClientParking = ClientParking.query.filter_by(client_id=client_id, parking_id=parking_id).first()
        if not client_parking:
            return jsonify({'error': 'Клиент не найден на парковке.'}), HTTPStatus.NOT_FOUND
        
        client_parking.time_out = datetime.now()
        parking: Parking = Parking.query.get(parking_id)
        if parking:
            parking.count_available_places += 1
            db.session.add(parking)
            db.session.add(client_parking)

            db.session.commit()
            return jsonify({'message': 'Клиент успешно выехал с парковки.'}), HTTPStatus.OK
        else:
            return jsonify({'error': 'Парковка не найдена.'}), HTTPStatus.NOT_FOUND

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)