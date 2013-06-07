import visa
import time
import qt
import msvcrt
import smtplib
from email.mime.text import MIMEText

waittime = 10 # minutes

t_start = time.time() - 60*waittime


def send_email(recipient,subject,message):
    """Sends an email to 'recipient' (string or array of strings), with subject and message"""
    msg = MIMEText(message)
    me = 'cryolt2@gmail.com'
   
    msg['Subject'] = subject
    msg['From'] = me
    msg['To'] = recipient

    # Send the message via our own SMTP server, but don't include the
    # envelope header.
    username='cryolt2'
    password='Diamond=Geil!'

    server = smtplib.SMTP('smtp.gmail.com:587')  
    server.starttls()  
    server.login(username,password)  
    server.sendmail(me, recipient, msg.as_string())  
    server.quit()


while  msvcrt.kbhit() == 0:
    t_num = time.time()
    qt.msleep(1)
    if t_num-t_start > waittime * 60:
        t_start = t_num
        t_str = time.asctime()
        print('current time: %s'%t_str)
        print('current temperatureA: %.2f'%TemperatureController.get_kelvinA())
        print('current temperatureB: %.2f'%TemperatureController.get_kelvinB())

        
        temp_maxA = 10 #K
        temp_limit= 15 #K
        
        if (TemperatureController.get_kelvinA() > temp_maxA):
            subject= 'Warning from Flow Cryo!'
            message = 'Warning from Flow Cryo: \n' +\
                    'current temperatureA: %.2f'%TemperatureController.get_kelvinA()\
                    + '\n' + 'current temperatureB: %.2f'%TemperatureController.get_kelvinB() + '\n'+ 'Please help me!!!\n xxx LT1'
            recipient  = 'diamond-tnw@lists.tudelft.nl'
            #recipient  = 'B.J.Hensen@tudelft.nl'
            print message
            try:
                send_email(recipient,subject,message)
            except smtplib.SMTPException:
                print "Mailing error"

        if (TemperatureController.get_kelvinA() > temp_limit):
            execfile('warmup.py')
            break




