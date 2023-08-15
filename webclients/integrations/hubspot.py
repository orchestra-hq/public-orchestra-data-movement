from webclients.authentication.secretsManager import AWSSecretsManagerService
from webclients.utility.http import HTTP
import json 

class Hubspot(HTTP):
    def __init__(self):
        self.secret_keys = [
            f"hubspot-api-key"
        ]
        kv = AWSSecretsManagerService()
        self.__secrets = kv.get_secrets(self.secret_keys)
        self.apikey = self.__secrets["hubspot-api-key"]
        self.base_url = 'https://api.hubspot.com'
        super().__init__(self.base_url)
        self.add_default_headers({"Authorization": f"Bearer {self.apikey}"})

    def fetch_contacts(self):
        endpoint = "/contacts/v1/lists/all/contacts/all"
        method = "GET"
        vid_offset = None
        all_contacts = []
        while True:
            params = {"vidOffset": vid_offset} if vid_offset else None
            response = self.base_request(endpoint, method, headers=self.headers, params=params)
            if response["status_code"] == 200:
                contacts = response.get("contacts", [])
                all_contacts.extend(contacts)
                has_more = response.get("has-more")
                if not has_more:
                    break
                vid_offset = response.get("vid-offset")
            else:
                status_code = response.get("status_code")
                raise Exception(f"Error fetching contacts: {status_code}")

        return all_contacts
    
    def update_contacts(self, json_list, fields_to_update):
        self.headers = {**self.headers, **{'Content-Type': 'application/json'}}
        responses = []
        for json_data in json_list:
            vid = json_data.get("vid")
            if not vid:
                continue

            contact_updates = {}
            for field in fields_to_update:
                if field in json_data:
                    contact_updates[field] = json_data[field]

            if contact_updates:
                endpoint = f"crm/v3/objects/contacts/{vid}"
                response = self.base_request(endpoint, "PATCH", headers=self.headers, data=json.dumps({"properties": contact_updates}))
                responses.append(response)
                if response["status_code"] != 200:
                    status_code = response.get("status_code")
                    raise Exception(f"Error updating contact {vid}: {status_code}")

        return responses


