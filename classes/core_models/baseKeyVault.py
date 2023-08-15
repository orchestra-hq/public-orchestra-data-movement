import abc
from datetime import datetime
from pydantic import BaseModel, UUID4

from typing import Union
from enum import Enum

class secretStatus(BaseModel):
    status: str
    message: Union[None, str]

class AWSSecret(BaseModel):
    ARN: str
    Name: str
    VersionId: str
    SecretString: str
    VersionStages: list
    CreatedDate: datetime
    ResponseMetadata: dict


class KeyVaultServiceBase:
    def __init__(self, key_vault_name):
        self.__vault_name = key_vault_name
        self.__client = None
        self.cache = {}

    @abc.abstractmethod
    def get_secret(self, secret_key: str) -> str:
        pass

    def fetch_secret_into_cache(self, secret_key: str) -> str:
        """Fetches a secret from keyvault and stores it into the cache"""
        secret_value = self.get_secret(secret_key)
        self.cache[secret_key] = {
            "value": secret_value,
            "last_fetched_at": datetime.now(),
        }
        return secret_value

    def fetch_secret_from_cache(self, secret_key: str, timeout=60) -> str:
        """Fetches a secret from the cache if it exists and satisfies the timeout condition, otherwises fetches the secret into cache"""
        cached_value = self.cache.get(secret_key)
        if (
            cached_value
            and (datetime.now() - cached_value["last_fetched_at"]).seconds < timeout
        ):
            return cached_value["value"]
        return self.fetch_secret_into_cache(secret_key)

    @abc.abstractmethod
    def update_secret(
        self, secret_name: str, secret_value
    ) -> secretStatus:
        pass

    @abc.abstractmethod
    def create_secret(
        self,
        secret_name: str,
        secret_key: Union[int, str],
        ignore_existing: bool = True,
    ) -> secretStatus:
        pass

    def create_secrets(self, secrets, secret_values) -> secretStatus:
        if len(secrets) != len(secret_values):
            raise Exception(
                message="Length of secrets and secrets value should be equal"
            )
        try:
            [
                self.create_secret(item, secret_values[i])
                for i, item in enumerate(secrets)
            ]
            return secretStatus.parse_obj({"status": "success"})
        except Exception as error:
            return secretStatus.parse_obj({"status": "failure", "message": str(error)})

    def get_secrets(self, secret_keys: list) -> dict:
        secrets = [self.fetch_secret_from_cache(key) for key in secret_keys]
        return dict(zip(secret_keys, secrets))

    @abc.abstractmethod
    def create_or_update_secret(
        self, secret_name: str, secret_key: Union[int, str]
    ) -> secretStatus:
        pass
