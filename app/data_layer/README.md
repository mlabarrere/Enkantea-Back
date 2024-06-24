# Data Layer

This folder contains the modules for the data layer of the Enkantea-Back application. The data layer is responsible for CRUD (Create, Read, Update, Delete) operations on the database, as well as managing interactions with external services.

## Structure

The folder contains the following files:

- `clients.py`: Manages operations related to clients
- `lots.py`: Manages operations related to lots
- `organisations.py`: Manages operations related to organizations
- `sales.py`: Manages operations related to sales
- `sellers.py`: Manages operations related to sellers
- `users.py`: Manages operations related to users

## Main Features

Each module provides functions to:
- Create new entries in the database
- Retrieve existing entries
- Update existing entries
- Delete entries
- Perform specific queries (e.g., retrieve all users of an organization)

## Usage

These modules are used by the service layer to perform operations on the database. They should not be called directly from the web layer.

Example of usage in the service layer:

```python
from app.data_layer.users import create_user
from app.models.users import UserCreate

def service_create_user(user_data: UserCreate, session: Session):
    # Additional business logic if needed
    return create_user(session, user_data)
```

## Error Handling
The data layer modules raise specific exceptions in case of errors, such as DatabaseOperationError, UserNotFoundError, etc. These exceptions should be handled in the service layer.

## Security
Data layer operations do not handle authorizations. Authorization checks should be performed in the service layer before calling data layer functions.

## Maintenance
When adding new features or modifying data models, make sure to update the corresponding modules in this folder.

## Dependencies
The data layer modules depend on:
- SQLModel for ORM operations
- Custom exception classes defined in app.core.exceptions
- Data models defined in app.models

Ensure these dependencies are properly maintained when making changes to the data layer.

## Testing
Unit tests for the data layer should be written to ensure the correctness of CRUD operations and error handling. These tests should use a separate test database to avoid affecting production data.

## Performance Considerations
When dealing with large datasets, consider implementing pagination in list retrieval functions to optimize performance and resource usage.

## Future Improvements
- Implement caching mechanisms for frequently accessed data
- Add logging for critical database operations
- Develop more advanced querying capabilities as needed by the application
