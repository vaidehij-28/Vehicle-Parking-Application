from flask import Flask
from flask_security import Security
from flask_restful import Api
from flask_security.utils import hash_password
from flask_cors import CORS

from models import db,user_datastore,Spotreservation
from controllers.config import Config
from celery_app import cache

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    security = Security(app, user_datastore)
    cache.init_app(app)

    api = Api(app, prefix='/api')

    with app.app_context():
        db.create_all()
        admin_role = user_datastore.find_or_create_role(name='admin', description='Administrator')
        user_role = user_datastore.find_or_create_role(name='user', description='Regular User')

        if not user_datastore.find_user(email='admin@gmail.com'):
            user_datastore.create_user(
                email = 'admin@gmail.com',
                fullname = 'Administrator',
                address = 'Lal Danth Raod, Haldwani',
                pincode = '231639',
                password = hash_password('admin123'),
                roles = [admin_role]
            )
        db.session.commit()

    return app, api

app, api = create_app()
CORS(app, resources={r"/api/*":{"origins":"*"}}, supports_credentials=True, automatic_options=True)

from controllers.authenticator import Register, Login, Logout, CheckEmail, Users

api.add_resource(Register, '/register')
api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
api.add_resource(CheckEmail, '/checkemail')
api.add_resource(Users, '/users', '/users/<int:userid>')

from controllers.transactions import LotTransactions, SpotTransactions, BookingTransactions
api.add_resource(LotTransactions, '/parkinglot', '/parkinglot/<int:lot_id>')
api.add_resource(SpotTransactions, '/parkingspot', '/parkingspot/spot/<int:spot_id>', '/parkingspot/lot/<int:lot_id>')
api.add_resource(BookingTransactions, '/bookingspot', '/bookingspot/reservation/<int:reservation_id>', '/bookingspot/spot/<int:spot_id>', '/bookingspot/user/<int:user_id>')

@app.route('/api/generate_csv', methods=['GET'])
def generate_csv():
    data = getbookingdetails()
    from celery_app import generate_csv
    generate_csv.delay(data)
    return {
        'message' : "CSV generateion task has been started"
    }, 200

def getbookingdetails():
    from app import app
    reservations = Spotreservation.query.all()
    response = []
    bookingcount = 0
    completedbookings = 0
    ongoingbookings = 0
    revenue = 0
    for reservation in reservations:
        bookingcount = bookingcount + 1
        if (reservation.leaving_time != None):
            completedbookings = completedbookings + 1
        if (reservation.parking_cost != None):
            revenue = revenue + reservation.parking_cost
    ongoingbookings = bookingcount - completedbookings    
    response.append({
        'totalbookings': bookingcount,
        'completedbookings': completedbookings,
        'ongoingbookings': ongoingbookings,
        'totalrevenue': revenue        
    })

    return response

if __name__ == "__main__":
    app.run(debug=True)

