#!/usr/bin/python
import time
import json
import requests
import sys
import traceback
import ast
# import IPython

DEBUG = False
requests.packages.urllib3.disable_warnings()


APIC_EM_SERVER = '1.1.1.1'
USER = 'admin'
PASSWORD = 'password'
GET = "get"
POST = "post"
files = {'config': None, 'image': None}
ticket = None


def getServiceTicket():
    """ Service Ticket is used for authorization for all REST Calls throughout the script
    """
    ticket = None
    payload = {"username": USER, "password": PASSWORD}
    url = "https://" + APIC_EM_SERVER + "/api/v1/ticket"

    # Content type must be included in the header
    header = {"content-type": "application/json"}

    # Format the payload to JSON and add to the data.  Include the header in the call.
    # SSL certification is turned off, but should be active in production environments
    response = requests.post(url, data=json.dumps(payload), headers=header, verify=False)

    # Check if a response was received. If not, print(an error message.)
    if(not response):
        print(("No data returned! " + url))
        return None
    else:
        # Data received.  Get the ticket and print(to screen.)
        r_json = response.json()
        ticket = r_json["response"]["serviceTicket"]
        return ticket


def doRestCall(aTicket, command, url, aData=None):
    """ doRestCall is for simplifying REST calls to APIC-EM
    """
    response_json = None
    payload = None
    try:
        # if data for the body is passed in put into JSON format for the payload
        if(aData is not None):
            payload = json.dumps(aData)

        # add the service ticket and content type to the header
        header = {"X-Auth-Token": aTicket, "content-type": "application/json"}
        if(command == GET):
            r = requests.get(url, data=payload, headers=header, verify=False)
        elif(command == POST):
            r = requests.post(url, data=payload, headers=header, verify=False)
        else:
            # if the command is not GET or POST we don't handle it.
            print(("Unknown command!"))
            return None

        # if no data is returned print(a message; otherwise print(data to the screen)
        if(not r):
            print("No data returned! " + url)
            return None
        else:
            if DEBUG:
                print(("Returned status code: %d" % r.status_code))

        # put into dictionary format
        response_json = r.json()
        # print(response_json)
        return response_json
    except:
        err = sys.exc_info()[0]
        msg_det = sys.exc_info()[1]
        print("Error: %s  Details: %s StackTrace: %s" %
              (err, msg_det, traceback.format_exc()))


def refreshFileList(type='config'):
    if type != 'config' and type != 'image':
        return None
    if type == 'config':
        files[type] = doRestCall(ticket, GET, "https://" + APIC_EM_SERVER + "/api/v1/file/namespace/config")
    elif type == 'image':
        files[type] = doRestCall(ticket, GET, "https://" + APIC_EM_SERVER + "/api/v1/file/namespace/image")


def getFileIdByName(fileName, type='config'):
    if type != 'config' and type != 'image':
        return None
    if files[type] is None:
        refreshFileList(type)
    for file in files[type]['response']:
        if file['name'] == fileName:
            return file['id']

    # If no hits update files and try again
    refreshFileList(type)
    for file in files[type]['response']:
        if file['name'] == fileName:
            return file['id']

    # If no hists after update, return None
    return None


def getTaskId(taskId):
    response = doRestCall(ticket, GET, "https://" + APIC_EM_SERVER + "/api/v1/task/" + taskId)
    if(not response):
        return {'isError': True, 'failureReason': 'Unable to retrieve TaskId'}
    else:
        # IPython.embed()
        retryCount = 0
        while ('endTime' not in response["response"]) and retryCount < 10:
            time.sleep(2)
            response = doRestCall(ticket, GET, "https://" + APIC_EM_SERVER + "/api/v1/task/" + taskId)
            retryCount += 1

        if ('endTime' not in response["response"]):
            return {'isError': True, 'failureReason': 'Task did not complete in 20 seconds'}
        else:
            return response["response"]


