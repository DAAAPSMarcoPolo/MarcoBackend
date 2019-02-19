
### /editProfile
Receives:
{
email: "sdblatz@gmail.com"
newEmail: "sblatz@purdue.edu" //optional
newName: "Sawyer" //optional
}

Sends:
{
sucess: "true"
error: "Email does not exist." //optional
}

### /profile

Receives:
{
email: "sdblatz@gmail.com"
}

Sends:
{
sucess: "true"
name: "Sawyer"
email: "sdblatz@gmail.com"
password: "securePass"
prefersEmailUpdates: "0"
postCount: "3"
}

### /createAccount

Receives:
{
email: "sdblatz@gmail.com",
name: "Sawyer",
email: "sdblatz@gmail.com",
password: "securePass",
phoneNumber: "2008657700",
prefersEmailUpdates: "0"
}

Sends:
{
sucess: "true"
error: "Email already exists." //optional
}

### /deleteAccount

Receives:
{
email: "sdblatz@gmail.com"
}

Sends:
{
sucess: "true"
error: "Email doesn't exist." //optional
}

### /changePassword

Receives:
{
email: "sdblatz@gmail.com"
password: "oldPassword"
newPassword: "newPassword"
}

Sends:
{
sucess: "true"
error: "Email doesn't exist." //optional
}



### /addpicture

Receives:
{
    file: image ->(multipart/form-data)
    email: "luna.ad2@gmail.com"
}

Send:

{

    success: "true",

    error: "success: false"

}

### /getPicture

Receives:

{
    'email': ''
}

Send:

{
    "success": "true"
    error: "success: false"
}
