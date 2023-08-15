from pydantic import BaseModel, Field, Extra
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
    company: Union[str, None] = Field(default=None)
    lastname: Union[str, None] = Field(default=None)



class SnowflakeWrite(BaseModel):
    table_name: str
    schema__: Union[dict, None]  =Field(default=None, alias='schema')
    method: Literal["overwrite", "upsert"]
    data: Union[list, None] = Field(default = None)
    primary_key: str
    class Config:
        extra = Extra.allow

class HubspotContactSnowflakeWrite(SnowflakeWrite):
    data: list
    schema__: dict = Field(alias ='schema')
    pass

class fetchDataSnowflake(BaseModel):
    limit: Union[None, int]
    columns: list

class HubspotContactPush(fetchDataSnowflake):
    data: list
    fields: list