#!/usr/bin/env python3

import argparse
import os
import string
import random

import ekc_config.default_config as default_config
import ekc_config.version as version
#global hostname_random_part


def init():
    # Argument Parsing
    parser = argparse.ArgumentParser(description=f"{version.__tool_name_long__}",
                                     formatter_class=argparse.RawTextHelpFormatter)

    # Version Information
    parser.add_argument('-v', '--version',
                        action='store',
                        dest='version',
                        type=bool,
                        default=False,
                        const=True,
                        nargs='?',
                        help=f'Display {version.__tool_name_long__} version and operational information')

    # Loglevel
    parser.add_argument('-l', '--loglevel',
                        action='store',
                        dest='loglevel',
                        type=str.upper,
                        default=(os.environ.get('EKC_LOGLEVEL') or default_config.default_log_level),
                        choices=default_config.log_levels_available,
                        help=f"Adjust the loglevel Default: {default_config.default_log_level}\n"
                             f"ENV_VAR: EKC_LOGLEVEL")

    # EKC STUFF
    ekc_group = parser.add_argument_group(title="EKC Configuration",
                                          description="Configure the EKC Settings")

    # The EKC Hostname (or random if not set)
    hostname_random_part = ''.join(random.choice(string.ascii_uppercase) for _ in range(default_config.default_connector_random_size))
    ekc_group.add_argument('--connector_name',
                          action='store',
                          dest='connector_name',
                          type=str,
                          default=(os.environ.get('CONNECTOR_NAME') or f"{default_config.default_connector_name_prefix}-{hostname_random_part}"),
                          help=f"Connector Name. (Default: {default_config.default_connector_name_prefix}-{hostname_random_part}) - randomly generated\n"
                               f"ENV_VAR: CONNECTOR_NAME"
                           )

    ekc_group.add_argument('--disable_client_support',
                          action='store',
                          dest='disable_client_support',
                          type=bool,
                          default=(os.environ.get('DISABLE_EAA_CLIENT_SUPPORT') or f"{default_config.disable_client_support}"),
                          help=f"Disable the EAA Connector client support (Default: {default_config.disable_client_support})\n"
                               f"ENV_VAR: DISABLE_EAA_CLIENT_SUPPORT",
                           )

    ekc_group.add_argument('--network_mode',
                          action='store',
                          dest='network_mode',
                          type=str,
                          default=(os.environ.get('NETWORK_MODE') or f"{default_config.default_network_mode}"),
                          help=f"Disable the EAA Connector client support (Default: {default_config.default_network_mode})\n"
                               f"ENV_VAR: NETWORK_MODE"
                           )

    ekc_group.add_argument('--temp_dir',
                           action='store',
                           dest='temp_dir',
                           type=str,
                           default=(os.environ.get('EKC_TEMP_DIR') or f"{default_config.default_temp_dir}"),
                           help=f"Disable the EAA Connector client support (Default: {default_config.default_temp_dir})\n"
                                f"ENV_VAR: EKC_TEMP_DIR"
                           )

    # EDGERC STUFF
    edgerc_group = parser.add_argument_group(title="EDGERC Configuration",
                                             description="Configure the EDGERC Settings")

    edgerc_group.add_argument('--edgerc_file',
                              action='store',
                              dest='edgerc_file',
                              type=str,
                              default=(os.environ.get('EDGERC') or f"{default_config.default_edgerc_file}"),
                              help=f"The location of the edgerc file. (Default: {default_config.default_edgerc_file})\n"
                                   f"ENV_VAR: EDGERC"
                              )

    edgerc_group.add_argument('--edgerc_section',
                          action='store',
                          dest='edgerc_section',
                          type=str,
                          default=(os.environ.get('EDGERC_SECTION') or f"{default_config.default_edgerc_section}"),
                          help=f"The section to pick within the edgerc file. (Default: {default_config.default_edgerc_section})\n"
                               f"ENV_VAR: EDGERC_SECTION",
                          )



    return parser.parse_args()