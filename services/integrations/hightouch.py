from services.authentication.secretsManager import AWSSecretsManagerService
from services.utility.http import HTTP



class Hightouch(HTTP):
    def __init__(self, clientid: str):
        # kv = KeyVaultService("codat-data") # this needs to change to clientid
        self.secret_keys = [
            f"hightouch-base-url",  # This should come later surely
            f"hightouch-api-key-{clientid}",
        ]
        kv = KeyVaultService("public-api")
        self.__secrets = kv.get_secrets(self.secret_keys)
        self.postgres = Postgres()
        self.clientid = clientid
        apikey_string = f"hightouch-api-key-{clientid}"
        self.apikey = self.__secrets[apikey_string]
        super().__init__(self.__secrets["hightouch-base-url"])
        self.add_default_headers({"Authorization": f"Bearer {self.apikey}"})

    def trigger_connector_sync(self, syncid: int, body: dict = {"fullResync": False}):
        return self.base_request(f"syncs/{syncid}/trigger", method="POST", body=body)

    def get_sync(self, sync_run_id: int):
        """
        {
                "id": 544033,
                "slug": "pipeline-results-to-google-sheets",
                "workspaceId": 37597,
                "createdAt": "2023-04-02T20:48:35.974Z",
                "updatedAt": "2023-04-02T21:19:27.511Z",
                "destinationId": 72403,
                "modelId": 692519,
                "configuration": {
                    "mode": "mirror",
                    "mappings": [],
                    "sheetName": "Destination",
                    "configVersion": 1,
                    "spreadsheetId": "1M7V28YolonRA_TWbivA_rddfPaSc0LMGTP2R6RtXOjU",
                    "sheetSelection": "input",
                    "autoSyncColumns": true
                },
                "schedule": null,
                "status": "success",
                "disabled": false,
                "lastRunAt": "2023-04-02T21:19:25.030Z",
                "referencedColumns": [],
                "primaryKey": "pipelinerunguid"
            }
        """
        return self.base_request(f"syncs/{sync_run_id}", method="GET")

    def get_sync_run(self, syncid: int, sync_run_id: int):
        """
        {
            "data": [
                {
                    "id": 157045676,
                    "createdAt": "2023-04-10T17:56:52.279Z",
                    "startedAt": "2023-04-10T17:56:52.553Z",
                    "finishedAt": "2023-04-10T17:57:02.685Z",
                    "querySize": 109,
                    "status": "success",
                    "completionRatio": 1,
                    "plannedRows": {
                        "addedCount": 109,
                        "changedCount": 0,
                        "removedCount": 0
                    },
                    "successfulRows": {
                        "addedCount": 0,
                        "changedCount": 0,
                        "removedCount": 0
                    },
                    "failedRows": {
                        "addedCount": 0,
                        "changedCount": 0,
                        "removedCount": 0
                    },
                    "error": null
                }
            ]
        }
        """
        return self.base_request(
            f"syncs/{syncid}/runs?runId={sync_run_id}", method="GET"
        )
