import config
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from tuya import get_device
from state import BulbState

state = BulbState()

scheduler = BackgroundScheduler(timezone="UTC")
scheduler.start()

@scheduler.scheduled_job('interval', seconds=int(config.call_interval))
def scrap():
    
    current_state = state.state
    new_state = {}

    new_state['latest_check_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    try:
        device_data = get_device()
    except Exception as e:
        new_state['status'] = "Nieznany"
        new_state['message'] = f"Wystąpił błąd podczas pobierania danych diwajsa: {e}"
        print(f"  Device data retrieval failed: {type(e)}: {e.args}")
        return
    
    print("  Device data retrieved")
    new_state['latest_api_response'] = device_data

    try:
        online = device_data['result']['online']
        if online != current_state['latest_online_status'] and current_state['status'] != "Nieznany":
            new_state['latest_update_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"  Status updated at {new_state['latest_update_time']}")
        else:
            new_state['latest_update_time'] = current_state['latest_update_time']
            print("  Status remained")
        
        new_state['latest_online_status'] = online

    except Exception as e:
        new_state['status'] = "Nieznany"
        new_state['message'] = f"Wystąpił błąd podczas parsowania danych diwajsa: {type(e)}: {e.args}"
        print(f"  Unable to retrieve data: {type(e)}: {e.args}")
        return
    
    if online:
        new_state['status'] = "Online"
        new_state['message'] = f"KDP wygląda na otwarty! Żarówka nad barem jest online od {new_state['latest_update_time']}."
        print("  We're online")
    else:
        new_state['status'] = "Offline"
        new_state['message'] = f"KDP niestety jest zamknięty. Żarówka nad barem jest offline od {new_state['latest_update_time']}."
        print("  We're offline")

    print(f"  We checked at {current_state['latest_check_time']}")

    state.set_state(new_state)
