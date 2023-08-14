import uuid
from typing import Annotated, List, Union
import httpx
from fastapi import APIRouter, Body, Depends, HTTPException, Query, Response, Path
from sqlalchemy.orm import Session
from starlette.background import BackgroundTasks
from starlette.responses import JSONResponse
from pydantic_models.core_models import HubspotContact, HubspotFetchData, SnowflakeWrite, HubspotContactSnowflakeWrite,HubspotContactPush, fetchDataSnowflake
from routers.api.api_management import APIManagement
import pandas as pd
from webclients.databases.snowflake_s import Snowflake

router = APIRouter(dependencies=[]) # Insert deps here
APImgmt = APIManagement()

## User auth flow

@router.get("/hubspot/account", status_code=200, response_model=list[HubspotContact])
def fetch_accounts(
    response: Response,
    fetchData: HubspotFetchData = Body()
):
    data = APImgmt.fetch_hubspot_contacts()
    flattened_data = [APImgmt.flatten_hubspot_contacts(x) for x in data]
    return [HubspotContact.parse_obj(x) for x in flattened_data]

@router.post("/snowflake/write", status_code=200)
def snowflake_write( response: Response, writeData: SnowflakeWrite = Body()):  
    overwrite = False
    if writeData.method == 'overwrite':
        overwrite = True
    
    df = pd.DataFrame(writeData.data)
    snowflake = Snowflake()
    staging_name = writeData.table_name + "_staging"
    try:
        # Write a staging table
        snowflake.write_pandas_to_sf(df, staging_name, overwrite=overwrite)
    except Exception as error:
        print(str(error))
        return
    try:
        # If this succeeds, try to upsert the data
        snowflake.upsert_data(writeData.table_name, staging_name, writeData.primary_key, writeData.schema )
    except Exception as error:
        print(str(error))
    # Drop the staging table
    finally:
        snowflake.drop_table(staging_name)

    response.status_code = 200

@router.post("/hubspot/account/snowflake/sync", status_code=200)
def fetch_accounts_and_push_to_snowflake(
    response: Response,
    triggerSync: HubspotContactSnowflakeWrite = Body()
):
    triggerSync.data = fetch_accounts(response, triggerSync)
    triggerSync.schema = dict(triggerSync.data[0])
    return snowflake_write(response, triggerSync)

@router.get("/snowflake/{tablename}", status_code=200)
def fetch_snowflake_data(
    response: Response,
    fetchDataSnowflake: fetchDataSnowflake = Body()
):
    snowflake=Snowflake()
    query = f"SELECT * FROM {fetchDataSnowflake.table_name}"
    response.status_code = 200
    return snowflake.run_query(query, False)

@router.post("/hubspot/contacts/snowflake/{tablename}", status_code=200, response_model=list[HubspotContact])
def push_hubspot_contacts(
    response: Response,
    HubspotContactPush: HubspotContactPush = Body()
):
    data = fetch_snowflake_data(response, HubspotContactPush)