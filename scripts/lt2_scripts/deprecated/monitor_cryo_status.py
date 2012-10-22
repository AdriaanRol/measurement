import visa
import time
import qt
import msvcrt
import smtplib
from email.mime.text import MIMEText

levelmeter = visa.instrument('GPIB::8::INSTR')
keithley =  visa.instrument('GPIB::11::INSTR')
waittime = 10 # minutes

t_start = time.time() - 60*waittime

while  msvcrt.kbhit() == 0:
    t_num = time.time()
    qt.msleep(1)
    if t_num-t_start > waittime * 60:
        t_start = t_num
        t_str = time.asctime()
        print('current time: %s'%t_str)
        print('current cryovac levelmeter reading:')
        levelmeter.write('chan 2')
        lev1 = levelmeter.ask('meas?')
        lev1_flt=float((lev1.split(' '))[0])
        print('  LHe1 (upper tank): %s'%(lev1))
        levelmeter.write('chan 1')
        lev2 = levelmeter.ask('meas?')
        lev2_flt=float((lev2.split(' '))[0])
        print('  LHe2 (lower tank): %s'%(lev2))
    
        volt = 'n/a'
        keith_meas = keithley.ask(':func?')
        if keith_meas == '"VOLT:DC"':
            volt = float(keithley.ask(':data?'))
            print('current sensor voltage: %.3f'%(volt))
    
        f = open('//tudelft.net/staff-groups/tnw/ns/qt/Diamond/setups/LT2/cryo.txt','a')
        f.write('%.0f\t%s\t%s\t%s\t%.3f V\n'%(t_num,t_str,lev1,lev2,volt))
        f.close()
        
        lev2_min = 0.5 #cm
        volt_min = 1.5 #volt = > 6 K
        if (lev2_flt < lev2_min) or (volt != 'n/a' and volt < volt_min):
            subject= 'Warning from Cryo LT2!'
            message = 'Warning from Cryo LT2: Measured levels: \n'+\
                      'current cryovac levelmeter reading:\n' + \
                      '  LHe1 (upper tank): %s'%(lev1) + '\n' + \
                      '  LHe2 (lower tank): %s'%(lev2) + '\n' + \
                      'current sensor voltage: %.3f'%(volt) + '.\n' + \
                      'This is below minimum values (LHe2 < %.3f'%(lev2_min) + ' cm' +\
                      ', voltage < %.3f'%(volt_min) + 'V ( = 6 K)). \n' + \
                      'Please help me!!!\n xxx LT2'
            recipient  = 'diamond-tnw@lists.tudelft.nl'
            #recipient  = 'B.J.Hensen@tudelft.nl'
            print message
            try:
               send_email(recipient,subject,message)
            except smtplib.SMTPException:
               print "Mailing error"
            

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
