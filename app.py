from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from tuya import get_device

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def index():
    status = "Nieznany"
    message = "Z jakiegoś powodu nie możemy określić statusu otwarcia KDP"

    try:
        device_data = get_device()
    except Exception as e:
        meesage = f"Wystąpił błąd podczas pobierania danych diwajsa: {e}"

    try:
        online = device_data['result']['online']
        update_time = device_data['result']['update_time']
        print(online)
        print(update_time)

        if online:
            status = "Online!"
            message = "Żarówka nad barem się świeci od "
        else:
            status = "Offline!"
            message = "Żarówka nad barem jest zgaszona od "
            print(status)

        message += str(update_time)

    except Exception as e:
        status = "Nieznany"
        meesage = f"Wystąpił błąd podczas parsowania danych diwajsa: {e}"

    return f"{status}, {message}"