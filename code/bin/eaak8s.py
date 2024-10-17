#!/usr/bin/env python3

# Copyright 2024 Akamai Technologies, Inc. All Rights Reserved
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
import modules.ekc_args as args
import ekc_config.version as version

# Setup logging
# Initialize the configuration
my_args = args.init()

akalog = logging.getLogger("ekc")
console_handler = logging.StreamHandler()
#formatter = logging.Formatter('%(asctime)s %(name)s %(levelname).1s %(message)s')
console_formatter = logging.Formatter('%(asctime)s %(name)s %(message)s', datefmt='%Y%m%d-%H:%M:%S')

console_handler.setFormatter(console_formatter)
akalog.addHandler(console_handler)
akalog.setLevel(my_args.loglevel)
akalog.debug(f"Logging initialized (Level: {logging.getLevelName(akalog.getEffectiveLevel())})")


if my_args.version:
    print(f"{version.__tool_name_long__} - v{version.__version__}")
    sys.exit(0)

# Loading the Variables
## TEMP DIR
local_tmp_con_file = f"{my_args.temp_dir}/connector.tar.gz"
akalog.debug(f"EKC_TEMP_DIR has been set to '{my_args.temp_dir}' - resulting in the tmp con file: {local_tmp_con_file}")

## Connector name
connector_name = my_args.connector_name
akalog.debug(f"CONNECTOR_NAME has been set to '{connector_name}'")

## Connector Description
connector_desc = "EAA Connector for k8s - automated via eaa-k8s-sidecar script"

## EAA_CLIENT_SUPPORT
disable_eaa_client_support = my_args.disable_client_support
akalog.debug(f"DISABLE_EAA_CLIENT_SUPPORT has been set to '{my_args.disable_client_support}'")

## EDGERC FILE
edgerc = my_args.edgerc_file
akalog.debug(f"EDGERC (file location) has been set to '{edgerc}'")
### Verify it is a file
if not os.path.isfile(edgerc):
    akalog.critical(f"EDGERC file '{edgerc}' does not exist. Cannot continue without ! - exiting")
    sys.exit(1)

## EDFGERC Section
edgerc_section = my_args.edgerc_section
akalog.debug(f"EDGERC_SECTION has been set to '{edgerc_section}'")

## NETWORK MODE
network_mode = my_args.network_mode
akalog.debug(f"NETWORK_MODE has been set to '{network_mode}'")



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

def check_free_local_space(path=None):
    my_stats = os.statvfs(path)
    bytes_avail = (my_stats.f_bavail * my_stats.f_frsize)
    gb_avail = bytes_avail / 1024 / 1024 / 1024
    return int(gb_avail)

