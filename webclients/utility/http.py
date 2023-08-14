from datetime import datetime
import requests
from requests.adapters import HTTPAdapter, Retry
import asyncio
import aiohttp
import httpx
import os

class HTTP:
    def __init__(self, base_url):
        self.base_url = base_url
        self.headers = None

    def add_default_headers(self, headers):
        self.headers = headers
        return self

    def add_headers(self, new_headers):
        if self.headers:
            self.headers = {**self.headers, **new_headers}
        self.headers = new_headers

    def simple_request(
        self, endpoint, method="GET", params=None, headers=None, body=None, data=None
    ):
        full_url = self.base_url
        if endpoint:
            full_url = f"{full_url}/{endpoint}"
        if headers:
            self.add_headers(headers)
        return requests.request(
            method,
            full_url,
            params=params,
            headers=self.headers,
            json=body,
            data=data,
        )

    def base_request(
        self, endpoint, method="GET", params=None, headers=None, body=None, data=None
    ):
        s = requests.Session()

        retries = Retry(
            total=5, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504]
        )
        s.mount("http://", HTTPAdapter(max_retries=retries))
        full_url = self.base_url
        if endpoint:
            full_url = f"{full_url}/{endpoint}"
        if headers:
            self.add_headers(headers)
        try:
            response = s.request(
                method,
                full_url,
                params=params,
                headers=self.headers,
                json=body,
                data=data,
            )
            log_message = f"{response.request.method} {response.request.url} - {response.status_code} {response.reason}"
            if isinstance(response.json(), list):
                return {
                    **{"data": response.json()},
                    **{"status_code": response.status_code, "reason": response.reason},
                }

            return {
                **response.json(),
                **{"status_code": response.status_code, "reason": response.reason},
            }

        except Exception as error:
            return {
                "status_code": response.status_code,
                "reason": response.reason,
                "error": "Internal error: " + str(error),
            }
