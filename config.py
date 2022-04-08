import os

tuya_client_id = os.getenv("TUYA_CLIENT_ID", "kcxtmm5nbhlctx7giq13")
tuya_client_secret = os.getenv("TUYA_CLIENT_SECRET")
tuya_device_id = os.getenv("TUYA_DEVICE_ID", "bfa2136abce036da4cw7zo") # bar prawy

tuya_api_url = "https://openapi.tuyaeu.com"
tuya_token_path = "/v1.0/token?grant_type=1"
tuya_device_path = f"/v1.0/devices/{tuya_device_id}"