def new_connector():
    """
    The process creates a new connector on {OPEN} API and on the docker hostvui
    :return:
    """
    # Checking Free space in our tmp dir (this caused an issue earlier ...)
        # does the directory exist
    akalog.info(f"Testing for sufficent free space (~20GB) in '{my_args.temp_dir}'")
    if not os.path.exists(my_args.temp_dir):
        akalog.critical(f"The tmp path '{my_args.temp_dir}' does not exist. Cannot continue without ! - exiting")
        sys.exit(1)

        # do we have enough space
    if check_free_local_space(my_args.temp_dir) < 20:
        akalog.critical(f"Free space on '{my_args.temp_dir}' is less than 20G. We cannot build a connector here - exiting")
        time.sleep(600)
        sys.exit(1)

    # Test the connection to OpenAPI
    akalog.info(f"Testing Connection to AKAMAI {{OPEN}}API")
    check_return(myAkaApi.test_connection())

    # Test the connection to Docker
    akalog.info(f"Testing Connection to Docker (DinD)")
    docker_version=myDocker.get_version()
    check_return(docker_version)
    akalog.debug(f"Docker Server reachable: {docker_version}")

    # check if a container (checking for every container) is/was already running
    akalog.info(f"Checking if a container with a connector is already running")
    #running = myDocker.container_running()
    running = myDocker.container_running_by_name(containername=f"{connector_name}-con")
    if running:
        akalog.critical(f"A container hosting the desried connnector is already running: {running} - exiting")
        sys.exit(1)
        #return False

    # EME-835 - We should check online, if there is already a connector online with the same name
    # And also check the state of the connector
    # tbd

    # Create a new connector (retries=0)
    akalog.info(f"Creating a new connector on AKAMAI {{OPEN}}API")
    newConnector = myAkaApi.create_connector(connector_name=connector_name, connector_desc=connector_desc)
    check_return(newConnector)
    connector_id = newConnector['uuid_url']


    # EME-835 sometimes the image URL is not instantly available - this led to a RACE CONDITION
    # Rather check  a couple of times if we do have a download URL
    url_retries = 100
    url_retry_delay = 30
    my_connector = newConnector

    while url_retry_delay > 0 and not my_connector['download_url']:
        akalog.warning(f"It seems like the download URL isn't available, yet - we're retrying in  {url_retry_delay} seconds (Attempts left: {url_retries})")
        time.sleep(url_retry_delay)
        my_connector = myAkaApi.list_connector(connector_id=connector_id)
        url_retry_delay = url_retry_delay + 60
        url_retries = url_retries - 1

    if not my_connector['download_url']:
        akalog.critical("No Download URL received, i am giving up now ... - exiting !")
        sys.exit(1)
    # /EME-835




    # Download connector image
    akalog.info(f"Downloading connector image for the new connector to disk (this can take a while)")
    if os.path.exists(local_tmp_con_file):
        os.remove(local_tmp_con_file)
    download = myAkaApi.download_connector(download_url=my_connector['download_url'], download_file=local_tmp_con_file)
    check_return(retvar=download, connector_id=connector_id)

    # Load the eaa connector image into docker
    akalog.info(f"Importing connector image into docker (this can take a while)")
    connector_filename = my_connector['download_url'].split('?')[0].split('/')[-1]
    connector_image_name = "akamai_docker_connector_" + connector_filename.split('.')[0]
    docker_load = myDocker.load_image(container_file=local_tmp_con_file)
    check_return(docker_load)
    image = myDocker.search_image(connector_image_name)
    check_return(retvar=image, connector_id=connector_id)
    # Eventually we should also clean up the download file !!!
    try:
        os.remove(local_tmp_con_file)
    except OSError as error:
        akalog.warning(f"Was not able to remove file '{local_tmp_con_file}' - Error: {error}")


    # CREATE A VOLUME
    akalog.info(f"Creating a docker volume")
    my_volume = myDocker.volume_create(volumename=f"{connector_name}-vol")
    check_return(my_volume)

    # Start the connector (mounting the above volume)
    akalog.info(f"Starting the new connector within docker")
    if not disable_eaa_client_support:
        akalog.info(f"Client Support has been enabled for this connector - applying corresponding settings")
        connector_caps = ["NET_ADMIN", "NET_RAW"]
        volumes = [f"{connector_name}-vol:/opt/wapp", "/lib/modules:/lib/modules"]
    else:
        connector_caps = []
        volumes = [f"{connector_name}-vol:/opt/wapp"]

    container = myDocker.run_container(image_name=connector_image_name,
                                       container_name=f"{connector_name}-con",
                                       volumes=volumes,
                                       cap_add=connector_caps,
                                       network_mode=network_mode)
    check_return(retvar=container, connector_id=connector_id)

    # Check if connector is ready for approval
    akalog.info(f"Checking if the connector is ready for approval on AKAMAI {{OPEN}}API")
    retries = 10
    time_wait = 60
    counter = 1

    while counter <= 5:
        con_state = myAkaApi.list_connector(connector_id=connector_id)['state']
        check_return(con_state)
        akalog.debug(f"State: {con_state} (Needs to be \'3\' to proceed) - no worries - we will try this again, soon !")
        if con_state == 3:
            break
        time.sleep(time_wait)
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