class pnpProject:
    def __init__(self):
        self.id = None
        self.error = False
        self.errorReason = ''
        self.deviceList = {}

    def createProject(self, projectParameters):
        """ projectParameters needs to be a dictionary of the following format (not all fields required):

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
            }
        """
        response = doRestCall(ticket, POST, "https://" + APIC_EM_SERVER + "/api/v1/pnp-project", [projectParameters])
        taskStatus = getTaskId(response['response']['taskId'])

        if (taskStatus['isError']):
            self.id = None
            self.error = True
            self.errorReason = taskStatus['failureReason']
            return None
        else:
            if taskStatus['progress'].find('siteId'):
                progress_json = ast.literal_eval(taskStatus['progress'])
                self.id = progress_json['siteId']
                self.getProjectById(self.id, False)
                print "Project Created: " + self.siteName + ' (' + self.id + ')'

    def addDevice(self, deviceParameters):
        device = pnpDevice()
        device.createDevice(deviceParameters, self)
        if device.error:
            print 'Error Adding Device to Project: ' + device.errorReason + '(Device Name: ' + deviceParameters['hostName'] + ')'
        else:
            self.deviceList[device.hostName] = device

    def getDeviceByName(self, name):
        if name in self.deviceList:
            return self.deviceList[name]
        else:
            print 'Error: Device Name not in Project'
            return None

    def getDeviceById(self, id):
        for device in self.deviceList:
            if self.deviceList[device].id == id:
                return self.deviceList[device]

        print 'Error: Unable to locate device with that Id'
        return None

    def getProjectByName(self, name):
        response = doRestCall(ticket, GET, "https://" + APIC_EM_SERVER + "/api/v1/pnp-project?offset=1&limit=500")
        value = response['response']
        if 'errorCode' in value:
            print "Error: Unable to get Project: " + value['message'] + ' (' + value['detail'] + ')'
            return None

        for project in value:
            if project['siteName'] == name:
                return self.getProjectById(project['id'])

        print "Unable to locate Project: " + name
        return None

    def getProjectById(self, id, getDevices=True):
        response = doRestCall(ticket, GET, "https://" + APIC_EM_SERVER + "/api/v1/pnp-project/" + id)
        value = response['response']
        if 'errorCode' in value:
            print "Error: Unable to get Project: " + value['message'] + ' (' + value['detail'] + ')'
            return None

        if 'state' in value: self.state = value['state']
        if 'provisionedBy' in value: self.provisionedBy = value['provisionedBy']
        if 'provisionedOn' in value: self.provisionedOn = value['provisionedOn']
        if 'siteName' in value: self.siteName = value['siteName']
        if 'tftpServer' in value: self.tftpServer = value['tftpServer']
        if 'tftpPath' in value: self.tftpPath = value['tftpPath']
        if 'note' in value: self.note = value['note']
        if 'deviceCount' in value: self.deviceCount = value['deviceCount']
        if 'pendingDeviceCount' in value: self.pendingDeviceCount = value['pendingDeviceCount']
        if 'deviceLastUpdate' in value: self.deviceLastUpdate = value['deviceLastUpdate']
        if 'installerUserID' in value: self.installerUserID = value['installerUserID']

        if getDevices and self.deviceCount > 0:
            response = doRestCall(ticket, GET, 'https://' + APIC_EM_SERVER + '/api/v1/pnp-project/' + id + '/device?offset=1&limit=500')
            for deviceDetail in response['response']:
                device = pnpDevice()
                if 'errorCode' in deviceDetail:
                    print "Error: Unable to get Devices: " + deviceDetail['message'] + ' (' + deviceDetail['detail'] + ')'
                    return None

                device.populateDeviceFromAPIC(None, deviceDetail)
                self.deviceList[device.hostName] = device


