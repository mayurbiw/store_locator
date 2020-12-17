from celery import shared_task 
from time import sleep
from io import BytesIO
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from . import bk
from . import pizza_hurt
from . import smartandfinal
from . import starbucks
from . import verizon


@shared_task
def send_email_task(brandname,recipient_email):
    print(f"Report for {brandname} is getting generated....")
    
    subject = 'Report: Store locator for ' + brandname
    message = 'Hi, Find the report in the attachment'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = []
    recipient_list.append(recipient_email)

    if brandname == "Smart & Final":
        wb = smartandfinal.get_stores()

    if brandname == "Starbucks":
        wb = starbucks.starbucks_report_us()
    
    if brandname == "Pizza Hut":
        wb = pizza_hurt.get_stores()
    
    if brandname == "Verizon Wireless":
        wb = verizon.get_stores()
    
    if brandname == "Burger King":
        wb = bk.get_stores()
    
    if wb:
        email = EmailMessage(
        subject,
        message,
        email_from,
        recipient_list
        )
        output = BytesIO()
        wb.save(output)
        email.attach(brandname + '_report.xls', output.getvalue() , 'application/ms-excel')
        email.send()
    
    else:
        message = "Report creation failed..."
        email = EmailMessage(
                subject,
                message,
                email_from,
                recipient_list
                )
        email.send()       
    
    return None