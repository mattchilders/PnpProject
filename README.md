# PnpProject
PnpProject is a python class for creating and modifying Plug-n-Play Projects on APIC-EM.  The goal was to make a simple interface to programatically create/update a project and devices, as well as access device information, such as status and error states.
See main() for example of how to create a new project and populate with devices..

# ###############
###Get an existing Project:
Instantiate the Project and then call 'get_project_by_name' or 'get_project_by_id'
```python
>>> credentials = login(username='admin', password='password', server='1.1.1.1')
>>>
>>> proj = PnpProject(credentials)
>>> proj.get_project_by_name('myProject')
>>>
```

device_list is a property of the PnpProject class that keeps a dictionary with the device hostName as the key, and a pnpDevice object as the value:
```python
>>> proj.device_list
{u'switch1': <__main__.pnpDevice instance at 0x10e235f38>, u'switch2': <__main__.pnpDevice instance at 0x10e2431b8>, u'switch3': <__main__.pnpDevice instance at 0x10e243098>}
>>>
>>>
```

Access PnpDevice class via the device_list Property:
```python
>>> proj.device_list['switch1'].hostName
u'switch1'
>>> proj.device_list['switch1'].configId
u'cb87c80b-9011-433f-9275-9e5c92897f0a'
>>> proj.device_list['switch1'].imageId
u'f439bbc9-a73f-45e9-88f0-11f86152cd08'
>>>
```

 deviceCount is a property of PnpProject (notice camelCase for device and project properties... to maintain consistency with naming in APIC-EM)
```python
>>> proj.deviceCount
9
```

get_device_by_name and get_device_by_id are methods of PnpProject that return the pnpDevice object in the Project
```python
>>> proj.get_device_by_name('switch1').id
u'aa5550b6-3df0-468f-9cae-5ab4c2136b37'
>>> proj.get_device_by_id('aa5550b6-3df0-468f-9cae-5ab4c2136b37').hostName
u'switch1'
```

# ###############
###Methods and Properties of the pnpDevice class:
```python
>>> dir(proj.get_device_by_name('switch1'))
['__doc__', '__init__', '__module__', 'apCount', 'attributeInfo', 'create_device', 'error', 'error_reason', 'hostName', 'id', 'imageId', 'isMobilityController', 'pkiEnabled', 'platformId', 'populate_device_from_apic', 'site', 'state', 'stateDisplay', 'sudiRequired']
```

# ###############
###Add a device to an existing Project
```python
>>> image_id = get_file_id_by_name(credentials, 'cat3k_caa-universalk9.SPA.03.07.04.E.152-3.E4.bin', 'image')
>>> config_id = get_file_id_by_name(credentials, 'switch4.txt')
>>> device_definition = {'imageId': image_id, 'platformId': 'WS-C3650-48PQ', 'configId': config_id, 'hostName': 'switch4'}
>>> proj.add_device(device_definition)
Device Added to Project: switch4 (3ecc60a8-19a8-41c9-977d-f0e39383b953) added to Project myProject (be358095-2f6a-4e47-8dcd-e6b9bdf66ecc)
```

# ###############
### Create a Project with specific settings (like tftpserver and path...):
Instantiate the Project and create the definition of the project (camelCase for Project Definitions to maintain consistency with APIC-EM naming)
```python
>>> credentials = login(username='admin', password='password', server='1.1.1.1')
>>> proj = PnpProject(credentials)
>>> projectDef = {'siteName' : 'TFTPProject', 'tftpServer' : '1.1.1.1', 'tftpPath' : '/files/'}
```

Call the create_project method of the PnpProject to creat the project
```python
>>> proj.create_project(projectDef)
Project Created: TFTPProject (00cdf394-48d7-474a-b4d5-535b51e488d9)
```

Access the properties of the Project (camelCase)
```python
>>> proj.tftpServer
u'1.1.1.1'
>>> proj.tftpPath
u'/files/'
```
 
# ###############
### Get File Id's in PnP's file repository:

get_file_id_by_name function takes a file name and returns the id - by default it will search the config file store
```python
>>> get_file_id_by_name('switch1')
u'cb87c80b-9011-433f-9275-9e5c92897f0a'
>>>
>>>
```

To get an image id, pass the 'image' attribute along with the file name:
```python
>>> get_file_id_by_name('c2960x-universalk9-mz.152-2.E3.bin', 'image')
u'f439bbc9-a73f-45e9-88f0-11f86152cd08'
```
