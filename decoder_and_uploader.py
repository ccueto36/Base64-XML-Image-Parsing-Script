import os
import sys
import shutil
import requests
import errno
import xml.etree.cElementTree as ET
import pybase64
import configparser

#Creates empty directory with passed name if it doesn't already exist	
def createDirectory(foldername):
	if not os.path.exists(os.path.dirname(foldername)):
		try:
			os.makedirs(os.path.dirname(foldername))
		except OSError as exc: # Guard against race condition
			if exc.errno != errno.EEXIST:
				raise

#Decodes the passed XML file's Base64 strings to .JPG images
#Creates a directory containing 16000 images each, estimated to be nearly 100MB per directory
#If directory surpasses 16000 images, a new directory will be created to keep storing the rest
def decodeBase64Strings(filePath):
	folder_name = "images1"
	createDirectory("images/" + folder_name + "/")

	print("Decoding Base64 strings, please wait...")
	folderNameCounter = 2
	fileCounter = 0
	totalFileCounter = 0
	for event, elem in ET.iterparse(filePath):
		if event == 'end':
			if fileCounter < 16000:
				if elem.tag == 'row':
					fileCounter += 1
					totalFileCounter += 1
					find_and_decode(elem, folder_name)
			else:
				if elem.tag == 'row':
					print("New directory created, previous exceeds size limit.")
					folder_name = "images" + str(folderNameCounter)
					createDirectory("images/" + folder_name + "/")
					fileCounter = 0
					totalFileCounter += 1
					find_and_decode(elem, folder_name)
					folderNameCounter += 1
	print(str(totalFileCounter) + " images decoded")

#Helper function, finds employee_id and employee_photo from the given parent element and decodes employee_photo as 'employee_id.jpg'
def find_and_decode(elem, folder_name):
	if(elem[0].tag == 'EMPLID'):
		employee_id = elem[0].text
	elif(elem[1].tag == 'EMPLOYEE_PHOTO'):
		employee_photo = str.encode(elem[1].text)
	elem.clear() #frees up 'elem' from working tree to free up memory as tree gets built, very important for memory optimization
	with open("images/" + folder_name + "/" + employee_id + ".jpg", "wb") as fh:
		fh.write(pybase64.b64decode(employee_photo, altchars=None, validate=False))

#Compresses child directories of the 'images' parent directory that were created by decodeBase64Strings()
#Stores all zipped directories into "zippedFiles" directory 
def createZip():
	print("Zipping image folders...")
	rootDirectory = "images"
	zipCount = 1
	for file in os.listdir(rootDirectory):
		try:
			shutil.make_archive("zippedFiles" + "/" + str(file),'zip',
				rootDirectory + "/" + str(file))
		except OSError as e:
			print("Error: %s - %s." % (e.filename, e.strerror))
			return False
		else: 
			print("Directory " + str(zipCount) + " successfully zipped!")
			zipCount += 1
	return True

#Uploads all zipped folders within "zippedFolders" directories via HTTPS POST.
#Parses config.ini for API credentials needed for Basic Authentication
#Should only run if createZip() returns success (True)
def uploadZip():
	print("Uploading zipped image folders...")
	rootDirectory = "zippedFiles"
	uploadCount = 1
	config = configparser.ConfigParser()
	config.read('config.ini')
	url = pybase64.b64decode(config['api-auth']['api-url']).decode('utf-8')
	username = pybase64.b64decode(config['api-auth']['api-username']).decode('utf-8')
	api_key = pybase64.b64decode(config['api-auth']['api-key']).decode('utf-8')
	auth = (username, api_key)
	for file in os.listdir(rootDirectory):
		files = {'data': open(rootDirectory + '/' + str(file), 'rb')}
		try:
			r = requests.post(url, auth=auth, files=files)
		except requests.exceptions.RequestException as e:
			print(e)
			sys.exit(1)
		if(r.status_code == 200):
			print("Zipped folder " + str(uploadCount) + " uploaded successfully!")
			uploadCount += 1
		else:
			print("Error occurred while uploading. ")
			print("Status code " + str(r.status_code))
			return False
	return True

#Removes all directories created by script, including directories and zipped folders.
#Called after createZip() returns success (True). 
def removeDirectories():
	print("Removing directories for future use...")
	try:
		shutil.rmtree("images")
		shutil.rmtree("zippedFiles")
	except OSError as e:
		print("Error: %s - %s." % (e.filename, e.strerror))
		return False
	else: 
		print("Directories successfully removed!")
	return True