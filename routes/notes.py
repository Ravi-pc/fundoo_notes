from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session
from core.model import get_db, Notes, User, verify_password
from core.schema import UpdateNotes, UserLogin

routers = APIRouter()


@routers.post('/add_notes', status_code=status.HTTP_200_OK)
def add_notes(notes: UpdateNotes, user: UserLogin, response: Response, db: Session = Depends(get_db)):
    """
        Description: add_notes function is used to add a note to the database.

        Parameter: Notes details, User details, response, get_db.

        Return: Json Response.

    """
    try:
        valid_user = db.query(User).filter_by(user_name=user.user_name).one_or_none()
        if not valid_user:
            raise HTTPException(detail='Username Not Valid!!', status_code=status.HTTP_401_UNAUTHORIZED)
        if not verify_password(valid_user.password, user.password):
            raise HTTPException(detail='Invalid Password!!', status_code=status.HTTP_401_UNAUTHORIZED)

        notes_data = notes.model_dump()
        notes_data['user_id'] = valid_user.id
        new_note = Notes(**notes_data)
        db.add(new_note)
        db.commit()
        db.refresh(new_note)
        return {'message': 'Notes Added', 'status': 201, 'data': notes}

    except Exception as ex:
        response.status_code = 400
        return {'message': str(ex), 'status': 400}


@routers.get('/get_notes/', status_code=status.HTTP_200_OK)
def retrieve_all_notes(user: UserLogin, response: Response, db: Session = Depends(get_db)):
    """
        Description: retrieve_notes function is used to retrieve a note from the database.

        Parameter: User details, response, get_db.

        Return: Json Response.

    """
    try:
        valid_user = db.query(User).filter_by(user_name=user.user_name).one_or_none()
        if not valid_user:
            raise HTTPException(detail='Username Not Valid!!', status_code=status.HTTP_401_UNAUTHORIZED)
        if not verify_password(valid_user.password, user.password):
            raise HTTPException(detail='Invalid Password!!', status_code=status.HTTP_401_UNAUTHORIZED)

        notes = db.query(Notes).filter_by(user_id=valid_user.id).all()
        return {'message': 'Notes Retrieved', 'status': 201, 'data': notes}

    except Exception as ex:
        response.status_code = 400
        return {'message': str(ex), 'status': 400}


@routers.post('/delete_notes', status_code=status.HTTP_200_OK)
def delete_notes(user: UserLogin, response: Response, db: Session = Depends(get_db)):
    """
        Description: delete_notes function is used to delete a note from the database.

        Parameter: User details, response, get_db.

        Return: Json Response.

    """
    try:
        valid_user = db.query(User).filter_by(user_name=user.user_name).one_or_none()
        if not valid_user:
            raise HTTPException(detail='Username Not Valid!!', status_code=status.HTTP_401_UNAUTHORIZED)
        if not verify_password(valid_user.password, user.password):
            raise HTTPException(detail='Invalid Password!!', status_code=status.HTTP_401_UNAUTHORIZED)

        notes = db.query(Notes).filter_by(user_id=valid_user.id).first()
        db.delete(notes)
        db.commit()

        return {'message': 'Notes Deleted', 'status': 201}

    except Exception as ex:
        response.status_code = 400
        return {'message': str(ex), 'status': 400}


@routers.put('/update_notes/{note_id}', status_code=status.HTTP_200_OK)
def update_notes(user: UserLogin, note_id: int, notes_schema: UpdateNotes, response: Response,
                 db: Session = Depends(get_db)):
    """
        Description: update_notes function is used to update a note from the database.

        Parameter: User details,notes details, notes_id, response, get_db.

        Return: Json Response.

    """
    try:
        valid_user = db.query(User).filter_by(user_name=user.user_name).one_or_none()
        if not valid_user or not verify_password(valid_user.password, user.password):
            raise HTTPException(detail='Invalid username or password', status_code=status.HTTP_401_UNAUTHORIZED)

        notes = db.query(Notes).filter_by(id=note_id, user_id=valid_user.id).first()
        if notes:
            updated_notes = notes_schema.model_dump()
            for key, value in updated_notes.items():
                setattr(notes, key, value)
            db.commit()
            db.refresh(notes)
            return {'message': 'Notes Updated', 'status': 200}
        else:
            raise HTTPException(detail='No notes found for the user', status_code=404)

    except NoResultFound:
        raise HTTPException(detail='User not found', status_code=status.HTTP_401_UNAUTHORIZED)

    except Exception as ex:
        response.status_code = 500
        return {'message': str(ex), 'status': 500}
