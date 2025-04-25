from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from typing import List
from pydantic import EmailStr, BaseModel
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Email configuration for MailHog
conf = ConnectionConfig(
    MAIL_USERNAME="",  # Not needed for MailHog
    MAIL_PASSWORD="",  # Not needed for MailHog
    MAIL_FROM="test@example.com",  # Can be any email for testing
    MAIL_PORT=1025,  # MailHog SMTP port
    MAIL_SERVER="localhost",  # MailHog server
    MAIL_STARTTLS=False,  # MailHog doesn't use TLS
    MAIL_SSL_TLS=False,  # MailHog doesn't use SSL
    USE_CREDENTIALS=False,  # No auth needed for MailHog
    VALIDATE_CERTS=False  # No cert validation needed for MailHog
)

class EmailSchema(BaseModel):
    email: List[EmailStr]

async def send_lead_notification(lead_data: dict, attorney_email: str):
    # Send email to prospect
    prospect_message = MessageSchema(
        subject="Thank you for your interest",
        recipients=[lead_data["email"]],
        body=f"""
        Dear {lead_data['first_name']} {lead_data['last_name']},

        Thank you for submitting your information. Our team will review your application and get back to you soon.

        Best regards,
        The Legal Team
        """,
        subtype=MessageType.plain
    )

    # Send email to attorney
    attorney_message = MessageSchema(
        subject="New Lead Submission",
        recipients=[attorney_email],
        body=f"""
        A new lead has been submitted:

        Name: {lead_data['first_name']} {lead_data['last_name']}
        Email: {lead_data['email']}

        Please review the attached resume and reach out to the prospect.
        """,
        subtype=MessageType.plain,
        attachments=[lead_data['resume_path']]
    )

    fm = FastMail(conf)
    await fm.send_message(prospect_message)
    await fm.send_message(attorney_message) 