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
    response: Response
):
    data = APImgmt.fetch_hubspot_contacts()
    flattened_data = [APImgmt.flatten_hubspot_contacts(x) for x in data]
    return [HubspotContact.parse_obj(x) for x in flattened_data]

@router.post("/snowflake/write", status_code=200)
def snowflake_write( response: Response, writeData: SnowflakeWrite = Body()):  
    overwrite = False
    if writeData.method == 'overwrite':
        overwrite = True
    df = pd.DataFrame([dict(x) for x in writeData.data])
    snowflake = Snowflake()
    staging_name = writeData.table_name + "_staging"
    try:
        # Write a staging table
        output = snowflake.write_pandas_to_sf(df, staging_name, overwrite=overwrite)
    except Exception as error:
        print(str(error))
        return
    
    try:
        # If this succeeds, add the main table in if it does not exist 
        snowflake.create_snowflake_table(writeData.table_name,writeData.schema)
        # If this succeeds, try to upsert the data
        snowflake.upsert_data(writeData.table_name, staging_name, writeData.primary_key, writeData.schema )
    except Exception as error:
        print(str(error))
    # Drop the staging table
    finally:
        print("snowflake.drop_table(staging_name)")

    response.status_code = 200

@router.post("/hubspot/account/snowflake/sync", status_code=200)
def fetch_accounts_and_push_to_snowflake(
    response: Response,
    triggerSync: SnowflakeWrite = Body()
):
    triggerSync.data = fetch_accounts(response)
    triggerSync.schema = dict(triggerSync.data[0])
    return snowflake_write(response, triggerSync)

@router.get("/snowflake/{tablename}", status_code=200)
def fetch_snowflake_data(
    response: Response,
    tablename:str,
    fetchDataSnowflake: fetchDataSnowflake=Body()
):
    col_string = ",".join(fetchDataSnowflake.columns)
    snowflake=Snowflake()
    query = f"SELECT {col_string} FROM {tablename}"
    response.status_code = 200
    data = snowflake.run_query(query, False)
    data['columns'] = fetchDataSnowflake.columns
    data['data'] = [ dict(zip(data['columns'], item))  for item in data['data']  ]
    return data

@router.post("/hubspot/contacts/", status_code=200)
def push_hubspot_contacts(
    response: Response,
    HubspotContactPush: HubspotContactPush = Body()
):
    response = APImgmt.update_contacts(HubspotContactPush.data, HubspotContactPush.columns)
    return response 
    
@router.get("/snowflake/{tablename}/hubspot/contacts", status_code=200)
def pull_contacts_and_push(
    response: Response,
    tablename:str,
    fetchDataSnowflake: fetchDataSnowflake=Body()
):
    data = fetch_snowflake_data( response, tablename, fetchDataSnowflake)
    hubspot_contacts = HubspotContactPush.parse_obj({"data":data["data"] , "columns":fetchDataSnowflake.columns})
    return push_hubspot_contacts(response, hubspot_contacts)