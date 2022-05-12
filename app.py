from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from apscheduler.schedulers.background import BackgroundScheduler
from tuya import get_device

from state import state

app = FastAPI()
templates = Jinja2Templates(directory="templates")
sched = BackgroundScheduler(timezone="UTC")
sched.start()

@sched.scheduled_job('interval', seconds=5)
def scrap():
    current_state = state.get_state()
    
    current_state['latest_check_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    try:
        device_data = get_device()
    except Exception as e:
        current_state['status'] = "Nieznany"
        current_state['message'] = f"Wystąpił błąd podczas pobierania danych diwajsa: {e}"
        print(f"  Device data retrieval failed: {type(e)}: {e.args}")
        return
    
    print("  Device data retrieved")
    current_state['latest_api_response'] = device_data

    try:
        online = device_data['result']['online']
        if online != current_state['latest_online_status'] and current_state['status'] != "Nieznany":
            current_state['latest_update_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"  Status updated at {current_state['latest_update_time']}")
        else:
            print("  Status remained")
        
        current_state['latest_online_status'] = online

    except Exception as e:
        current_state['status'] = "Nieznany"
        current_state['meesage'] = f"Wystąpił błąd podczas parsowania danych diwajsa: {type(e)}: {e.args}"
        print(f"  Unable to retrieve data: {type(e)}: {e.args}")
        return
    
    if online:
        current_state['status'] = "Online"
        current_state['message'] = f"KDP wygląda na otwarty! Żarówka nad barem świeci się od {current_state['latest_update_time']}."
        print("  We're online")
    else:
        current_state['status'] = "Offline"
        current_state['message'] = f"KDP niestety jest zamknięty. Żarówka nad barem jest zgaszona od {current_state['latest_update_time']}."
        print("  We're offline")

    print(f"  We checked at {current_state['latest_check_time']}")

    state.set_state(current_state)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    current_state = state.get_state()

    epoch_days = (datetime.utcnow() - datetime(1970,1,1)).days
    ip = request.client.host

    if epoch_days == current_state['visitors_today']['day']:
        current_state['visitors_today']['visitors'].add(ip)
    else:
        current_state['visitors_today']['day'] = epoch_days
        current_state['visitors_today']['visitors'] = {ip}

    number_of_visitors_today = len(current_state['visitors_today']['visitors'])

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
            "number_of_visitors_today": number_of_visitors_today,
            "client_ip": ip
        }
    )

@app.get("/latest_response.json")
async def index():
    return state.get_state()['latest_api_response']

@app.get("/woz")
async def index(lid: str): # Albo sprawdzmy czy jest w kuki
    if not lid:
        return RedirectResponse()
    # If lid=asdasdasd w passie jest inny niż to co znajdziemy w arrayu z sesjami 

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/static", StaticFiles(directory="static"), name="static")