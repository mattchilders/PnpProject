# PnpProject
PnpProject is a python class for creating and modifying Plug-n-Play Projects on APIC-EM.  The goal was to make a simple interface to programatically create/update a project and devices, as well as access device information, such as status and error states.
See main() for example of how to create a new project and populate with devices..

# ###############
#Get an existing Project:
Instantiate the Project and then call "getProjectByName" or "getProjectById"
```python
>>> proj = pnpProject()
>>> proj.getProjectByName('myProject')
>>>
```

deviceList is a property of the pnpProject class that keeps a dictionary with the device hostName as the key, and a pnpDevice object as the value:
```python
>>> proj.deviceList
{u'switch1': <__main__.pnpDevice instance at 0x10e235f38>, u'switch2': <__main__.pnpDevice instance at 0x10e2431b8>, u'switch3': <__main__.pnpDevice instance at 0x10e243098>}
>>>
>>>
```

Access pnpDevice class via the deviceList Property:
```python
>>> proj.deviceList['switch1'].hostName
u'switch1'
>>> proj.deviceList['switch1'].configId
u'cb87c80b-9011-433f-9275-9e5c92897f0a'
>>> proj.deviceList['switch1'].imageId
u'f439bbc9-a73f-45e9-88f0-11f86152cd08'
>>>
```

 deviceCount is a property of pnpProject
```python
>>> proj.deviceCount
9
```

getDeviceByName and getDeviceById are methods of pnpProject that return the pnpDevice object in the Project
```python
>>> proj.getDeviceByName('switch1').id
u'aa5550b6-3df0-468f-9cae-5ab4c2136b37'
>>> proj.getDeviceById('aa5550b6-3df0-468f-9cae-5ab4c2136b37').hostName
u'switch1'
```

# ###############
#Methods and Properties of the pnpDevice class:
```python
>>> dir(proj.getDeviceByName('switch1'))
['__doc__', '__init__', '__module__', 'apCount', 'attributeInfo', 'configId', 'createDevice', 'error', 'errorReason', 'hostName', 'id', 'imageId', 'isMobilityController', 'pkiEnabled', 'platformId', 'populateDeviceFromAPIC', 'site', 'state', 'stateDisplay', 'sudiRequired']
```

# ###############
# Create a Project with specific settings (like tftpserver and path...):
Instantiate the Project and create the definition of the project
```python
>>> myProj = pnpProject()
>>> projectDef = {'siteName' : 'TFTPProject', 'tftpServer' : '1.1.1.1', 'tftpPath' : '/files/'}
```

Call the createProjet method of the pnpProject to creat the project
```python
>>> myProj.createProject(projectDef)
Project Created: TFTPProject (00cdf394-48d7-474a-b4d5-535b51e488d9)
```

Access the properties of the Project
```python
>>> myProj.tftpServer
u'1.1.1.1'
>>> myProj.tftpPath
u'/files/'
```
 
# ###############
# Get File Id's in PnP's file repository:

getFileByName function takes a file name and returns the id - by default it will search the config file store
```python
>>> getFileIdByName('switch1')
u'cb87c80b-9011-433f-9275-9e5c92897f0a'
>>>
>>>
```

To get an image id, pass the 'image' attribute along with the file name:
```python
>>> getFileIdByName('c2960x-universalk9-mz.152-2.E3.bin', 'image')
u'f439bbc9-a73f-45e9-88f0-11f86152cd08'
>>> getFileIdByName('c2960x-universalk9-mz.152-2.E3.bin')
```
