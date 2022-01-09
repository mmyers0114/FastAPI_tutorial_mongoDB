from .. import models, schemas, utils, database, oauth2
from sqlalchemy.orm.session import Session
from fastapi import status, HTTPException, APIRouter
from fastapi.params import Depends


router = APIRouter(
    prefix='/users',
    tags=['Users']
)


# CREATE
@router.post('/', status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate,
                db: Session = Depends(database.get_db),
                ):

    email_in_db = db.query(models.User).filter(
        models.User.email == user.email).first()
    if email_in_db:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Email already in use.')

    # hash the password (imported from our utils.py file)
    hashed_pwd = utils.hash(user.password)
    # update the user object with the hashed password
    user.password = hashed_pwd
    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# READ
@router.get('/{id}', response_model=schemas.UserOut)
def get_user(id: int,
             db: Session = Depends(database.get_db),
             current_user: models.User = Depends(oauth2.get_current_user)):

    user_query = db.query(models.User).filter(models.User.id == id)
    user = user_query.first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'User with ID {id} was not found.')

    return user
