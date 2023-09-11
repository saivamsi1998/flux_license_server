# django_server

To start the server:
```
python3 manage.py runserver 0.0.0.0:80
```

## APIs

```
API: /flux/reg
POST params: userId=xyz@AdobeId&deviceId=dfgh&nglAppId=photoshop1
Response on success: {"profile_status": "PROFILE_AVAIALBLE", "status": "success"}
Response on fail: {"profile_status": "PROFILE_DENIED", "status": "fail", "err_msg": "Offer isn't available for given (user_id, app_id)= (xyz@AdobeId,photoshop2)"}
```

```
API: /flux/heartbeat
POST params: userId=xyz@AdobeId&deviceId=dfgh&nglAppId=photoshop1
Response on success: {"profile_status": "PROFILE_AVAIALBLE", "status": "success"}
Response on fail: {"profile_status": "PROFILE_DENIED", "status": "fail", "err_msg": "Offer isn't available for given (user_id, app_id)= (xyz@AdobeId,photoshop2)"}
```

```
API: /flux/dereg
POST params: userId=xyz@AdobeId&deviceId=dfgh&nglAppId=photoshop1
Response on success: {"status": "success"}
Response on fail: {"status": "fail", "err_msg": "Dereg call made for non existant license entry"}
```
