#### Adding user to database from command line
First time setup notes:

Frontend:
* yarn/npm install
    * Installs all the project dependencies for the project
* yarn/npm start
    * runs the development server. Really straightforward.

Backend:
* Things to install:
    * Ensure python3.X is installed
    * Ensure pip is installed
    * I’m pretty sure installing Anaconda takes care of both of these (keep reading for more info)
* Creating a python virtual environment:
    * I use anaconda for all my python management. I think it’s one of the more straightforward installation procedures and provides a lot of command line tools that are crossplatform
        * you can download that here: https://www.anaconda.com/download/#macos
        * Make sure you choose the python 3.x version
    * To create a new anaconda environment run: conda create -n marcopolo python=3
    * to activate an environment:
        * mac: source activate marcopolo
        * windows: activate marcopolo
    * to deactivate:
        * mac: source deactivate
        * windows: deactivate
    * to list the environments:
        * conda env list
    * To verify all the packages and versions installed in the environment (specifically look for pip):
        * conda list
        * if pip isn’t installed then activate the marcopolo environment and do: conda install pip
* make sure you’re in the proper environment (marcopolo if you’ve followed my instructions)
* CD into the root of the repository
* run: “pip install -r dependencies.txt”
    * Make sure that any time you add a new dependency/django module you add that to the list of dependencies cause that allows us to automate deployment
* run “python manage.py runserver”
* You should see some indication that the server is running.
* Currently you can visit 127.0.0.1:8000/api once it’s running to see the boilerplate API for the Django backend for the placeholder app.


####DON'T DO THIS STUFF
1. Create fixture file (i.e. allowing us to retrieve a properly hashed password)
- Run `python manage.py dumpdata auth.User --indent 4 > users.json`
2. Importing fixture into database
- Move file from above to `fixtures` directory
- Run `python manage.py loaddata users` to import `users.json`

####Do this to seed the first user
- Run `python manage.py loaddata users` to import `users.json`

####Database requirements for development (due to firstlogin not working)
- firstlogin = false
- your phone number must be in userprofile
- twilio must validate your phone number