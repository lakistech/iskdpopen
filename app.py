from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from apscheduler.schedulers.background import BackgroundScheduler
from tuya import get_device

#from state import state

app = FastAPI()
templates = Jinja2Templates(directory="templates")
sched = BackgroundScheduler(timezone="UTC")
sched.start()

# Global status
status = "Nieznany"
message = "Z jakiegoś powodu nie możemy określić statusu otwarcia KDP"
latest_online_status = False
latest_check_time = "Nigdy"
latest_update_time = "jakiegoś czasu"
visitors_today = {"day": 0, "visitors": {}}
latest_api_response = {}
sessions = [] # {"created_at": ..., "pic": }

@sched.scheduled_job('interval', seconds=5)
def scrap():
    print("Scrap job")
    global latest_update_time, status, message, online, latest_check_time, latest_online_status, latest_api_response
    
    latest_check_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    try:
        device_data = get_device()
    except Exception as e:
        status = "Nieznany"
        message = f"Wystąpił błąd podczas pobierania danych diwajsa: {e}"
        print(f"  Device data retrieval failed: {type(e)}: {e.args}")
        return
    
    print("  Device data retrieved")
    latest_api_response = device_data

    try:
        online = device_data['result']['online']
        if online != latest_online_status and status != "Nieznany":
            latest_update_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"  Status updated at {latest_update_time}")
        else:
            print("  Status remained")
        
        latest_online_status = online

    except Exception as e:
        status = "Nieznany"
        meesage = f"Wystąpił błąd podczas parsowania danych diwajsa: {type(e)}: {e.args}"
        print(f"  Unable to retrieve data: {type(e)}: {e.args}")
        return
    
    if online:
        status = "Online"
        message = f"KDP wygląda na otwarty! Żarówka nad barem świeci się od {latest_update_time}."
        print("  We're online")
    else:
        status = "Offline"
        message = f"KDP niestety jest zamknięty. Żarówka nad barem jest zgaszona od {latest_update_time}."
        print("  We're offline")

    print(f"  We checked at {latest_check_time}")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    global visitors_today

    epoch_days = (datetime.utcnow() - datetime(1970,1,1)).days
    ip = request.client.host

    if epoch_days == visitors_today['day']:
        visitors_today['visitors'].add(ip)
    else:
        visitors_today['day'] = epoch_days
        visitors_today['visitors'] = {ip}

    number_of_visitors_today = len(visitors_today['visitors'])

    image_url = "static/unknown_sign.png"

    if status == "Online":
        image_url = "static/open_sign.png"
    elif status == "Offline":
        image_url = "static/closed_sign.png"
    
    return templates.TemplateResponse("index.html", 
        {
            "request": request,
            "picture_link": image_url,
            "message": message,
            "latest_check_time": latest_check_time,
            "number_of_visitors_today": number_of_visitors_today,
            "client_ip": ip
        }
    )

@app.get("/latest_response.json")
async def index():
    return latest_api_response

@app.get("/woz")
async def index(lid: str): # Albo sprawdzmy czy jest w kuki
    if not lid:
        return RedirectResponse()
    # If lid=asdasdasd w passie jest inny niż to co znajdziemy w arrayu z sesjami 
    return latest_api_response

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/static", StaticFiles(directory="static"), name="static")