# EAA Kubernetes Connector

This repository holds all required components to run an [Enterprise Application Access](https://www.akamai.com/products/enterprise-application-access) Connector within a Kubernetes environment.

This solution leverages EAA Connector in their Docker flavor, so only web application (client-less) are supported.

## TL;DR

Fully automated setup a "long lived" EAA Connector (statefulSet) within k8s.

## Requirements

- The EAA-k8s-connector requires a DinD container which needs to run with the "privileged" attribute
- Persistent Volumes (that can be bound to any of your worker nodes)
- A working `.edgerc` file prepared for EAA {OPEN} API
- Kubernetes API access (+ `kubectl`) to create secrets and deployments/statefulsets

## ENV VARS

| Variable       | Default | Description               |
|----------------|---------|---------------------------|
| EDGERC_SECTION | default | The EdgeRC Section to use | 


## How to

### helm deployment

Continue reading [here](helm/README.md)

### manual deployment

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
  
## Known issues

- "privileged" flag required for the DinD (Docker in Docker) container
- EAA .edgerc file needs to be provided as secret
- Connector name = pod name

## Support

Solution is provided as-is, Akamai Support will only be able to help on the EAA Connector as Docker container.

For anything about the current solution, please open a GitHub ticket.
