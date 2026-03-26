import math
from flask import request, jsonify, make_response
from flask_restful import Resource
from flask_security import auth_token_required, roles_required, utils
from datetime import datetime
from celery_app import cache

from models import *
from controllers.helper import *

class LotTransactions(Resource):
    @cache.cached(timeout=10, key_prefix='lots_cache')
    def get(self, lotid=None):
        if lotid:
            lot = Parkinglot.query.filter_by(id=lotid, status='A').first()
            if not lot:
                return make_response(jsonify({'message' : 'Lot details not found'}), 400)
            
            response ={
                'id': lot.id,
                'location': lot.location_name,
                'price': lot.price,
                'address': lot.address,
                'pincode': lot.pincode,
                'noofspots': lot.no_of_spots,
                'status': lot.status,
                'spots':[
                    {
                        'spotid': spot.id,
                        'status': spot.status
                    }
                    for spot in lot.lot_spots                         
                ]
            }
            return make_response(jsonify(response), 200)
        else:
            #lots = Parkinglot.query.filter_by(status='A').all()
            lots = Parkinglot.query.all()
            response = []
           
            for lot in lots:
                response.append({
                    'id': lot.id,
                    'location': lot.location_name,
                    'price': lot.price,
                    'address': lot.address,
                    'pincode': lot.pincode,
                    'noofspots': lot.no_of_spots,
                    'status': lot.status,
                    'spots':[
                        {
                            'spotid': spot.id,
                            'status': spot.status
                        }
                        for spot in lot.lot_spots                         
                    ]
                })
            return make_response(jsonify(response), 200)  

    @auth_token_required
    @roles_required('admin')
    def post(self):
        data =request.get_json()
        if not data:
            return make_response(jsonify({'message': 'Please provide input data'}))
 
        name = data.get('location_name')        
        address = data.get('address')
        price = data.get('price')
        pincode = data.get('pincode')
        no_of_spots = data.get('noofspots')

        if not name:
            return make_response(jsonify({'message': 'Location name is required'}))    
        
        if Parkinglot.query.filter(Parkinglot.location_name == name, Parkinglot.status != 'D').first():
                return make_response(jsonify({'message': 'Location already exists'}),400)
        new_lot = Parkinglot(location_name=name, price=price, address=address, pincode=pincode, no_of_spots=no_of_spots, status='A')

        db.session.add(new_lot)
        db.session.flush()
        
        # add rows to spot table
        spots = createspots(new_lot.id, no_of_spots)
        db.session.add_all(spots)
        db.session.commit()
        cache.delete('lots_cache')

        response = {
            'message': 'New Parking lot added successfully',
            'data':{
                'id': new_lot.id,
                'name': new_lot.location_name,
                'address': new_lot.address,
                'pincode': new_lot.pincode,
                'price': new_lot.price,
                'noofspots': new_lot.no_of_spots,
                'status' : new_lot.status,
                'spots': [
                    {
                        'spotid': spot.id,
                        'status': spot.status
                    }
                    for spot in new_lot.lot_spots
                ]
            }
        }
        return make_response(jsonify(response), 200)
    
    @auth_token_required
    @roles_required('admin')
    def put(self, lot_id):
        data =request.get_json()
        lot = Parkinglot.query.filter_by(id=lot_id, status='A').first()
        if not lot:
            return make_response(jsonify({'mesage': 'Parking Lot not found'}))
        
        if not data:
            return make_response(jsonify({'mesage': 'No input data provided'}))
        
        name = data.get('location')
        if name:
            existinglot = Parkinglot.query.filter(Parkinglot.location_name == name, Parkinglot.status != 'D').first()
            #if Parkinglot.query.filter_by(location_name=name).first():
            if existinglot.id != lot_id:
                return make_response(jsonify({'mesage': 'Location already exists'}))
        lot.location_name = name
        lot.price = data.get('price')
        lot.address = data.get('address')
        lot.pincode = data.get('pincode')
        existingspots = lot.no_of_spots
        updatedspots = int(data.get('noofspots'))
        lot.no_of_spots = data.get('noofspots')
        lot.status = 'A'

        try:
            if updatedspots > existingspots:
                # Add new spots
                new_spots = createspots(lot.id, updatedspots - existingspots)
                db.session.add_all(new_spots)
            elif updatedspots < existingspots:
                # Remove available spots (only those not in use)
                availablespots = Parkingspot.query.filter_by(lot_id=lot.id, status='A').order_by(Parkingspot.id.desc()
                                    ).limit(existingspots - updatedspots).all()
                if len(availablespots) < (existingspots - updatedspots):
                    return make_response(jsonify({'message': 'Too few available spots for removal'}), 400)
                
                for spot in availablespots:
                    db.session.delete(spot)

            db.session.commit()
            cache.delete('lots_cache')
            response = {
                'message': 'Parking lot updated successfully',
                'data':{
                    'id': lot.id,
                    'location': lot.location_name,
                    'address': lot.address,
                    'pincode': lot.pincode,
                    'price': lot.price,
                    'noofspots': lot.no_of_spots,
                    'status': lot.status,
                    'spots': [
                        {
                            'spotid': spot.id,
                            'status': spot.status
                        }
                        for spot in lot.lot_spots
                    ]
                }
            }
            return make_response(jsonify(response), 200)
        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({'message': 'Could not update lots', 'error': str(e)}), 500)
    
    
    @auth_token_required
    @roles_required('admin')
    def delete(self, lot_id):
        removeFlag = True
        lot = Parkinglot.query.filter_by(id=lot_id, status='A').first()
        if not lot:
             return make_response(jsonify({"message": "Locaton not found"}), 400)

        #check for reserved spots
        occupiedspots = Parkingspot.query.filter_by(lot_id=lot.id, status='O').first()
        if occupiedspots:
            return make_response(jsonify({'message': 'This lot Cannot be deleted as some spots are aleady reserved'}), 400)
        
        #deletedspots = Parkingspot.query.filter_by(lot_id=lot.id, status='D').all()
        spotsList = lot.lot_spots
        for spot in spotsList:
            if spot.status=='D':
                removeFlag = False
                break
            else:
                reservationList = spot.spot_reservations
                if reservationList:
                    removeFlag = False
                    break
                
        try:
            if removeFlag:
                Parkingspot.query.filter_by(lot_id=lot.id).delete()
                db.session.delete(lot)
            else:
                spotlist = Parkingspot.query.filter_by(lot_id=lot.id).all()
                for spot in spotlist:
                    spot.status='D'
                lot.status='D'    
            db.session.commit()
            cache.delete('lots_cache')

            response = {
                "message": "Location deleted successfully"
            }
            return make_response(jsonify(response), 200)
        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({'message': 'Lot deletion failed', 'error': str(e)}), 500)
    
