from pydantic import BaseModel, Field
from typing import Union, Literal

class fetchDataoBject(BaseModel):
    integration: str

class HubspotFetchData(fetchDataoBject):
    object_type: str
    fields: Union[list, None] = Field(default=None)
    increment_field: Union[str, None]  = Field(default=None, description="The API will filter based on this field to load data incrementally")
    increment_threshold: Union[int, None] = Field(default=None)
    increment_type: Union[None,Literal['day', 'hour']] = Field(default=None)

class HubspotReturnObject(BaseModel):
    pass

class HubspotContact(HubspotReturnObject):
    vid: int
    canonical_vid: int
    portal_id: int
    addedAt: int
    is_contact: str
    firstname: str
    lastmodifieddate: int
    company: str
    lastname: str

class HubspotContactPush(fetchDataSnowflake):
    vid: int
    fields: dict

class SnowflakeWrite(BaseModel):
    table_name: str
    schema: Union[dict, None]  =Field(default=None)
    method: Literal["overwrite", "upsert"]
    data: Union[list, None] = Field(default = None)
    primary_key: str

class HubspotContactSnowflakeWrite(HubspotContact, SnowflakeWrite):
    pass

class fetchDataSnowflake(BaseModel):
    table_name: str
    limit: Union[None, int]
    filters: Union[None, dict]