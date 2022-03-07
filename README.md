# EAA Kubernetes Connector
This repo holds all required stuff to run an [Enterprise Application Access](https://www.akamai.com/products/enterprise-application-access) Connector wihtin kubernetes.

## TR;DR
Fully automated setup a "long lived" EAA Conenctor (statefulSet) within k8s

 
## Requirements
- The EAA-k8s-connector requires a DinD container which needs to run with the "privileged" attribute
- Persistent Volumes (that can be bound to any of your worker nodes)
- A working .edgerc file prepared for EAA {OPEN}API
- Kubernetes API access (+ kubectl) to create secrets and deployments/statefulsets


## How to
### helm deployment
continue reading [here](helm/README.md)

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
- "privilegted" flag required for the DinD (Docker in Docker) container
- EAA .edgerc file needs to be provided as secret
- Connector name = pod name