from .. import models, schemas, database, oauth2
from sqlalchemy.orm.session import Session
from fastapi import status, HTTPException, APIRouter
from fastapi.params import Depends


router = APIRouter(prefix='/vote',
                   tags=['Vote'])


# cast a vote
@router.post('/', status_code=status.HTTP_201_CREATED)
def vote(vote: schemas.Vote,
         db: Session = Depends(database.get_db),
         current_user: models.User = Depends(oauth2.get_current_user)):

    post = db.query(models.Post).filter(models.Post.id == vote.post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Post with id: {vote.post_id} does not exist')

    vote_query = db.query(models.Vote).filter(
        models.Vote.post_id == vote.post_id, models.Vote.user_id == current_user.id)

    vote_found = vote_query.first()

    if vote.direction == 1:
        if vote_found:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail=f'User {current_user.id} has already voted on post {vote.post_id}')

        new_vote = models.Vote(user_id=current_user.id, post_id=vote.post_id)
        db.add(new_vote)
        db.commit()
        return {'message': 'successfully add vote'}
    else:
        if not vote_found:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail='vote does not exist')

        vote_query.delete(synchronize_session=False)
        db.commit()
        return {'message': 'successfully removed vote'}
