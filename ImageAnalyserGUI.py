from tkinter import *
#Imports tkinter
from tkinter import ttk
#Imports tkinter ttk module
from tkinter.filedialog import *
#Imports tkinter filedialog module
import tkinter.messagebox
#Imports tkinter message box module
from PIL import Image, ImageTk, ImageDraw
#Imports all required PIL modules
import imageio
#Imports imaheio, used for generating GIFs
import sys
#Imports sys module
import os
#Imports os module
import shutil
#Imports shutil module
IconPath = "C:\\Users\\mattd\\Desktop\\CS Coursework\\GUI\\Final\\Icons\\ImageAnalyserIcon.ico"
#Path of the icon for the GUI

class ImageAnalyserGUI:
    def __init__(self,master):

        self.menu = Menu(root)
        root.config(menu=self.menu)
        #Creates a dropdown menu widget in the root window
        BuildMenu(self)
        #Runc the BuildMenu(self) subroutine that adds the menu buttons

        self.content = Frame(root)
        self.content.pack(side=TOP)
        #Creates a content from within the root wondow

        self.imageFrame = Frame(self.content,height=500,width=500,bg="black")
        self.imageFrame.pack(side=LEFT)
        #Creates the image frame on the left side of the content frame

        self.inputFrame= Frame(self.content,height=500,width=250)
        self.inputFrame.pack(side=LEFT)
        #Created the imput fram on the right side of the content frame

        self.status = Label(root,text="Ready for Images",bd=1,relief=SUNKEN,anchor=W)
        self.status.pack(side=BOTTOM,fill=X)
        #Creates a status bar at the bottom of the root window

        self.topFill = Label(self.inputFrame,text=" ")
        self.topFill.grid(column=0,row=0)
        #Creates a filler label for spacing the input buttons in the input frame

        self.upload = ttk.Button(self.inputFrame,text="Select Images",command=self.SelectFile)
        self.upload.grid(column=0,row=1,columnspan=2,padx=(0,100))
        #Creates the 'Select Images' button in the input frame
        
        self.imageSelect = Label(self.inputFrame,text="No Images Selected")
        self.imageSelect.grid(column=1,row=1,padx=(100,0))
        #Creates the label that displays the number of imges in the .zip file in the input fram

        global checkCircle
        checkCircle = IntVar()
        self.circleNEOCheck = Checkbutton(self.inputFrame,text="Circle Near Earth Objects in images",variable=checkCircle)
        self.circleNEOCheck.grid(column=1,row=2,columnspan=2,pady=10)
        #Creates the check box for circling NEOs in the input frame
        
        self.analyse = ttk.Button(self.inputFrame,text="Analyse",command=self.AnalyseImages,state=DISABLED)
        self.analyse.grid(column=1,row=3)
        #Creates the 'Analyse' button in the inout frame

        self.analyseBreak = Label(self.inputFrame,text="")
        self.analyseBreak.grid(column=0,row=5,pady=30)
        #Creates a filler label between the analyse section and the navigation section in the input frame

        self.imageNum = Label(self.inputFrame,text="No Images Selected")
        self.imageNum.grid(column=1,row=6)
        #Creates the image number label of the navigation sectioon in the input frame
        
        self.previousImage = ttk.Button(self.inputFrame,text="<",width=3,command=self.PreviousImage)
        self.previousImage.grid(column=0,row=6,padx=(10,0))
        #Creates the previous image button in the input frame

        self.nextImage = ttk.Button(self.inputFrame,text=">",width=3,command=self.NextImage)
        self.nextImage.grid(column=3,row=6,padx=(0,10))
        #Creates the next image button in the input frame

        self.resultsBreak = Label(self.inputFrame,text="")
        self.resultsBreak.grid(column=0,row=7,pady=30)
        #Creates a filler lable to seperate the navigation section and the results section in the input frame

        self.results = Label(self.inputFrame,text="No Images Analysed")
        self.results.grid(column=1,row=8)
        #Creates the label that displays the results of the analysis in the input frame

        self.checkInfo = Label(self.inputFrame,text="Use the check box to toggle circles")
        self.checkInfo.grid(column=1,row=9,pady=10)
        #Creates the label that give infomation about the check box in the input frame

        self.viewCoordinates = ttk.Button(self.inputFrame,text="View Coordinates",command=self.ViewCoordinates,state=DISABLED)
        self.viewCoordinates.grid(column=1,row=10)
        #Creates the button that displays the coordinates of objects in image in the input frame

        self.bottomFill = Label(self.inputFrame,text="")
        self.bottomFill.grid(column=0,row=11)
        #Creates a filler label for spacing the input buttons in the input frame

        self.noImageText = Label(self.imageFrame,text="No Images Selected",width=70,height=30,fg="white",bg="black")
        self.noImageText.pack()
        #Creates the display if 'No Images Selected' in the image frame

        
    def New(self):
        answer = tkinter.messagebox.askquestion("Do you want to open a new window?","Are you sure you want to open a new window? Any images will not be saved.")
        #Open message box checking if the user wants to open a new instance of the program
        if answer == "yes":
            python = sys.executable
            os.execl(python, python, * sys.argv)
            #Closes the program and opens a new instance of it
            try:
                os.remove("tempImages.zip")
                #Deletes the temporary zip file of circled images if it exists
            except FileNotFoundError:
                pass

    def Open(self):
        file = askopenfilename(filetypes=(("Zipped files","*.zip"),("All files","*")))
        #Opens a file dialog for the user to select a file to open
        global path
        path = file
        global displayImageNum
        displayImageNum = 0
        global drawCircles
        drawCircles = False
        self.analyse.config(state=DISABLED)
        #Disables the 'Analyse' button
        OpenImages(self,path,displayImageNum)
        #Calls the OpenImages() subroutine

    def SaveZIP(self):
        try:
            if drawCircles is False:
                #Checks if the images have been circled
                answer = tkinter.messagebox.askquestion("Do you want to save?","The images have not been changed. If you save, it will save a duplicate of the original .zip file. Do you want to save?")
                #Informs the user that no changes have been made, and asks if they still want to save
                if answer == "yes":
                    SaveImagesZip(path)
                    #Calls the SaveImagesZip() subroutine
            else:
                SaveImagesZip("tempImages.zip")
                #Calls the SaveImagesZip subroutine for the temporary .zip file of circled images
        except NameError:
            self.status.config(text="Save Error")
            alert = tkinter.messagebox.showerror("Save Error","No images have been analysed. Please analyse images and try again.")
            self.status.config(text="Ready for Images")
            #If no images have been analysed, generates a message box to inform the user

    def SaveGIF(self):
        try:
            if drawCircles is False:
                SaveImagesGif(path)
                #Calls the SaveImagesGif() subroutine
            else:
                SaveImagesGif("tempImages.zip")
                #Calls the SaveImagesGif subroutine for the temporary .zip file of circled images
        except NameError:
            self.status.config(text="Save Error")
            alert = tkinter.messagebox.showerror("Save Error","No images have been analysed. Please analyse images and try again.")
            self.status.config(text="Ready for Images")
            #If no images have been analysed, generates a message box to inform the user

    def About(self):
        aboutWindow = Toplevel()
        aboutWindow.title("About")
        aboutWindow.resizable(width=False, height=False)
        #Generates a new window titles 'About'

        aboutLabel = Label(aboutWindow,text="\nThe Near Earth Object Image Analyser is\na program that allows you to upload\na series of images of the night\nsky to be analysed for Near Earth Objects.\n")
        aboutLabel.pack()
        #Adds text to the window

        closeButton = ttk.Button(aboutWindow, text="Close", command=aboutWindow.destroy)
        closeButton.pack()
        #Generates the close button for the window

    def Instructions(self):
        instructionsWindow = Toplevel()
        instructionsWindow.title("Instructions")
        instructionsWindow.geometry("800x525")
        instructionsWindow.resizable(width=False, height=False)
        #Generates a new window titles 'Instructions'

        selectInfo = Label(instructionsWindow,text="\nSelect Images:\nThis allows you to select the images that you want to analyse.\nThese images must be stored in a .zip file.")
        selectInfo.pack()

        circleInfo = Label(instructionsWindow,text="\nCircle NEOs:\nThis allows you to toggle if any Near Earth Objects in the images have circles drawn around them.")
        circleInfo.pack()

        analyseInfo = Label(instructionsWindow,text="\nAnalysing Images:\nThis will analyse the images for Near Earth Objects.\nPlease not that while images are being analysed, the program may say 'Not Responding'. This is normal, you might just have to wait a while.")
        analyseInfo.pack()

        chooseInfo = Label(instructionsWindow,text="\nImage Selector:\nWhen you images have finished being analysed they will be displayed on the left hand of the screen.\nYou can use these buttons to navigate between the images. Please note, for circled images the selection process may be slow.")
        chooseInfo.pack()

        coordinatesInfo = Label(instructionsWindow,text="\nView Coordinates:\nThis allows you to view the pixel coordinates of the centre points of all the objects in the images.")
        coordinatesInfo.pack()

        newInfo = Label(instructionsWindow,text="\nNew:\nThis will close the current NEO Image Analyser window and open a new one.")
        newInfo.pack()

        openInfo = Label(instructionsWindow,text="\nOpen:\nThis allows you to open a series of imags and view them.\nYou will be able to save them but not analyse them however.")
        openInfo.pack()

        saveInfo = Label(instructionsWindow,text="\nSaving Images:\nYou are able to save your image in two ways, either all images in new .zip file or as a .gif file.\n")
        saveInfo.pack()

        #Adds text to the window

        closeButton = ttk.Button(instructionsWindow, text="Close", command=instructionsWindow.destroy)
        closeButton.pack()
        #Generates the close button for the window

    def Exit(self):
        answer = tkinter.messagebox.askquestion("Do you want to exit?","Are you sure you want to exit? Any images will not be saved.")
        #Asks the user if they are sure that they want to close the program
        if answer == "yes":
            try:
                os.remove("tempImages.zip")
                #Deletes the temporary zip file of circled images if it exists
            except FileNotFoundError:
                pass
            root.quit()
            #Closes the program

    def SelectFile(self):
        file = askopenfilename(title="Select Images",filetypes=(("Zipped files","*.zip"),("All files","")))
        #Opens a file dialog and asks the user for the file
        self.analyse.config(state=NORMAL)
        #Enables the 'Analyse' button
        global path
        path = file
        GetImagesInZip(self,path)
        #Calls the GetImagesInZip() subroutine from Base Algorithm

    def AnalyseImages(self):
        global drawCircles
        drawCircles = False
        if (checkCircle.get()) == 1:
            drawCircles = True
            #Checks if the circle images checkbox has been ticked
        try:
            OpenZip(self,FileNames,path,meanOfLen)
            #Calls the OpenZip() subroutine from the Base Algorithm
            self.analyse.config(state=DISABLED)
            #Disables the 'Analyse' button
            if drawCircles is True:
                self.checkInfo.config(text="Any Near Earth Objects have been circled")
                #Updates the check box information
            self.viewCoordinates.config(state=NORMAL)
            #Enables the 'View Coordinates' button
        except OSError:
            self.status.config(text="File Error")
            alert = tkinter.messagebox.showerror("File Error","There was a problem with the contents of the .zip file. Make sure it only contains images")
            self.status.config(text="Ready for Images")
            #If the zip file contains anyhting but images, it informs the user

    def PreviousImage(self):
        global displayImageNum
        self.imageLabel.pack_forget()
        #Deletes the contents of the image label
        displayImageNum = DisplayPreviousImage(self,displayImageNum)
        #Updates the image number being displayed
        DisplayImages(self,displayImageNum)
        #Calls the DisplayImages() subroutine

    def NextImage(self):
        global displayImageNum
        self.imageLabel.pack_forget()
        #Deletes the contents of the image label
        displayImageNum = DisplayNextImage(self,displayImageNum)
        #Updates the image number being displayed
        DisplayImages(self,displayImageNum)
        #Calls the DisplayImages() subroutine

    def ViewCoordinates(self):
        coordsWindow = Toplevel()
        coordsWindow.title("Image Coordinates")
        coordsWindow.resizable(width=False, height=False)
        #Creates a new window to display the coordinates of all objects in the images

        imageNum = Label(coordsWindow,text="Image "+str(displayImageNum+1)+":")
        imageNum.pack()
        #Displays the image number

        for Object in NearEarthObjects[displayImageNum]:
            imageObjects = ""
            if NearEarthObjects[displayImageNum][Object] is True:
                objectType = "Near Earth Object"
                #If it is NEO, displays that it is next to the coordinates
            else:
                objectType = "Star"
                #If it is not NEO, displays that it is a star next to the coordinates
            imageObjects+=objectType+" at ("+str(Object)+")"
            #Displays the coordinates of the object
            displayObjects = Label(coordsWindow,text=imageObjects,anchor=W)
            displayObjects.pack()

        closeButton = ttk.Button(coordsWindow, text="Close", command=coordsWindow.destroy)
        closeButton.pack()
        #Generates the close button for the window
            
        
        

