#!/usr/bin/env python3

# Copyright 2022 Akamai Technologies, Inc. All Rights Reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import requests
import os
import logging




from urllib.parse import parse_qs
from akamai.edgegrid import EdgeGridAuth, EdgeRc


class AkaApi:
    """
    AKAMAI API CLASS for EAA k8s handler
    """
    def __init__(self, edgerc_section="default",
                        edgerc="/opt/akamai/.edgerc" ):
        # Instanciate logging
        self.akalog = logging.getLogger("ekc.AkaApi")
        self.akalog.info("loaded")

        edgerc = EdgeRc(os.path.expanduser(edgerc))
        section = edgerc_section
        self.baseurl = f"https://{edgerc.get(section, 'host')}"

        self.session = requests.Session()
        self.session.auth = EdgeGridAuth(
            client_token=edgerc.get(section, 'client_token'),
            client_secret=edgerc.get(section, 'client_secret'),
            access_token=edgerc.get(section, 'access_token'))
        # The OLD extraQS way of doing account switching (will be disregarded some day !!)
        self.extraqs = None
        scanned_extra_qs = None
        scanned_extra_qs = edgerc.get(section, 'extra_qs', fallback=None)
        if scanned_extra_qs:
            self.akalog.debug(f"Found Extra QS in the .edgerc file: {scanned_extra_qs}")
            self.extraqs = parse_qs(scanned_extra_qs)

        # The NEW account_key way of doing account switching
        account_key = None
        self.account_key = None
        account_key = edgerc.get(section, 'account_key', fallback=None)
        if account_key:
            self.akalog.debug(f"Found an accountSwitchKey (account_key) in the .edgerc file: {account_key}")
            self.account_key = {'accountSwitchKey': account_key}

        # Checking for a contract configuration
        self.contract = None
        scanned_contract = edgerc.get(section, 'contract_id', fallback=None)
        if scanned_contract:
            self.akalog.debug(f"Found a contract ID in the .edgerc file: {scanned_contract}")
            self.contract = {'contractId': scanned_contract}


    def _api_request(self, method="GET", path=None, params={}, payload=None, headers={}, expected_status_list=[200]):
        try:
            my_url = self.baseurl + path
            # Put either the account_key (preferred) or the old extra_qa stuff
            if self.account_key:
                params.update(self.account_key)
            elif self.extraqs:
                params = params | (self.extraqs)

            if self.contract:
                params.update(self.contract)
            self.akalog.debug(f"Sending Request - Method: {method}, Path: {path}")
            my_request = self.session.request(method=method.upper(), url=my_url, params=params, headers=headers, json=payload)
            self.akalog.debug(f"Received Status: {my_request.status_code}, Text: {my_request.text}")
            if my_request.status_code in expected_status_list and my_request.text:
                self.akalog.debug(f"REQ finsihed, returning JSON")
                return my_request.json()
            elif my_request.status_code in expected_status_list:
                self.akalog.debug(f"REQ finsihed, returning True")
                return True
            else:
                self.akalog.warn(f"Request returned wrong status: Status: {my_request.status_code}, Text: {my_request.text}")
                return False
        except Exception as error:
            self.akalog.warn(f"Request error: {error}")
            return False

    def test_connection(self):
        """
        Test the API connection
        :return: True on success
        """
        self.akalog.debug(f"Starting Connection Test")
        return self._api_request(method="GET", path="/crux/v1/mgmt-pop/agents")

    def list_connectors(self):
        """
        List all available connectors with some of the data
        :return: json containing all available containers
        """
        self.akalog.debug(f"Listing Connectors")
        return self._api_request(path="/crux/v1/mgmt-pop/agents")

    def list_connector(self, connector_id: str):
        """
        List all details for a  single connector specified by 'connector_id'
        :param connector_id: Connector ID to list all deatils
        :return: json containing all connector details
        """
        self.akalog.debug(f"Listing single connector: {connector_id}")
        return self._api_request(path=f"/crux/v1/mgmt-pop/agents/" + connector_id)

    def search_connector_by_name(self, connector_name: str):
        """
        Search for a connector in the list of all connectors
        :param connector_name: The name of the connector to search for
        :return: Connector details or False if not found
        """
        self.akalog.debug(f"Searching for connector: {connector_name}")
        page_limit = 100
        max_cycles = 20
        my_params = {"limit": page_limit, "offset": 0}

        while max_cycles > 0:
            result = self._api_request(path="/crux/v1/mgmt-pop/agents", params=my_params)

            for item in result['objects']:
                # print(item['name'])
                if connector_name in item['name']:
                    self.akalog.debug(f"Found connector: {connector_name} with UUID {item['uuid']}")
                    return item['uuid_url']

            if result['meta']['next']:
                my_params["offset"] += page_limit
            else:
                self.akalog.warning(f"No connectors found with name {connector_name}")
                return False


    def create_connector(self, connector_name: str, connector_desc: str, ):
        """
        Create a new connector
        :param connector_name: Specify a name for the new connector
        :param connector_desc: Specify a descriptoin for the new connector
        :return: json containing new connector details
        """
        package_type = 6        # 6 for docker
        payload = {
           "status": 1,
            "auth_service": True,
            "data_service": True,
            "package": package_type,
            "name": connector_name,
            "description": connector_desc,
            "debug_channel_permitted": True,
            "advanced_settings": {
                "network_info": [
                    "0.0.0.0/0"
                ]
            }
        }

        #{'advanced_settings': {'network_info': ['0.0.0.0/0']}, 'agent_type': 1, 'agent_upgrade_enabled': True, 'agent_upgrade_suspended': False, 'agent_version': None, 'auth_service': True, 'cpu': None, 'created_at': '2022-02-21T11:18:23.581819', 'data_service': True, 'debug_channel_permitted': True, 'description': 'EAA - K8s Connector - autoeaa', 'dhcp': 'enabled', 'disk_size': None, 'dns_server': None, 'download_url': 'https://soha-agents-prod.s3.amazonaws.com/7f94ef96-7230-4d27-bb5d-c33172f3b0ba.tar.gz?AWSAccessKeyId=AKIA33AGNFD43EJBRJUS&Signature=5m08kbnzsJIQYVl6THDhju0JYrI%3D&Expires=1648034303', 'gateway': None, 'geo_location': None, 'hostname': None, 'ip_addr': None, 'last_checkin': None, 'load_status': None, 'logging_settings': '[]', 'mac': None, 'manual_override': False, 'modified_at': '2022-02-21T11:18:23.703357', 'name': 'testname', 'os_upgrades_up_to_date': True, 'os_version': None, 'package': 6, 'policy': 'OM9ew-j3Rz2UodydkPYyiQ', 'private_ip': None, 'public_ip': None, 'pwd_comments': None, 'pwdsyncflag': False, 'ram_size': None, 'reach': 0, 'region': None, 'resource_uri': {'href': '/api/v1/agents/GuvhdkwLQnmlSZmNmyMF8Q'}, 'setpwd_attempt': 1, 'state': 1, 'status': 1, 'subnet': None, 'tz': None, 'uuid_url': 'GuvhdkwLQnmlSZmNmyMF8Q'}

        self.akalog.debug(f"Creating new connector: Name: {connector_name}, Desc: {connector_desc}")
        self.akalog.debug(f"Payload: {payload}")
        return self._api_request(method="POST", path="/crux/v1/mgmt-pop/agents", payload=payload)


    def download_connector(self, download_url: str, download_file: str='/tmp/connector.tar.gz'):
        """
        Downloads a connector image from the 'download_url' and stores it to 'download_file'
        :param download_url: URL to download connector from (can be retrieved from connector creation)
        :param download_file: File (incl. path) to store connector to
        :return: True on success
        """
        # 2DO Delete if file exists / Overwrite (safety only)
        try:
            req = requests.get(download_url, allow_redirects=True, stream = True)
            self.akalog.debug("Downloading Connector image (this can take a while)")
            self.akalog.debug(f"Connector DownloadURL: {download_url}")
            self.akalog.debug(f"Target file: {download_file}")

            # Add Progressbar here
            # TQDM
            with open(download_file, 'wb') as outfile:
                for chunk in req.iter_content(chunk_size=1024):
                    outfile.write(chunk)
            return True
        except Exception as err:
            self.akalog.warn(f"Error downloading connector image. Exception: {err}")
            return False


    def approve_connector(self, connector_id: str):
        """
        Approve a newly started connector
        :param connector_id: Connector ID (can be obtained during creation or from the connector list)
        :return: json struct on success
        """
        self.akalog.debug(f"Approving Connector with ID {connector_id}")
        return self._api_request(method="POST", path=f"/crux/v1/mgmt-pop/agents/{connector_id}/approve")

    def delete_connector(self, connector_id: str):
        """
        Delte a connector if something went wrong (saves manual work)
        :param connector_id: Connector ID (can be obtained during creation or from the connector list)
        :return: Json on success
        """
        return self._api_request(method="DELETE", path=f"/crux/v1/mgmt-pop/agents/{connector_id}",
                                 expected_status_list=[204])
