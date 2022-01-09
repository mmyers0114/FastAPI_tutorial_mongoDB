from fastapi import Depends, status, HTTPException
from jose import jwt, JWTError
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from . import schemas, database, models, config


# oauth2_scheme in this case is used as a dependency that checks the request headers for
# an authorization header with a value of 'Bearer' and a jwt token.
# it then returns the token --> token: str =  Depends(oauth2_scheme)
# the tokenUrl property is set to the path name of the function that creates and returns
# the jwt token (used for documentation)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')


SECRET_KEY = config.settings.secret_key
ALGORITHM = config.settings.algorithm
TOKEN_EXPIRE_MINUTES = config.settings.token_expire_minutes


def create_access_token(payload: dict):
    # copy the data so we do not modify the original
    data_to_encode = payload.copy()

    # set an expiration time for our token
    expire = datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRE_MINUTES)

    # add the expiration to our raw token
    data_to_encode.update({'exp': expire})

    token = jwt.encode(data_to_encode, SECRET_KEY,
                       algorithm=ALGORITHM)

    return token


def verify_acces_token(token: str, creds_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY,
                             algorithms=[ALGORITHM])
        user_id = payload.get('user_id')

        if not user_id:
            raise creds_exception

        token_data = schemas.TokenData(user_id=user_id)
    except JWTError:
        raise creds_exception

    return token_data


def get_current_user(token: str = Depends(oauth2_scheme),
                     db: Session = Depends(database.get_db)):

    token_data = verify_acces_token(token, creds_exception=HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                                                         detail='Could not validate credentials.',
                                                                         headers={'WWW-Authenticate': 'Bearer'}))
    user_query = db.query(models.User).filter(
        models.User.id == token_data.user_id)
    user = user_query.first()

    return user
