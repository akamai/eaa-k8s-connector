FROM            python:3.11-slim-bullseye
LABEL 	        MAINTAINER="Mike Schiessl - mike.schiessl@akamai.com"
LABEL	        APP_LONG="EAA kubernetes Connector"
LABEL           APP_SHORT="EKC"
LABEL           VENDOR="Akamai Technologies"


# CONFIGURATION ARGS
ARG             HOMEDIR="/opt/akamai"
ARG             EKC_DIR="$HOMEDIR/code"

# ENV VARS
ENV             EKC_DIR=$EKC_DIR


# PREPARE ENVIRONMENT
# ENV PREP
RUN	            apt-get update && \
	            apt-get --no-install-recommends -y install ca-certificates && \
		        rm -rf /var/lib/apt/lists/

# USER & GROUP
RUN 	        groupadd akamai && \
                useradd -g akamai -s /bin/bash -m -d ${HOMEDIR} akamai
#USER            akamai
WORKDIR         ${HOMEDIR}
RUN             mkdir -p ${EKC_DIR}


# Install EKC
COPY            code/ ${EKC_DIR}/
WORKDIR         ${EKC_DIR}
RUN             pip3 install -r ${EKC_DIR}/requirements.txt


# ENTRYPOINTS / CMD
ENTRYPOINT      ["/usr/local/bin/python3","-u","bin/eaak8s.py"]
# EOF
