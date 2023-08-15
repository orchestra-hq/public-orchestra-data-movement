import boto3
from botocore.config import Config
import json
from typing import Union

from classes.core_models.baseKeyVault import (
    KeyVaultServiceBase,
    secretStatus
)


class AWSSecretsManagerService(KeyVaultServiceBase):
    def __init__(
        self,
        key_vault_name="",
        service_name: str = "secretsmanager",
        region: str = "eu-west-2",
    ):
        self.aws_config = Config(
            region_name=region,
            signature_version="v4",
            retries={"max_attempts": 10, "mode": "standard"},
        )
        self.service_name = service_name
        self.region = region
        super().__init__(key_vault_name)
        self.client = boto3.client(self.service_name, config=self.aws_config)

    def get_secret(self, secret_key: str) -> str:
        secret = self.client.get_secret_value(SecretId=secret_key)
        returned_item = secret["SecretString"]
        try:
            return json.loads(returned_item.replace("'", '"'))[secret_key]
        except json.decoder.JSONDecodeError:
            return returned_item
        except TypeError:
            return returned_item

    def update_secret(
        self, secret_name: str, secret_value
    ) -> secretStatus:
        self.client.update_secret(SecretId=secret_name, SecretString=secret_value)
        return secretStatus.parse_obj({"status": "success"})

    def create_secret(
        self, secret_name: str, secret_key: Union[str, int]
    ) -> secretStatus:
        self.client.create_secret(Name=secret_name, SecretString=secret_key)
        return secretStatus.parse_obj({"status": "success"})

    def create_or_update_secret(
        self, secret_name: str, secret_key: Union[int, str]
    ) -> secretStatus:
        try:
            return self.create_secret(secret_name, secret_key)
        except self.client.exceptions.ResourceExistsException:
            return self.update_secret(secret_name, secret_key)
        except Exception as error:
            return secretStatus.parse_obj({"status": "failure", "message": str(error)})
