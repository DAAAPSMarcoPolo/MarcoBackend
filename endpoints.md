- Unless otherwise stated, responses will have the status (200).
- Unless otherwise stated, responses are assuming a successful request.

## User
#### POST /api/auth/login/
Send:
```json
{
  "username": "sean.becker15@gmail.com",
  "password": "password"
}
```
Response (success, first login):
```json
{
  "message": "first login",
  "token": "aldklafljas"
}
```
Response (success, __not__ first login):
```json
{
  "message": "code sent"
}
```
Response (failure, invalid credentials):
- status 400
```json
{
  non_field_errors: [
    'Unable to log in with provided credentials.',
  ]
}
```
#### POST /api/auth/loginfactor/
Send:
```json
{
  "username": "sean.becker15@gmail.com",
  "password": "password",
  "code": "123456",
}
```
Response (success):
```json
{
  "message": "code correct",
  "token": "token",
  "isAdmin": true | false
}
```
Response (failure, incorrect code):
- status 400
```json
{
  "error": "incorrect code"
}
```

### **All of the below require authentication**
#### POST /api/auth/firstlogin/
Send (requires all!):
```json
{
  "username": "sean.becker15@gmail.com",
  "first_name": "Sean",
  "last_name": "Becker",
  "phone_number": "1234567891",
  "password": "password",
  "new_password": "new_password"
}
```
Response (success):
```json
{
  "message": "profile updated."
}
```
Response (failure, did not attach username or password):
- TBD
Response (failure, did not attach first or last name):
```json
{
  "message": "UpdateAuthUserSerializer invalid."
}
```
Response (failure, attached a field not allowed):
```json
{
  "message": "UserProfileSerializer invalid."
}
```
#### GET /api/user/settings/
Response:
```json
{
    "user": {
        "username": "sean.becker15@gmail.com",
        "first_name": "Sean",
        "last_name": "Becker",
        "profile__phone_number": "8479775375"
    }
}
```
#### PUT /api/user/settings/
Send:
```json
{
  username: "sean.becker15@gmail.com",
  first_name: "Sean",
  last_name: "Becker",
  phone_number: "8479775375"
  password: "password",
  new_password: "new_password"
}
```
Response (success):
```json
{
  "message": "updated profile."
}
```
### **All of the below require admin privileges**
#### GET /api/users/list/
Response:
```json
{"users":[{"username":"sean.becker15@gmail.com"},{"username":"pshoroff@hotmail.com"}]}
```
#### DELETE /api/users/list/
Send:
```json
{
  "username": "sean.becker15@gmail.com"
}
```
Response:
```json
{
  "message": "user deleted."
}
```
#### POST /auth/adduser
Send:
```json
{
  "username": "sean.becker15@gmail.com",
  "password": "password"
}
```
Response: (should be modified after sprint 1- remove token)
```json
{
  "user": "sean.becker15@gmail.com",
  "token": "alksjdlajsfkjlalskdj"
}
```