class SpotTransactions(Resource):
    @cache.cached(timeout=10, key_prefix='spots_cache')
    def get(self, spotid=None):
        if spotid:
            spot = Parkingspot.query.filter(Parkingspot.id==spotid, Parkingspot.status != 'D').all()
            if not spot:
                return make_response(jsonify({'message' : 'Spot details not found'}), 400)
            
            response ={
                'id': spot.id,
                'lot_id': spot.lot_id,
                'status': spot.status
            }
            return make_response(jsonify(response), 200)
        else:
            spots = Parkingspot.query.filter(Parkingspot.status != 'D').all()
            response = []
            for spot in spots:
                response.append({
                    'id': spot.id,
                    'lot_id': spot.lot_id,
                    'status': spot.status
                })
            return make_response(jsonify(response), 200)  

    @auth_token_required
    @roles_required('admin')
    def delete(self, spot_id):
        spot = Parkingspot.query.filter(Parkingspot.id == spot_id, Parkingspot.status != 'D').first()
                
        if not spot:
             return make_response(jsonify({"message": "Parking Spot not found"}), 400)
        if spot.status == 'O':
            return make_response(jsonify({"message": "Spot can not be deleted as it is reserved"}), 400)
        
        reservation = Spotreservation.query.filter_by(spot_id=spot.id).all()
        try:
            if not reservation:
                lot = spot.parkinglot
                db.session.delete(spot)

                # Decrease the lot's no_of_spots
                if lot.no_of_spots > 0:
                    lot.no_of_spots -= 1
            else:
                spot.status = 'D'

            db.session.commit()
            cache.delete('spots_cache')
        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({"message": "Failed to delete spot", "error": str(e)}), 500)

        response = {
            "message": "Parking Spot deleted successfully"
        }
        return make_response(jsonify(response), 200)
    
