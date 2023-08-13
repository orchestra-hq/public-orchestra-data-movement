import uuid
from fastapi.testclient import TestClient
from main import app
from services.integrations.authzero import AuthZero
from services.integrations.aws import AWS
from services.integrations.slack import SlackWebApiClient
from services.utility.constants import clientguid, internal_token
from services.authentication.azure_kv import KeyVaultService

client = TestClient(app)
authZeroInstance = AuthZero()
headers = {"Authorization": f"Bearer {jwt}"}
keyvault = KeyVaultService("public-api")


def test_aws_connection():
    """TODO"""
    aws = AWS()
    schedule = aws.get_schedules()
    assert schedule is not None

