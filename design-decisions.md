# Design Decisions

## API Security and Access Control

### Public Lead Submission Endpoint
The lead submission endpoint (`/api/leads/`) is intentionally public (no authentication required) for several reasons:
- Reduces friction in the lead capture process, making it easier for potential clients to submit their information
- Allows integration with various front-end forms without requiring user accounts
- Enables third-party services to submit leads programmatically
- Follows the principle that capturing potential business should have minimal barriers

### Protected Administrative Endpoints
Other endpoints (lead management, user management) require authentication because:
- They provide access to sensitive client information
- They allow modifications to lead data
- They expose internal business operations
- They follow the principle of least privilege - only authorized personnel should have access

### Attorney Registration
Attorney registration is required because:
- It establishes accountability for lead handling
- It enables tracking of which attorney is handling which leads
- It allows for role-based access control
- It creates an audit trail for compliance purposes
- It enables personalized dashboards and lead assignment

## Technical Choices

### Pydantic for Data Validation
Pydantic was chosen for schema validation because:
- It provides runtime type checking and data validation
- It integrates seamlessly with FastAPI
- It automatically generates OpenAPI/Swagger documentation
- It offers clean error messages for invalid data
- It supports complex data structures and nested models
- It enables easy serialization/deserialization of data

### JWT (JSON Web Tokens) for Authentication
JWT was selected as the authentication mechanism because:
- It's stateless, reducing database load
- It's self-contained, carrying all necessary user information
- It's widely supported across different platforms and languages
- It's secure when implemented correctly
- It scales well in distributed systems

### 30-Minute JWT Expiration
The 30-minute token expiration was chosen to:
- Balance security with user experience
- Reduce the window of opportunity for token theft
- Force regular re-authentication for sensitive operations
- Align with common security best practices
- Provide sufficient time for normal user sessions

## API Design Decisions

### Separate Resume Download Endpoint
The resume download endpoint is separate from the main lead endpoints because:
- It handles binary file data differently from JSON responses
- It requires different security considerations for file access
- It needs specific headers and content-type handling
- It can be cached differently from regular API responses
- It allows for future enhancements like file format conversion or preview generation
- It separates concerns between lead data management and file serving

### Pagination with After-ID Strategy
Pagination using the "after_id" strategy was implemented because:
- It's more reliable than offset-based pagination for large datasets
- It handles concurrent updates better (no skipping or duplicating records)
- It's more performant as the database can use indices effectively
- It provides consistent results even when data is being modified
- It scales well with large datasets

## Future Considerations

- Implementing rate limiting for public endpoints
- Adding support for multiple file types beyond resumes
- Enhancing lead assignment algorithms
- Implementing real-time notifications
- Adding analytics and reporting features 