def BuildMenu(self):
    fileMenu = Menu(self.menu,tearoff=False)
    fileMenu.add_command(label="New",command=self.New)
    fileMenu.add_command(label="Open",command=self.Open)
    self.menu.add_cascade(label="File",menu=fileMenu)
    #Generates the buttons for the 'File' section of the menu

    saveMenu = Menu(fileMenu,tearoff=False)
    saveMenu.add_command(label="Save Images as.zip",command=self.SaveZIP)
    saveMenu.add_command(label="Save as .gif",command=self.SaveGIF)
    fileMenu.add_cascade(label="Save",menu=saveMenu)
    #Generates the buttons for the 'Save' section of the file menu

    fileMenu.add_separator()
    fileMenu.add_command(label="Exit",command=self.Exit)
    #Adds a seperator and an exit button to the 'File' menu

    analyseMenu = Menu(self.menu,tearoff=False)
    analyseMenu.add_command(label="Select Images",command=self.SelectFile)
    analyseMenu.add_command(label="Analyse",command=self.AnalyseImages)
    self.menu.add_cascade(label="Analyse",menu=analyseMenu)
    #Generates the 'Select Images' and 'Analyse' buttons of the 'Analyse' menu

    helpMenu = Menu(self.menu,tearoff=False)
    helpMenu.add_command(label="Instructions",command=self.Instructions)
    helpMenu.add_command(label="About",command=self.About)
    self.menu.add_cascade(label="Help",menu=helpMenu)
    #Generates the 'Instructions' and 'About' buttons of the 'Analyse' menu


