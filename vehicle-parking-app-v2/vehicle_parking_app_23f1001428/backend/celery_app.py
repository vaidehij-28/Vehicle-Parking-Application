from flask_caching import Cache
from celery import Celery
from mail import send_email
from celeryhelper import *
from app_factory import create_app

cache = Cache()

celery = Celery(
    'tasks',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0'
)

celery.conf.update(
    timezone = 'Asia/Kolkata',
    enable_utc=False
)

@celery.task()
def generate_csv(data):
    csv_content = "Total_Bookings, Completed_Bookings, Ongoing_Bookings, Total_Revenue\n"
    for row in data:
        csv_content += f"{row['totalbookings']},{row['completedbookings']},{row['ongoingbookings']},{row['totalrevenue']}\n"

    with open('data.csv', 'w') as f:
        f.write(csv_content)

    send_email('admin@gmail.com', 'Booking Report', getadminemailmsg(data))

@celery.task()
def send_reminder():
    app = create_app()
    with app.app_context():
        subject= "Booking Report "
        users =  getallUsers()
        userBookingMap = getuserbookingdetails()
        for user in users:
            if user.id in userBookingMap:
                body = getuseremailmsg(userBookingMap[user.id].get("bookingcount"), 
                                userBookingMap[user.id].get("parkingcost"))
                send_email(user.email, subject, body)

        return "Reminder emails sent to each of the user!"    

from celery.schedules import crontab

celery.conf.beat_schedule = {
    'send-hourly-reminder': {
        'task': 'celery_app.send_reminder',
        'schedule': timedelta(minutes=2), 
    }
}



    


