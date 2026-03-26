from models import User,Spotreservation 
from datetime import datetime,timedelta

def getallUsers():
    return User.query.filter(id != 1).all()

def getuserbookingdetails():
    reservations = Spotreservation.query.all()
    userBookingMap = {}
    for reservation in reservations:
        user_id = reservation.user_id
        if (user_id not in userBookingMap):
          userBookingMap[user_id] =  {
            'bookingcount': 1,
            'parkingcost': reservation.parking_cost if reservation.parking_cost is not None else 0
          }            
        else : 
          existing = userBookingMap[reservation.user_id]
          existing['bookingcount'] +=  1
          existing['parkingcost'] += reservation.parking_cost if reservation.parking_cost is not None else 0
        
    return userBookingMap  

def getadminemailmsg(data):
    totalbookings = data[0].get("totalbookings")
    completedbookings = data[0].get("completedbookings")
    ongoingbookings = data[0].get("ongoingbookings")
    totalrevenue = data[0].get("totalrevenue")
    generatedtime = datetime.now()

    msg = f"""Dear Admin,

    Here is your generated parking report summary:
    - Total Bookings: {totalbookings}
        -Completed Bookings: {completedbookings} 
        -Ongoing Bookings: {ongoingbookings}
    -Total Revenue Of Bookings: Rs. {totalrevenue}
    -Generated at {generatedtime}



    Best Regards,
    ZippyPark System
    """
    return msg

def getuseremailmsg(totalbookings, totalcost):
    generatedtime = datetime.now()
    msg = f"""Dear User,

    Here is your latest parking report summary:
    - Total Bookings till now: {totalbookings}
    - Total parking Charges paid till now : Rs. {totalcost}

    -Generated at {generatedtime}

    Best Regards,
    ZippyPark System
    """    
    return msg
