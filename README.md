# EAA Kubernetes Connector
This repository contains the code for a sidecar container which installs all the required components to run an [Enterprise Application Access](https://www.akamai.com/products/enterprise-application-access) Connector in Docker environment. 

Currently Web, RDP, and SSH application (client-less) is supported only.From 2022.03.02, EAA will also support TCP-type and Tunnel-type client-access application traffic.


## TL;DR
Fully automated setup of a "long lived" EAA Connector within:
- kubernetes (k8s)
- on a docker host


## Supported Environment Variables 

| Variable                   | Default               | Description                                                                                                                               |
|----------------------------|-----------------------|-------------------------------------------------------------------------------------------------------------------------------------------|
| EDGERC                     | "/opt/akamai/.edgerc" | The EdgeRC File to use                                                                                                                    |
| EDGERC_SECTION             | default               | The EdgeRC Section to use                                                                                                                 | 
| CONNECTOR_NAME             | $HOSTNAME             | The Connector name                                                                                                                        |
| DISABLE_EAA_CLIENT_SUPPORT | False                 | Disabling EAA Client support by removing additional capabilities <br>Set to "True" to disable.                                            | 
| NETWORK_MODE               | bridge                | Specify the desired network mode for the EAA CONNECTOR CONTAINER (Only use in DOCKER ENV) [bridge,none,container:<name\|id>,host,ports]   | 

# Deployments
## Kubernetes
This repo helps you to deploy EAA docker connector within a kubernetes environment, enabling features like:
 - host failure tolerancy
 - scaling
 - k8s version upgrades

### Requirements within k8s
- The EAA-k8s-connector requires a DinD container which needs to run with the "privileged" attribute
- Persistent Volumes (that can be bound to any of your worker nodes)
- A working `.edgerc` file prepared for EAA {OPEN} API
- Kubernetes API access (+ `kubectl`) to create secrets and deployments/statefulsets

### K8s HELM deployment  
Continue reading [here](helm/README.md)

### K(S YAML deployment
- Create a namespace for the connector  
  ```text
  kubectl create namespace <your_namespace>
  ```

- Upload your .edgerc file to k8s  
  Ensure that the credentials are specifically (only) set for EAA.
    ```bash
    kubectl create secret generic akamai-edgerc -n <your_namespace> --from-file=edgerc=/home/username/.edgerc
    ```

- Deploy your workload to k8s  
The following command will start one EAA connector (name=podname)
  ```text
  kubectl apply -n <your_namespace> -f examples/StatefulSet.yml
  ```
  
### Known issues on k8s

- "privileged" flag required for the DinD (Docker in Docker) container
- EAA .edgerc file needs to be provided as secret (please use a proper secret privisioning service !)
---

## Docker
This repo also allows you "auto deploy" an EAA connector on a single docker host

### Requirements within Docker
- container needs to run with the "privileged" attribute (if docker is accessed through the socket)
- A working `.edgerc` file prepared for EAA {OPEN} API

### Docker deployment
The privileged container is only a "sidecar" container that can be removed, once the connector has been started successfully.
```bash
# Put the hostname into an ENV variable 
export AKA_CON_NAME=<YOUR CONNECTOR NAME>

sudo docker run --rm --privileged \
  --volume /var/run/docker.sock:/var/run/docker.sock \
  --volume /root/.edgerc:/opt/akamai/.edgerc \
  --name akamai-ekc \
  --env CONNECTOR_NAME=${AKA_CON_NAME} \
  --name ${AKA_CON_NAME}-ekc \
  akamai/eaa-k8s-connector:latest
```

# Support
Solution is provided as-is, Akamai Support will only be able to help on the EAA Connector as Docker container.  
For anything about the current solution, please open a GitHub ticket.  
This code is not recommended to be run in production environments.  
Please be aware that this setup is not officially supported nor recommended by Akamai. 
