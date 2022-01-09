from .. import models, schemas, database, oauth2
from sqlalchemy.orm.session import Session
from fastapi import Response, status, HTTPException, APIRouter
from fastapi.params import Depends
from typing import List, Optional
from sqlalchemy import func


# prefix is added to the path for each route
# tags allow for seperation of functionality in the /docs page
router = APIRouter(
    prefix='/posts',
    tags=['Posts']
)


@router.get('/', response_model=List[schemas.PostVotesResponse])
def get_posts(db: Session = Depends(database.get_db),
              limit: int = 50,
              skip: int = 0,
              search: Optional[str] = ''):
    # cursor.execute('''SELECT * FROM posts
    #                ORDER BY id;''')
    # posts = cursor.fetchall()

    # this creates the sql query that gives us all the information about a post paired with its dynamically calculated number of votes
    post_votes_query = db.query(models.Post, func.count(models.Vote.post_id).label('votes')).join(
        models.Vote,
        models.Vote.post_id == models.Post.id,
        isouter=True
    ).group_by(models.Post.id).filter(
        models.Post.title.contains(search))

    post_votes = post_votes_query.limit(limit).offset(skip).all()

    return post_votes


# CREATE (requires login)
# we can assign more detailed status codes for each route (status_code=)
@router.post('/', status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse)
def create_post(post: schemas.PostCreate,
                db: Session = Depends(database.get_db),
                current_user: models.User = Depends(oauth2.get_current_user)):

    # never use f-strings for SQL (sql injection vulnerability). use the placeholder syntax instead (%s, %s)
    # cursor.execute('''
    # INSERT INTO posts
    # (title, content) VALUES (%s, %s) RETURNING *;
    # ''', (post.title, post.content))
    # saving the newly created post with fetchone(). must use RETURNING keyword
    # new_post = cursor.fetchone()
    # we 'stage' the changes to the database above (cursor.execute()) and use the commit method of the connection object to
    # push the changes to the database (conn.commit())
    # conn.commit()

    # we set the user_id field of the new post here to be the id of current_user (logged in user)
    # setting the keyword parameters (title=, content=, etc.) by automatically unpacking the dictionary form of the post
    new_post = models.Post(user_id=current_user.id, **post.dict())

    db.add(new_post)
    db.commit()
    # db.refresh() retrieves the newly created post and returns it to the new_post variable
    db.refresh(new_post)
    return new_post


# READ (requires login)
@router.get('/{id}', response_model=schemas.PostVotesResponse,)
# fastapi validates and converts (if possible) the data here (id: int). throws error if integer not passed
def get_post(id: int,
             db: Session = Depends(database.get_db),
             current_user: models.User = Depends(oauth2.get_current_user)):
    # because the SQL query is a string we must convert id back to a string to pass it to the placeholder
    # cursor.execute('''
    # SELECT * FROM posts ==> db.query(models.Post) the __tablename__ property of the class sets the table the database searches
    # WHERE id = %s; ==> filter(models.Post.id == id)
    # ''', (str(id)))
    # post = cursor.fetchone()

    post_votes_query = db.query(models.Post, func.count(models.Vote.post_id).label('votes')).join(
        models.Vote,
        models.Vote.post_id == models.Post.id,
        isouter=True
    ).group_by(models.Post.id).filter(models.Post.id == id)
    post = post_votes_query.first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Post with id {id} was not found.')
    return post


# DELETE (requires login)
@router.delete('/{id}')
def delete_post(id: int,
                db: Session = Depends(database.get_db),
                current_user: models.User = Depends(oauth2.get_current_user)):

    # cursor.execute(
    #     '''
    # DELETE FROM posts
    # WHERE id = %s RETURNING *;
    # ''', (str(id),)
    # )
    # del_post = cursor.fetchone()

    # if not del_post:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
    #                         detail=f'Post with id {id} was not found.')
    # conn.commit()

    del_query = db.query(models.Post).filter(models.Post.id == id)
    del_post = del_query.first()
    if not del_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Post with id {id} was not found.')

    if del_post.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='Cannot delete other user\'s posts')

    del_query.delete(synchronize_session=False)
    db.commit()

    # http code 204 is used when deleting items. data should not be returned when deleting an item, just the response
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# UPDATE (requires login)
@router.put('/{id}', status_code=status.HTTP_202_ACCEPTED, response_model=schemas.PostResponse)
def update_post(id: int,
                upd_post: schemas.PostCreate,
                db: Session = Depends(database.get_db),
                current_user: models.User = Depends(oauth2.get_current_user)):

    # cursor.execute(
    #     """
    # UPDATE posts
    # SET title = %s, content = %s, published = %s
    # WHERE id = %s RETURNING *;
    # """, (post.title, post.content, post.published, str(id))
    # )
    # upd_post = cursor.fetchone()
    # conn.commit()

    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()
    # checking if post with that id exists
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Post with ID {id} was not found.')

    if post.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='Cannot update other user\'s posts')

    # .update() takes a python dict for the update data as the first arg
    post_query.update(upd_post.dict(), synchronize_session=False)
    db.commit()
    return post_query.first()
