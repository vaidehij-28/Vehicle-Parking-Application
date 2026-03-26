from models import db, Parkingspot

def createspots(lotid, noofspots):
    spots = []
    for i in range(noofspots):
        spot = Parkingspot(lot_id=lotid, status='A')
        db.session.add(spot)
        spots.append(spot)
    return spots