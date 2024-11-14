import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_email(sender_email, sender_password, receiver_email, subject, message):
    
    smtp_server = 'smtp.gmail.com'
    port = 587  
    server = smtplib.SMTP(smtp_server, port)
    server.starttls()
    
    # Login to your email account
    server.login(sender_email, sender_password)
    
    # Create a multipart message and set headers
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    
    # Add message body
    msg.attach(MIMEText(message, 'plain'))
    
    # Send the email
    server.send_message(msg)
    
    # Clean up
    server.quit()