def OpenImages(self,path,displayImageNum):
    archive = zipfile.ZipFile(path,"r")
    #Gets the .zip file from the path and reads it
    global FileNames
    FileNames = archive.namelist()
    #Gets a list of file names from the .zip file
    archive.close()
    self.noImageText.pack_forget()
    #Deletes the 'No Images Selected' text from the image frame
    try:
       self.imageLabel.pack_forget()
       #If there are already images in the image frame, deletes them
    except AttributeError:
        pass
    DisplayImages(self,displayImageNum)
    #Calls the DisplayImages() subroutine

def DisplayImages(self,displayImageNum):
    if drawCircles is False:
        #If the check box for circling in images is NOT ticked:
        archive = zipfile.ZipFile(path,"r")
        #Gets the .zip file from the path and reads it
        FileName = FileNames[displayImageNum]
        #Gets the file name of the image number
        image = Image.open(archive.open(FileName))
        #Opens the image
        image = image.resize((496,456),Image.ANTIALIAS)
        #Resizes the image so that it can be displayed in the program
        photo = ImageTk.PhotoImage(image)
        #Sets the image to a variable
        
        self.imageLabel = Label(self.imageFrame,image=photo)
        #Displays the image in the GUI
        self.imageLabel.image = photo
        #Keeps a reference of the image to avoid deletion
        self.imageLabel.pack()
        self.imageNum.config(text="Image "+str(displayImageNum+1)+" of "+str(len(FileNames)))
        #Updates the current image number
        archive.close()
        #Closes the .zip file
    else:
        #If the check box for circling in images IS ticked:
        DrawImageCircles()
        #Calls the DrawImageCircles() subroutine
        archive = zipfile.ZipFile("tempImages.zip","r")
        #Gets the .zip file from the path and reads it
        FileName = FileNames[displayImageNum]
        #Gets the file name of the image number
        image = Image.open(archive.open(FileName))
        #Opens the image
        image = image.resize((496,456),Image.ANTIALIAS)
        #Resizes the image so that it can be displayed in the program
        photo = ImageTk.PhotoImage(image)
        #Sets the image to a variable
        
        self.imageLabel = Label(self.imageFrame,image=photo)
        #Displays the image in the GUI
        self.imageLabel.image = photo
        #Keeps a reference of the image to avoid deletion
        self.imageLabel.pack()
        self.imageNum.config(text="Image "+str(displayImageNum+1)+" of "+str(len(FileNames)))
        #Updates the current image number
        archive.close()
        #Closes the .zip file

