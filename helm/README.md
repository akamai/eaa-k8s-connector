# Helm usage (recommended)

## Run a Connetor via helm 

### Install Git helper plugin for helm
This step is only required, as long asa there is no "official" akamai HELM REPO
Based on the helm [git-repo plugin](https://artifacthub.io/packages/helm-plugin/git/helm-git)
```text
helm plugin install https://github.com/aslafy-z/helm-git

# Verifiy installation
helm plugin list
```

### Add the Helm Repo (mocked with helm-git)
This steps (together with the one before) adds the helm "mocked" repo to helm repo 
```text
helm repo add akamai-ekc "git+https://github.com/akamai/eaa-k8s-connector@helm?ref=development"

# Verify Repo installation
helm repo list
helm search repo akamai-ekc
```

### Create a namespace for your connectors
```text
kubectl create namespace <your_namespace>
```

### Upload your .edgerc file to k8s (API Credentials)
Ensure that the credentials are specifically (only) set for EAA.  
*Please bare in mind that kubernetes secrets will NOT encrypt your credentials hence they will become visible to all other users of the cluster*

```bash
kubectl create secret generic akamai-edgerc -n <your_namespace> --from-file=edgerc=/home/username/.edgerc
```

### Install your new connector via helm
With the following command, helm will install the EAA Kubernetes Connector helm package.  
It will create 200 GB PVC in the default storage class (multi AZ storageclases recommended).
```text
helm upgrade --install --create-namespace --namespace <your_namespace> <your-connector-name> akamai-ekc
```

# Known issues
## pod errors
The pod will not come up immediately, as there are some cross - requirements.
you might see a couple of 
```bash
connector     1/2     Error     1 (17s ago)   63s
```
or even
```bash
connector     1/2     CrashLoopBackOff   1 (12s ago)    68s
```
but in the end it should come up perfectly fine 