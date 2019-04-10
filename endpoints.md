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
    "Unable to log in with provided credentials.",
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


## Backtest
#### POST /api/backtest/
##### runs a backtest.  A response will be given to the front end right away and the user will receive a text after the backtest finishes running
Send:
```json
{
	"strategy": 34,
	"universe": 65,
	"start_date": "2018-1-1",
	"end_date": "2019-3-1",
	"initial_funds": 2000
}
```
Response:
```
"backtest is running"
```
#### GET /api/backtest/\<backtestId\>
##### returns one backtest object
Response:
```json
{
    "backtest": {
        "id": 19,
        "universe": {
            "id": 23,
            "name": "Universe for quick backtest",
            "updated": "2019-03-27T14:49:28.515380Z",
            "user": 5,
            "stocks": [
                "BIOC",
                "ALDX",
                "BA",
                "SAEX",
                "TSLA",
                "MAXR",
                "DGAZ",
                "UGAZ",
                "MSFT"
            ]
        },
        "strategy": {
            "id": 34,
            "name": "mean_reversion",
            "description": "mean reversion",
            "strategy_file": "http://localhost:8000/backendStorage/uploads/algos/mean_reversion.py",
            "approved": false,
            "live": false,
            "created_at": "2019-03-23T19:11:36.123175Z",
            "user": 5
        },
        "complete": true,
        "start_date": "2018-01-01T00:00:00Z",
        "end_date": "2019-03-01T00:00:00Z",
        "initial_cash": 2000,
        "end_cash": 4093.0496,
        "sharpe": 2.89,
        "created_at": "2019-03-27T14:49:28.912147Z",
        "user": 5
    },
    "trades": [
        {
            "id": 443,
            "backtest_id": 19,
            "symbol": "DGAZ",
            "buy_time": "2019-03-27T14:49:38.528675Z",
            "sell_time": "2019-03-27T14:49:38.528736Z",
            "buy_price": 24.65,
            "sell_price": 32.15,
            "qty": 32
        },
        {
            "id": 444,
            "backtest_id": 19,
            "symbol": "MSFT",
            "buy_time": "2019-03-27T14:49:38.674042Z",
            "sell_time": "2019-03-27T14:49:38.674064Z",
            "buy_price": 87.66,
            "sell_price": 88.2,
            "qty": 88
        }
    ]
}
```

#### GET /api/backtest/
##### returns an aray of all completed backtests
Response:
```json
[
    {
        "backtest": {
            "id": 19,
            "universe": {
                "id": 23,
                "name": "Universe for quick backtest",
                "updated": "2019-03-27T14:49:28.515380Z",
                "user": 5,
                "stocks": [
                    "BIOC",
                    "ALDX",
                    "BA",
                    "SAEX",
                    "TSLA",
                    "MAXR",
                    "DGAZ",
                    "UGAZ",
                    "MSFT"
                ]
            },
            "strategy": {
                "id": 34,
                "name": "mean_reversion",
                "description": "mean reversion",
                "strategy_file": "http://localhost:8000/backendStorage/uploads/algos/mean_reversion.py",
                "approved": false,
                "live": false,
                "created_at": "2019-03-23T19:11:36.123175Z",
                "user": 5
            },
            "complete": true,
            "start_date": "2018-01-01T00:00:00Z",
            "end_date": "2019-03-01T00:00:00Z",
            "initial_cash": 2000,
            "end_cash": 4093.0496,
            "sharpe": 2.89,
            "created_at": "2019-03-27T14:49:28.912147Z",
            "user": 5
        },
        "trades": [
            {
                "id": 443,
                "backtest_id": 19,
                "symbol": "DGAZ",
                "buy_time": "2019-03-27T14:49:38.528675Z",
                "sell_time": "2019-03-27T14:49:38.528736Z",
                "buy_price": 24.65,
                "sell_price": 32.15,
                "qty": 32
            },
            {
                "id": 444,
                "backtest_id": 19,
                "symbol": "MSFT",
                "buy_time": "2019-03-27T14:49:38.674042Z",
                "sell_time": "2019-03-27T14:49:38.674064Z",
                "buy_price": 87.66,
                "sell_price": 88.2,
                "qty": 88
            }
        ]
    }
]
```

