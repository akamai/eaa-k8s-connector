# Version History

## 0.0.11
|        |                     |
|--------|---------------------|
| Date   | 2024-10-17          |
| Kind   | Feature release     |
| Author | mschiess@akamai.com |  
**BugFixes**
- dropped old way of reading ENV vars in favor of ARGSPARSER - VAR NAMES stayes the same
- Added a "Free Space Check" into EKC to avoid running wild if we don't have enough space to download the connector
- Removing Connector download file after loading it into docker 
- fixed a bug in handling the client_support
- fixed a bug not properly halting when a container already exists 
- fixed a bug that resulted in using the wrong container hostname

## 0.0.10
|||
|---|---|
|Date|2024-07-23
|Kind| Feature release
|Author| mschiess@akamai.com  
**BugFixes**
- fixed a bug that prevented enabling "client support" 

## 0.0.9
|||
|---|---|
|Date|2024-07-19 
|Kind| Feature release
|Author| mschiess@akamai.com  

**BugFixes**
- merged a bugfix (TYPO) PR (thx 2 @aandreev-akamai)
- Eventually fixed the "main" branch
- Fixed Versions in the helm documentation

**Housekeeping**
- Added a higher timeout - waiting for the image
- Added a couple of TCP Client Mode fixes
- Changed the container name from dind-daemon to dind (yeah - lazy me)
- Several documentation changes 
---

## 0.0.8
|||
|---|---|
|Date|2023-05-03
|Kind| Feature release
|Author| mschiess@akamai.com  
**Housekeeping**
- upgraded python version from 3.11 to 3.12 (docker)
---

## 0.0.7
|||
|---|---|
|Date|2023-05-03
|Kind| Feature release
|Author| mschiess@akamai.com
- **bugfix**
  - fixed a bug that prevented cliented traffic to be onboarded
---

## 0.0.6
|||
|---|---|
|Date|2023-04-26
|Kind| Feature release
|Author| mschiess@akamai.com
- **Features**
  - Amending the required CAP'S (net_raw & net_admin) by default (disable via "DISABLE_EAA_CLIENT_SUPPORT" ENV var)
  - Added the new account_key - edgerc enhancement to trigger "accountSwitchKey" (still maintaining the old construct)
----

## 0.0.5
|||
|---|---|
|Date|2023-03-02
|Kind| Feature release
|Author| mschiess@akamai.com
- **Features**
  - Contract ID  (contract_id) now being treated within the .edgerc
  - Connector Data will be stored in a volume now
- **Bugfixes**
  - Fixed some bogus data in the README (docker)

---


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
---


## 0.0.3
|||
|---|---|
|Date|2023-01-24
|Kind| Bugfix release
|Author| mschiess@akamai.com
- **Bugfixes**
  - Changed the connection checking "HEAD" request to a "GET" request as HEAD returned a 400
---

## 0.0.2
|||
|---|---|
|Date|2023-01-19
|Kind| Feature release
|Author| mschiess@akamai.com
- **Bugfixes**
  - fixed a bug in the helm chart (not reading dind tag from values)
  - increased the approval retries from 5 to 10
----

- **HouseKeeping**
  - updated DinD version
  - updated python ekc version
  - Added build manual for M1 silicon
---

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
