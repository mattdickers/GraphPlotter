import numpy as np
import scipy as sp
import csv
import zipfile
import os

import matplotlib
import matplotlib.pyplot as plt
plt.rc('mathtext', fontset="cm")
matplotlib.use("TkAgg")

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation

from tkinter import ttk
from tkinter.filedialog import *
import tkinter.messagebox
from tkinter.colorchooser import *

f = Figure(figsize=(5, 5), dpi=100)
a = f.add_subplot(111)

global elements
global elementNames
advanced = False
elements = {}
elementNames = []
elementTypes = ["Data", "Plot Equation", "Line", "Text", "Fit Function", "MultiPlot"]

global buttonColours
buttonColours = {"line":(0, 0, 0), "errorBar":(0, 0, 255), "text":(0, 0, 0), "eline":(0, 0, 0), "eqnline":(0, 0, 0)}
lineStylesDict = {"─":"-", "•":".", ".":",", "┄":"--"}

def animateGraph(interval):
    global xs
    global ys
    global xErr
    global yErr
    a.clear()
    if WithErrors.get() == 0:
        try:
            xs, ys = np.genfromtxt(path, delimiter=",", unpack=True)
        except NameError:
            pass
        except OSError:
            try:
                del xs
                del ys
            except NameError:
                pass
    elif WithErrors.get() == 1:
        try:
            xs, ys, xErr, yErr = np.genfromtxt(path, delimiter=",", unpack=True)
        except NameError:
            pass
        except OSError:
            try:
                del xs
                del ys
            except NameError:
                pass

    try:
        if XLog.get() == 1 and YLog.get() == 1:
            a.loglog(xs, ys, lineStylesDict[lineStyle.get()], color=RGBtoFloat(buttonColours["line"]), label=DataLegendEntry.get())
            if WithErrors.get() == 1:
                a.errorbar(xs, ys, xerr=xErr, yerr=yErr, capsize=2, linestyle="none",
                           color=RGBtoFloat(buttonColours["errorBar"]), label=ErrorLegendEntry.get())
        elif XLog.get() == 1:
            a.semilogx(xs, ys, lineStylesDict[lineStyle.get()], color=RGBtoFloat(buttonColours["line"]), label=DataLegendEntry.get())
            if WithErrors.get() == 1:
                a.errorbar(xs, ys, xerr=xErr, yerr=yErr, capsize=2, linestyle="none",
                           color=RGBtoFloat(buttonColours["errorBar"]), label=ErrorLegendEntry.get())
        elif YLog.get() == 1:
            a.semilogy(xs, ys, lineStylesDict[lineStyle.get()], color=RGBtoFloat(buttonColours["line"]),
                       label=DataLegendEntry.get())
            if WithErrors.get() == 1:
                a.errorbar(xs, ys, xerr=xErr, yerr=yErr, capsize=2, linestyle="none",
                           color=RGBtoFloat(buttonColours["errorBar"]), label=ErrorLegendEntry.get())
        else:
            a.plot(xs, ys, lineStylesDict[lineStyle.get()], color=RGBtoFloat(buttonColours["line"]),
                       label=DataLegendEntry.get())
            if WithErrors.get() == 1:
                a.errorbar(xs, ys, xerr=xErr, yerr=yErr, capsize=2, linestyle="none",
                           color=RGBtoFloat(buttonColours["errorBar"]), label=ErrorLegendEntry.get())
    except (UnboundLocalError, NameError):
        pass

    a.set_title(TitleEntry.get())
    a.set(xlabel=xEntry.get(), ylabel=yEntry.get())
    if WithErrors.get() == 1 and ErrorLegend.get() == 1:
        a.legend()

    xLim, yLim = ConvertLimits()
    try:
        if len(xLim) == 2:
            a.set_xlim(xLim)
    except UnboundLocalError:
        pass
    try:
        if len(yLim) == 2:
            a.set_ylim(yLim)
    except UnboundLocalError:
        pass