#### GET /api/backtest/\<backtestId\>
##### returns an array of backtest objects containing all backtests run
Response:
```json
[
{
    "backtest": {
        "id": 16,
        "complete": true,
        "start_date": "2018-01-01T00:00:00Z",
        "end_date": "2019-03-01T00:00:00Z",
        "initial_cash": 2000,
        "end_cash": 4093.0496,
        "sharpe": 2.89,
        "created_at": "2019-03-27T00:18:08.572453Z",
        "strategy": 34,
        "universe": 20,
        "user": 5
    },
    "trades": [
        {
            "id": 207,
            "backtest_id": 16,
            "symbol": "DGAZ",
            "buy_time": "2019-03-27T00:18:17.251256Z",
            "sell_time": "2019-03-27T00:18:17.251316Z",
            "buy_price": 24.65,
            "sell_price": 32.15,
            "qty": 32
        },
        {
            "id": 208,
            "backtest_id": 16,
            "symbol": "MSFT",
            "buy_time": "2019-03-27T00:18:17.398419Z",
            "sell_time": "2019-03-27T00:18:17.398472Z",
            "buy_price": 87.66,
            "sell_price": 88.2,
            "qty": 88
        }
    ]
}
]

```
#### GET /api/algorithm/
##### returns an array of all strategies with the best backtest for each 
Response:
```json
[
    {
        "algo_details": {
            "name": "mean_reversion",
            "description": "mean reversion",
            "user": 5,
            "created_at": "2019-03-23T19:11:36.123175Z",
            "approved": false
        },
        "best_backtest": {
            "id": 35,
            "strategy_id": 34,
            "universe_id": 39,
            "user_id": 5,
            "complete": true,
            "successful": true,
            "start_date": "2017-01-01T00:00:00Z",
            "end_date": "2019-03-01T00:00:00Z",
            "initial_cash": 1000,
            "end_cash": 2636.5377,
            "sharpe": 2.94,
            "created_at": "2019-03-27T15:49:15.083884Z"
        }
    },
    {
        "algo_details": {
            "name": "testalgo",
            "description": "algoDescription",
            "user": 13,
            "created_at": "2019-03-27T21:23:48.064777Z",
            "approved": false
        },
        "best_backtest": ""
    }
]
```

#### GET /api/algorithm/\<strategyId\>
##### returns an array of strategy specified by strategyid 
Response:
```json
{
    "algo_details": {
        "name": "mean_reversion",
        "description": "mean reversion",
        "user": 5,
        "created_at": "2019-03-23T19:11:36.123175Z",
        "approved": false
    },
    "bt_list": [
        {
            "id": 37,
            "strategy_id": 34,
            "universe_id": 41,
            "user_id": 5,
            "complete": false,
            "successful": false,
            "start_date": "2010-01-01T00:00:00Z",
            "end_date": "2019-03-01T00:00:00Z",
            "initial_cash": 1000000,
            "end_cash": 1000000,
            "sharpe": -1,
            "created_at": "2019-03-27T15:49:22.972281Z"
        },
        {
            "id": 35,
            "strategy_id": 34,
            "universe_id": 39,
            "user_id": 5,
            "complete": true,
            "successful": true,
            "start_date": "2017-01-01T00:00:00Z",
            "end_date": "2019-03-01T00:00:00Z",
            "initial_cash": 1000,
            "end_cash": 2636.5377,
            "sharpe": 2.94,
            "created_at": "2019-03-27T15:49:15.083884Z"
        }
    ]
}
```