def DisplayPreviousImage(self,displayImageNum):
    if displayImageNum != 0:
        displayImageNum-=1
        #Subtracts 1 from the current image number of it is not 0
    return displayImageNum

def DisplayNextImage(self,displayImageNum):
    if displayImageNum <= len(FileNames)-2:
        displayImageNum+=1
        #Adds 1 to the curret image number if it is not the total number of images
    return displayImageNum

def DrawImageCircles():
    openArchive = zipfile.ZipFile(path,"r")
    saveArchive = zipfile.ZipFile("tempImages.zip","w")
    #Creates a temporary .zip file to store the circled images
    #Below loops for all the images in the .zip file
    for imageNum in range(len(FileNames)):
        FileName = FileNames[imageNum]
        image = Image.open(openArchive.open(FileName))
        rgb_drawImage = image.convert('RGB')
        #Converts to RGB so pixels can be drawn
        #Below loops for all images in the NearEarthObject list
        for Object in NearEarthObjects[imageNum]:
            imageObjects = ""
            if NearEarthObjects[imageNum][Object] is True:
                #If it is a NEO:
                radius = GetRadius(imageNum,Object)
                #Gets its radius from the list
                CalculateCirclePoints(intCoordinates,radius)
                #Calls the CalculateCirclePoints() subroutine
                circleNEO = ImageDraw.Draw(rgb_drawImage)
                #Makes the image drawable
                circleNEO.ellipse((circlePoints[0],circlePoints[1],circlePoints[2],circlePoints[3]),outline=(0,255,94))
                #Drawn a circle around the NEO
        rgb_drawImage.save(FileName)
        #Saves the image with the same file name temporaraly
        saveArchive.write(FileName)
        #Saves the edited image to the temporary .zip file
        os.remove(FileName)
        #Deletes the temporary copy of the image
    saveArchive.close()
    #Closes the .zip file
                

