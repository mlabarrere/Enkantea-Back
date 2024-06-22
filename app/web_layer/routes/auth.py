from fastapi import HTTPException, APIRouter, Request
import pyrebase
from app.core.config import settings
from requests.exceptions import HTTPError


firebase = pyrebase.initialize_app(settings.FIREBASE_CONFIG)

# Firebase Authentication
auth = firebase.auth()

router = APIRouter()

@router.post("/signup", include_in_schema=True)
async def signup(*, email:str, password:str): 
    if email is None or password is None:
        return HTTPException(detail={'message': 'Error! Missing Email or Password'}, status_code=400)
    #TODO : Error handling
    try:
        user = auth.create_user_with_email_and_password(email=email,password=password)
        print(user)
    except HTTPError as http:
        return HTTPException(detail={'message': http.response}, status_code=400)

        return {'message': f'Successfully created user {user.uid}'}    
    except:
        return HTTPException(detail={'message': 'Error Creating User'}, status_code=400)

@router.post("/login", include_in_schema=False)
async def login(request: Request):
   req_json = await request.json()
   email = req_json['email']
   password = req_json['password']
   try:
       user = auth.sign_in_with_email_and_password(email, password)
       jwt = user['idToken']
       return {'token': jwt}
   except:
       return HTTPException(detail={'message': 'There was an error logging in'}, status_code=400)
