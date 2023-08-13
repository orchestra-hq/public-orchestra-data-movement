from pydantic import BaseModel, Field
from typing import Union, Literal

class fetchDataoBject(BaseModel):
    integration: str


class SalesforceFetchData(fetchDataoBject):
    sf_object: str
    fields: list
    increment_field: Union[str, None]  = Field(default=None, description="The API will filter based on this field to load data incrementally")
    increment_threshold: Union[int, None] = Field(default=None)
    increment_type: Union[None,Literal['day', 'hour']] = Field(default=None)

class SalesforceReturnObject(BaseModel):
    pass

class SalesforceAccount(SalesforceReturnObject):
    accountId: str
    name: str
    pass