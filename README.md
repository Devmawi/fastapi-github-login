# GitHub login demo with FastAPI

First, copy `.env.sample` to `.env`:

    $ cp .env.sample .env

Create your GitHub OAuth Client and fill the client ID and secret
into `.env`, then run:

    $ python app.py

When register your GitHub OAuth Client, remember to put:

    http://127.0.0.1:8000/

into the client redirect uris list.