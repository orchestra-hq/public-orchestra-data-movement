import abc
from classes.baseKeyVault import AWSSecretsManagerService
from pydantic_models.core_models import fetchDataoBject

class BaseIntegration(metaclass=abc.ABCMeta):
    """
    This Class represents all the methods an integration should have
    It also acts as a container for secrets that should exist at the integration level
    """

    def __init__(self, secret_keys=[]):
        kv = AWSSecretsManagerService()
        self.kv = kv
        self.secret_keys = secret_keys
        self.secrets = kv.get_secrets(self.secret_keys)

    @abc.abstractmethod
    def get_access_token(self, body: authRequest) -> baseAuthResponse:
        pass

    def fetch_data(self, fetchDataoBject: )