class GUI:
    def __init__(self, root):

        self.menu = Menu(root)
        root.config(menu=self.menu)
        self.BuildMenu()
        self.menu.add_command(label="Help", command=self.Help)

        self.content = Frame(root)
        self.content.pack(side=TOP)

        self.plotFrame = Frame(self.content, height=500, width=500, bg="white", relief=GROOVE, bd=2)
        self.plotFrame.grid(column=0, row=1, padx=(5,0), sticky=W)

        self.inputFrame = Frame(self.content, height=500, width=250, bg=ColourConvert((240,240,240)))
        self.inputFrame.grid(column=0, row=1, padx=(0,70), sticky=E)

        self.bottomFrame = Frame(self.content, height=5, width=785)
        self.bottomFrame.grid(column=0, row=2)

        # Data Selection:
        self.dataLabel = Label(self.inputFrame, text="Data:")
        self.dataLabel.grid(column=0, row=0, columnspan=2, sticky=W, pady=(0,5))

        self.upload = ttk.Button(self.inputFrame, text="Select Data", command=self.SelectData)
        self.upload.grid(column=0, row=1, columnspan=2, padx=(0,100))

        global WithErrors
        WithErrors = IntVar()
        self.WithErrors = ttk.Checkbutton(self.inputFrame, text="Includes Errors", variable=WithErrors, command=self.errorBarCheck)
        self.WithErrors.grid(column=1, row=1, padx=(100,0))

        self.dataSelect = Label(self.inputFrame, text="No Data")
        self.dataSelect.grid(column=1, row=4)

        # Axes Limits:
        self.dataLabel = Label(self.inputFrame, text="Axes Limits:")
        self.dataLabel.grid(column=0, row=5, columnspan=2, sticky=W, pady=(10,5))

        self.xLimitLabel = Label(self.inputFrame, text="x Limit:")
        self.xLimitLabel.grid(column=0, row=6, columnspan=2, padx=(0,100))

        global xLimit
        xLimit = StringVar()
        self.xLimit = ttk.Entry(self.inputFrame, width=7, textvariable=xLimit)
        self.xLimit.grid(column=1, row=6, columnspan=2, padx=(100,0), sticky=W)

        self.yLimitLabel = Label(self.inputFrame, text="y Limit:")
        self.yLimitLabel.grid(column=0, row=7, columnspan=2, padx=(0, 100), pady=(5,5))

        global yLimit
        yLimit = StringVar()
        self.yLimit = ttk.Entry(self.inputFrame, width=7, textvariable=yLimit)
        self.yLimit.grid(column=1, row=7, columnspan=2, padx=(100, 0), pady=(5,5), sticky=W)

        global XLog
        XLog = IntVar()
        self.xLog = ttk.Checkbutton(self.inputFrame, text="Log x", variable=XLog,)
        self.xLog.grid(column=1, row=6, padx=(150, 0))

        global YLog
        YLog = IntVar()
        self.yLog = ttk.Checkbutton(self.inputFrame, text="Log y", variable=YLog, )
        self.yLog.grid(column=1, row=7, padx=(150, 0))

        # Label Selection:
        self.dataLabel = Label(self.inputFrame, text="Title and Axes Labels:")
        self.dataLabel.grid(column=0, row=8, columnspan=2, sticky=W, pady=(10,5))

        self.titleLabel = Label(self.inputFrame, text="Plot Title:")
        self.titleLabel.grid(column=0, row=9, columnspan=2, padx=(0,100))

        global TitleEntry
        TitleEntry = StringVar()
        self.titleEntry = ttk.Entry(self.inputFrame, width=16, textvariable=TitleEntry)
        self.titleEntry.grid(column=1, row=9, columnspan=2, padx=(100,0), sticky=W)

        self.xLabel = Label(self.inputFrame, text="x Label:")
        self.xLabel.grid(column=0, row=10, columnspan=2, padx=(0, 100), pady=(5,5))

        global xEntry
        xEntry = StringVar()
        self.xEntry = ttk.Entry(self.inputFrame, width=16, textvariable=xEntry)
        self.xEntry.grid(column=1, row=10, columnspan=2, padx=(100, 0), pady=(5,5), sticky=W)

        self.yLabel = Label(self.inputFrame, text="y Label:")
        self.yLabel.grid(column=0, row=11, columnspan=2, padx=(0, 100))

        global yEntry
        yEntry = StringVar()
        self.yEntry = ttk.Entry(self.inputFrame, width=16, textvariable=yEntry)
        self.yEntry.grid(column=1, row=11, columnspan=2, padx=(100, 0), sticky=W)

        # Style Section:
        self.colourSection = Label(self.inputFrame, text="Plot Style:")
        self.colourSection.grid(column=0, row=12, columnspan=2, sticky=W, pady=(10,5))

        self.lineColourLabel = Label(self.inputFrame, text="Line Style:")
        self.lineColourLabel.grid(column=0, row=13, columnspan=2, padx=(0, 100))

        self.lineColourButton = Button(self.inputFrame, width=3, background = ColourConvert(buttonColours["line"]), borderwidth=1, activebackground=ColourConvert(buttonColours["line"]), relief="flat")
        self.lineColourButton.config(command=lambda: self.updateButtonColour(self.lineColourButton, "line", False))
        self.lineColourButton.grid(column=1, row=13, columnspan=2, padx=(100,0),sticky=W)

        global lineStyle
        lineStyle = StringVar()
        lineStyle.set("Select")
        self.drop = ttk.OptionMenu(self.inputFrame, lineStyle, "─", *["─","•",".","┄"])
        self.drop.grid(column=1, row=13, padx=(140,0))

        self.errorColourLabel = Label(self.inputFrame, text="Error Bar Style:", state="disabled")
        self.errorColourLabel.grid(column=0, row=14, columnspan=2, padx=(0, 100), pady=(5,0))

        self.errorColourButton = Button(self.inputFrame, width=3, background = ColourConvert((160,160,160)), borderwidth=1, activebackground=ColourConvert(buttonColours["errorBar"]), relief="flat")
        self.errorColourButton.config(command=lambda: self.updateButtonColour(self.errorColourButton, "errorBar", False))
        self.errorColourButton.grid(column=1, row=14, columnspan=2, padx=(100,0), sticky=W, pady=(5,0))

        global ErrorLegend
        ErrorLegend = IntVar()
        self.errorLegend = ttk.Checkbutton(self.inputFrame, text="Legend", variable=ErrorLegend, state="disabled", command=self.legendCheck)
        self.errorLegend.grid(column=1, row=14, padx=(140,0), pady=(5,0))

        self.DataLegendLabel = Label(self.inputFrame, text="Data Legend:", state="disabled")
        self.DataLegendLabel.grid(column=0, row=15, columnspan=2, padx=(0, 100))

        global DataLegendEntry
        DataLegendEntry = StringVar()
        self.DataLegendEntry = ttk.Entry(self.inputFrame, width=16, textvariable=DataLegendEntry, state="disabled")
        self.DataLegendEntry.grid(column=1, row=15, columnspan=2, padx=(100, 0), pady=(5,5), sticky=W)

        self.ErrorLegendLabel = Label(self.inputFrame, text="Error Legend:", state="disabled")
        self.ErrorLegendLabel.grid(column=0, row=16, columnspan=2, padx=(0, 100))

        global ErrorLegendEntry
        ErrorLegendEntry = StringVar()
        self.ErrorLegendEntry = ttk.Entry(self.inputFrame, width=16, textvariable=ErrorLegendEntry, state="disabled")
        self.ErrorLegendEntry.grid(column=1, row=16, columnspan=2, padx=(100, 0), sticky=W)

        # Bottom Buttons
        self.advancedButton = ttk.Button(self.inputFrame, text="Show Advanced Settings", command=self.Advanced, width=21.5)
        self.advancedButton.grid(column=1, row=17, pady=(15,0))
        self.advancedButton.config(width=21.5)

        self.savePlotButton = ttk.Button(self.inputFrame, text="Save Plot", command=self.Save)
        self.savePlotButton.grid(column=1, row=18, pady=(5,0))

        # Plot:
        canvas = FigureCanvasTkAgg(f, self.plotFrame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=True)

        self.elementUIload = {"Data":self.elementData, "Plot Equation":self.elementEquation,
                              "Line":self.elementLine, "Text":self.elementText, "Fit Function":self.elementFuncFit, "MultiPlot":self.elementMulti}

    def New(self):
        global path
        answer = tkinter.messagebox.askquestion("Do you want to close current graph?",
                                                "Are you sure you want to close the current graph? Any graphs will not be saved.")
        if answer == "yes":
            self.ResetLabels()
            self.ResetLimits()
            self.ResetColours()
            self.ResetLegend()
            self.ResetElements()
            ErrorLegend.set(0)
            self.legendCheck()
            path = ""
            WithErrors.set(0)
            self.errorBarCheck()
            self.dataSelect.config(text="No Data")
            self.upload.config(state="normal")
            self.WithErrors.config(state="normal")
            self.fileMenu.entryconfig(1, state="normal")
            lineStyle.set("─")

    def SelectData(self):
        file = askopenfilename(title="Select Images",filetypes=(("CSV files","*.csv"),("All files","*")))
        if ".csv" not in file:
            tkinter.messagebox.showerror("File Error",
                                         "Incorrect file type. Please use a CSV file.")
        else:
            F = open(file)
            read = csv.reader(F, delimiter=",")
            columns = len(next(read))
            F.close()
            if (WithErrors.get() == 0 and columns == 2) or (WithErrors.get() == 1 and columns == 4):
                global path
                path = file
                for charNum, char in enumerate(path[::-1]):
                    if char == "/":
                        file = path[len(path)-charNum:]
                        break
                self.dataSelect.config(text=file)
                self.upload.config(state="disabled")
                self.WithErrors.config(state="disabled")
                self.fileMenu.entryconfig(1, state="disabled")
            else:
                if WithErrors.get() == 0 and columns == 4:
                    tkinter.messagebox.showerror("File Error",
                                                "Too many columns in data. Please use data without errors in this mode.")
                elif WithErrors.get() == 1 and columns == 2:
                    tkinter.messagebox.showerror("File Error",
                                                 "Too few columns in data. Please use data with errors in this mode.")
                else:
                    tkinter.messagebox.showerror("File Error",
                                                 "Incorrect number of columns in data. Please use either 2 or 4 columns depending on the error mode.")

    def Save(self):
        try:
            filePath = asksaveasfilename(title="Save Graph", filetypes=(("PNG and SVG", "*.png"), ("All files", "*")))
            if filePath !="":
                pngFile = filePath + ".png"
                svgFile = filePath + ".svg"

                plt.cla()
                if XLog.get() == 1 and YLog.get() == 1:
                    plt.loglog(xs, ys, lineStylesDict[lineStyle.get()], color=RGBtoFloat(buttonColours["line"]),
                             label=DataLegendEntry.get())
                    if WithErrors.get() == 1:
                        plt.errorbar(xs, ys, xerr=xErr, yerr=yErr, capsize=2, linestyle="none",
                                   color=RGBtoFloat(buttonColours["errorBar"]), label=ErrorLegendEntry.get())
                elif XLog.get() == 1:
                    plt.semilogx(xs, ys, lineStylesDict[lineStyle.get()], color=RGBtoFloat(buttonColours["line"]),
                               label=DataLegendEntry.get())
                    if WithErrors.get() == 1:
                        plt.errorbar(xs, ys, xerr=xErr, yerr=yErr, capsize=2, linestyle="none",
                                   color=RGBtoFloat(buttonColours["errorBar"]), label=ErrorLegendEntry.get())
                elif YLog.get() == 1:
                    plt.semilogy(xs, ys, lineStylesDict[lineStyle.get()], color=RGBtoFloat(buttonColours["line"]),
                               label=DataLegendEntry.get())
                    if WithErrors.get() == 1:
                        plt.errorbar(xs, ys, xerr=xErr, yerr=yErr, capsize=2, linestyle="none",
                                   color=RGBtoFloat(buttonColours["errorBar"]), label=ErrorLegendEntry.get())
                else:
                    plt.plot(xs, ys, lineStylesDict[lineStyle.get()], color=RGBtoFloat(buttonColours["line"]),
                           label=DataLegendEntry.get())
                    if WithErrors.get() == 1:
                        plt.errorbar(xs, ys, xerr=xErr, yerr=yErr, capsize=2, linestyle="none",
                                   color=RGBtoFloat(buttonColours["errorBar"]), label=ErrorLegendEntry.get())
                plt.title(TitleEntry.get())
                plt.xlabel(xEntry.get())
                plt.ylabel(yEntry.get())
                xLim, yLim = ConvertLimits()
                if len(xLim) == 2:
                    plt.xlim(xLim[0], xLim[1])
                if len(yLim) == 2:
                    plt.ylim(yLim[0], yLim[1])
                if WithErrors.get() == 1 and ErrorLegend.get() == 1:
                    plt.legend()

                zip = zipfile.ZipFile(pngFile.replace(".png", "")+".zip", mode='w')
                plt.savefig(pngFile)
                plt.savefig(svgFile)
                zip.write(pngFile, os.path.basename(pngFile))
                zip.write(svgFile, os.path.basename(svgFile))
                os.remove(pngFile)
                os.remove(svgFile)
                tkinter.messagebox.showinfo("Graph Saved", "The graph was successfully saved.")
                zip.close()
            else:
                tkinter.messagebox.showerror("Save Error",
                                             "There is no file name. Please provide a file name and try again.")
        except NameError:
            tkinter.messagebox.showerror("Save Error",
                                         "No graph has been plotted. Please plot a graph and try again.")

    def ResetLabels(self):
        self.titleEntry.delete(0, END)
        self.xEntry.delete(0, END)
        self.yEntry.delete(0, END)

    def ResetLimits(self):
        self.xLimit.delete(0, END)
        self.yLimit.delete(0, END)

    def ResetColours(self):
        buttonColours["line"] = (0, 0, 0)
        buttonColours["errorBar"] = (0, 0, 255)
        self.lineColourButton.config(background=ColourConvert(buttonColours["line"]),
                                     activebackground=ColourConvert(buttonColours["line"]))
        if WithErrors.get() == 0:
            self.errorColourButton.config(state="disabled", background=ColourConvert((160,160,160)))
        elif WithErrors.get() == 1:
            self.errorColourButton.config(background=ColourConvert(buttonColours["errorBar"]),
                                          activebackground=ColourConvert(buttonColours["errorBar"]))

    def ResetLegend(self):
        self.DataLegendEntry.delete(0, END)
        self.ErrorLegendEntry.delete(0, END)

    def ResetElements(self):
        try:
            for element in elementNames:
                print(element)
                del elements[element]
            elementNames.clear()
            self.updateDropdownList()
            self.ElementNum.config(text=str(len(elementNames)) + " Plot Elements")
        except AttributeError:
            pass

    def Help(self):
        instructionsWindow = Toplevel()
        instructionsWindow.title("Help")
        instructionsWindow.geometry("217x160")
        instructionsWindow.resizable(width=False, height=False)

        selectInfo = Label(instructionsWindow,text="\nIncludes Errors:\nDefines if the CSV file has error bar data.\nIf so, must be in 3rd and 4th columns.")
        selectInfo.grid(column=0, row=0)

        circleInfo = Label(instructionsWindow,text="\nx and y Limits:\nMust be of the form 'x1,x2' or 'y1,y2'.")
        circleInfo.grid(column=0, row=1)

        closeButton = ttk.Button(instructionsWindow, text="Close", command=instructionsWindow.destroy)
        closeButton.grid(column=0, row=2, pady=(10,0))

    def Exit(self):
        answer = tkinter.messagebox.askquestion("Do you want to exit?","Are you sure you want to exit? Any graphs will not be saved.")
        if answer == "yes":
            root.quit()

    def Advanced(self):
        global advanced
        global variable
        if advanced == False:
            advanced = True
            root.geometry("1135x505")
            self.advancedButton.config(text="Hide Advanced Settings", width=21.5)
            self.advancedFrame = Frame(self.content, height=200, width=287, bg="red", background=ColourConvert((240,0,0)))
            self.elementFrame = Frame(self.content, height=200, width=287, background=ColourConvert((0,240,0)))
            self.advancedFrame.grid(column=1, row=1, padx=(0, 70), pady=(0,405), sticky=W)
            self.elementFrame.grid(column=1, row=1, padx=(0, 70), pady=(85,0), sticky=N)

            self.ElementsTitle = Label(self.advancedFrame, text="Select Plot Element:")
            self.ElementsTitle.grid(column=0, row=0, columnspan=2, sticky=W, pady=(0, 5))

            self.ElementNum = Label(self.advancedFrame, text=str(len(elementNames)) + " Plot Elements")
            self.ElementNum.grid(column=0, row=2, columnspan=3)

            self.selectedElement = StringVar(self.advancedFrame)
            self.selectedElement.set("Select Element")
            self.ElementsDropdown = ttk.OptionMenu(self.advancedFrame, self.selectedElement, "Select Element", *elementNames, command=self.getDropdownSelectUpdate)
            self.ElementsDropdown.grid(column=0, row=1)
            self.ElementsDropdown.config(width=17)

            self.ElementAdd = ttk.Button(self.advancedFrame, text="Add", command=self.createPlotElement)
            self.ElementAdd.grid(column=1, row=1)

            self.ElementRemove = ttk.Button(self.advancedFrame, text="Remove", command=self.removePlotElement)
            self.ElementRemove.grid(column=2, row=1)

            self.statsFrame = Frame(self.content, height=100, width = 250, background=ColourConvert((240,240,240)))
            self.statsFrame.grid(column=1, row=1, padx=(0, 70), pady=(300, 0), sticky=W)

            self.statsLabel = Label(self.statsFrame, text="Plot Statistics:")
            self.statsLabel.grid(column=0, row=0, columnspan=2, sticky=W, pady=(10, 5), padx=(0, 210))

            self.xMeanLabel = Label(self.statsFrame, text="x Axis Mean:")
            self.xMeanLabel.grid(column=0, row=1)

            #TODO: add the correct formatting for this section^

            self.xMean = Label(self.statsFrame, text="No Data")
            self.xMean.grid(column=1, row=1)

        else:
            advanced = False
            root.geometry("735x505")
            self.advancedButton.config(text="Show Advanced Settings", width=21.5)
            self.advancedFrame.grid_forget()
            self.elementFrame.grid_forget()
            self.statsFrame.grid_forget()

        if self.selectedElement.get() == "Select Element":
            self.noElements = Label(self.elementFrame, text="No Plot Element Selected")
            self.noElements.grid(column=0, row=0, pady=(150,0))

    def updateDropdownList(self):
        menu = self.ElementsDropdown["menu"]
        menu.delete(0, "end")
        for string in elementNames:
            menu.add_command(label=string,
                             command=tkinter._setit(self.selectedElement, string, self.getDropdownSelectUpdate))

    def createPlotElement(self):
        self.clearElementFrame()
        self.elementFrame.grid_configure(pady=(85, 0))

        # New Element:
        self.newElementLabel = Label(self.elementFrame, text="Create New Plot Element:")
        self.newElementLabel.grid(column=0, row=0, columnspan=2, sticky=W, pady=(10, 5), padx=(0, 147))

        self.elementNameLabel = Label(self.elementFrame, text="Element Name:")
        self.elementNameLabel.grid(column=0, row=2, columnspan=2, padx=(0, 150))

        global elementName
        elementName = StringVar()
        self.elementName = ttk.Entry(self.elementFrame, width=16, textvariable=elementName)
        self.elementName.grid(column=1, row=2, columnspan=2, padx=(0, 0), sticky=W)

        self.elementTypeLaabel = Label(self.elementFrame, text="Element Type:")
        self.elementTypeLaabel.grid(column=0, row=3, columnspan=2, padx=(0, 150), pady=(5, 5))

        global elementType
        elementType = StringVar(self.elementFrame)
        elementType.set("Select")
        self.elementType = ttk.OptionMenu(self.elementFrame, elementType, "Element Type", *elementTypes)
        self.elementType.grid(column=1, row=3, columnspan=2, padx=(0, 0), pady=(5, 5), sticky=W)
        self.elementType.config(width=11.5)

        self.addElementButton = ttk.Button(self.elementFrame, text="Add Element", command=self.addPlotElement)
        self.addElementButton.grid(column=0, row=4, columnspan=3)

    def addPlotElement(self):
        if elementName.get() == "" and elementType.get() == "Element Type":
            tkinter.messagebox.showerror("Element Error",
                                         "Please specify an element name and type.")
        elif elementName.get() == "":
            tkinter.messagebox.showerror("Element Error",
                                         "Please Specify an element name.")
        elif elementType.get() == "Element Type":
            tkinter.messagebox.showerror("Element Error",
                                         "Please specify an element type.")
        elif elementName.get() in elementNames:
            tkinter.messagebox.showerror("Element Error",
                                         "An element with this name already exists.")
        else:
            element = PlotElement(root, elementName.get(), elementType.get())
            elementNames.append(element.name)
            self.newElementName = element.name
            elements[element.name] = element
            self.updateDropdownList()
            self.ElementNum.config(text=str(len(elementNames)) + " Plot Elements")
            self.selectedElement.set(element.name)
            self.displayElementEdit()

    def clearElementFrame(self):
        for widget in self.elementFrame.winfo_children():
            widget.destroy()

    def removePlotElement(self):
        if len(elementNames) == 0:
            tkinter.messagebox.showerror("Element Error",
                                         "There no elements to remove.")
        elif self.selectedElement.get() == "Select Plot Element":
            tkinter.messagebox.showerror("Element Error",
                                         "No element selected.")
        else:
            answer = tkinter.messagebox.askquestion("Do you want to remove the selected element?",
                                                    "Are you sure you want to remove the selected element?")
            if answer == "yes":
                elementNames.remove(self.selectedElement.get())
                del elements[self.selectedElement.get()]
                self.updateDropdownList()
                self.ElementNum.config(text=str(len(elementNames)) + " Plot Elements")

    def getDropdownSelectUpdate(self, variable):
        self.displayElementEdit()

    def displayElementEdit(self):
        self.clearElementFrame()
        element = elements[self.selectedElement.get()]
        self.elementUIload[element.type]()

    def lineElementEntryUpdate(self, value):
        if value == "Horizontal":
            self.lineXLabel.config(state="active")
            self.lineXstart.config(state="active")
            self.lineXend.config(state="active")
            self.lineYLabel.config(state="disabled")
            self.lineYstart.config(state="disabled")
            self.lineYend.config(state="disabled")
        elif value == "Vertical":
            self.lineXLabel.config(state="disabled")
            self.lineXstart.config(state="disabled")
            self.lineXend.config(state="disabled")
            self.lineYLabel.config(state="active")
            self.lineYstart.config(state="active")
            self.lineYend.config(state="active")
        elif value == "Points":
            self.lineYLabel.config(state="active")
            self.lineYstart.config(state="active")
            self.lineYend.config(state="active")
            self.lineXLabel.config(state="active")
            self.lineXstart.config(state="active")
            self.lineXend.config(state="active")

    def basicElementOutline(self, elementName):
        self.elementLabel = Label(self.elementFrame, text=elementName+str(":"))
        self.elementLabel.grid(column=0, row=0, columnspan=2, sticky=W, pady=(10, 5), padx=(0, 205))

        hidden = IntVar()
        self.hidden = ttk.Checkbutton(self.elementFrame, text="Hidden", variable=hidden)
        self.hidden.grid(column=1, row=0, pady=(5, 5))

        self.elementName = Label(self.elementFrame, text="Name:")
        self.elementName.grid(column=0, row=1, pady=(0, 5))

        self.elementNameText = Label(self.elementFrame, text=self.selectedElement.get())
        self.elementNameText.grid(column=1, row=1, pady=(0, 5))

        self.elementLabelLineX = Label(self.elementFrame, text="x Position:")
        self.elementLabelLineX.grid(column=0, row=2, columnspan=2, padx=(0, 150), pady=(0, 5))

        global elementX
        elementX = StringVar()
        self.elementEntryX = ttk.Entry(self.elementFrame, width=16, textvariable=elementX)
        self.elementEntryX.grid(column=1, row=2, pady=(0, 5))

        self.elementLabelY = Label(self.elementFrame, text="y Position:")
        self.elementLabelY.grid(column=0, row=3, columnspan=2, padx=(0, 150), pady=(0, 5))

        global elementY
        elementY = StringVar()
        self.elementEntryY = ttk.Entry(self.elementFrame, width=16, textvariable=elementY)
        self.elementEntryY.grid(column=1, row=3, pady=(0, 5))


    def elementData(self):
        self.basicElementOutline("Data Element")

    def elementEquation(self):
        self.basicElementOutline("Equation Element")

        self.elementEqnLabel = Label(self.elementFrame, text="Equation:")
        self.elementEqnLabel.grid(column=0, row=4, pady=(0, 5))

        global eqn
        eqn = StringVar(value="y=")
        self.elementEqn = ttk.Entry(self.elementFrame, width=16, textvariable=eqn)
        self.elementEqn.grid(column=1, row=4, pady=(0, 5))

        self.fill = Label(self.elementFrame, text="")
        self.fill.grid(column=0, row=5, pady=(0 ,5))

        self.fill = Label(self.elementFrame, text="")
        self.fill.grid(column=0, row=6, pady=(0, 5))

        self.fill = Label(self.elementFrame, text="")
        self.fill.grid(column=0, row=7, pady=(0, 5))

        self.eqnLineStyelLabel = Label(self.elementFrame, text="Line Style:")
        self.eqnLineStyelLabel.grid(column=0, row=8, pady=(0, 5))

        self.eqnLineColour = Button(self.elementFrame, width=3, background=ColourConvert(buttonColours["eqnline"]),
                                        borderwidth=1, activebackground=ColourConvert(buttonColours["eqnline"]),
                                        relief="flat")
        self.eqnLineColour.config(command=lambda: self.updateButtonColour(self.elementLineColour, "eqnline", False))
        self.eqnLineColour.grid(column=1, row=8, pady=(0, 5), sticky=W, padx=(27, 0))

        global eqnlineStyle
        eqnlineStyle = StringVar()
        eqnlineStyle.set("Select")
        self.eqnLineDrop = ttk.OptionMenu(self.elementFrame, eqnlineStyle, "─", *["─","•",".","┄"])
        self.eqnLineDrop.grid(column=1, row=8, padx=(60, 0), pady=(0, 5))

    def elementLine(self):
        self.basicElementOutline("Line Element")

        self.elementLineTypeLabel = Label(self.elementFrame, text="Line Type:")
        self.elementLineTypeLabel.grid(column=0, row=4, pady=(0, 5))

        global lineType
        lineType = StringVar(value="Select")
        lineType.set("Select")
        self.lineTypeDrop = ttk.OptionMenu(self.elementFrame, lineType, "Select Type",
                                            *["Horizontal", "Vertical", "Points"], command=self.lineElementEntryUpdate)
        self.lineTypeDrop.grid(column=1, row=4, pady=(0, 5))

        self.lineXLabel = Label(self.elementFrame, text="x Start/End Points:", state="disabled")
        self.lineXLabel.grid(column=0, row=5, pady=(0, 5))

        global startX
        startX = StringVar()
        self.lineXstart = ttk.Entry(self.elementFrame, width=7, textvariable=startX, state="disabled")
        self.lineXstart.grid(column=1, row=5, pady=(0, 5), padx=(0,55))

        global endX
        endX = StringVar()
        self.lineXend = ttk.Entry(self.elementFrame, width=7, textvariable=endX, state="disabled")
        self.lineXend.grid(column=1, row=5, pady=(0, 5), padx=(55, 0))

        self.lineYLabel = Label(self.elementFrame, text="y Start/End Points:", state="disabled")
        self.lineYLabel.grid(column=0, row=6, pady=(0, 5))

        global startY
        startY = StringVar()
        self.lineYstart = ttk.Entry(self.elementFrame, width=7, textvariable=startY, state="disabled")
        self.lineYstart.grid(column=1, row=6, pady=(0, 5), padx=(0, 55))

        global endY
        endY = StringVar()
        self.lineYend = ttk.Entry(self.elementFrame, width=7, textvariable=endY, state="disabled")
        self.lineYend.grid(column=1, row=6, pady=(0, 5), padx=(55, 0))

        self.lineStyelLabel = Label(self.elementFrame, text="Line Style:")
        self.lineStyelLabel.grid(column=0, row=7, pady=(0, 5))

        self.elementLineColour = Button(self.elementFrame, width=3, background=ColourConvert(buttonColours["eline"]),
                                        borderwidth=1, activebackground=ColourConvert(buttonColours["eline"]),
                                        relief="flat")
        self.elementLineColour.config(command=lambda: self.updateButtonColour(self.elementLineColour, "eline", False))
        self.elementLineColour.grid(column=1, row=7, pady=(0, 5), sticky=W, padx=(27, 0))

        global elineStyle
        elineStyle = StringVar()
        elineStyle.set("Select")
        self.lineDrop = ttk.OptionMenu(self.elementFrame, elineStyle, "─", *["─", "┄"])
        self.lineDrop.grid(column=1, row=7, padx=(60, 0), pady=(0, 5))


    def elementText(self):
        self.basicElementOutline("Text Element")

        self.elementTextLabel = Label(self.elementFrame, text="Text:")
        self.elementTextLabel.grid(column=0, row=4, pady=(0, 5))

        global text
        text = StringVar()
        self.elementText = ttk.Entry(self.elementFrame, width=16, textvariable=text)
        self.elementText.grid(column=1, row=4, pady=(0, 5))

        self.elementTextColourLabel = Label(self.elementFrame, text="Text Style:")
        self.elementTextColourLabel.grid(column=0, row=5, pady=(0, 5))

        self.elementTextColour = Button(self.elementFrame, width=3, background=ColourConvert(buttonColours["text"]),
                                       borderwidth=1, activebackground=ColourConvert(buttonColours["text"]),
                                       relief="flat")
        self.elementTextColour.config(command=lambda: self.updateButtonColour(self.elementTextColour, "text", False))
        self.elementTextColour.grid(column=1, row=5, pady=(0,5), sticky=W, padx=(27, 0))
        #TODO update to to True when element check implimented

        global textStyle
        textStyle = StringVar()
        textStyle.set("Select")
        self.textStyleDrop = ttk.OptionMenu(self.elementFrame, textStyle, "Normal", *["Normal", "Bold", "Italic", "Underline"])
        self.textStyleDrop.grid(column=1, row=5, pady=(0, 5), sticky=W, columnspan=2, padx=(60, 0))

        self.elementTextSizeLabel = Label(self.elementFrame, text="Text Size:")
        self.elementTextSizeLabel.grid(column=0, row=6, pady=(0, 5))

        global TextSize
        TextSize = StringVar(value="12")
        self.elementTextSize = ttk.Entry(self.elementFrame, width=16, textvariable=TextSize)
        self.elementTextSize.grid(column=1, row=6, pady=(0, 5))

    def elementFuncFit(self):
        self.elementLabel = Label(self.elementFrame, text="Function Fit:")
        self.elementLabel.grid(column=0, row=0, columnspan=2, sticky=W, pady=(0, 75), padx=(0, 210))

    def elementMulti(self):
        self.elementLabel = Label(self.elementFrame, text="MultiPlot:")
        self.elementLabel.grid(column=0, row=0, columnspan=2, sticky=W, pady=(0, 75), padx=(0, 215))


    def updateButtonColour(self, button, function, isElement):
        if not isElement:
            colour = buttonColours[function]
            prev = colour
            try:
                colour = GetColour()
                button.config(background=ColourConvert(colour),
                                             activebackground=ColourConvert(colour))
                buttonColours[function] = colour
            except TypeError:
                colour = prev
                button.config(background=ColourConvert(colour),
                                             activebackground=ColourConvert(colour))
        else:
            pass
        #TODO if is element, set colour to the colour defined in the element object, and save for that

    def errorBarCheck(self):
        if WithErrors.get() == 0:
            self.errorColourLabel.config(state="disabled")
            self.errorColourButton.config(state="disabled", background=ColourConvert((160,160,160)))
            self.errorLegend.config(state="disabled")
        elif WithErrors.get() == 1:
            self.errorColourLabel.config(state="normal")
            self.errorColourButton.config(state="normal", background=ColourConvert(buttonColours["errorBar"]))
            self.errorLegend.config(state="normal")
        self.legendCheck()

    def legendCheck(self):
        if WithErrors.get() == 1:
            if ErrorLegend.get() == 0:
                self.DataLegendLabel.config(state="disabled")
                self.DataLegendEntry.config(state="disabled")
                self.ErrorLegendLabel.config(state="disabled")
                self.ErrorLegendEntry.config(state="disabled")
            elif ErrorLegend.get() == 1:
                self.DataLegendLabel.config(state="normal")
                self.DataLegendEntry.config(state="normal")
                self.ErrorLegendLabel.config(state="normal")
                self.ErrorLegendEntry.config(state="normal")
        else:
            self.DataLegendLabel.config(state="disabled")
            self.DataLegendEntry.config(state="disabled")
            self.ErrorLegendLabel.config(state="disabled")
            self.ErrorLegendEntry.config(state="disabled")

    def BuildMenu(self):
        self.fileMenu = Menu(self.menu,tearoff=False)
        self.fileMenu.add_command(label="New",command=self.New)
        self.fileMenu.add_command(label="Select Data",command=self.SelectData)
        self.fileMenu.add_command(label="Save Plot", command=self.Save)
        self.menu.add_cascade(label="File",menu=self.fileMenu)

        self.fileMenu.add_separator()
        self.fileMenu.add_command(label="Exit",command=self.Exit)

        self.PlotMenu = Menu(self.menu,tearoff=False)
        self.PlotMenu.add_command(label="Reset Labels", command=self.ResetLabels)
        self.PlotMenu.add_command(label="Reset Limits",command=self.ResetLimits)
        self.PlotMenu.add_command(label="Reset Colours", command=self.ResetColours)
        self.PlotMenu.add_command(label="Reset Legend", command=self.ResetLegend)
        self.PlotMenu.add_command(label="Reset Elements", command=self.ResetElements)
        self.menu.add_cascade(label="Plot",menu=self.PlotMenu)