class pnpDevice:
    def __init__(self):
        self.id = None
        self.error = False
        self.errorReason = ''

    def createDevice(self, deviceParameters, project):
        """ deviceParameters needs to be a dictionary of the following format (not all fields required):
        deviceParameters {
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
        }
        """
        response = doRestCall(ticket, POST, "https://" + APIC_EM_SERVER + "/api/v1/pnp-project/" + project.id + "/device", [deviceParameters])
        taskStatus = getTaskId(response['response']['taskId'])
        # if DEBUG: print taskStatus
        # IPython.embed()

        if (taskStatus['isError']):
            self.error = True
            self.errorReason = taskStatus['failureReason']
            return None
        else:
            if taskStatus['progress'].find('ruleId'):
                progress_json = ast.literal_eval(taskStatus['progress'])
                self.id = progress_json['ruleId']
                self.projectId = project.id
                self.populateDeviceFromAPIC(self.id)
                print "Device Added to Project: " + self.hostName + ' (' + self.id + ') added to Project ' + project.siteName + ' (' + project.id + ')'

    def populateDeviceFromAPIC(self, deviceId, deviceDetail=None):
        if deviceId is not None and deviceDetail is None:
            response = doRestCall(ticket, GET, 'https://' + APIC_EM_SERVER + '/api/v1/pnp-project/' + self.projectId + '/device?offset=1&limit=500')
            for devicesDetail in response['response']:
                if 'id' in devicesDetail:
                    if deviceId == devicesDetail['id']:
                        deviceDetail = devicesDetail

        if 'state' in deviceDetail: self.state = deviceDetail['state']
        if 'authStatus' in deviceDetail: self.authStatus = deviceDetail['authStatus']
        if 'lastContact' in deviceDetail: self.lastContact = deviceDetail['lastContact']
        if 'deviceId' in deviceDetail: self.deviceId = deviceDetail['deviceId']
        if 'lastStateTransitionTime' in deviceDetail: self.lastStateTransitionTime = deviceDetail['lastStateTransitionTime']
        if 'stateDisplay' in deviceDetail: self.stateDisplay = deviceDetail['stateDisplay']
        if 'hostName' in deviceDetail: self.hostName = deviceDetail['hostName']
        if 'serialNumber' in deviceDetail: self.serialNumber = deviceDetail['serialNumber']
        if 'tag' in deviceDetail: self.tag = deviceDetail['tag']
        if 'id' in deviceDetail: self.id = deviceDetail['id']
        if 'platformId' in deviceDetail: self.platformId = deviceDetail['platformId']
        if 'site' in deviceDetail: self.site = deviceDetail['site']
        if 'imageId' in deviceDetail: self.imageId = deviceDetail['imageId']
        if 'configId' in deviceDetail: self.configId = deviceDetail['configId']
        if 'bootStrapId' in deviceDetail: self.bootStrapId = deviceDetail['bootStrapId']
        if 'licenseString' in deviceDetail: self.licenseString = deviceDetail['licenseString']
        if 'apCount' in deviceDetail: self.apCount = deviceDetail['apCount']
        if 'isMobilityController' in deviceDetail: self.isMobilityController = deviceDetail['isMobilityController']
        if 'pkiEnabled' in deviceDetail: self.pkiEnabled = deviceDetail['pkiEnabled']
        if 'sudiRequired' in deviceDetail: self.sudiRequired = deviceDetail['sudiRequired']
        if 'connectedToDeviceId' in deviceDetail: self.connectedToDeviceId = deviceDetail['connectedToDeviceId']
        if 'connectedToPortId' in deviceDetail: self.connectedToPortId = deviceDetail['connectedToPortId']
        if 'connectedToPortName' in deviceDetail: self.connectedToPortName = deviceDetail['connectedToPortName']
        if 'connetedToLocationCivicAddr' in deviceDetail: self.connetedToLocationCivicAddr = deviceDetail['connetedToLocationCivicAddr']
        if 'imagePreference' in deviceDetail: self.imagePreference = deviceDetail['imagePreference']
        if 'connectedToDeviceHostName' in deviceDetail: self.connectedToDeviceHostName = deviceDetail['connectedToDeviceHostName']
        if 'connetedToLocationGeoAddr' in deviceDetail: self.connetedToLocationGeoAddr = deviceDetail['connetedToLocationGeoAddr']
        if 'configPreference' in deviceDetail: self.configPreference = deviceDetail['configPreference']
        if 'attributeInfo' in deviceDetail: self.attributeInfo = deviceDetail['attributeInfo']


def main():
    global ticket
    myProjectDef = {'siteName': 'myProject'}
    ticket = getServiceTicket()
    if ticket is None:
        print "Error: Unable to get a REST Service Ticket"
        quit()

    IMAGE_ID = getFileIdByName('c2960x-universalk9-mz.152-2.E3.bin', 'image')
    PLATFORM = 'WS-C2960X-48FPS'

    devices = {
        'switch1': {"imageId": IMAGE_ID, "platformId": PLATFORM, "configId": None, "hostName": "switch1"},
        'switch2': {"imageId": IMAGE_ID, "platformId": PLATFORM, "configId": None, "hostName": "switch2"},
        'switch3': {"imageId": IMAGE_ID, "platformId": PLATFORM, "configId": None, "hostName": "switch3"},
    }

    newProject = pnpProject()
    newProject.createProject(myProjectDef)
    if newProject.error:
        print "Error Creating Project: " + newProject.errorReason
        quit()

    for device in devices:
        devices[device]['configId'] = getFileIdByName(devices[device]['hostName'])
        # If .txt extension needed:
        # devices[device]['configId'] = getFileIdByName(devices[device]['hostName'] + '.txt')
        if devices[device]['configId'] is None:
            print 'WARNING: Creating device ' + devices[device]['hostName'] + ' without a config file!!!'
        newProject.addDevice(devices[device])

    # IPython.embed()


if __name__ == "__main__":
    main()