## Strategy Backtest
#### GET /api/strategybacktests/\<StrategyId\>
##### This function will return an array of all backtests run for a specified strategy
Response:
```json
[
{
    "backtest": {
        "id": 16,
        "complete": true,
        "start_date": "2018-01-01T00:00:00Z",
        "end_date": "2019-03-01T00:00:00Z",
        "initial_cash": 2000,
        "end_cash": 4093.0496,
        "sharpe": 2.89,
        "created_at": "2019-03-27T00:18:08.572453Z",
        "strategy": 34,
        "universe": 20,
        "user": 5
    },
    "trades": [
        {
            "id": 207,
            "backtest_id": 16,
            "symbol": "DGAZ",
            "buy_time": "2019-03-27T00:18:17.251256Z",
            "sell_time": "2019-03-27T00:18:17.251316Z",
            "buy_price": 24.65,
            "sell_price": 32.15,:
            "qty": 32
        },
        {
            "id": 208,
            "backtest_id": 16,
            "symbol": "MSFT",
            "buy_time": "2019-03-27T00:18:17.398419Z",
            "sell_time": "2019-03-27T00:18:17.398472Z",
            "buy_price": 87.66,
            "sell_price": 88.2,
            "qty": 88
        }
    ]
}
]
```

## Live Trading Instance
#### Post /api/live/
##### This response can be sent one of two ways to either start or stop a backtest as seen below
###### To start a backtest...
Send:
```json
{
  "mode": "start",
  "backtest": 34
}
```
Response:
Starting up a live instance.
###### To stop a backtest...(* Note that id is the id of the live instance)

Send:
```json
{
  "mode": "stop",
  "id": 20
}
```
Response:
"Successfully shut down live instance."

#### GET /api/live/\<live_instance_id>
##### Returns a live trading instance and its trades
Response:
```json
{
    "live_instance": {
        "id": 19,
        "pid": 31127,
        "live": false,
        "backtest": 74
    },
    "trades": [
        {
            "id": 1,
            "live_trade_instance_id": 19,
            "symbol": "AAPL",
            "open": true,
            "open_date": "2019-04-10T16:43:15.619000Z",
            "close_date": null,
            "qty": 1,
            "open_price": 2,
            "close_price": null
        },
        {
            "id": 2,
            "live_trade_instance_id": 19,
            "symbol": "MSFT",
            "open": false,
            "open_date": "2019-04-10T19:11:10.413000Z",
            "close_date": "2019-04-10T19:11:12.947000Z",
            "qty": 1,
            "open_price": 2,
            "close_price": 3
        }
    ]
}
```

#### GET /api/live/
##### Returns all live trading instance and their trades
Response:
```json
[
    {
        "live_instance": {
            "id": 19,
            "pid": 31127,
            "live": false,
            "backtest": 74
        },
        "trades": [
            {
                "id": 1,
                "live_trade_instance_id": 19,
                "symbol": "AAPL",
                "open": true,
                "open_date": "2019-04-10T16:43:15.619000Z",
                "close_date": null,
                "qty": 1,
                "open_price": 2,
                "close_price": null
            },
            {
                "id": 2,
                "live_trade_instance_id": 19,
                "symbol": "MSFT",
                "open": false,
                "open_date": "2019-04-10T19:11:10.413000Z",
                "close_date": "2019-04-10T19:11:12.947000Z",
                "qty": 1,
                "open_price": 2,
                "close_price": 3
            }
        ]
    },
    {
        "live_instance": {
            "id": 20,
            "pid": 31122,
            "live": false,
            "backtest": 74
        },
        "trades": [
            {
                "id": 1,
                "live_trade_instance_id": 19,
                "symbol": "AAPL",
                "open": true,
                "open_date": "2019-04-10T16:43:15.619000Z",
                "close_date": null,
                "qty": 1,
                "open_price": 2,
                "close_price": null
            },
            {
                "id": 2,
                "live_trade_instance_id": 19,
                "symbol": "MSFT",
                "open": false,
                "open_date": "2019-04-10T19:11:10.413000Z",
                "close_date": "2019-04-10T19:11:12.947000Z",
                "qty": 1,
                "open_price": 2,
                "close_price": 3
            }
        ]
    }
]

```


