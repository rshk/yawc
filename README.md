# YAWC (Yet Another Web Chat)

## Configuration

You need to set a few environment variables for the process.

For development, you can simply create a ``.env`** file, containing a
few variables like this:

    PYTHONPATH=.
    SECRET_KEY=notasecret
    DATABASE_URL=postgres://postgres:@localhost:5432/yawc
    REDIS_URL=redis://localhost:6379

**Note:** I'm not 100% sure why pipenv isn't setting up the
``PYTHONPATH`** correctly, but it appears that setting it manually is
required.

**Important:** make sure you set ``SECRET_KEY`` to something
*actually* secret in production. I usually run ``pwgen -s 40 1`` to
generate random secret keys.


## Development

Install Python dependencies:

    pipenv install


Install Nodejs dependencies:

    cd web
    yarn install


Run services (PostgreSQL, Redis) via Docker:

    docker-compose up


Run database migrations:

    pipenv run alembic upgrade head


Start API server:

    pipenv run gunicorn -k flask_sockets.worker yawc.app_dev:app --reload --bind localhost:5000


Start frontend server:

    cd web
    API_URL=http://localhost:5000/graphql yarn start


Access the application by visiting http://localhost:8000

**Note:** head to http://localhost:8000/login to log in. There
currently is no redirect in place for non-authenticated users.


## User management

To create a new user:

    pipenv run python -m yawc user create 'myuser@example.com'


To list users:

    pipenv run python -m yawc user list


To change user password (for user #1 in this case):

    pipenv run python -m yawc user set-password 1
