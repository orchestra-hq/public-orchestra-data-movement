
from webclients.integrations.hubspot import Hubspot

class APIManagement():
    def __init__(self):
        pass

    def fetch_hubspot_contacts(self):
        hubspot_client = Hubspot()
        return hubspot_client.fetch_contacts()

    def update_contacts(self, json_list, fields_to_update):
        hubspot_client = Hubspot()
        return hubspot_client.update_contacts(json_list, fields_to_update)

    def flatten_hubspot_contacts(self, data:dict):
        return {
            "vid": data['vid'],
            "canonical_vid": data['canonical-vid'],
            "portal_id": data['portal-id'],
            "addedAt": data['addedAt'],
            "is_contact": data['is-contact'],
            "firstname": data['properties']['firstname']['value'],
            "lastmodifieddate": data['properties']['lastmodifieddate']['value']
            }
           