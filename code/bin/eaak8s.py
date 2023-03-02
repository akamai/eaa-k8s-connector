#!/usr/bin/env python3

# Copyright 2023 Akamai Technologies, Inc. All Rights Reserved
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

# Akamai Modules
import sys
import os
import time
import logging

#import modules.eaaK8sConfig as eaaK8sConfig
import modules.aka_api as aka_api
import modules.aka_docker as Docker


# Setup logging
akalog = logging.getLogger("ekc")
console_handler = logging.StreamHandler()
#formatter = logging.Formatter('%(asctime)s %(name)s %(levelname).1s %(message)s')
console_formatter = logging.Formatter('%(asctime)s %(name)s %(message)s', datefmt='%Y%m%d-%H:%M:%S')

console_handler.setFormatter(console_formatter)
akalog.addHandler(console_handler)
akalog.setLevel("DEBUG")
akalog.debug(f"Logging initialized (Level: {logging.getLevelName(akalog.getEffectiveLevel())})")


#myconfig = eaaK8sConfig.eaaK8sConfig()
#print(myconfig.get())

# Some variables
local_tmp_con_file = '/tmp/connector.tar.gz'

# Connector name
try:
    connector_name=os.environ['CONNECTOR_NAME']
except KeyError:
    connector_name = os.environ['HOSTNAME']


connector_desc = "EAA Connector for k8s - automated via eaa-k8s-sidecar script"

# EDFGERC Section
try:
        edgerc_section = os.environ['EDGERC_SECTION']
except KeyError:
    edgerc_section = "default"

# EDGERC FILE
try:
    edgerc = os.environ['EDGERC']
except KeyError:
    edgerc = "/opt/akamai/.edgerc"

# Instanciate the worker classes
myAkaApi = aka_api.AkaApi(edgerc_section=edgerc_section, edgerc=edgerc)
myDocker = Docker.AkaDocker()



def check_return(retvar, connector_id: str=None):
    """
    Validate the return value not to be False - if connector_id is given, delete the connector on the AKAMAI {OPEN} API
    :param retvar:
    :param connector_id: connector iD
    :return:
    """
    if not retvar:
        if connector_id:
            akalog.debug(f"Trying to remove created connector {connector_id} from AKAMAI {{OPEN}}API")
            del_con = myAkaApi.delete_connector(connector_id)
            if del_con:
                akalog.debug(f"Connector {connector_id} successfully removed")
            else:
                akalog.critical(f"Connector {connector_id} removal failed. "
                                f"Please remove it manual in Enterprise Control Center")

        akalog.critical(f"Error Occured in previous step. Received: {retvar} - exiting")
        time.sleep(600)
        sys.exit(1)


def new_connector():
    """
    The process creates a new connector on {OPEN} API and on the docker hostvui
    :return:
    """

    # Test the connection to OpenAPI
    akalog.info(f"Testing Connection to AKAMAI {{OPEN}}API")
    check_return(myAkaApi.test_connection())

    # Test the connection to Docker
    akalog.info(f"Testing Connection to Docker (DinD)")
    docker_version=myDocker.get_version()
    check_return(docker_version)
    akalog.debug(f"Docker Server reachable: {docker_version}")

    # check if a container (checking for every container) is/was already running
    akalog.info(f"Checking if a container / connector is already running")
    #running = myDocker.container_running()
    running = myDocker.container_running_by_name(containername=f"{connector_name}-con")
    if running:
        akalog.critical(f"A container is already running: {running} - exiting")
        return False


    # Create a new connector (retries=0)
    akalog.info(f"Creating a new connector on AKAMAI {{OPEN}}API")
    newConnector = myAkaApi.create_connector(connector_name=connector_name, connector_desc=connector_desc)
    check_return(newConnector)
    connector_id = newConnector['uuid_url']
    connector_filename = newConnector['download_url'].split('?')[0].split('/')[-1]
    connector_image_name = "akamai_docker_connector_" + connector_filename.split('.')[0]


    # Download connector image
    akalog.info(f"Downloading connector image for the new connector to disk (this can take a while)")
    if os.path.exists(local_tmp_con_file):
        os.remove(local_tmp_con_file)
    download = myAkaApi.download_connector(download_url=newConnector['download_url'], download_file=local_tmp_con_file)
    check_return(retvar=download, connector_id=connector_id)

    # Load the eaa connector image into docker
    akalog.info(f"Importing connector image into docker (this can take a while)")
    docker_load = myDocker.load_image(container_file=local_tmp_con_file)
    check_return(docker_load)
    image = myDocker.search_image(connector_image_name)
    check_return(retvar=image, connector_id=connector_id)

    # CREATE A VOLUME
    akalog.info(f"Creating a docker volume")
    my_volume = myDocker.volume_create(volumename=f"{connector_name}-vol")
    check_return(my_volume)

    # Start the connector (mounting the above volume)
    akalog.info(f"Starting the new connector within docker")
    container = myDocker.run_container(image_name=connector_image_name, container_name=f"{connector_name}-con", volume_name=f"{connector_name}-vol")
    check_return(retvar=container, connector_id=connector_id)

    # Check if connector is ready for approval
    akalog.info(f"Checking if the connector is ready for approval on AKAMAI {{OPEN}}API")
    retries = 10
    time_wait = 60
    counter = 1

    while counter <= 5:
        con_state = myAkaApi.list_connector(connector_id=connector_id)['state']
        check_return(con_state)
        akalog.debug(f"State: {con_state} (Needs to be \'3\' to proceed)")
        if con_state == 3:
            break
        time.sleep(60)
        counter = counter + 1
    if not con_state == 3:
        akalog.critical(f"Connector state did not turn ready within {retries} attempts (slept {time_wait}s in between - exiting")
        check_return(retvar=False, connector_id=connector_id)
        sys.exit(1)

    # Approve the Connector
    akalog.info(f"Approving the newly started connector on AKAMAI {{OPEN}}API")
    approval = myAkaApi.approve_connector(connector_id=connector_id)
    check_return(retvar=approval, connector_id=connector_id)

    # remove tmp artefacts
    akalog.info(f"Removing Download artefacts")
    if os.path.exists(local_tmp_con_file):
        os.remove(local_tmp_con_file)

    # Finish off successfully
    akalog.info(f"Connector Creation finished successfully")


if __name__ == "__main__":
    while True:
        new_connector()
        time.sleep(60)