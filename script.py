import decoder_and_uploader as du
import time

#Gets called on program execution
def main():
	path = "\\\\ad.fiu.edu\\offprovost\\AdvisingTech\\EAB Photos\\photos.xml"
	start = time.time()
	du.decodeBase64Strings(path)
	end = time.time()
	totalTime = round(end - start)
	print("Decoding took " + str(totalTime) + " seconds", end =" ")
	print(" - %d minutes(s) and %d second(s)" % (totalTime // 60, totalTime % 60))		
	if(du.createZip() == True): #Compresses image folders into zipped folders
		du.uploadZip()  #Uploads the newly created zipped folders upon successful zip creation
	du.removeDirectories() #Removes all directories for future use

main()



	