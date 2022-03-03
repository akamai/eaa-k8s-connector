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

import logging

class AkaLog:
    def __init__(self, log_name: str, log_level: str = "WARN"):
        self.akalog = logging.getLogger(log_name)
        console_handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s %(name)s %(levelname).1s %(message)s')
        console_handler.setFormatter(formatter)
        self.akalog.addHandler(console_handler)
        self.akalog.setLevel(log_level)
        self.akalog.debug(f"Logging initialized (Level: {log_level})")

    def init(self):
        return self.akalog

    def get_logger(self, logger_name: str):
        return logging.getLogger(logger_name)


    def updateLevel(self, log_level: str="WARN"):
        self.akalog.setLevel(log_level)
# EOF
