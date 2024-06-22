# Enkantea-Back - Project Architecture

Our project is structured into five distinct layers, each with a specific responsibility:

## 1. Web Layer
- **Purpose**: Input/output layer over HTTP
- **Responsibilities**:
  - Assembles client requests
  - Calls the Service Layer
  - Returns responses to clients
- **Technologies**: FastAPI

## 2. Service Layer
- **Purpose**: Houses the business logic
- **Responsibilities**:
  - Implements core business rules and workflows
  - Calls the Data Layer when data access is needed
- **Key Components**: FastAPI

## 3. Data Layer
- **Purpose**: Manages data access and external service interactions
- **Responsibilities**:
  - Provides access to data stores
  - Interfaces with external services
- **Technologies**: FastAPI, SQLModel

## 4. Model
- **Purpose**: Defines data structures used across all layers
- **Responsibilities**:
  - Provides shared data definitions
  - Ensures data consistency across the application
- **Key Models**: SQLModel

## 5. Database
- **Type**: Postgres
- **Hosting**: Google Cloud Platform (GCP)
- **Purpose**: Persistent data storage for the application

## Architecture Diagram

![Diagram](img/Schema.png)

## Data Flow

1. Client request → Web Layer
2. Web Layer → Service Layer
3. Service Layer → Data Layer (if data access is needed)
4. Data Layer → Database
5. Response flows back through the layers to the client

This layered architecture promotes separation of concerns, making the codebase more maintainable, testable, and scalable.


## Security Layer

Security is a cross-cutting concern that integrates with all layers of our architecture:

### Web Layer Security
- **Authentication Middleware**: Verifies JWT tokens or sessions for each request
- **Input Validation**: Validates and sanitizes all user inputs
- **CORS Configuration**: Manages Cross-Origin Resource Sharing policies
- **Rate Limiting**: Limits the number of requests per user to prevent abuse

### Service Layer Security
- **Authorization Logic**: Implements Role-Based Access Control (RBAC)
- **Business Rule Enforcement**: Ensures all operations comply with business and security rules
- **Audit Logging**: Records important actions for traceability

### Data Layer Security
- **Query Parameterization**: Prevents SQL injections
- **Data Encryption**: Encrypts sensitive data before storage
- **Access Control**: Applies data access restrictions based on security policies

### Model Security
- **Data Validation**: Includes validators to ensure data integrity
- **Sensitive Data Handling**: Specifically marks and manages sensitive data fields

### Database Security
- **Encryption at Rest**: Ensures data is encrypted in the database
- **Secure Connections**: Uses SSL/TLS for database connections
- **Least Privilege Access**: Applies the principle of least privilege for database access

### Cross-Cutting Security Concerns
- **Secret Management**: Uses secret managers (e.g., Google Secret Manager) to handle keys and passwords
- **Dependency Security**: Regularly scans and updates dependencies for known vulnerabilities
- **Logging and Monitoring**: Implements secure logging and continuous monitoring for potential threats
- **Error Handling**: Ensures error messages do not disclose sensitive information

## Security Flow

1. Client request is first validated and authenticated in the Web Layer
2. Authorization is checked in the Service Layer before processing
3. Data access is secured in the Data Layer
4. All interactions with the database are encrypted and controlled

This multi-layered security approach ensures that each component of our architecture contributes to the overall security posture of the application.
