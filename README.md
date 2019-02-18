#### Adding user to database from command line
1. Create fixture file (i.e. allowing us to retrieve a properly hashed password)
- Run `python manage.py dumpdata auth.User --indent 4 > users.json`
2. Importing fixture into database
- Move file from above to `fixtures` directory
- Run `python manage.py loaddata users` to import `users.json`
