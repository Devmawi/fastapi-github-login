from typing import Optional, List, Dict
from fastapi import FastAPI, status, Request, Depends, HTTPException
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
import uvicorn
from starlette.middleware.sessions import SessionMiddleware
import time
from fastapi.responses import RedirectResponse, FileResponse, HTMLResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, OpenIdConnect
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
import json


app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="some-random-string")


# see more on https://docs.github.com/en/developers/apps/building-oauth-apps/authorizing-oauth-apps#web-application-flow
# and https://docs.authlib.org/en/latest/client/starlette.html#starlette-client
# and https://docs.authlib.org/en/latest/client/frameworks.html#frameworks-clients
config = Config('.env')
oauth = OAuth()
oauth.register(
    'github',
    # client_id=<YOUR CLIENT_ID>,
    # client_secret='<YOUR CLIENT_SECRET>',
    access_token_url='https://github.com/login/oauth/access_token',
    authorize_url='https://github.com/login/oauth/authorize',
    client_kwargs={
        'scope': 'user'
    }
)


@app.get('/')
async def homepage(request: Request):
    user = request.session.get('user')
    if user:
        data = json.dumps(user)
        html = (
            f'<pre>{data}</pre>'
            '<a href="/logout">logout</a>'
        )
        return HTMLResponse(html)
    return HTMLResponse('<a href="/login">login</a>')


@app.get('/login')
async def login(request: Request):
    redirect_uri = request.url_for('auth')
    return await oauth.github.authorize_redirect(request, redirect_uri)


@app.get('/auth')
async def auth(request: Request):
    token = await oauth.github.authorize_access_token(request)
    url = 'https://api.github.com/user'
    resp = await oauth.github.get(
        url, token=token)
    user = resp.json()
    request.session['user'] = dict(user)
    return RedirectResponse(url='/')


@app.get('/logout')
async def logout(request: Request):
    request.session.pop('user', None)

    return RedirectResponse(url='https://github.com/logout')


if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8000)