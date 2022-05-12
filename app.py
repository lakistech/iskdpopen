import uuid
import config
import requests
import urllib
import base64
from datetime import datetime
from fastapi import FastAPI, Request, Cookie, Response, Depends, HTTPException, Form, Header
from typing import Optional
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

async def get_session_id(ssid: Optional[str] = Cookie(None)):
    if ssid:
        return ssid

    raise HTTPException(
        status_code=401, detail="Attempted to make an API call without session ID in cookie")


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
async def index(request: Request, x_real_ip: Optional[str] = Header(None)):
    current_state = state.get_state()

    epoch_days = (datetime.utcnow() - datetime(1970,1,1)).days

    if epoch_days == current_state['visitors_today']['day']:
        current_state['visitors_today']['visitors'].add(x_real_ip)
    else:
        current_state['visitors_today']['day'] = epoch_days
        current_state['visitors_today']['visitors'] = {x_real_ip}

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
            "client_ip": x_real_ip,
            "crew_information": current_state['crew_information']
        }
    )

@app.get("/latest_response.json")
async def index():
    return state.get_state()['latest_api_response']

@app.get('/msg')
async def index(request: Request, response: Response, ssid: Optional[str] = Cookie(None)):
    if not ssid:
        ssid = str(uuid.uuid4())
        response.set_cookie('ssid', str(ssid), secure=True)
        return RedirectResponse(config.oauth2_login_url)

    current_state = state.get_state()
    active_admin_sessions = [s for s in current_state['admin_sessions'] if s['ssid'] == ssid]

    if not active_admin_sessions:
        return RedirectResponse(config.oauth2_login_url)
    
    admin_session = active_admin_sessions[0]

    return templates.TemplateResponse("msg.html", 
        {
            "request": request,
            "user_name": admin_session['name'],
            "picture_base64": admin_session['picture'].decode(),
            "logout_link": "logout"
        }
    )

@app.get('/oauth_callback')
def main(code: str, ssid: str = Depends(get_session_id)):
    token_data = requests.get(f"{config.oauth2_token_fetch_url}&code={code}")
    if token_data.status_code != 200:
        raise HTTPException(status_code=401, detail="Token fetch failed with {:d}: {}".format(
            token_data.status_code, token_data.text))

    token = token_data.json()['access_token']
    user_query_url = f"{config.oauth2_user_info_url}/?access_token={token}"
    user_info = requests.get(user_query_url).json()

    if user_info['id'] not in config.allowed_userids:
        return f"Witaj {user_info['name']}! Niestety nie jesteś upoważniony do zmiany wiadomości od załogi. Twój User ID to: {user_info['id']}"

    # Get profile pic
    pic_query_url = f"https://graph.facebook.com/v13.0/{user_info['id']}/picture?access_token={token}"
    pic_temp_path = f"/tmp/{user_info['id']}.jpg"

    urllib.request.urlretrieve(pic_query_url, pic_temp_path)

    # base64 the image
    encoded_pic = ""
    with open(pic_temp_path, "rb") as image_file:
        encoded_pic = base64.b64encode(image_file.read())

    current_active_sessions = state.get_state()['admin_sessions']

    # If user already have active admin sessions - remove them to create new one
    for s in current_active_sessions:
        if s['ssid'] == ssid:
            current_active_sessions.remove(s)

    current_active_sessions.append(
        {
            "created_at": (datetime.utcnow() - datetime(1970,1,1)).days,
            "picture": encoded_pic,
            "name": str(user_info['name']),
            "ssid": ssid
        }
    )

    state.set_state({"admin_sessions": current_active_sessions})
    return RedirectResponse("/msg")


@app.post('/update_msg')
async def main(request: Request, ssid: str = Depends(get_session_id), new_message: str = Form(...)):
    
    current_state = state.get_state()

    active_admin_sessions = [s for s in current_state['admin_sessions'] if s['ssid'] == ssid]
    if not active_admin_sessions:
        return "To się nie uda."
    
    admin_session = active_admin_sessions[0]

    new_crew_information = {
        "picture": admin_session['picture'].decode(),
        "name": admin_session['name'],
        "message": new_message,
        "date": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    state.set_state({"crew_information": new_crew_information})
    return RedirectResponse(url='/', status_code=303)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/static", StaticFiles(directory="static"), name="static")