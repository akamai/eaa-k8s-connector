# LOGLEVEL
default_log_level = "WARNING"
log_levels_available = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']


# EKC
default_connector_name_prefix = "EKC"
default_connector_random_size = 10
default_network_mode = "bridge"
disable_client_support = True
default_temp_dir = "/tmp"
    # The time we sleep if a connector is already up & running (we could sleep forever actually)
default_ok_sleep_time = 60 * 60 * 24 * 7 # a week by default

# EDGERC
default_edgerc_file = "/opt/akamai/.edgerc"
default_edgerc_section = "default"