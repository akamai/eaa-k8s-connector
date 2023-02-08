# Version History
## 0.0.4
|||
|---|---|
|Date|2023-02-07
|Kind| Bugfix release
|Author| mschiess@akamai.com
- **Bugfixes**
  - Removed user privilege drop "security-feature" in Dockerfile to allow "socket access"  
    Also pinned the edgerc path to: `/opt/akamai/.edgerc`, allowing to be overwritten by the EDGERC ENV var
  - using name based checking of a connector-container already exists (vs. is there a container at all before) 
  - added docker documentation (works stand-alone on a docker host)

## 0.0.3
|||
|---|---|
|Date|2023-01-24
|Kind| Bugfix release
|Author| mschiess@akamai.com
- **Bugfixes**
  - Changed the connection checking "HEAD" request to a "GET" request as HEAD returned a 400

## 0.0.2
|||
|---|---|
|Date|2023-01-19
|Kind| Feature release
|Author| mschiess@akamai.com
- **Bugfixes**
  - fixed a bug in the helm chart (not reading dind tag from values)
  - increased the approval retries from 5 to 10

- **HouseKeeping**
  - updated DinD version
  - updated python ekc version
  - Added build manual for M1 silicon

## v0.0.1alpha
|||
|---|---|
|Date|2022-XX-XX
|Kind| Feature release
|Author| mschiess@akamai.com
- **Features**
  - initial POC of the "sidecar" script
  
- **Minor improvements**

- **Bugfixes**