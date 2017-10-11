# Blog App

Project that implements full CRUD operation using PostgreSQL, Peewee, and Tornado

## Getting Started
1. Install [Python3](https://www.python.org/downloads/)

2. Clone Repository:

        $ git clone https://github.com/egarcia410/blogApp.git

3. Change Directory:

        $ cd blogApp

4. Install [VirtualWrapper](https://virtualenvwrapper.readthedocs.io/en/latest/install.html)

5. Create and Activate Virtualenv:

        $ mkvirtualenv -a `pwd` -p `which python3` INSERT_VIRTUALENV_NAME
    
6. Install Dependencies:

        $ pip install -r requirements.txt

7. Create an `.env` file:

        $ touch .env

8. Insert secret into `.env` file:

        ```
        SECRET=INSERT_SECRET_PHRASE_HERE
        ```

**This phrase can be any length of numbers and letters**

9. Run Program:

        $ python app.py