def GetRadius(imageNum,Object):
    #Below loops for each star in each image
    for star in range(len(ImageStarsCopy[imageNum])):
        coordinates = str(ImageStarsCopy[imageNum][star][1])
        coordinates = coordinates.lstrip("[").rstrip("]")
        #Converts the coordinates of the object to a form that the dictionary can interpret
        if Object == coordinates:
            #If the coordinates match those in the dictionary
            global intCoordinates
            intCoordinates = ImageStarsCopy[imageNum][star][1]
            radius = ImageStarsCopy[imageNum][star][0]
            #Get the radius form the dictionary
    return radius
    #Returns the radius
    
def CalculateCirclePoints(intCoordinates,radius):
    global circlePoints
    circlePoints = []
    midpoint = intCoordinates
    diameter = 2*radius
    #Calculates the diameter
    x0 = midpoint[0]-(diameter+starRemovalModifier)
    y0 = midpoint[1]-(diameter+starRemovalModifier)
    x1 = midpoint[0]+(diameter+starRemovalModifier)
    y1 = midpoint[1]+(diameter+starRemovalModifier)
    #Claculates the coordinates of each corner of the circle to circle the NEO
    circlePoints.append(x0)
    circlePoints.append(y0)
    circlePoints.append(x1)
    circlePoints.append(y1)
    #Appends the coordinates to a list
    
