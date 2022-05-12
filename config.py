import os

tuya_client_id = os.getenv("TUYA_CLIENT_ID", "kcxtmm5nbhlctx7giq13")
tuya_client_secret = os.getenv("TUYA_CLIENT_SECRET")
tuya_device_id = os.getenv("TUYA_DEVICE_ID", "bfa2136abce036da4cw7zo") # bar prawy

tuya_api_url = "https://openapi.tuyaeu.com"
tuya_token_path = "/v1.0/token?grant_type=1"
tuya_device_path = f"/v1.0/devices/{tuya_device_id}"


oauth2_token_url = 'https://graph.facebook.com/v6.0/oauth/access_token'
oauth2_user_info_url = 'https://graph.facebook.com/v6.0/me'
oauth2_client_id = os.getenv('OAUTH2_CLIENT_ID', 'oauth2_client_id')
oauth2_client_secret = os.getenv('OAUTH2_CLIENT_SECRET', 'sekret')
oauth2_redirect_uri = os.getenv('OAUTH2_REDIRECT_URI', 'oauth2_redirect_uri')

oauth2_token_fetch_url = oauth2_token_url+'?client_id='+oauth2_client_id + \
    '&client_secret='+oauth2_client_secret+'&redirect_uri='+oauth2_redirect_uri
oauth2_app_creds_fetch_url = "{}?client_id={}&client_secret={}&grant_type=client_credentials".format(
    "https://graph.facebook.com/oauth/access_token", oauth2_client_id, oauth2_client_secret
)


allowed_userids = [
    100001820504411, # Stachu
    1401053905 # Ja
]