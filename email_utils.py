from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from typing import List
from pydantic import EmailStr, BaseModel

# These should be moved to environment variables
conf = ConnectionConfig(
    MAIL_USERNAME="your-email@example.com",
    MAIL_PASSWORD="your-password",
    MAIL_FROM="your-email@example.com",
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True
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
        attachments=[lead_data['resume_path']]
    )

    fm = FastMail(conf)
    await fm.send_message(prospect_message)
    await fm.send_message(attorney_message) 