def SaveImagesZip(filePath):
    file = asksaveasfilename(title="Save As .zip",filetypes=(("Zipped files","*.zip"),("All files","*")))
    #Asks the user for their save location and file name
    file = file+".zip"
    #Adds .zip to the end of the users file name
    shutil.copy(filePath,file)
    #Copies the .zip file, either the original or the temporary one containing circled images
    tkinter.messagebox.showinfo("Images Saved","The images were successfully saved.")
    #Informs the user that the images were saved

def SaveImagesGif(filePath):
    file = asksaveasfilename(title="Save As .gif",filetypes=(("GIF files","*.gif"),("All files","*")))
    #Asks the user for their save location and file name
    file = file+".gif"
    #Adds .gif to the end of the users file name
    images = []
    #Creates a list of images to add to the GIF
    archive = zipfile.ZipFile(filePath,"r")
    #Gets the .zip file from the path and reads it
    fileNames = archive.namelist()
    #Gets all file names from the .zip file
    for imageNum in range(len(fileNames)):
        FileName = fileNames[imageNum]
        #Gets the file name
        image = Image.open(archive.open(FileName))
        #Opend the imahe
        image.save(FileName)
        #Saves the image temporaraly
    for filename in fileNames:
        images.append(imageio.imread(filename))
        #Appends the image name to the list of imahes
    imageio.mimsave(file,images,duration=0.3)
    #From the images in the list, saves the images as a GIF
    for imageNum in range(len(fileNames)):
        os.remove(fileNames[imageNum])
        #Deletes the temporary saves of the images
    

import zipfile #Allows pyhthon to open and read the contents of .zip files
#from skynalyse import skynalyseCore, skynalyseNEO #skynalyse is a custom module that is used to look at images of the night sky with python
#skynalyseCore provides the functionality of getting stars from images, while skynalyseNEO allows Near Earth Objects to be found in images

#tempSavePath = os.path.expanduser(r'~\Desktop')
#tempSavePath = "C:\\Users\\mattd\Desktop\\"
Sizes = [] #Stores the dimensions of each image
ImageLen = 0 #Stores the number of images being analysed
meanOfLen = 0
ImageStars = [] #Stors positions of centres of each star and their radius
Objects = {} #Stores the centre points of each star and if it is a Near Earth Object (NEO)
NearEarthObjects = [] # Stores the Objects values for each image
maxStarDiameter = 10 #Defines the maximum diameter that a star can be on an image
starRemovalModifier = 8 #Value is added to make sure the whole star is removed
checkRadiusModifier = 5 #Defines the upper and lower limits of the radius when stars are checked
checkStarModifier = 20 #Defines the upper and lower limits of the x & y values when satrs are checked
NEOCheckDifference = 5 #Defines the minimum x & y difference that an object is classed as a NEO

