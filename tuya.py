import datetime
import hmac
import hashlib
import requests
import config

def create_headers_str(headers):
    headers_str = ""
    for h in ["client_id", "sign_method"]:
        headers_str += f"{h}:{headers[h]}\n"

    return headers_str

def create_signature(ts, headers, token, url):
    headers_str = create_headers_str(headers)
    content_sha = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855" # Empty payload hashed
    string_to_sign = f"GET\n{content_sha}\n{headers_str}\n{url}"
    message = config.tuya_client_id + token + ts + string_to_sign
    print(message)
    sign = hmac.new(bytes(config.tuya_client_secret, 'utf-8'), msg=bytes(message, 'utf-8'), digestmod=hashlib.sha256).hexdigest().upper()
    return sign

def create_headers(api_path, token=""):
    ts = str(int(datetime.datetime.now().timestamp() * 1000))

    headers = {
        "Signature-Headers" : "client_id:sign_method",
        "client_id": config.tuya_client_id,
        "sign_method": "HMAC-SHA256",
        "t": ts,
        "mode": "cors",
        "Content-Type": "application/json"
    }

    headers['sign'] = create_signature(ts, headers, token, api_path)
    return headers


def get_token():
    headers = create_headers(config.tuya_token_path)
    r = requests.get(config.tuya_api_url + config.tuya_token_path, headers=headers)
    return r.json()

def get_device():
    try:
        token_response = get_token()
        token = token_response['result']['access_token']
    except Exception as e:
        return {"msg": f"Unable to retrieve token from Tuya API! {e}"}
    
    print(f"\n\nTOKEN: {token_response}\n\n")
    headers = create_headers(config.tuya_device_path, token)
    headers['access_token'] = token
    r = requests.get(config.tuya_api_url + config.tuya_device_path, headers=headers)
    return r.json()
