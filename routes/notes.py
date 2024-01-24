import json

from fastapi import APIRouter, status, Depends, HTTPException, Response, Request
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session
from core.model import get_db, Notes, User, collaborator
from core.schema import UpdateNotes, CollaboratorDetails
from core.utils import Redis, logger
routers = APIRouter()


@routers.post('/add_notes', status_code=status.HTTP_201_CREATED, tags=['Notes'])
def add_notes(notes: UpdateNotes, request: Request, response: Response, db: Session = Depends(get_db)):
    """
        Description: add_notes function is used to add a note to the database.

        Parameter: Notes details, User details, response, get_db.

        Return: Json Response.

    """
    try:
        notes_data = notes.model_dump()
        notes_data['user_id'] = request.state.user.id
        new_note = Notes(**notes_data)
        db.add(new_note)
        db.commit()
        db.refresh(new_note)
        Redis.add_redis(new_note.user_id, new_note.id, json.dumps(notes_data))
        return {'message': 'Notes Added', 'status': 201, 'data': notes}

    except Exception as ex:
        response.status_code = status.HTTP_400_BAD_REQUEST
        logger.exception(ex)
        return {'message': str(ex), 'status': 400}


@routers.get('/get_notes/', status_code=status.HTTP_200_OK, tags=['Notes'])
def retrieve_all_notes(request: Request, response: Response, db: Session = Depends(get_db)):
    """
        Description: retrieve_notes function is used to retrieve a note from the database.

        Parameter: User details, response, get_db.

        Return: Json Response.

    """
    try:
        redis_cons = Redis.get_redis(request.state.user.id)
        if redis_cons:
            for key, value in redis_cons.items():
                redis_cons[key] = json.loads(value)
            return {'message': 'Notes Retrieved', 'status': 201, 'data': redis_cons}
        existing_notes = db.query(Notes).filter_by(user_id=request.state.user.id).all()
        collab_notes = db.query(collaborator).filter_by(user_id=request.state.user.id).all()
        notes = db.query(Notes).filter(Notes.id.in_(list(map(lambda x: x.note_id, collab_notes)))).all()
        print(notes)
        existing_notes.extend(notes)
        return {'message': 'Notes Retrieved', 'status': 201, 'data': existing_notes}

    except Exception as ex:
        response.status_code = status.HTTP_400_BAD_REQUEST
        logger.exception(ex)
        return {'message': str(ex), 'status': 400}


@routers.delete('/delete_notes/{note_id}', status_code=status.HTTP_200_OK, tags=['Notes'])
def delete_notes(note_id: int, request: Request, response: Response, db: Session = Depends(get_db)):
    """
        Description: delete_notes function is used to delete a note from the database.

        Parameter: User details, response, get_db.

        Return: Json Response.

    """
    try:

        notes = db.query(Notes).filter_by(user_id=request.state.user.id, id=note_id).first()
        db.delete(notes)
        db.commit()
        Redis.del_redis(request.state.user.id, note_id)
        return {'message': 'Notes Deleted', 'status': 200}

    except Exception as ex:
        response.status_code = status.HTTP_400_BAD_REQUEST
        logger.exception(ex)
        return {'message': str(ex), 'status': 400}


@routers.put('/update_notes/{note_id}', status_code=status.HTTP_200_OK, tags=['Notes'])
def update_notes(note_id: int, notes_schema: UpdateNotes, request: Request, response: Response,
                 db: Session = Depends(get_db)):
    """
        Description: update_notes function is used to update a note from the database.

        Parameter: User details,notes details, notes_id, response, get_db.

        Return: Json Response.

    """
    try:
        notes = db.query(Notes).filter_by(user_id=request.state.user.id, id=note_id).first()
        if notes is None:
            collab = db.query(collaborator).filter_by(note_id=note_id, user_id=request.state.user.id).filter()
            if collab:
                notes = db.query(Notes).filter_by(id=note_id).first()
            updated_notes = notes_schema.model_dump()
            [setattr(notes, key, value) for key, value in updated_notes.items()]
            db.commit()
            db.refresh(notes)
            Redis.add_redis(request.state.user.id, notes.id, json.dumps(updated_notes))
            return {'message': 'Notes Updated', 'status': 200}
        else:
            raise HTTPException(detail='No notes found for the user', status_code=404)

    except NoResultFound:
        raise HTTPException(detail='User not found', status_code=status.HTTP_401_UNAUTHORIZED)

    except Exception as ex:
        response.status_code = status.HTTP_400_BAD_REQUEST
        logger.exception(ex)
        return {'message': str(ex), 'status': 400}


@routers.post('/add_collaborator', status_code=status.HTTP_201_CREATED, tags=['Notes'])
def add_collaborator(body: CollaboratorDetails,  request: Request, response: Response, db: Session = Depends(get_db)):
    """
        Description: add_collaborator function is used to add list of collaborator to the notes.

        Parameter: body as Collaborator object, request as Request object, response as Response object
                    get_db as session object.

        Return: response and status code.

    """
    try:
        note = db.query(Notes).filter_by(user_id=request.state.user.id, id=body.note_id).first()
        if not note:
            raise HTTPException(detail='Note not found', status_code=status.HTTP_404_NOT_FOUND)
        for user_id in body.user_ids:
            if user_id != request.state.user.id:
                collab = db.query(User).filter_by(id=user_id).first()
                if collab and collab not in note.user_m2m:
                    note.user_m2m.append(collab)
                else:
                    raise HTTPException(detail='User Not Found', status_code=status.HTTP_404_NOT_FOUND)
        db.commit()
        return {'message': 'Collaborator Added', 'status': 201}
    except Exception as ex:
        response.status_code = status.HTTP_400_BAD_REQUEST
        logger.exception(ex)
        return {'message': str(ex), 'status': 404}


@routers.delete('/delete_collaborator', status_code=status.HTTP_200_OK, tags=['Notes'])
def delete_collaborator(data: CollaboratorDetails, request: Request, response: Response, db: Session = Depends(get_db)):
    note = db.query(Notes).filter_by(id=data.note_id, user_id=request.state.user.id).first()
    if not note:
        raise HTTPException(status_code=404, detail='Note not found')
    for user in data.user_ids:
        collab = db.query(User).filter_by(id=user).first()
        if not collab:
            raise HTTPException(status_code=404, detail='User Not Found')
        if collab in note.user_m2m:
            note.user_m2m.remove(collab)
    db.commit()
    return {"message": "User deleted from note", "status": 201, "data": note}
