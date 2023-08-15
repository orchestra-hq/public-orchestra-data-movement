import uuid
from fastapi.testclient import TestClient
from main import app
from webclients.authentication.secretsManager import AWSSecretsManagerService

client = TestClient(app)
keyvault = AWSSecretsManagerService()


def test_aws_connection():
    secret = keyvault.get_secret('hubspot-base-url')
    assert secret is not None

