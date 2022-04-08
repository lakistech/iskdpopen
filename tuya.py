import datetime
import hmac
import hashlib
import requests
from config import tuya_device_id, tuya_client_id, tuya_client_secret

token = ""

tuya_api_url = "https://openapi.tuyaeu.com"
tuya_token_path = "/v1.0/token?grant_type=1"

device_details_api_url = f"https://openapi.tuyaeu.com/v1.0/devices/{tuya_device_id}"
token_api_url = "https://openapi.tuyaeu.com/v1.0/token?grant_type=1"

def create_headers_str(headers):
    headers_str = ""
    for h in ["client_id", "sign_method"]:
        headers_str += f"{h}:{headers[h]}\n"

    return headers_str


def create_signature(ts, headers, url):
    headers_str = create_headers_str(headers)
    content_sha = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855" # 
    string_to_sign = f"GET\n{content_sha}\n{headers_str}\n{url}"
    message = tuya_client_id + token + ts + string_to_sign
    print(message)

    sign = hmac.new(bytes(tuya_client_secret, 'utf-8'), msg=bytes(message, 'utf-8'), digestmod=hashlib.sha256).hexdigest().upper()
    return sign


def create_headers():
    ts = str(int(datetime.datetime.now().timestamp() * 1000))

    headers = {
        "Signature-Headers" : "client_id:sign_method",
        "client_id": tuya_client_id,
        "sign_method": "HMAC-SHA256",
        "t": ts,
        "mode": "cors",
        "Content-Type": "application/json"
    }

    sign = create_signature(ts, headers, tuya_token_path)
    headers['sign'] = sign
    return headers





def get_device(device_id):
    #headers = 
    headers["access_token"] = "c42d0bac153415fc33477f4c7168fabb"
    headers["sign"] = "F77898135E7CE7140A424DA978D35BE610D7C98750F5CE4A32DE760417E2E174"
    

#HMAC-SHA256(client_id + t + nonce + stringToSign, secret).toUpperCase()

