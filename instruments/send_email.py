from instrument import Instrument
import types
import smtplib
from email.mime.text import MIMEText

class send_email(Instrument):
    '''This instrument sends an email using a 
	gmall account defined by the (username,password) parameters'''
	
	
    def __init__(self, name, username='not_set', password='not_set'):
        Instrument.__init__(self,name)

        self.add_parameter('username',
                type=types.StringType,
                flags=Instrument.FLAG_GETSET)
        self.add_parameter('password',
                type=types.StringType,
                flags=Instrument.FLAG_GETSET)				

        self._username = username
        self._password = password

        self.add_function("send_email")
		
        self._host='smtp.gmail.com:587'
        self._mail_append='@googlemail.com'
		
    def do_get_username(self):
        return self._username

    def do_set_username(self, username):
        self._username = username

    def do_get_password(self):
        return self._password

    def do_set_password(self, password):
        self._password = password

    def send_email(self,recipients,subject,message):
        '''Sends an email to 'recipients' (string or list of strings), with subject and message'''
        if isinstance(recipients,str):recipients=[recipients]
        try:
            for recipient in recipients:
                self._actually_send(recipient,subject,message)
        except smtplib.SMTPException as mailerror:
            print "Mailing error:", mailerror
            return False
        return True
	
    def _actually_send(self,recipient,subject,message):
        msg = MIMEText(message)
        sender = self._username + self._mail_append
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = recipient

        server = smtplib.SMTP(self._host)  
        server.starttls()  
        server.login(self._username,self._password)  
        server.sendmail(sender, recipient, msg.as_string())  
        server.quit()
	
