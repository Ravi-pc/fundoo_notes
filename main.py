"""
@Author: Ravi Singh

@Date: 2024-02-01 10:20:30

@Last Modified by:

@Last Modified time: 2024-16-01 12:20:30

@Title : Fundoo Notes
"""
from fastapi import FastAPI, Security, Depends, Request
from fastapi.security import APIKeyHeader
from routes.user import router
from routes.notes import routers
from routes.labels import router_label
from core.utils import authorization, request_logger

app = FastAPI()


@app.middleware('http')
def add_middleware(request: Request, call_next):
    response = call_next(request)
    request_logger(request)
    return response


app.include_router(router, prefix='/user')
app.include_router(routers, prefix='/notes', dependencies=[Security(APIKeyHeader(name='authorization')),
                                                           Depends(authorization)])
app.include_router(router_label, prefix='/labels', dependencies=[Security(APIKeyHeader(name='authorization')),
                                                                 Depends(authorization)])
