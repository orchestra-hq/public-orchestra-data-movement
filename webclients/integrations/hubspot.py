from webclients.authentication.secretsManager import AWSSecretsManagerService
from webclients.utility.http import HTTP

class Hubspot(HTTP):
    def __init__(self):
        self.secret_keys = [
            f"hubspot-base-url",  # This should come later surely
            f"hubspot-api-key",
        ]
        kv = AWSSecretsManagerService()
        self.__secrets = kv.get_secrets(self.secret_keys)
        apikey_string = f"hightouch-api-key"
        self.apikey = self.__secrets[apikey_string]
        super().__init__(self.__secrets["hightouch-base-url"])
        self.add_default_headers({"Authorization": f"Bearer {self.apikey}"})

    def fetch_contacts(self):
        endpoint = "/contacts/v1/lists/all/contacts/all"
        method = "GET"
        vid_offset = None
        all_contacts = []
        while True:
            params = {"vidOffset": vid_offset} if vid_offset else None
            response = self.base_request(endpoint, method, headers=self.headers, params=params)

            if response.status_code == 200:
                response_data = response.json()
                contacts = response_data.get("contacts", [])
                all_contacts.extend(contacts)
                has_more = response_data.get("has-more")
                if not has_more:
                    break
                vid_offset = response_data.get("vid-offset")
            else:
                raise Exception(f"Error fetching contacts: {response.status_code} - {response.text}")

        return all_contacts