class BookingTransactions(Resource):
    def get(self, reservation_id=None, spot_id=None, user_id=None):
        reservation = None
        if reservation_id is not None :
            reservation = Spotreservation.query.get(reservation_id) 
            if reservation is None:
                return make_response(jsonify({'message': 'No active booking for this spot'}), 404)
            response ={
                'id': reservation.id,
                'spotid': reservation.spot_id,
                'userid': reservation.user_id,
                'vehicleno': reservation.vehicle_no,
                'parkingtime': reservation.parking_time,
                'leavingtime': reservation.leaving_time,
                'parkingcost': reservation.parking_cost,
                'lotid': reservation.reservedspot.lot_id
            } 
            return make_response(jsonify(response), 200)
           
        elif spot_id is not None :
            reservations = Spotreservation.query.filter_by(spot_id=spot_id).all()
            if reservations is None:
                return make_response(jsonify({'message': 'No active booking for this spot'}), 404)
            for res in reservations:
                if res.reservedspot.status == 'O' and res.leaving_time is None  :
                        reservation = res
                        break 
            leaving_time = datetime.now()
            duration =  leaving_time - reservation.parking_time
            lotprice = reservation.reservedspot.parkinglot.price 
            parkedhours = math.ceil(duration.total_seconds()/ 3600)
            parkingcost =  round(lotprice * parkedhours,2)   
            reservation.parking_cost = parkingcost
            response ={
                'id': reservation.id,
                'spotid': reservation.spot_id,
                'userid': reservation.user_id,
                'vehicleno': reservation.vehicle_no,
                'parkingtime': reservation.parking_time,
                'leavingtime': reservation.leaving_time,
                'parkingcost': reservation.parking_cost,
                'lotid': reservation.reservedspot.lot_id
            } 
            return make_response(jsonify(response), 200)     
        elif user_id is not None:
            reservations = Spotreservation.query.filter_by(user_id=user_id).all()
            response = []
            for reservation in reservations:
                cost = reservation.parking_cost if reservation.parking_cost is not None else Parkingspot.query.get(reservation.spot_id).parkinglot.price
                response.append({
                    'id': reservation.id,
                    'spotid': reservation.spot_id,
                    'userid': reservation.user_id,
                    'vehicleno': reservation.vehicle_no,
                    'parkingtime': reservation.parking_time,
                    'leavingtime': reservation.leaving_time,
                    #'parkingcost': reservation.parking_cost,
                    'parkingcost': cost,
                    'lotid': reservation.reservedspot.lot_id,
                    'location': reservation.reservedspot.parkinglot.location_name
                })
            return make_response(jsonify(response), 200)
        else:
            reservations = Spotreservation.query.all()
            response = []
            for reservation in reservations:
                response.append({
                    'id': reservation.id,
                    'spotid': reservation.spot_id,
                    'userid': reservation.user_id,
                    'username': reservation.user.fullname,
                    'vehicleno': reservation.vehicle_no,
                    'parkingtime': reservation.parking_time,
                    'leavingtime': reservation.leaving_time,
                    'parkingcost': reservation.parking_cost,
                    'lotid': reservation.reservedspot.lot_id,
                    'location': reservation.reservedspot.parkinglot.location_name
                })
            return make_response(jsonify(response), 200) 
    
    @auth_token_required
    def post(self):        
        data =request.get_json()
        if not data:
            return make_response(jsonify({'message': 'Please provide input data'}))
 
        spot_id = data.get('spotid') 
        lot_id = data.get('lotid')        
        user_id = data.get('userid')
        vehicle_no = data.get('vehicleno')
        parking_time = datetime.now()
        spot = Parkingspot.query.filter_by(id=spot_id).first()
        if not spot:
            return make_response(jsonify({'message': 'Spot not found'}))
        
        if spot.status == 'O':
            return make_response(jsonify({'mesage': 'spot is already reserverd'}))
        
        new_reservation = Spotreservation(spot_id=spot_id, user_id=user_id, vehicle_no=vehicle_no, parking_time=parking_time)
        spot.status='O'

        db.session.add(new_reservation)
        db.session.commit()
        cache.delete('spots_cache')

        response = {
            'message': 'Parking spot has been reserved successfully',
            'data':{
                'spot_id': new_reservation.spot_id,
                'user_id': new_reservation.user_id,
                'vehicle_no': new_reservation.vehicle_no,
                'parking_time': new_reservation.parking_time
            }
        }
        return make_response(jsonify(response), 200)

    @auth_token_required
    def put(self, reservation_id):
        reservation = Spotreservation.query.get(reservation_id) 
        if not reservation:
            return make_response(jsonify({'mesage': 'No such booking found'}), 400)
        
        spot = reservation.reservedspot 
        if not spot:
            return make_response(jsonify({'mesage': "Parking Spot not found"}), 400)    
              
        lotprice = spot.parkinglot.price

                
        reservation.leaving_time = datetime.now()
        duration =  reservation.leaving_time - reservation.parking_time 

        parkedhours = math.ceil(duration.total_seconds()/ 3600)
        parkingcost =  round(lotprice * parkedhours, 2)  

        reservation.parking_cost = parkingcost  
        spot.status = 'A'      

        db.session.commit()

        response = {
            'message': 'Parking spot has been released successfully',
            'data':{
                'id': reservation.id,
                'spotid': reservation.spot_id,
                'leavingtime': reservation.leaving_time,
                'parkingcost': reservation.parking_cost,
            }
        }
        return make_response(jsonify(response), 200)



     
    

