# harbor_py_ctl

### fork from [official harbor repo](https://github.com/goharbor/harbor/blob/master/contrib/registryapi)
+ a simple client tool based on api class, which contains basic read and delete operations for repo, tag, manifest
```
usage:
./cli.py --username username --password passwrod --registry_endpoint http://www.your_registry_url.com/ target action params

target can be: repo, tag, manifest
action can be: list, get, delete
params can be: --repo --ref --tag

more see: ./cli.py -h
```
