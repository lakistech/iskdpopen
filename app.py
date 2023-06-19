from scheduled import scheduler
from datetime import datetime
from fastapi import FastAPI, Request, Header
from typing import Optional
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from state import BulbState, VisitCounter

bulb_state = BulbState()
counter = VisitCounter()

app = FastAPI()

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request, x_real_ip: Optional[str] = Header(None)):
    current_state = bulb_state.state

    now_epoch_days = (datetime.utcnow() - datetime(1970,1,1)).days

    counter.insert_visitor(now_epoch_days, x_real_ip)

    image_url = "static/unknown_sign.png"

    if current_state['status'] == "Online":
        image_url = "static/open_sign.png"
    elif current_state['status'] == "Offline":
        image_url = "static/closed_sign.png"
    
    return templates.TemplateResponse("index.html", 
        {
            "request": request,
            "picture_link": image_url,
            "message": current_state['message'],
            "latest_check_time": current_state['latest_check_time'],
            "number_of_visitors_today": counter.get_todays_visitors_count(),
            "client_ip": x_real_ip,
        }
    )

@app.get("/latest_response.json")
async def index():
    return bulb_state.state['latest_api_response']

app.mount("/static", StaticFiles(directory="static"), name="static")