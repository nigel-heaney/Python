#!/bin/env python
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate
from email import Encoders
import os,sys

relay="localhost"
emaillist="root@localhost,nigel@localhost"

if sys.platform == "linux" or sys.platform == "linux2":
        sender=os.environ['USER'] + '@' + os.environ['HOSTNAME']
elif sys.platform == "win32":
        sender=os.environ['USERNAME'] + '@' + os.environ['USERDOMAIN']

def sendMail(to, sender, subject, text, server="localhost"):
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = to
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject
    msg.attach( MIMEText(text) )

    smtp = smtplib.SMTP(server)
    smtp.sendmail(sender, to.split(','), msg.as_string() )
    smtp.close()


def sendMailfile(to, sender, subject, text,file="" server="localhost"):
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = to
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject
    msg.attach( MIMEText(text) )

    part = MIMEBase('application', "octet-stream")
    part.set_payload( open(file,"rb").read() )
    Encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(file))
    msg.attach(part)

    smtp = smtplib.SMTP(server)
    smtp.sendmail(sender, to.split(','), msg.as_string() )
    smtp.close()


# Example:
sendMail(emaillist,sender,'Test Python!','Err this is an email :)',relay)
