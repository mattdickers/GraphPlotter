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

from tkinter import *
from tkinter import ttk
from tkinter.filedialog import *
import tkinter.messagebox
from tkinter.colorchooser import *

f = Figure(figsize=(5, 5), dpi=100)
a = f.add_subplot(111)

global elements
global OPTIONS
advanced = False
elements = []
OPTIONS = []

lineColour = (0, 0, 0)
errorColour = (0, 0, 255)
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
        a.plot(xs, ys, lineStylesDict[lineStyle.get()], color=RGBtoFloat(lineColour), label=DataLegendEntry.get())
        if WithErrors.get() == 1:
            a.errorbar(xs, ys, xerr=xErr, yerr=yErr, capsize=2, linestyle="none",
                       color=RGBtoFloat(errorColour), label=ErrorLegendEntry.get())
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
        self.xLimit = ttk.Entry(self.inputFrame, width=16, textvariable=xLimit)
        self.xLimit.grid(column=1, row=6, columnspan=2, padx=(100,0), sticky=W)

        self.yLimitLabel = Label(self.inputFrame, text="y Limit:")
        self.yLimitLabel.grid(column=0, row=7, columnspan=2, padx=(0, 100), pady=(5,5))

        global yLimit
        yLimit = StringVar()
        self.yLimit = ttk.Entry(self.inputFrame, width=16, textvariable=yLimit)
        self.yLimit.grid(column=1, row=7, columnspan=2, padx=(100, 0), pady=(5,5), sticky=W)

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

        self.lineColourButton = Button(self.inputFrame, width=3, background = ColourConvert(lineColour), borderwidth=1, activebackground=ColourConvert(lineColour), relief="flat",
                                       command=self.updateLineButtonColour)
        self.lineColourButton.grid(column=1, row=13, columnspan=2, padx=(100,0),sticky=W)

        global lineStyle
        lineStyle = StringVar()
        lineStyle.set("Select")
        self.drop = ttk.OptionMenu(self.inputFrame, lineStyle, "─", *["─","•",".","┄"])
        self.drop.grid(column=1, row=13, padx=(140,0))

        self.errorColourLabel = Label(self.inputFrame, text="Error Bar Style:", state="disabled")
        self.errorColourLabel.grid(column=0, row=14, columnspan=2, padx=(0, 100), pady=(5,0))

        self.errorColourButton = Button(self.inputFrame, width=3, background = ColourConvert((160,160,160)), borderwidth=1, activebackground=ColourConvert(errorColour), relief="flat",
                                        command=self.updateErrorButtonColour, state="disabled")
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
        self.advancedButton = ttk.Button(self.inputFrame, text="Show Advanced Settings", command=self.Advanced, state="disabled")
        self.advancedButton.grid(column=1, row=17, pady=(15,0))

        self.savePlotButton = ttk.Button(self.inputFrame, text="Save Plot", command=self.Save)
        self.savePlotButton.grid(column=1, row=18, pady=(5,0))

        # Plot:
        canvas = FigureCanvasTkAgg(f, self.plotFrame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=True)

    def New(self):
        global path
        answer = tkinter.messagebox.askquestion("Do you want to close current graph?",
                                                "Are you sure you want to close the current graph? Any graphs will not be saved.")
        if answer == "yes":
            self.ResetLabels()
            self.ResetLimits()
            self.ResetColours()
            self.ResetLegend()
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
            xs
            filePath = asksaveasfilename(title="Save Graph", filetypes=(("PNG and SVG", "*.png"), ("All files", "*")))
            pngFile = filePath + ".png"
            svgFile = filePath + ".svg"

            plt.cla()
            plt.plot(xs, ys, lineStylesDict[lineStyle.get()], color=RGBtoFloat(lineColour), label=DataLegendEntry.get())
            if WithErrors.get() == 1:
                plt.errorbar(xs, ys, xerr=xErr, yerr=yErr, capsize=2, linestyle="none",
                           color=RGBtoFloat(errorColour), label=ErrorLegendEntry.get())
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
        global lineColour
        global errorColour
        lineColour = (0, 0, 0)
        errorColour = (0, 0, 255)
        self.lineColourButton.config(background=ColourConvert(lineColour), activebackground=ColourConvert(lineColour))
        if WithErrors.get() == 0:
            self.errorColourButton.config(state="disabled", background=ColourConvert((160,160,160)))
        elif WithErrors.get() == 1:
            self.errorColourButton.config(background=ColourConvert(errorColour), activebackground=ColourConvert(errorColour))

    def ResetLegend(self):
        self.DataLegendEntry.delete(0, END)
        self.ErrorLegendEntry.delete(0, END)

    def Help(self):
        instructionsWindow = Toplevel()
        instructionsWindow.title("Help")
        instructionsWindow.geometry("217x160")
        instructionsWindow.resizable(width=False, height=False)

        selectInfo = Label(instructionsWindow,text="\nIncludes Errors:\nDefines if the CSV file has error bar data.\nIf so, must be in 3rd and 4th columns.")
        selectInfo.grid(column=0, row=0)

        circleInfo = Label(instructionsWindow,text="\nx and y Limis:\nMust be of the form 'x1,x2' or 'y1,y2'.")
        circleInfo.grid(column=0, row=1)

        closeButton = ttk.Button(instructionsWindow, text="Close", command=instructionsWindow.destroy)
        closeButton.grid(column=0, row=2, pady=(10,0))

    def Exit(self):
        answer = tkinter.messagebox.askquestion("Do you want to exit?","Are you sure you want to exit? Any graphs will not be saved.")
        if answer == "yes":
            root.quit()

    def Advanced(self):
        global advanced
        if advanced == False:
            advanced = True
            root.geometry("1135x505")
            self.advancedButton.config(text="Hide Advanced Settings")
            self.advancedFrame = Frame(self.content, height=500, width=250, bg="red", background=ColourConvert((240,240,240)))
            #TODO add advanced settings title in centre
            self.advancedFrame.grid(column=1, row=1, padx=(0, 70), sticky=E)

            self.ElementsTitle = Label(self.advancedFrame, text="Select Plot Element:")
            self.ElementsTitle.grid(column=0, row=0, columnspan=2, sticky=W, pady=(0, 5))

            variable = StringVar(self.advancedFrame)
            variable.set("Select")
            self.ElemetsDropdown = ttk.OptionMenu(self.advancedFrame, variable, "Select Plot Element", *OPTIONS)
            self.ElemetsDropdown.grid(column=0, row=1)

            self.ElementAdd = ttk.Button(self.advancedFrame, text="Add", command=self.addPlotElement)
            self.ElementAdd.grid(column=1, row=1)

            self.ElementRemove = ttk.Button(self.advancedFrame, text="Remove")
            self.ElementRemove.grid(column=2, row=1)
        else:
            advanced = False
            root.geometry("735x505")
            self.advancedButton.config(text="Show Advanced Settings")
            self.advancedFrame.grid_forget()

            #TODO make the OPTIONS list update without requiring advanced button press

    def addPlotElement(self):
        import random
        elements.append(PlotElement(root, str(random.randint(0,100)), "ooh"))
        for element in elements:
            OPTIONS.append(element.name)

    def updateLineButtonColour(self):
        global lineColour
        prev = lineColour
        try:
            lineColour = GetColour()
            self.lineColourButton.config(background=ColourConvert(lineColour), activebackground=ColourConvert(lineColour))
        except TypeError:
            lineColour = prev
            self.lineColourButton.config(background=ColourConvert(lineColour), activebackground=ColourConvert(lineColour))

    def updateErrorButtonColour(self):
        global errorColour
        prev = errorColour
        try:
            errorColour = GetColour()
            self.errorColourButton.config(background=ColourConvert(errorColour), activebackground=ColourConvert(errorColour))
        except TypeError:
            errorColour = prev
            self.errorColourButton.config(background=ColourConvert(errorColour), activebackground=ColourConvert(errorColour))

    def errorBarCheck(self):
        if WithErrors.get() == 0:
            self.errorColourLabel.config(state="disabled")
            self.errorColourButton.config(state="disabled", background=ColourConvert((160,160,160)))
            self.errorLegend.config(state="disabled")
        elif WithErrors.get() == 1:
            self.errorColourLabel.config(state="normal")
            self.errorColourButton.config(state="normal", background=ColourConvert(errorColour))
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
        self.menu.add_cascade(label="Plot",menu=self.PlotMenu)

class PlotElement:
    def __init__(self, root, name, type):
        self.name = name
        self.type = type


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

root.mainloop()
