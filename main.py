'''
Starts a Twitter Clone webserver
'''

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import sqlite3
import uvicorn

app = FastAPI()
templates = Jinja2Templates(directory='templates')
app.mount('/static', StaticFiles(directory='static'), name='static')


def check_credentials(request: Request):
    '''
    Returns username if user is logged in, None otherwise.
    '''
    return request.cookies.get('username')


@app.get('/', response_class=HTMLResponse)
async def index(request: Request):
    con = sqlite3.connect('twitter_clone.db')
    cur = con.cursor()
    sql = '''
    SELECT messages.message, messages.created_at, users.username, users.age
    FROM messages
    JOIN users ON messages.sender_id = users.id
    ORDER BY messages.created_at DESC;
    '''
    cur.execute(sql)
    rows = cur.fetchall()
    con.close()

    messages = [
        {
            'message': row[0],
            'created_at': row[1],
            'username': row[2],
            'age': row[3],
        }
        for row in rows
    ]

    return templates.TemplateResponse(
        request=request,
        name='index.html',
        context={
            'is_logged_in': check_credentials(request),
            'username': check_credentials(request),
            'messages': messages,
        }
    )


@app.get('/login', response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse(
        request=request,
        name='login.html',
        context={
            'is_logged_in': check_credentials(request),
            'error': None,
        }
    )


@app.post('/login', response_class=HTMLResponse)
async def login_post(request: Request):
    form = await request.form()
    username = form.get('username')
    password = form.get('password')

    con = sqlite3.connect('twitter_clone.db')
    cur = con.cursor()
    cur.execute(
        'SELECT id FROM users WHERE username=? AND password=?',
        (username, password)
    )
    user = cur.fetchone()
    con.close()

    if user:
        response = RedirectResponse(url='/', status_code=303)
        response.set_cookie('username', username)
        return response
    else:
        return templates.TemplateResponse(
            request=request,
            name='login.html',
            context={
                'is_logged_in': None,
                'error': 'Invalid username or password.',
            }
        )


@app.get('/logout', response_class=HTMLResponse)
async def logout(request: Request):
    response = RedirectResponse(url='/', status_code=303)
    response.delete_cookie('username')
    return response


@app.get('/create_message', response_class=HTMLResponse)
async def create_message(request: Request):
    return templates.TemplateResponse(
        request=request,
        name='create_message.html',
        context={'is_logged_in': check_credentials(request)}
    )


@app.post('/create_message', response_class=HTMLResponse)
async def create_message_post(request: Request):
    username = check_credentials(request)
    if not username:
        return RedirectResponse(url='/login', status_code=303)

    form = await request.form()
    message = form.get('message')

    con = sqlite3.connect('twitter_clone.db')
    cur = con.cursor()
    cur.execute('SELECT id FROM users WHERE username=?', (username,))
    user = cur.fetchone()
    if user:
        cur.execute(
            'INSERT INTO messages (sender_id, message) VALUES (?, ?)',
            (user[0], message)
        )
        con.commit()
    con.close()

    return RedirectResponse(url='/', status_code=303)


@app.get('/create_user', response_class=HTMLResponse)
async def create_user(request: Request):
    return templates.TemplateResponse(
        request=request,
        name='create_user.html',
        context={
            'is_logged_in': check_credentials(request),
            'error': None,
        }
    )


@app.post('/create_user', response_class=HTMLResponse)
async def create_user_post(request: Request):
    form = await request.form()
    username = form.get('username')
    password = form.get('password')
    age = form.get('age')

    con = sqlite3.connect('twitter_clone.db')
    cur = con.cursor()
    try:
        cur.execute(
            'INSERT INTO users (username, password, age) VALUES (?, ?, ?)',
            (username, password, age)
        )
        con.commit()
        con.close()
        response = RedirectResponse(url='/', status_code=303)
        response.set_cookie('username', username)
        return response
    except sqlite3.IntegrityError:
        con.close()
        return templates.TemplateResponse(
            request=request,
            name='create_user.html',
            context={
                'is_logged_in': None,
                'error': 'Username already exists.',
            }
        )


if __name__ == '__main__':
    uvicorn.run("main:app", host='127.0.0.1', port=8080, reload=True)