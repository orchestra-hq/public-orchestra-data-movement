import uuid
from typing import Annotated, List, Union
import httpx
from fastapi import APIRouter, Body, Depends, HTTPException, Query, Response, Path
from sqlalchemy.orm import Session
from starlette.background import BackgroundTasks
from starlette.responses import JSONResponse
from dependencies import auth0_token, get_db, get_client_raw
from pydantic_models.core_models import SalesforceAccount, SalesforceFetchData
from routers.api.api_management import APIManagement


router = APIRouter(dependencies=[]) # Insert deps here
APImgmt = APIManagement()

## User auth flow


@router.get("/salesforce/account", status_code=200, response_model=SalesforceAccount)
def check_or_create_user(
    response: Response,
    fetchData: SalesforceFetchData
):

    something = {}
    return SalesforceAccount.parse_obj(something)

