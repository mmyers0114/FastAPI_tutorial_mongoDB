from .. import database, oauth2, schemas, models, utils
from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session


router = APIRouter(tags=['Authentication'])


@router.post('/login', response_model=schemas.Token)
def login(user_creds: OAuth2PasswordRequestForm = Depends(),
          db: Session = Depends(database.get_db)):
    # the oauth2 password form is a dict with only 2 fields (username and password)
    # in our case email is the equivalent of username so we use that for comparison
    user_query = db.query(models.User).filter(
        models.User.email == user_creds.username)
    user = user_query.first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Invalid credentials.'
        )

    if not utils.verify(user_creds.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Invalid credentials.'
        )

    access_token = oauth2.create_access_token(payload={'user_id': user.id})

    return {'access_token': access_token, 'token_type': 'bearer'}