#Gets the image file names from the zip file specified in the path
def GetImagesInZip(self,path):
   #Specifies the path of the zip file containing the images
   print("Current Path:",path)
   try:
       os.remove("tempImages.zip")
   except FileNotFoundError:
       pass
   archive = zipfile.ZipFile(path,"r")
   #Opens the zip file at the specified path, setting it to read only
   global FileNames
   FileNames = archive.namelist()
   #Gets a list of the file names within the zip file
   imageNumOutput = str(len(FileNames))+" Images Selected" 
   self.imageSelect.config(text=imageNumOutput)
   status = str(len(FileNames))+" Images Uploaded"
   self.status.config(text=status)
   archive.close()

#Opens the zip file and uses the image files within it (uses next subroutine)
def OpenZip(self,FileNames,path,meanOfLen):
   ImageLen = len(FileNames)
   archive = zipfile.ZipFile(path,"r")
   for imageNum in range(ImageLen):
      Pixels = []
      FileName = FileNames[imageNum]
      #Records the name of the file currently being used
      image = Image.open(archive.open(FileName))
      #Opens the image with the specified file name
      size = image.size
      Sizes.append(size)
      #Records the dimentions of the image
      rgb_image = image.convert('RGB')
      #Converts the image to an RGB image type so the pixel colour values can be read
      skynalyseCore.FindStars(ImageStars,FileName,imageNum,ImageLen,size,Sizes,rgb_image,maxStarDiameter,starRemovalModifier)
      #Gets stars using the FindStars function of skynalyseCore
      status = FileNames[imageNum]+" uploaded"
      print(status)
      self.status.config(text=status)
   archive.close()
   #Closes the zip file as it not longer needs to be accessed
   meanOfLen = skynalyseCore.MeanStarNumber(ImageStars)
   #Calls the GetMeanNumberOfStars subroutine to find the mean number of stars in each image
   global ImageStarsCopy
   ImageStarsCopy = ImageStars[:]
   #Copies ImageStars by splicing, as later subroutines will edit it and an unedited copy is required
   skynalyseNEO.FindNEOs(ImageStars,ImageStarsCopy,checkStarModifier,NEOCheckDifference,checkRadiusModifier,checkStarModifier,meanOfLen,Objects,NearEarthObjects) #Gets NEOs using the FindNEOs function of skynalyseNEO
   print("Done")
   self.status.config(text="Done")
   GetNEOcount(self,meanOfLen)
   global displayImageNum
   displayImageNum = 0
   self.noImageText.pack_forget()
   try:
       self.imageLabel.pack_forget()
   except AttributeError:
       pass
   DisplayImages(self,displayImageNum)

#Works out how many NEO are present in all of the images
def GetNEOcount(self,meanOfLen):
   NEOcount = 0
   checkValue = len(FileNames)-1
   #Sets a values to check for NEO numbers by looking at the last image in the NearEarthObjects list of dictionary Objects
   meanOfLen = skynalyseCore.MeanStarNumber(ImageStarsCopy)
   for star in range(meanOfLen):
      coordinates = str(ImageStarsCopy[checkValue][star][1])
      #Gets each coordinate value, convertng it to a usable string without square brackets
      coordinates = coordinates.lstrip("[").rstrip("]")
      isNEO = NearEarthObjects[checkValue][coordinates]
      #Gets the Trye/False value of if those specific coordinates are a NEO
      if isNEO == True:
         NEOcount+=1
         #If that star is a NEO, the NEOcount is incremented
   if NEOcount == 1:
       results = str(NEOcount)+" Near Earth Object Found"
   else:
       results = str(NEOcount)+" Near Earth Objects Found"
   self.results.config(text=results,fg="red")
   #The final number of NEOs is returned


root = Tk()
#Sets up the root window
GUI = ImageAnalyserGUI(root)
root.wm_title("Near Earth Object Image Analyser")
#Sets the window title
#root.iconbitmap(IconPath)
#Sets the window icon
root.geometry("785x479")
#Sets the side of the window
root.resizable(width=False, height=False)
#Sets it so that the user cannot change the size of the window
root.pack_propagate(0)
#Sets it so that the window size never changes
root.mainloop()
#A loop that keeps the root window open unless closed
