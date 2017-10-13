from PnpProject import *

# Directions:
# Create a folder and populate it with the device configs, WITHOUT any .txt extension.  This will be added automatically
# Point the "CONFIG_PATH" variable below to the folder you just created
# This assumes all the platforms are the same... if not, you'll need some logic to determine the platform based on the file name
# Setup the variables below including the Image path, name, and site name, and then run the script
# It should create a site with a device corresponding to each file name in the folder
# The only thing you'll need to do then is associate a serial number with each device, which can be done by scanning the serial number
# of the device on the box into APIC-EM.

SITE_NAME='Site1'
CONFIG_PATH = '/path/to/configs/'
IMAGE_NAME = 'cat3k_caa-universalk9.SPA.03.07.04.E.152-3.E4.bin'
IMAGE_PATH = '/path/to/images/'
PLATFORM = 'WS-C3650-48P'

credentials = pnp_login(username='admin', password='password', server='1.1.1.1')

fh = PnpFileHandler(credentials)

proj = PnpProject(credentials)
proj.siteName = SITE_NAME
proj.create_project()

image_id = fh.get_file_id_by_name(IMAGE_NAME, 'image')
if image_id is None:
    image_id = fh.upload_file(IMAGE_PATH + IMAGE_NAME, 'image')

#Loop through the configs in the config path and upload the config and create a device for each
#Name the files the device_name (don't add the .txt extension) and it create the device based on the name in the 
for file in os.listdir(CONFIG_PATH):
    config_id = fh.get_file_id_by_name(file)
    if config_id is None:
        config_id = fh.upload_file(CONFIG_PATH+'/'+file+'.txt')
    if config_id is not None:
        #replace any dots in the file name with dashes because device names cannot include dots
        device_name = file.replace('.', '-')
        device_definition = {'imageId': image_id, 'platformId': PLATFORM, 'configId': config_id, 'hostName': device_name}
        proj.add_device_with_parameters(device_definition)

