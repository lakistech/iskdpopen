import datetime
import hmac
import hashlib
import requests
import config

token = ""

def create_headers_str(headers):
    headers_str = ""
    for h in ["client_id", "sign_method"]:
        headers_str += f"{h}:{headers[h]}\n"

    return headers_str

def create_signature(ts, headers, url):
    headers_str = create_headers_str(headers)
    content_sha = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855" # 
    string_to_sign = f"GET\n{content_sha}\n{headers_str}\n{url}"
    message = config.tuya_client_id + token + ts + string_to_sign
    print(message)

    sign = hmac.new(bytes(config.tuya_client_secret, 'utf-8'), msg=bytes(message, 'utf-8'), digestmod=hashlib.sha256).hexdigest().upper()
    return sign


def create_headers():
    ts = str(int(datetime.datetime.now().timestamp() * 1000))

    headers = {
        "Signature-Headers" : "client_id:sign_method",
        "client_id": config.tuya_client_id,
        "sign_method": "HMAC-SHA256",
        "t": ts,
        "mode": "cors",
        "Content-Type": "application/json"
    }

    sign = create_signature(ts, headers, config.tuya_token_path)
    headers['sign'] = sign
    return headers


def get_token():
    r = requests.get(config.tuya_api_url + config.tuya_token_path, headers=create_headers())
    return r.json()




def get_device(device_id):
    #headers = 
    headers["access_token"] = "c42d0bac153415fc33477f4c7168fabb"
    headers["sign"] = "F77898135E7CE7140A424DA978D35BE610D7C98750F5CE4A32DE760417E2E174"
    

#HMAC-SHA256(client_id + t + nonce + stringToSign, secret).toUpperCase()

