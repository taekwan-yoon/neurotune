# neurotune

## As soon as you git clone / git pull...

### Make sure you are in "neurotune" folder

Install the virtualenv package:

- pip install virtualenv

Create a virtual environment:

- virtualenv venv

Start the virtual environment:

- in Mac:
  - source venv/bin/activate
- in Windows:
  - venv\Scripts\activate

Install all packages:

- pip install -r requirements.txt

Also in a separate terminal/command prompts:

- npm i

## To start the project...

### Make sure you are in "neurotune" folder

First, do everything that was needed for "As soon as you git clone / git pull..."
Second, start the backend server:

- python {path to backend_server.py}

Example for mac:

- python ./src/model/backend_server.py

Third, start the frontend server:

- npm start

## Before you want to push...

### Make sure you are in "neurotune" folder

Save all requirements in requirements.txt:

- pip freeze > requirements.txt
