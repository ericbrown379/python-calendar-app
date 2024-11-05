import os  # For working with the files
import smtplib
from email.mime.text import MIMEText  # Required for plain text
from email.mime.multipart import MIMEMultipart  # Helps with attachments and other file types
import re
import dns.resolver
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request  # For HTTP functionality
from flask import url_for


SCOPES = ['https://www.googleapis.com/auth/gmail.send']
SENDER_EMAIL = 'calendarhive1@gmail.com'
APP_PASSWORD = 'dqinbifpiuwxlmtl'


def get_gmail_credentials():
    """Gets credentials from the GMAIL API for our app to send emails to users"""
    creds = None
    token_path = 'token.json'
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if not creds or not creds.valid:#If no valid creds are available, prompt the user to log in
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=8080)
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
    return creds


def is_valid_email_format(email):
    """Checks if user's email is in the correct format such as having @ and .com"""
    # Regular expression for validating an Email
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None


def domain_has_mx_records(domain):    
    try:
        # Get MX records for the domain
        mx_records = dns.resolver.resolve(domain, 'MX')
        return bool(mx_records)
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
        return False


def check_email_exists(email_address): 
    """A placeholder for now because it's not 100% accurate"""
    if not is_valid_email_format(email_address):
        print("Invalid email format.")
        return False

    domain = email_address.split('@')[1]

    if not domain_has_mx_records(domain):
        print("Domain does not have MX records.")
        return False

    print("Email format is valid and the domain has MX records.")
    return True


def send_email_via_gmail_oauth2(to_email, subject, body):
    """Sending an email to the user through the GMAIL API"""
    creds = get_gmail_credentials()
    # Prepare email message
    message = MIMEMultipart('alternative')
    message['From'] = SENDER_EMAIL
    message['To'] = to_email
    message['Subject'] = subject

    # Attach both plain text and HTML versions
    message.attach(MIMEText(body, 'plain'))  # Use 'plain' or 'html' depending on your content
    message.attach(MIMEText(body, 'html'))   # Ensure body is valid HTML if using this

    # Send the email without base64 encoding
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.ehlo()
            server.starttls()  # Upgrade to a secure connection
            server.ehlo()
            server.login(SENDER_EMAIL, APP_PASSWORD)  # Use correct login method
            server.sendmail(SENDER_EMAIL, to_email, message.as_string())  # Use as_string() here
    except Exception as e:
        print(f"Error sending email: {e}")


def send_verification_email(email, username, token):
    """Creates a verification email"""
    if not token:
        print("Token is None or empty.")  # Debug print
        return  # Prevents further execution if token is invalid

    # Generate verification link with token
    verification_link = url_for('verify_email', token=token, _external=True)    
    to_email = email  # Corrected this line
    subject = "Verify your account"
    body = f"Hello {username}, please verify your email by clicking the following link: {verification_link}"
    print(body)  # Debug print to check email body
    send_email_via_gmail_oauth2(to_email, subject, body)
