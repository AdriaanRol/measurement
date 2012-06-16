# Import smtplib for the actual sending function
import smtplib

# Import the email modules we'll need
from email.mime.text import MIMEText

# Open a plain text file for reading.  For this example, assume that
# the text file contains only ASCII characters.
textfile = 'testmail.txt'
fp = open(textfile, 'rb')
# Create a text/plain message
msg = MIMEText(fp.read())
fp.close()

me = 'cryolt2@gmail.com'
you = 'diamond-tnw@lists.tudelft.nl'


msg['Subject'] = 'Welcome to the diamond lt2 warning service'
msg['From'] = me
msg['To'] = you

# Send the message via our own SMTP server, but don't include the
# envelope header.
username='cryolt2'
password='Diamond=Geil!'

server = smtplib.SMTP('smtp.gmail.com:587')  
server.starttls()  
server.login(username,password)  
server.sendmail(me, you, msg.as_string())  
server.quit()

