'''
Starts a hello world webserver
'''

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import uvicorn

app = FastAPI()
templates = Jinja2Templates(directory='templates')

@app.get('/', response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        request=request,
        name='index.html',
    )

if __name__ == '__main__':
    uvicorn.run("main:app", host='127.0.0.1', port=8080, reload=True)

# Now we'e gonna load html from a file
# So added jinja2 and template stuff
# internal server error always means an internal python error inside of the function that 
# corresponds to the rout or page that was connected
