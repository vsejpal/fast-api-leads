# 🚀 Lead Management System

A modern FastAPI application for managing legal leads, handling resume submissions, and automating email notifications.

## 📋 Table of Contents

- [System Design](#-system-design)
- [Implementation Details](#-implementation-details)
- [Getting Started](#-getting-started)
- [API Documentation](#-api-documentation)
- [Security](#-security)
- [Development](#-development)
- [Future Improvements](#-future-improvements)

## 🎯 System Design

### Components

- **FastAPI Backend**: RESTful API service
- **SQLite Database**: Local data storage
- **Email Service**: Notification system using SMTP
- **File Storage**: Local resume storage system

### Data Models

```python
# Lead Model
class Lead:
    id: int
    first_name: str
    last_name: str
    email: str
    resume_path: str
    state: LeadState  # PENDING or REACHED_OUT
    created_at: datetime
    updated_at: datetime

# User Model (Attorneys)
class User:
    id: int
    email: str
    hashed_password: str
    is_active: bool
    created_at: datetime
```

### API Endpoints

```plaintext
POST   /api/auth/token       # Login for access token
POST   /api/auth/register    # Register new attorney
POST   /api/leads           # Create new lead with resume
GET    /api/leads           # List leads (paginated)
PATCH  /api/leads/{id}      # Update lead state
GET    /api/leads/{id}/resume  # Download resume
```

## 🔧 Implementation Details

### Database Schema

- SQLAlchemy ORM with SQLite backend
- Automatic table creation and migrations
- Cursor-based pagination for efficient querying

### File Handling

```python
ALLOWED_RESUME_TYPES = {
    'application/pdf': '.pdf',
    'application/msword': '.doc',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
    'text/plain': '.txt'
}
```

- Secure file storage in `uploads/` directory
- Content-type validation
- Unique filename generation using email

### Email Notifications

- Automated emails on lead creation:
  - Confirmation to prospect
  - Notification to attorney with resume attachment
- Configurable SMTP settings (supports Gmail, MailHog for development)

### State Management

- Leads start in `PENDING` state
- Can be updated to `REACHED_OUT` by attorneys
- Audit trail with `created_at` and `updated_at` timestamps

## 🚀 Getting Started

### Prerequisites

```bash
python 3.8+
pip
virtualenv
```

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd lead-management-system

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your settings
```

### Running the Application

```bash
# Development
python -m app.main

# Production (using uvicorn)
uvicorn app.main:app --host 0.0.0.0 --port 8001
```

## 📖 How to Use

### Install Dependencies

```bash
# Install project dependencies
pip install -r requirements.txt

# Required packages will include:
# - fastapi
# - uvicorn
# - sqlalchemy
# - python-jose[cryptography]
# - passlib[bcrypt]
# - python-multipart
# - pydantic[email]
# - aiosmtplib
```

### Using MailHog for Development

```bash
# Install MailHog (macOS)
brew install mailhog

# Start MailHog
mailhog

# Access MailHog Web Interface
open http://localhost:8025

# Update .env file with MailHog settings
SMTP_HOST=localhost
SMTP_PORT=1025
SMTP_USER=
SMTP_PASSWORD=
SMTP_TLS=False
```

### Create an Attorney User

```bash
# Register a new attorney user
curl -X POST "http://localhost:8001/api/auth/register" \
     -H "Content-Type: application/json" \
     -d '{
           "email": "attorney@example.com",
           "password": "strongpassword123"
         }'

# Response:
{
    "id": 1,
    "email": "attorney@example.com",
    "is_active": true,
    "created_at": "2024-03-20T10:00:00"
}
```

### Get an Access Token

```bash
# Login to get JWT token
curl -X POST "http://localhost:8001/api/auth/token" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=attorney@example.com&password=strongpassword123"

# Response:
{
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "token_type": "bearer"
}

# Store token for later use
export TOKEN="eyJ0eXAiOiJKV1QiLCJhbGc..."
```

### Submit a Lead (Public Endpoint)

```bash
# Create a new lead with resume
curl -X POST "http://localhost:8001/api/leads" \
     -F "first_name=John" \
     -F "last_name=Doe" \
     -F "email=john.doe@example.com" \
     -F "resume=@/path/to/resume.pdf"

# Response:
{
    "id": 1,
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "resume_path": "uploads/john.doe@example.com_resume.pdf",
    "state": "PENDING",
    "created_at": "2024-03-20T10:15:00",
    "updated_at": "2024-03-20T10:15:00"
}
```

### List Leads (Protected Endpoint)

```bash
# Get paginated list of leads
curl -X GET "http://localhost:8001/api/leads?page_size=10" \
     -H "Authorization: Bearer $TOKEN"

# Response:
{
    "items": [
        {
            "id": 1,
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "state": "PENDING",
            "created_at": "2024-03-20T10:15:00",
            "updated_at": "2024-03-20T10:15:00"
        }
    ],
    "total": 1,
    "has_more": false,
    "last_id": 1
}

# Get next page using cursor pagination
curl -X GET "http://localhost:8001/api/leads?page_size=10&after_id=1" \
     -H "Authorization: Bearer $TOKEN"
```

### Update Lead (Protected Endpoint)

```bash
# Update lead state
curl -X PATCH "http://localhost:8001/api/leads/1" \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
           "state": "REACHED_OUT"
         }'

# Response:
{
    "id": 1,
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "state": "REACHED_OUT",
    "created_at": "2024-03-20T10:15:00",
    "updated_at": "2024-03-20T10:30:00"
}
```

### Download Resume

```bash
# Download lead's resume
curl -X GET "http://localhost:8001/api/leads/1/resume" \
     -H "Authorization: Bearer $TOKEN" \
     --output downloaded_resume.pdf

# The file will be downloaded as 'downloaded_resume.pdf'
```

## 📚 API Documentation

After starting the server, visit:

- Swagger UI: `http://localhost:8001/docs`
- ReDoc: `http://localhost:8001/redoc`

### Example API Usage

```bash
# Login
curl -X POST "http://localhost:8001/api/auth/token" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=attorney@example.com&password=secret"

# Create Lead (with resume)
curl -X POST "http://localhost:8001/api/leads" \
     -H "Authorization: Bearer <token>" \
     -F "first_name=John" \
     -F "last_name=Doe" \
     -F "email=john@example.com" \
     -F "resume=@/path/to/resume.pdf"
```

## 🔒 Security

### Authentication

- JWT-based token authentication
- Password hashing using bcrypt
- Token expiration and refresh mechanism

### File Security

- File type validation
- Secure file paths
- No direct file access without authentication

### Data Protection

- Input validation using Pydantic
- SQL injection protection via SQLAlchemy
- Rate limiting on authentication endpoints

## 💻 Development

### Project Structure

```
app/
├── api/
│   ├── endpoints/
│   │   ├── auth.py
│   │   └── leads.py
│   └── api.py
├── core/
│   └── security.py
├── crud/
│   ├── leads.py
│   └── users.py
├── db/
│   ├── models.py
│   └── session.py
├── services/
│   └── email.py
├── schemas.py
└── main.py
```

### Testing

```bash
# Run tests
pytest

# Coverage report
pytest --cov=app tests/
```

## 🚧 Future Improvements

### Planned Features

- [ ] Advanced search and filtering
- [ ] Document preview
- [ ] Analytics dashboard
- [ ] Bulk lead import/export
- [ ] Email templates customization

### Performance Enhancements

- [ ] Caching layer
- [ ] Background task processing
- [ ] File storage optimization
- [ ] Database indexing optimization

### Infrastructure

- [ ] Docker containerization
- [ ] CI/CD pipeline
- [ ] Cloud storage integration
- [ ] Monitoring and logging
- [ ] Load balancing

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
