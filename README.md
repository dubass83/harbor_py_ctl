# DEPRECATED: For now "harbor 2.0" support tags retention
---
# harbor_py_ctl

### fork from [official harbor repo](https://github.com/goharbor/harbor/blob/master/contrib/registryapi)

api for docker registry by token authorization

+ a simple api class which lies in registryapi.py, which simulates the interactions 
between docker registry and the vendor authorization platform like harbor.
```
usage:
from registryapi import RegistryApi
api = RegistryApi('username', 'password', 'http://www.your_registry_url.com/')
repos = api.getRepositoryList()
tags = api.getTagList('public/ubuntu')
manifest = api.getManifest('public/ubuntu', 'latest')
res = api.deleteManifest('public/ubuntu', '23424545**4343')

```
+ a simple client tool based on api class, which contains basic read and delete operations for repo, tag, manifest
```
usage:
./harborctl.py --username username --password passwrod --registry_endpoint http://www.your_registry_url.com/ target action params

target can be: repo, tag, manifest
action can be: list, get, delete
params can be: --repo --ref --tag

more see: ./cli.py -h
```
+ a simple retention policy based on harbor api class and use config.json
```
usage:
create file config/config.json in root folder and run ./harborctl.py
```
+ example of config.json
```json
{
"from_file" : true,
"action" : "clean",
"username" : "username",
"password" : "password",
"registry_endpoint" : "harbor.example.com", 
"repo" : [
"project/repo", "project/repo2"
],
"target" : "tag",
"count" : 20
}
```
