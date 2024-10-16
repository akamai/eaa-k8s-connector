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


import docker
import logging
import sys

class AkaDocker:
    def __init__(self):
        # Instanciate logging
        self.akalog = logging.getLogger("ekc.AkaDocker")
        self.akalog.info("loaded")
        try:
            self.client = docker.from_env(timeout=3600)
        except docker.errors.TLSParameterError:
            self.akalog.critical("TLS connection to docker failed - cant continue - exiting")
            sys.exit(1)

    def get_version(self):
        self.akalog.debug(f"Fetching Docker Server version")
        return self.client.version()

    def list_images(self):
        self.akalog.debug(f"Listing Docker images")
        return self.client.images.list()

    def search_image(self, searchpattern: str=None):
        self.akalog.debug(f"Searching Docker image: {searchpattern}")
        return (self.client.images.list(name=searchpattern))

    def list_containers(self):
        self.akalog.debug(f"Listing Docker containers (ps -a)")
        return self.client.containers.list()

    def load_image(self, container_file):
        self.akalog.debug(f"Importing Docker image from file ({container_file})")
        try:
            with open(container_file, 'rb') as readfile:
                self.client.images.load(data=readfile)
            return True
        except Exception as err:
            self.akalog.warning(f"Exception occurred during import of docker image from file. Exception: {err}")
            return False

    def run_container(self, image_name: str = None, container_name: str = None, volumes: list = None, cap_add: list = ["NET_ADMIN", "NET_RAW"], network_mode: str = "bridge"):
        self.akalog.debug(f"Start the new connector (Name: {container_name}) from image (Image: {image_name})")
        return self.client.containers.run(image=image_name, name=container_name, volumes=volumes, detach=True, restart_policy={"Name": "always"}, cap_add=cap_add, network_mode=network_mode)

    # Obsolete --> better container_running_by_name
    def container_running(self):
        self.akalog.debug(f"Check if a container is already running")
        return self.client.containers.list(all=True)

    def container_running_by_name(self, containername):
        self.akalog.debug(f"Check a container with my name is already running")
        return self.client.containers.list(filters={"name": containername})

    def volume_create(self, volumename=None):
        self.akalog.debug(f"Creating a new volume")
        return self.client.volumes.create(name=volumename)

# EOF