class PlotElement:
    def __init__(self, root, name, type):
        self.name = name
        self.type = type
        self.hidden = False
        self.colour = (0,0,0)
        self.xPos = None
        self.yPos = None
        #TODO check for the element type, and then store the contents of each element data piece, such as equation, lenght of line etc.


def ColourConvert(rgb):
    return "#%02x%02x%02x" % (int(rgb[0]), int(rgb[1]), int(rgb[2]))

def RGBtoFloat(rgb):
    return (int(rgb[0])/255, int(rgb[1])/255, int(rgb[2])/255)

def GetColour():
    colour = askcolor()
    return colour[0]

def ConvertLimits():
    xLim = []
    yLim = []
    try:
        xLim = [int(val.strip()) for val in xLimit.get().split(",")]
    except ValueError:
        pass
    try:
        yLim = [int(val.strip()) for val in yLimit.get().split(",")]
    except ValueError:
        pass
    return xLim, yLim

root = Tk()

GUI = GUI(root)
ani = animation.FuncAnimation(f, animateGraph, interval=100)

root.wm_title("Graph Plotter")
#root.iconbitmap(IconPath)

root.geometry("735x505")

root.resizable(width=False, height=False)

root.pack_propagate(0)
root.grid_propagate(0)

root.update()

root.mainloop()
