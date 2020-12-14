
from celery import shared_task 

from django.core.mail import send_mail, EmailMessage

from time import sleep

from django.conf import settings

from . import smartandfinal

from .import starbucks

from io import BytesIO


@shared_task
def sleepy(duration):
    sleep(duration)
    return None

@shared_task
def send_email_task(brandname,recipient_email):
   
    subject = 'Report: Store locator for ' + brandname
    message = 'Hi, Find the report in the attachment'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = []
    recipient_list.append(recipient_email)

    email = EmailMessage(
    subject,
    message,
    email_from,
    recipient_list
    )

    if brandname == "Smart & Final":
        print(f"Report for {brandname} is getting generated....")
        wb = smartandfinal.getStores()
        if wb is False:
            message = "Report creation failed..."
            email = EmailMessage(
                        subject,
                        message,
                        email_from,
                        recipient_list
                        )
            email.send()
        else:
            output = BytesIO()
            wb.save(output)
            email.attach(brandname + '_report.xls', output.getvalue() , 'application/ms-excel')
            email.send()

    
    elif brandname == "Starbucks":
        print(f"Report for {brandname} is getting generated....")
        
        wb = starbucks.starbucks_report_us()
    
        output = BytesIO()
        wb.save(output)
        
        email.attach(brandname + '_report.xls', output.getvalue() , 'application/ms-excel')
        email.send()

    else:
        print("No such brandname")
    
    
    
    #send_mail( subject, message, email_from, recipient_list )
    
    return None