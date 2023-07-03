from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
import os
import smtplib
import ssl

def send_email(application, SENDER, RECIPENTS, HOST, PORT, USERNAME_SMTP, PASSWORD_SMTP):

    RECIPENTS = eval(RECIPENTS)
    # Create the root message and fill in the from, to, and subject headers
    msgRoot = MIMEMultipart('related')
    msgRoot['Subject'] = f'{application} Application Health'
    msgRoot['From'] = SENDER
    msgRoot['To'] = ", ".join(RECIPENTS)
    msgRoot.preamble = 'This is a multi-part message in MIME format.'

    # Encapsulate the plain and HTML versions of the message body in an
    # 'alternative' part, so message agents can decide which they want to display.
    msgAlternative = MIMEMultipart('alternative')
    msgRoot.attach(msgAlternative)

    msgText = MIMEText('This is the alternative plain text message.')
    msgAlternative.attach(msgText)

    with open(os.getcwd()+'\ApplicationHealth.htm', 'r') as myfile:
        data=myfile.read()
    # We reference the image in the IMG SRC attribute by the ID we give it below
    msgText = MIMEText(data, 'html')
    msgAlternative.attach(msgText)

    # This example assumes the image is in the current directory
    fp = open(os.getcwd()+'\img\logo.png', 'rb')
    msgImage = MIMEImage(fp.read())
    fp.close()

    # Define the image's ID as referenced above
    msgImage.add_header('Content-ID', '<image1>')
    msgRoot.attach(msgImage)

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP(HOST, PORT) as server:
            server.starttls(context=context)
            server.login(USERNAME_SMTP, PASSWORD_SMTP)
            server.sendmail(SENDER, RECIPENTS, msgRoot.as_string())
            server.close()
            print("Email sent!")

    except smtplib.SMTPException as e:
        print("Error: ", e)
