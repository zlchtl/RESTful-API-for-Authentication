## RESTful API for Authentication

REST API for user authentication and authorization system using Django and Django REST Framework. The system supports user registration, authentication, token renewal, logout and updating of their personal information.

Technology stack: Django, django-constance, DjangoRestFramework, PyJWT.

API documentation: `/swagger/` or `/redoc/`.
Admin webpage: `/admin/`.
API webpages: 
- **POST** `/register/` - **Body**: username, email, password.
 -> **JSON**: id, email.
- **POST** `/login/` - **Body**: email, password.
 -> **JSON**: access_token, refresh_token.
- **POST** `/refresh/` - **Body**: refresh_token.
 -> **JSON**: access_token, refresh_token.
- **POST** `/logout/` - **Body**: refresh_token.
 -> **JSON**: message.
- **GET** `/me/` - **Headers**: Authorization: Bearer `access_token`.
 -> **JSON**: id, email, username.
- **PUT** `/me/` - **Headers**: Authorization: Bearer `access_token`, **Body**: username, email.
 -> **JSON**: id, email, username.
