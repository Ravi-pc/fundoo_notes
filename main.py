"""
@Author: Ravi Singh

@Date: 2024-02-01 10:20:30

@Last Modified by:

@Last Modified time: 2024-03-01 12:20:30

@Title : Fundoo Notes
"""
from fastapi import FastAPI, Security, Depends
from fastapi.security import APIKeyHeader
from routes.user import router
from routes.notes import routers
from core.utils import authorization
app = FastAPI()

app.include_router(router, prefix='/user')
app.include_router(routers, prefix='/notes', dependencies=[Security(APIKeyHeader(name='authorization')),
                                                           Depends(authorization)])
app.include_router(routers, prefix='/labels', dependencies=[Security(APIKeyHeader(name='authorization')),
                                                            Depends(authorization)])
