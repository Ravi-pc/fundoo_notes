from fastapi import APIRouter, status, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session
from core.model import get_db, Labels
from core.schema import LabelDetails

router_label = APIRouter()


@router_label.post('/labels_notes', status_code=status.HTTP_200_OK, tags=['Labels'])
def add_labels(body: LabelDetails, request: Request, response: Response, db: Session = Depends(get_db)):
    """
        Description: add_labels function is used to add a label to the database.

        Parameter: Labels details, Request, Response, get_db.

        Return: Json Response.

    """
    try:

        body = body.model_dump()
        body['user_id'] = request.state.user.id
        new_label = Labels(**body)
        db.add(new_label)
        db.commit()
        db.refresh(new_label)
        return {'message': 'Labels Added', 'status': 201, 'data': body}

    except Exception as ex:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {'message': str(ex), 'status': 400}


@router_label.get('/get_labels', status_code=status.HTTP_200_OK, tags=['Labels'])
def retrieve_all_labels(request: Request, response: Response, db: Session = Depends(get_db)):
    """
        Description: retrieve_labels function is used to retrieve all labels from the database.

        Parameter: Request, Response, get_db.

        Return: Json Response .

    """
    try:
        notes = db.query(Labels).filter_by(user_id=request.state.user.id).all()
        return {'message': 'Labels Retrieved', 'status': 201, 'data': notes}

    except Exception as ex:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {'message': str(ex), 'status': 400}


@router_label.delete('/delete_labels/{id}', status_code=status.HTTP_200_OK, tags=['Labels'])
def delete_labels(label_id: int, request: Request, response: Response, db: Session = Depends(get_db)):
    """
        Description: delete_labels function is used to delete a label from the database.

        Parameter: Label_id, Request, Response, get_db.

        Return: Json Response.

    """
    try:
        label = db.query(Labels).filter_by(user_id=request.state.user.id, id=label_id).first()
        db.delete(label)
        db.commit()

        return {'message': 'Labels Deleted', 'status': 200}

    except Exception as ex:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {'message': str(ex), 'status': 400}


@router_label.put('/update_labels/{label_id}', status_code=status.HTTP_200_OK, tags=['Labels'])
def update_labels(label_id: int, request: Request, notes_schema: LabelDetails, response: Response,
                  db: Session = Depends(get_db)):
    """
        Description: update_labels function is used to update a label from the database.

        Parameter: Label_id, Label details, Request, Response, get_db.

        Return: Json Response.

    """
    try:
        label = db.query(Labels).filter_by(user_id=request.state.user.id, id=label_id).first()
        if label:
            updated_labels = notes_schema.model_dump()
            [setattr(label, key, value) for key, value in updated_labels.items()]
            db.commit()
            db.refresh(label)
            return {'message': 'Label Updated', 'status': 200}
        else:
            raise HTTPException(detail='No Labels found for the user', status_code=404)

    except Exception as ex:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {'message': str(ex), 'status': 400}
    