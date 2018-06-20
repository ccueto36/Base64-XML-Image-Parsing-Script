import os
import shutil
import requests
import errno
import xml.etree.cElementTree as ET
import pybase64
import time
import configparser
from tkinter.filedialog import askopenfilename
from tkinter import Tk

def main():

	Tk().withdraw()
	print("Waiting for XML file selection...")
	filePath = askopenfilename(initialdir = os.getcwd(), title = "Select XML file", filetypes= (("XML file", "*.xml"), ("All Files", "*.*")))
	print(filePath + " selected. Please wait...")
	start = time.time()
	decodeBase64Strings(filePath)
	end = time.time()
	totalTime = round(end - start)
	print("Decoding took " + str(totalTime) + " seconds", end =" ")
	print(" - %d minutes(s) and %d second(s)" % (totalTime / 60, totalTime % 60))		
	if(createZip() == True): #Compresses image folders into zipped folders
		if(uploadZip() == True): #Uploads the newly created zipped folders on successful zipping
			removeDirectories() #Removes all directories upon successful upload for future use
		
def createDirectory(foldername):
	if not os.path.exists(os.path.dirname(foldername)):
		try:
			os.makedirs(os.path.dirname(foldername))
		except OSError as exc: # Guard against race condition
			if exc.errno != errno.EEXIST:
				raise

def decodeBase64Strings(filePath):
	root = ET.parse(filePath).getroot()

	folder_name = "images1"
	createDirectory("images/" + folder_name + "/")

	print("Decoding Base64 strings, please wait...")
	folderNameCounter = 2
	fileCounter = 0
	totalFileCounter = 0	
	for item in root:
		fileCounter += 1
		totalFileCounter += 1
		if(fileCounter < 16000):
			employee_id = item.find('EMPLID').text
			img_data = str.encode(item.find('EMPLOYEE_PHOTO').text)
			
			with open("images/" + folder_name + "/" + employee_id + ".jpg", "wb") as fh:
				fh.write(pybase64._pybase64.b64decode(img_data,altchars=None, validate=True))
					
		else:
			print("New directory created, previous exceeds size limit.")
			fileCounter = 0
			totalFileCounter += 1
			folder_name = "images" + str(folderNameCounter)
			createDirectory("images/" + folder_name + "/")
			employee_id = item.find('EMPLID').text
			img_data = str.encode(item.find('EMPLOYEE_PHOTO').text)
			
			with open("images/" + folder_name + "/" + employee_id + ".jpg", "wb") as fh:
				fh.write(pybase64.b64decode(img_data,altchars=None, validate=True))
			folderNameCounter += 1
	print(str(totalFileCounter) + " images decoded")

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

def removeDirectories():
	print("Removing directories for future use...")
	try:
		shutil.rmtree("images")
		shutil.rmtree("zippedFiles")
	except OSError as e:
		print("Error: %s - %s." % (e.filename, e.strerror))
	else: 
		print("Directories successfully removed!")

def uploadZip():
	print("Uploading zipped image folders...")
	rootDirectory = "zippedFiles"
	uploadCount = 1
	config = configparser.ConfigParser()
	config.read('config.ini')
	url = config['api-auth']['api-url']
	auth = (config['api-auth']['api-username'], config['api-auth']['api-key'])
	for file in os.listdir(rootDirectory):
		files = {'data': open(rootDirectory + '/' + str(file), 'rb')}
		r = requests.post(url, auth=auth, files=files)
		if(r.status_code == 200):
			print("Zipped folder " + str(uploadCount) + " uploaded successfully!")
			uploadCount += 1
		else:
			print("Error occurred while uploading. ")
			print("Status code " + str(r.status_code))
			return False
	return True
main()

	