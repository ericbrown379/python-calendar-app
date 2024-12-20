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
    
    # Check if the token already exists
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    
    # If no valid credentials are available, prompt the user to log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Build the credentials from environment variables
            client_id = os.getenv('GOOGLE_CLIENT_ID')
            client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
            redirect_uri = os.getenv('GOOGLE_REDIRECT_URIS')
            
            # Construct the flow object using the environment variables
            flow = InstalledAppFlow.from_client_config({
                'installed': {
                    'client_id': client_id,
                    'client_secret': client_secret,
                    'redirect_uris': redirect_uri,
                    'auth_uri': os.getenv('GOOGLE_AUTH_URI'),
                    'token_uri': os.getenv('GOOGLE_TOKEN_URI'),
                    'auth_provider_x509_cert_url': os.getenv('GOOGLE_AUTH_PROVIDER_CERT_URL'),
                    'project_id': os.getenv('GOOGLE_PROJECT_ID')
                }
            }, SCOPES)
            
            creds = flow.run_local_server(port=8080)
        
        # Save the credentials to the token.json file for future use
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
    """A placeholder for now because it's not 100% accurate SUpposed to check if the email exists outside this app"""
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
    subject = "Verify your calendarhive account"
    body = (
    f"Hello {username},\n\n"
    "Please verify your email by clicking the following link:\n\n"
    f"{verification_link}\n\n"
    "If you did not sign up for an account, please disregard this email.\n\n"
    "Best regards,\n"
    "The CalendarHive Team"
)
    print(body)  # Debug print to check email body
    send_email_via_gmail_oauth2(to_email, subject, body)

def send_password_reset_email(email, username, token):
    """Sends a reset password email to the user"""
    reset_password_link = url_for('reset_password', token=token, _external = True)
    subject = "Click the link below to reset your password"
    body = (
    f"Hi {username},\n\n"
    "If you requested to reset your password, please click the following link:\n\n"
    f"{reset_password_link}\n\n"
    "If you didn’t request a password reset, please disregard this email.\n\n"
    "Best regards,\n"
    "The CalendarHive Team"
)
    send_email_via_gmail_oauth2(email, subject, body)

