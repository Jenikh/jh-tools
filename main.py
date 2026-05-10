from json import JSONDecodeError

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import httpx
from fastapi import HTTPException
import uuid
import jinja2
import dotenv
import os
dotenv.load_dotenv()


app = FastAPI()

# Mount static files (same folder as before)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates (pointing to same folder like your Flask app)
templates = Jinja2Templates(directory="static")
CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")

data_cache = {}

# =========================
# Error Handlers
# =========================

@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    print("404 error occurred:", exc)
    return templates.TemplateResponse("404.html", {"request": request}, status_code=404)


@app.exception_handler(jinja2.exceptions.TemplateNotFound)
async def template_not_found_handler(request: Request, exc):
    print("Template not found:", exc)
    return templates.TemplateResponse("404.html", {"request": request}, status_code=404)


# =========================
# Routes
# =========================

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.head("/")
async def head():
    return JSONResponse(status_code=200,content={})


@app.get("/CodeGPT")
async def bot(request: Request):
    return templates.TemplateResponse("CodeGPT.html", {"request": request})




@app.get("/gitbotgpt/return")
async def bot_return(request: Request):

    code = request.query_params.get("code")

    if not code:
        raise HTTPException(status_code=400, detail="Missing code")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://github.com/login/oauth/access_token",
            headers={
                "Accept": "application/json"
            },
            data={
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "code": code,
            },
        )

    try:
        token_data = response.json()
    except JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid GitHub response")

    access_token = token_data.get("access_token")

    if not access_token:
        raise HTTPException(status_code=400, detail="Authorization failed")
        # TODO: Highlight to dont froget to disable this in prod
        access_token = "mock_token"
    auth_code = uuid.uuid4().hex

    while auth_code in data_cache:
        auth_code = uuid.uuid4().hex

    data_cache[auth_code] = access_token

    return templates.TemplateResponse(
        "returnAuthBot.html",
        {
            "request": request,
            "code": auth_code
        }
    )
# =========================
# Run (dev only)
# =========================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", "8000")))