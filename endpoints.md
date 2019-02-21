## User
### **All of the below require authentication**
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
- status: 200
```json
{
  "message": "updated profile."
}
```
