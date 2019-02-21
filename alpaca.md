## Alpaca API Keys
#### POST /api/alpaca/
##### updates or creates a 
Send:
```json
{
    "user": "5",
    "key_id": "321ehjkdfhghjfbcsadwkjq",
    "secret_key": "dhaukri3uqewd2fiu"
}
```
Response:
```json
{
    "user": "5",
    "key_id": "321ehjkdfhghjfbcsadwkjq",
    "secret_key": "dhaukri3uqewd2fiu"
}
```
#### GET /api/alpaca/\<user\>
Response:
```json
{
    "user": 5,
    "key_id": "321ehjkdfhghjfbcsadwkjq",
    "secret_key": "dhaukri3uqewd2fiu"
}
```