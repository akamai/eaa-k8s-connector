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


import confuse
import modules.aka_log as aka_log
import sys
import pathlib
import os.path

class eaaK8sConfig:
    """
    Class to parse Config File values and enable global file overwriting with "local" config to ensure update safety
    """
    def __init__(self, default_config=str(pathlib.Path(__file__).parent.resolve().parent.resolve().parent.resolve()) + "/" + "config/default_config.yml", local_config=str(pathlib.Path(__file__).parent.resolve().parent.resolve().parent.resolve()) + "/" + "config/local_config.yml"):
        # Check global config
        if not default_config:
            aka_log.log.critical(f"{__name__} No default configuration file specified. "
                                 f"Currently set to {default_config}. - EXITING")
            sys.exit(1)
        else:
            if os.path.isfile(default_config):
                default_config = default_config
                aka_log.log.debug(f"{__name__} Given default configuration file {default_config} loaded. ")
                self.config = confuse.Configuration("eaaK8s", __name__)
                self.config.set_file(default_config)
            else:
                aka_log.log.critical(f"{__name__} Given default configuration file not found. "
                                     f"Currently set to {default_config}. - EXITING")
                sys.exit(1)


        # Check local config

        if os.path.isfile(local_config):
            self.config.set_file(local_config)
        else:
            aka_log.log.critical(f"{__name__} Local configuration file not found. "
                                 f"Skipping loading of  {local_config}.")



    def get(self, root='base':
        #for k in key:
        #    data = data[k]
        #conf = self.config + keys
        return self.config['base'].get()