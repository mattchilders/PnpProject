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

Access PnpDevice class via the device_list property:
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
###Methods and Properties of the PnpProject and PnpDevice classes:
```python
>>> dir(proj)
['__doc__', '__init__', '__module__', 'add_device', 'create_project', 'credentials', 'deviceCount', 'deviceLastUpdate', 'device_list', 'error', 'error_reason', 'get_device_by_id', 'get_device_by_name', 'get_project_by_id', 'get_project_by_name', 'id', 'installerUserID', 'note', 'pendingDeviceCount', 'provisionedBy', 'provisionedOn', 'siteName', 'state', 'tftpPath', 'tftpServer']
>>>
>>>
>>> dir(proj.get_device_by_name('switch1'))
['__doc__', '__init__', '__module__', 'apCount', 'attributeInfo', 'authStatus', 'bootStrapId', 'configId', 'configPreference', 'connectedToDeviceHostName', 'connectedToDeviceId', 'connectedToPortId', 'connectedToPortName', 'connetedToLocationCivicAddr', 'connetedToLocationGeoAddr', 'create_device', 'deviceId', 'error', 'error_reason', 'hostName', 'id', 'imageId', 'imagePreference', 'isMobilityController', 'lastContact', 'lastStateTransitionTime', 'licenseString', 'pkiEnabled', 'platformId', 'populate_device_from_apic', 'serialNumber', 'site', 'state', 'stateDisplay', 'sudiRequired', 'tag']
>>>
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

# ###############
### Exposing Project and Device Attributes
when creating or attaching to an existing project, the attributes available are loaded as properties into the project or device class.  If the attribute doesn't exist on APIC-EM, it will be set to a default value of None

Project Attributes that will become class properties are:
```
projectParameters {
state (string, optional): Project state,
id (string): Project ID,
provisionedBy (string, optional): User creating the project,
provisionedOn (string, optional): Creation time for project,
siteName (string): Project name,
tftpServer (string, optional): TFTP server host name or IP address,
tftpPath (string, optional): TFTP server path,
note (string, optional): Project notes. Any file can be attached,
deviceCount (integer, optional): Number of devices under the project,
pendingDeviceCount (integer, optional): Number of devices in pending state,
deviceLastUpdate (string, optional): Last contact time among all devices in this project,
installerUserID (string, optional): Installer user ID
```

Device Attributes that will become class properties are:
```
serialNumber (string): Serial number,
id (string): ID of device,
site (string, optional): Site to which device belongs if auto-provisioned,
imageId (string, optional): Image file ID,
platformId (string): Platform ID,
hostName (string, optional): Host name,
configId (string, optional): Configuration file id,
bootStrapId (string, optional): Bootstrap file id,
pkiEnabled (boolean, optional): Configure PKCS#12 trust point during PNP workflow if true,
sudiRequired (boolean, optional),
licenseString (string, optional): License string,
apCount (string, optional): Wireless AP count,
isMobilityController (string, optional): Specify if device is a wireless mobility controller,
connectedToDeviceId (string, optional),
connectedToPortId (string, optional),
tag (string, optional): Tag of device,
connectedToPortName (string, optional),
connetedToLocationCivicAddr (string, optional),
imagePreference (string, optional),
connectedToDeviceHostName (string, optional),
configPreference (string, optional),
connetedToLocationGeoAddr (string, optional)
```

