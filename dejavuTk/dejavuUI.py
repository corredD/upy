# -*- coding: utf-8 -*-
"""
Created on Wed Feb  9 11:19:17 2011

@author: Ludovic Autin
"""
try :
    import tkinter
    from tkinter import *
    import filedialog
    import tkinter.message    
    import tkinter.simpledialog
    from tkinter.colorchooser import askcolor
except :
    import Tkinter as tkinter
    from Tkinter import *
    import tkSimpleDialog as simpledialog
    import tkMessageBox as messagebox
    import tkFileDialog as filedialog
    import tkColorChooser
    from tkColorChooser import askcolor#import tkinter.simpledialog
#try :
#    from ttk import *
#except :
#    print ("no ttk")
#import tkinter.messagebox
#import tkinter.messagebox
#import tkinter.filedialog
#import tkinter.colorchooser
#from tkinter.colorchooser import askcolor
#Pmw .... and mglutil as well
from functools import partial

from upy.uiAdaptor import uiAdaptor

#require pmw for advanced widget ?

#UI general interface
#setTitle should create the Windows, even if no root ? but then no 3d viewer.
#check also pmv gui and arviwer for example.
class ValidatingEntry(Entry):
    # base class for validating entry widgets

    def __init__(self, master, value="", **kw):
        Entry.__init__(*(self, master), **kw)
        self.__value = value
        self.__variable = StringVar()
        self.__variable.set(value)
        self.__variable.trace("w", self.__callback)
        self.config(textvariable=self.__variable)

    def __callback(self, *dummy):
        value = self.__variable.get()
        newvalue = self.validate(value)
        if newvalue is None:
            self.__variable.set(self.__value)
        elif newvalue != value:
            self.__value = newvalue
            self.__variable.set(self.newvalue)
        else:
            self.__value = value

    def validate(self, value):
        # override: return value, new value, or None if invalid
        return value
        
class IntegerEntry(ValidatingEntry):

    def validate(self, value):
        try:
            if value:
                v = int(value)
            return value
        except ValueError:
            return None

class FloatEntry(ValidatingEntry):

    def validate(self, value):
        try:
            if value:
                v = float(value)
            return value
        except ValueError:
            return None
            
            
class questionDialog(simpledialog.Dialog):
    def __init__(self,parent,title="",question=""):
        self.question=question
        self.answer=False        
        simpledialog.Dialog.__init__(self,parent,title=title)
        
    def buttonbox(self):
        # add standard button box. override if you don't want the
        # standard buttons
        box = Frame(self)
        w = Button(box, text="Yes", width=10, command=self.ok, default=ACTIVE)
        w.grid(sticky=W)#N+S+E+W)
        #w.pack(side=LEFT, padx=5, pady=5)
        w = Button(box, text="No", width=10, command=self.cancel)
        w.grid(sticky=W)#w.pack(side=LEFT, padx=5, pady=5)
        self.bind("&lt;Return>", self.ok)
        self.bind("&lt;Escape>", self.cancel)
        box.grid(sticky=N+S+E+W)#()

    #
    # standard button semantics
    def ok(self, event=None):
        self.answer = True
        if not self.validate():
            self.initial_focus.focus_set() # put focus back
            return
        self.withdraw()
        self.update_idletasks()
        self.apply()
        self.parent.focus_set()
        self.destroy()

    def cancel(self, event=None):
        # put focus back to the parent window
        self.answer = False
        self.parent.focus_set()
        self.destroy()

    def body(self, master):
        Label(master, text=self.question).grid(row=0)
        
    def apply(self):
        pass
        
class notebook:
    # CODE FROM : http://code.activestate.com/recipes/188537-a-simple-tkinter-notebook-like-widget/
    # # Copyright 2003, Iuri Wickert (iwickert yahoo.com)
    # References: "An Introduction to Tkinter", Fredrik Lundh "Practical programming in Tcl and Tk", Brent Welsh
    # initialization. receives the master widget
    # reference and the notebook orientation
    def __init__(self, master, side=LEFT):
        
        self.active_fr = None
        self.count = 0
        self.choice = IntVar(0)

        # allows the TOP and BOTTOM
        # radiobuttons' positioning.
        if side in (TOP, BOTTOM):
            self.side = LEFT
        else:
            self.side = TOP
        # creates notebook's frames structure
        self.rb_fr = Frame(master, borderwidth=2, relief=RIDGE)
        self.rb_fr.grid(sticky=E+W)#sticky=N+E+W
        #self.rb_fr.pack(side=side, fill=BOTH)
        self.screen_fr = Frame(master, borderwidth=2, relief=RIDGE)
        self.screen_fr.grid(sticky=E+W)#pack(fill=BOTH)sticky=N+E+W
        

    # return a master frame reference for the external frames (screens)
    def __call__(self):

        return self.screen_fr

        
    # add a new frame (screen) to the (bottom/left of the) notebook
    def add_screen(self, fr, title):
        #indicatoron=0,
        b = Radiobutton(self.rb_fr, text=title,   
            variable=self.choice, value=self.count, 
            command=lambda: self.display(fr))
        #b.pack(fill=BOTH, side=self.side)
        b.grid(sticky=E+W,row=0,column=self.count)
        # ensures the first frame will be
        # the first selected/enabled
        if not self.active_fr:
            fr.grid(sticky=E+W)
            #fr.pack(fill=BOTH, expand=1)
            self.active_fr = fr

        self.count += 1
        
        # returns a reference to the newly created
                # radiobutton (allowing its configuration/destruction)         
        return b


    # hides the former active frame and shows 
    # another one, keeping its reference
    def display(self, fr):        
        self.active_fr.forget()
        self.active_fr.grid_forget()
        fr.grid(sticky=E+W)#.pack(fill=BOTH, expand=1)
        self.active_fr = fr



class dejavuUI:
    """
    The blender uiAdaptor abstract class
    ====================================
        This Adaptor give access to the basic blender Draw function need for 
        create and display a gui.
    """

    host = "tk"
    maxStrLenght=100
    scale = 0.2
#    topLine = 700
    bid=1
    MousePos = [0, 0]
    ScrollPos = 0
    ScrollState = 0
    ScrollInc = 25 
    dock = False
    #special function for subdialog and UIblock
    subdialog = False
    drawUIblock = False
    block = False
    w=120
    h=120
    #need a root
    master = None
    root=None
    root_store = None
    col=0#column
    row=0#row
    ncol=0#column
    maxcol=0
    nrow=0#row
    #need to store the form layout position
    nlayout=0
    notebook = None
    rowFrame=None
    ystep = -30
    
    def withdraw(self):
        print "withdraw",self.root
        self.root.withdraw()

    def deiconify(self):
        print "deiconify",self.root
        self.root.deiconify()

    def close(self):
        self.Quit()
        
    def Quit(self):
        """ Close the windows"""
        #destroy or withdraw?
        self.root.destroy()
        self.created = False

    def CoreMessage(self, evt, val):
        pass

    def SetTitle(self,title):
        """ Initialised the windows and define the windows titles 
        @type  title: string
        @param title: the window title
        """
        print "title ",self.root
        if not title :
            title  = self.title
        self.root.title(title)
        self.root_frame = Frame(self.root)
        self.root_frame.grid(sticky=S+E+W)
        #self.root_frame.grid(sticky='news')
        self.root.protocol("WM_DELETE_WINDOW", self.withdraw)
        #self.root.geometry("%ix%i" % (self.w*2,self.h*2))
        #self.geometry('+'+w+'+'+h)
        
    def createMenu(self,menuDic,menuOrder=None):
        """ Define and draw the window/widget top file menu
        @type  menuDic: dictionary
        @param menuDic: the menu elements, ie entry, callback and submenu
        @type  menuOrder: array
        @param menuOrder: the menu keys oredered
        """        
        #There is no Actual Menu in Blender, bu we can use the Pull Down Menu
        #subMenu: create a callback that create another PupMenu with the subvalue
        #this is the lastine...
        #the menu id is the first elem id
        if menuOrder : 
            lookat = menuOrder
        else :
            lookat = list(menuDic.keys())
        x=5
        menubar = Menu(self.root)
        for mitem in lookat:
            mitem_menu = Menu(menubar, tearoff=0)
            for elem in menuDic[mitem]:            
                if elem["sub"] is not None:
                    submenu = Menu(mitem_menu, tearoff=0)
#                    self.MenuSubBegin(elem["name"])
                    for sub in elem['sub']:
                        if elem['sub'][sub]["action"] is not None :
                            submenu.add_command(label=elem['sub'][sub]["name"], 
                                        command=partial(elem['sub'][sub]["action"],sub))
                        else :
                            submenu.add_command(label=elem['sub'][sub]["name"])
                    mitem_menu.add_cascade(label=elem["name"], menu=submenu)
                else:
                    if elem["action"] is not None :
                        mitem_menu.add_command(label=elem["name"], command=elem["action"])
                    else :
                        mitem_menu.add_command(label=elem["name"], command=elem["action"])
            menubar.add_cascade(label=mitem, menu=mitem_menu)
        self.root.config(menu=menubar)
        
    def handleMenuEvent(self,ev,menu):
        """ This function handle the particular menu event, especially for 
        submenu level action
        @type  ev: int
        @param ev: the current event
        @type  menu: dictionary
        @param menu: the current menu
        """  
        pass

    def getFlagAlignement(self,alignement):
        pass

    def addVariable(self,type,value):
        """ Create a container for storing a widget states """
        if type == "int":
            var = IntVar(self.root)
            var.set(value)
            return var
        elif type == "float":
            var = DoubleVar(self.root)
            var.set(value)
            return var
        elif type == "str":
            var =  StringVar(self.root)
            var.set(value)
            return var
        elif type == "bool":
            var =  BooleanVar(self.root)
            var.set(value)
            return var
        elif type == "col":
            return [0,0,0]
        return None

    def startBlock(self,m=1,n=1):
#        print m,n
        self.ncol=m
        self.nrow=n
        self.m=0
        self.n=0
        
    def endBlock(self):
        self.ncol=0
        self.nrow=0
        self.m=0
        self.n=0

    def drawButton(self,elem,x,y,w=None,h=None):
        """ Draw a Button 
        @type  elem: dictionary
        @param elem: the button dictionary
        @type  x: int
        @param x: position on x in the gui windows
        @type  y: int
        @param y: position on y in the gui windows
        @type  w: int
        @param w: force the width of the item
        @type  h: int
        @param h: force the height of the item
        """
#        print x,y,w,h,elem["height"],elem["width"]
        w = 45
        w = int(elem["width"]*self.scale)
        st= int(len(elem["name"]))
        print(w,st)
        if st > w :
            w = st
        name = elem["name"]
        if elem["label"] != None:
            name = elem["label"]
            
        button = Button(self.root_frame, text=name, 
                                command=elem["action"],
                                #height = int(elem["height"]*self.scale),
                                width = int(w))
#        print "button",self.row,self.col
        button.grid(row=self.row,column=self.col,sticky='w')
        self.col = self.col +1
        if self.col == self.ncol:
            self.row = self.row +1 
            self.col = 0
        return button
#
#    def drawButtonToggle(self,elem,x,y,w=None,h=None):
#        """ Draw a checkBox 
#        @type  elem: dictionary
#        @param elem: the button dictionary
#        @type  x: int
#        @param x: position on x in the gui windows
#        @type  y: int
#        @param y: position on y in the gui windows
#        @type  w: int
#        @param w: force the width of the item
#        @type  h: int
#        @param h: force the height of the item
#        """     
#        w,h = self.checkwh(elem,w,h)
#        if self.subdialog :
#            elem["variable"]=self.check_addAction(Blender.Draw.Toggle,elem["action"],elem["name"],
#                                elem["id"], x, y, w,h,
#                                elem["variable"].val, 
#                                elem["tooltip"])
#        else :
#            elem["variable"]=Blender.Draw.Toggle(elem["name"], elem["id"], x, y, w,h,
#                                elem["variable"].val, 
#                                elem["tooltip"])

    def drawObj(self,elem,x,y,w=None,h=None):
        """ Draw an object input where you can drag on object 
        @type  elem: dictionary
        @param elem: the button dictionary
        @type  x: int
        @param x: position on x in the gui windows
        @type  y: int
        @param y: position on y in the gui windows
        @type  w: int
        @param w: force the width of the item
        @type  h: int
        @param h: force the height of the item
        """   
        pass


        """ Draw a Separative Line
        @type  elem: dictionary
        @param elem: the label dictionary
        @type  x: int
        @param x: position on x in the gui windows
        @type  y: int
        @param y: position on y in the gui windows
        @type  w: int
        @param w: force the width of the item
        @type  h: int
        @param h: force the height of the item
        """            
        if elem["value"] == "H":
            hr=True
        elif elem["value"] == "V":
            hr=False
        pass
        
    def drawCheckBox(self,elem,x,y,w=None,h=None):
#        print x,y
        name = elem["name"]
        if elem["label"] != None:
            name = elem["label"]
        chkbox = Checkbutton(self.root_frame,
                             text = name,
                             command = elem["action"],
                             variable = elem["variable"],
                             #height = int(elem["height"]*self.scale),
                             #width = int(elem["width"]*self.scale)
                             )
        if elem["value"] is not None :
            elem["variable"].set(elem["value"])
        else :
            elem["variable"].set(0)
#        if self.ncol < self.maxcol :
#            X X X X X X            
#            X  X  X  X
#            X   X
#            0   2
#            cs = (self.maxcol - self.ncol)
#            col = self.col 
#            chkbox.grid(row=self.row,column=self.col,sticky=E,columnspan= )
#        else :
        chkbox.grid(row=self.row,column=self.col,sticky=W)#S+E+'w')
        self.col = self.col +1
        if self.col == self.ncol:
            self.row = self.row +1 
            self.col = 0
        return chkbox
#
    def resetPMenu(self,elem):
        """ Add an entry to the given pulldown menu 
        @type  elem: dictionary
        @param elem: the pulldown dictionary
        """
        elem["id"]['menu'].delete(0, 'end')
        elem["value"]=[]
        #elem["variable"].val = len(elem["value"])

    def addItemToPMenu(self,elem,item):
        """ Add an entry to the given pulldown menu 
        @type  elem: dictionary
        @param elem: the pulldown dictionary
        @type  item: string
        @param item: the new entry
        """
        elem["value"].append(item)
        elem["id"]['menu'].delete(0, 'end')
        for x in elem["value"]:
            elem["id"]['menu'].add_command(label=x, command=partial(self.PM_cb,elem["id"],elem,x))
#        elem["variable"].val = len(elem["value"])
        elem["id"].configure(text=elem["value"][len(elem["value"])-1])
        
    def PM_cb(self,w,elem,item):
        w.configure(text=item)
        #elem["variable"] = Tkinter.IntVar(self.root)
        elem["variable"].set(item)
        if elem["action"] is not None:
            elem["action"](elem,item)
        
    def drawPMenu(self,elem,x,y,w=None,h=None):
        """ Draw a pulldown menu 
        @type  elem: dictionary
        @param elem: the pulldown dictionary
        @type  x: int
        @param x: position on x in the gui windows
        @type  y: int
        @param y: position on y in the gui windows
        @type  w: int
        @param w: force the width of the item
        @type  h: int
        @param h: force the height of the item
        """
        elem["variable"] = StringVar(self.root)
        if not elem["value"]:
            elem["value"] = [elem["name"],]
        elem["variable"].set(elem["value"][0])
        elem["id"] = OptionMenu(self.root_frame,elem["variable"],*elem["value"])
        #w = apply(OptionMenu, (self.root_frame, elem["variable"])+tuple(elem["value"]))
        #w["command"]=elem["action"]
        elem["id"].grid(row=self.row,column=self.col,sticky='w')
        #w.bind("<FocusIn>", partial(elem["action"],elem))
        elem["id"]['menu'].delete(0, 'end')
        for x in elem["value"]:
            elem["id"]['menu'].add_command(label=x, command=partial(self.PM_cb,elem["id"],elem,x))
        elem["id"].configure(text=elem["value"][0])
        self.col = self.col +1
        if self.col == self.ncol:
            self.row = self.row +1 
            self.col = 0
        return w

#        
#    def drawText(self,elem,x,y,w=None,h=None):
#        """ Draw a Label
#        @type  elem: dictionary
#        @param elem: the label dictionary
#        @type  x: int
#        @param x: position on x in the gui windows
#        @type  y: int
#        @param y: position on y in the gui windows
#        @type  w: int
#        @param w: force the width of the item
#        @type  h: int
#        @param h: force the height of the item
#        """     
##        elem["width"] = len(elem["label"])* 3.
#        if type(elem) == str :
#            label = elem
#        else :
#            label =elem["label"]
#            w,h = self.checkwh(elem,w,h)
#        Blender.BGL.glRasterPos2i(x,y+5)
#        Blender.Draw.Text(label)
##        elem["width"] = len(elem["label"])* 3 #TODO find a more flexible solution
#
    def drawLabel(self,elem,x,y,w=None,h=None):
        """ Draw a Label
        @type  elem: dictionary
        @param elem: the label dictionary
        @type  x: int
        @param x: position on x in the gui windows
        @type  y: int
        @param y: position on y in the gui windows
        @type  w: int
        @param w: force the width of the item
        @type  h: int
        @param h: force the height of the item
        """      
#        elem["width"] = 50#len(elem["label"])* 3.       
        if type(elem) == str :
            label = elem
        else :
            label =elem["label"]
        elem["variable"] = StringVar(self.root)
        elem["id"] = Label(self.root_frame, textvariable=elem["variable"])
        elem["variable"].set(label)
        elem["id"].grid(row=self.row,column=self.col,sticky='w')
        self.col = self.col +1
        if self.col == self.ncol:
            self.row = self.row +1 
            self.col = 0
        return elem["id"]
        
    def drawString(self,elem,x,y,w=None,h=None):
        """ Draw a String input elem
        @type  elem: dictionary
        @param elem: the string input dictionary
        @type  x: int
        @param x: position on x in the gui windows
        @type  y: int
        @param y: position on y in the gui windows
        @type  w: int
        @param w: force the width of the item
        @type  h: int
        @param h: force the height of the item
        """            
        e = Entry(self.root_frame,  
                                width = int(elem["width"]*self.scale),
                                textvariable=elem["variable"])
        if elem["value"] is not None :
            elem["variable"].set(elem["value"])
        else :
            elem["variable"].set("")
#        print "button",self.row,self.col
        e.grid(row=self.row,column=self.col,sticky='w')
        if elem["action"] is not None :
            e.bind('<Key-Return>',elem["action"])

        self.col = self.col +1
        if self.col == self.ncol:
            self.row = self.row +1 
            self.col = 0
        elem["id"] = e
        return elem["id"]

    def drawStringArea(self,elem,x,y,w=None,h=None):
        """ Draw a String Area input elem, ie multiline
        @type  elem: dictionary
        @param elem: the string area input dictionary
        @type  x: int
        @param x: position on x in the gui windows
        @type  y: int
        @param y: position on y in the gui windows
        @type  w: int
        @param w: force the width of the item
        @type  h: int
        @param h: force the height of the item
        """          
        elem["variable"] = Text(self.root_frame,maxundo=100,
                                width = int(elem["width"]*0.3),
                                height = int(elem["height"]*0.15))
        if elem["value"] is not None :
            elem["variable"].insert(END,elem["value"])
        else :
            elem["variable"].insert(END,"")
        elem["variable"].grid(row=self.row,column=self.col,sticky='w')
        if elem["action"] is not None :
            elem["variable"].bind('<Key-Return>',elem["action"])        
        self.col = self.col +1
        if self.col == self.ncol:
            self.row = self.row +1 
            self.col = 0
        return elem["variable"]

    def drawNumbers(self,elem,x,y,w=None,h=None):
        """ Draw a Int input elem
        @type  elem: dictionary
        @param elem: the Int input dictionary
        @type  x: int
        @param x: position on x in the gui windows
        @type  y: int
        @param y: position on y in the gui windows
        @type  w: int
        @param w: force the width of the item
        @type  h: int
        @param h: force the height of the item
        """        
        #elem["variable"] = Tkinter.StringVar(self.root)
        e = IntegerEntry(self.root_frame,
                                width = int(elem["width"]*self.scale))
        e["textvariable"]=elem["variable"]
        if elem["value"] is not None :
            elem["variable"].set(elem["value"])
        else :
            elem["variable"].set(0)
#        print "button",self.row,self.col
        e.grid(row=self.row,column=self.col,sticky='w')
        if elem["action"] is not None :
            e.bind('<Key-Return>',elem["action"])        
        self.col = self.col +1
        if self.col == self.ncol:
            self.row = self.row +1 
            self.col = 0
        return e

    def drawFloat(self,elem,x,y,w=None,h=None):
        """ Draw a Int input elem
        @type  elem: dictionary
        @param elem: the Int input dictionary
        @type  x: int
        @param x: position on x in the gui windows
        @type  y: int
        @param y: position on y in the gui windows
        @type  w: int
        @param w: force the width of the item
        @type  h: int
        @param h: force the height of the item
        """
        elem["variable"] = StringVar(self.root)        
        e = FloatEntry(self.root_frame,
                                width = int(elem["width"]*self.scale))
        e["textvariable"]=elem["variable"]
        if elem["value"] is not None :
            elem["variable"].set(elem["value"])
        else :
            elem["variable"].set(0.0)
#        print "button",self.row,self.col
        e.grid(row=self.row,column=self.col,sticky='w')
        #can use pack too for expand/filling
        if elem["action"] is not None :
            e.bind('<Key-Return>',elem["action"])        
        self.col = self.col +1
        if self.col == self.ncol:
            self.row = self.row +1 
            self.col = 0
        return e
    
    @classmethod
    def drawError(self,errormsg=""):
        """ Draw a error message dialog
        @type  errormsg: string
        @param errormsg: the messag to display
        """  
        messagebox.showinfo("Error",errormsg)
        return

    @classmethod
    def drawQuestion(self,title,question="",callback=None):
        """ Draw a Question message dialog, requiring a Yes/No answer
        @type  title: string
        @param title: the windows title       
        @type  question: string
        @param question: the question to display
        
        @rtype:   bool
        @return:  the answer     
        """
        #questionDialog(self.root,title=title,question=question)
        res = messagebox.askyesno(title, question)
        if callback is not None :
            callback(res)
        else :
            return res

    @classmethod        
    def drawMessage(self,title="",message=""):
        """ Draw a message dialog
        @type  title: string
        @param title: the windows title       
        @type  message: string
        @param message: the message to display   
        """
        messagebox.showinfo(title,message)
        return

#    def drawInputQuestion(self,title="",question="",callback=None):
#        """ Draw an Input Question message dialog, requiring a string answer
#        @type  title: string
#        @param title: the windows title       
#        @type  question: string
#        @param question: the question to display
#        
#        @rtype:   string
#        @return:  the answer     
#        """                  
#        result = Blender.Draw.PupStrInput(question, "", 100)
#        if result :
#            if callback is not None :
#                callback(result)
#            else :
#                return result
#
    def drawSliders(self,elem,x,y,w=None,h=None):
        """ Draw a Slider elem, the variable/value of the elem define the slider format
        @type  elem: dictionary
        @param elem: the slider input dictionary
        @type  x: int
        @param x: position on x in the gui windows
        @type  y: int
        @param y: position on y in the gui windows
        @type  w: int
        @param w: force the width of the item
        @type  h: int
        @param h: force the height of the item
        """
        slider = Scale(self.root_frame,from_=elem["mini"], to=elem["maxi"], resolution=elem["step"],
                                command=elem["action"],label=elem["label"],
                                #length = elem["height"]*self.scale,
                                #width = elem["width"]*self.scale,
                                variable = elem["variable"],
                                orient=HORIZONTAL)
        if elem["value"] is not None :
            elem["variable"].set(elem["value"])
        else :
            elem["variable"].set(elem["mini"])
#        print "slider",self.row,self.col
        slider.grid(row=self.row,column=self.col,sticky='w')
        self.col = self.col +1
        if self.col == self.ncol:
            self.row = self.row +1 
            self.col = 0        
        return slider
        
#    def drawImage(self,elem,x,y,w=None,h=None):
#        """ Draw an Image, if the host supported it
#        @type  elem: dictionary
#        @param elem: the image input dictionary
#        @type  x: int
#        @param x: position on x in the gui windows
#        @type  y: int
#        @param y: position on y in the gui windows
#        @type  w: int
#        @param w: force the width of the item
#        @type  h: int
#        @param h: force the height of the item
#        """           
#        w,h = self.checkwh(elem,w,h)
#        img = Blender.Image.Load(elem["value"])
#        #we can add some gl call to make some transparency if we want
#        #Blender.BGL.glEnable( Blender.BGL.GL_BLEND ) # Only needed for alpha blending images with background.
#        #Blender.BGL.glBlendFunc(Blender.BGL.GL_SRC_ALPHA, Blender.BGL.GL_ONE_MINUS_SRC_ALPHA) 
#        #Blender.BGL.glDisable( Blender.BGL.GL_BLEND )
#        Blender.Draw.Image(img, x, y-h-10)#, zoomx=1.0, zoomy=1.0, clipx=0, clipy=0, clipw=-1, cliph=-1)
#
    def ColorChooser_cb(self,elem):
        (rgb, hexval)= askcolor(title="choose a Color")
        elem["variable"] = rgb
        elem["id"].config(bg=hexval,activebackground=hexval)
        if elem["action"]:
            elem["action"]()

    def drawColorField(self,elem,x,y,w=None,h=None):
        """ Draw a Color entry Field
        @type  elem: dictionary
        @param elem: the color input dictionary
        @type  x: int
        @param x: position on x in the gui windows
        @type  y: int
        @param y: position on y in the gui windows
        @type  w: int
        @param w: force the width of the item
        @type  h: int
        @param h: force the height of the item
        """ 
        #display the current color
        #and bind to the choose color
        if elem["value"] is not None :
            elem["variable"] = elem["value"]
        else :
            elem["value"] = elem["variable"]
        elem["id"] = Button(self.root_frame,
                                command=partial(self.ColorChooser_cb,elem),
                                background="black",#elem["variable"],
                                activebackground="black",#elem["variable"],
                                #height = int(elem["height"]*self.scale),
                                width = int(elem["width"]*self.scale))
#        print "button",self.row,self.col
        elem["id"].grid(row=self.row,column=self.col,sticky='w')
        self.col = self.col +1
        if self.col == self.ncol:
            self.row = self.row +1 
            self.col = 0
        return elem["id"]

        
    def drawTab(self,bloc,x,y):
        """
        Function to draw a block as a tab frame layout of the gui. 
        
        @type  block: array or dictionary
        @param block: list or dictionary of item dictionary
        @type  x: int
        @param x: position on x in the gui windows, used for blender
        @type  y: int
        @param y: position on y in the gui windows, used for blender
        
        @rtype:   int
        @return:  the new horizontal position, used for blender
        """ 
        self.root_store = self.root_frame
        if self.notebook is None :
            self.notebook = notebook(self.root, TOP)
        self.root_frame = Frame(self.notebook())
        #add elem to the Frame
        self.maxcol=0
        for k,blck in enumerate(bloc["elems"]):
            if len(blck) >  self.maxcol:
                 self.maxcol = len(blck)         
        for k,blck in enumerate(bloc["elems"]):
            if type(blck) is list :
                self.ncol=len(blck)
                for index, item in enumerate(blck):
                    self._drawElem(item,0,0)
            else : #dictionary: multiple line / format dict?
                if "0" in blck:
                    y = self._drawGroup(blck,x,y)
                else :
                    y = self._drawFrame(blck,x,y)
        self.notebook.add_screen(self.root_frame, bloc["name"])
        self.root_frame = self.root_store
#        self.LayoutChanged(bloc["id"])
        return y
   
    def frame_cb(self,bloc):
#        print bloc["name"]
        bloc["collapse"] = bloc["variable"].get()
        print "collapse in cb",bloc["collapse"]
        bloc["id"].destroy()
        self.Frame(bloc,0,0)
#        bloc["id"].update()
        self.root_frame.update()
        
    def drawFrame(self,bloc,x,y):
        """
        Function to draw a block as a collapsable frame layout of the gui. 
        
        @type  block: array or dictionary
        @param block: list or dictionary of item dictionary
        @type  x: int
        @param x: position on x in the gui windows, used for blender
        @type  y: int
        @param y: position on y in the gui windows, used for blender
        
        @rtype:   int
        @return:  the new horizontal position, used for blender
        """            
        bloc["variable"] = IntVar(self.root)
        bloc["variable"].set(1)   
        bloc["collapse"] = bloc["variable"].get()
        bloc["labelwidget"] = Checkbutton(self.root,
                                              text = bloc["name"],
                                              command = partial(self.frame_cb,bloc),
                                              variable = bloc["variable"])
        bloc["nlayout"] = self.nlayout
        self.nlayout = self.nlayout + 1
        self.Frame(bloc,x,y)
#        self.LayoutChanged(bloc["id"])
        return y

    def Frame(self,bloc,x,y):
        self.root_store = self.root_frame
        #padx=5, pady=5,
        bloc["id"] = self.root_frame = LabelFrame(self.root_frame, text=bloc["name"], 
                                             labelwidget=bloc["labelwidget"],
                                            height = int(bloc["height"]*self.scale),
                                            width = int(bloc["width"]*self.scale))

        #self.root_frame.pack(padx=10, pady=10)
        #.grid(row=self.row,column=self.col,sticky='w')
        col = self.ncol
        if self.ncol == 0 :
            col = 1
        if self.rowFrame is None :
           self.rowFrame = self.row
        self.root_frame.grid(sticky=N+S+E+W,row=self.rowFrame+bloc["nlayout"],columnspan=3) 
#        print("COLLAPSE##########", bloc["collapse"], (bloc["collapse"]==True))
        print "collapse in frame ",bloc["collapse"],bloc["variable"].get()
        if bloc["collapse"] :
            self.startBlock(n=len(bloc["elems"]))#,m=len(blck))
            self.maxcol=0
            for k,blck in enumerate(bloc["elems"]):
                if len(blck) >  self.maxcol:
                     self.maxcol = len(blck)         
            for k,blck in enumerate(bloc["elems"]):
                self.ncol=len(blck)
#                print "grid ",self.nrow,self.ncol
                for index, item in enumerate(blck):
                #print index,item
                    self._drawElem(item,0,0)
            self.endBlock()
        else :
            w=Label(self.root_frame,width=bloc["width"])
            w.pack()        
        self.root_frame = self.root_store

    def drawGroup(self,bloc,x,y,w=10,h=10):
        self.root_store = self.root_frame
        bloc["id"] = self.root_frame = Frame(self.root_store)
        self.root_frame.grid(row=self.row,column=self.col,sticky='w')
        self.col = self.col +1
        if self.col == self.ncol:
            self.row = self.row +1 
            self.col = 0      
        #add elem to the Frame
        if "elems" in bloc :
            for k,blck in enumerate(bloc["elems"]):
                self.ncol=len(blck)
                for index, item in enumerate(blck):
                    self._drawElem(item,0,0)
        self.root_frame = self.root_store
  
#    def UpdateMenuData(self,blocklayout):
#        """ special to update the frame layout """
##        global ButtonData, Filters
#        selection       = ""
#        
#        if blocklayout is not None:
##            ArrayItem   = ButtonData[ArrayIndex]
#            #Figure Buttons
#            for index, item in enumerate(blocklayout["elems"]):
#                buttonCount = len(blocklayout["elems"])
#                if (buttonCount and index > buttonCount): break 
#                #If buttonCount is specified stop drawing button list past count
#                if (item["show"] == True): #Is button set to show
#                    if (item["type"] == "pullMenu"): 
#                        pass

    def fileDialog(self,label="",callback=None):
        """ Draw a File input dialog
        @type  label: string
        @param label: the windows title       
        @type  callback: function
        @param callback: the callback function to call
        """
        options={}
        options['defaultextension'] = '' # couldn't figure out how this works
        options['filetypes'] = [('all files', '.*'), ('text files', '.txt')]
        options['initialdir'] = ''
        options['initialfile'] = ''
        options['parent'] = self.root
        options['title'] = label
        file = filedialog.askopenfilename(**options)
        if callback is None:
            return file
        else :
            callback(file)
            
        #Blender.Window.FileSelector (callback, label)
#
#    def waitingCursor(self,toggle):
#        """ Toggle the mouse cursor appearance from the busy to idle.
#        @type  toggle: Bool
#        @param toggle: Weither the cursor is busy or idle 
#        """             
#        Blender.Window.WaitCursor(toggle)
#
    def getString(self,elem):
        """ Return the current string value of the String Input elem
        @type  elem: dictionary
        @param elem: the elem input dictionary       
        
        @rtype:   string
        @return:  the current string input value for this specific elem
        """                
        return str(elem["variable"].get())

    def setString(self,elem,val):
        """ Set the current String value of the string input elem
        @type  elem: dictionary
        @param elem: the elem input dictionary       
        @type  val: string
        @param val: the new string value    
        """            
        elem["variable"].set(str(val))         #for input
#        elem["id"].configure(text= str(val))  #for label


    def getStringArea(self,elem):
        """ Return the current string area value of the String area Input elem
        @type  elem: dictionary
        @param elem: the elem input dictionary       
        
        @rtype:   string
        @return:  the current string area input value for this specific elem
        """                
        return elem["variable"].get(1.0, END)

    def setStringArea(self,elem,val):
        """ Set the current String area value of the string input elem
        @type  elem: dictionary
        @param elem: the elem input dictionary       
        @type  val: string
        @param val: the new string value (multiline)   
        """   
        elem["variable"].delete(1.0, END)
        elem["variable"].insert(END,val)
        
    def getLong(self,elem):
        """ Return the current Int value of the Input elem
        @type  elem: dictionary
        @param elem: the elem input dictionary       
        
        @rtype:   Int
        @return:  the current Int value input for this specific elem
        """
        if elem["type"] == "pullMenu":
            choice = elem["variable"].get()
            return elem["value"].index(choice)
        else:
            return int(elem["variable"].get())#verify  #for menu...as its start at 1

    def setLong(self,elem,val):
        """ Set the current Int value of the Int input elem
        @type  elem: dictionary
        @param elem: the elem input dictionary       
        @type  val: Int
        @param val: the new Int value
        """                        
        if elem["type"] == "pullMenu":
            choice = elem["value"][int(val)]
            return elem["variable"].set(choice)
        else:
            elem["variable"].set(int(val))#+1?

    def getReal(self,elem):
        """ Return the current Float value of the Input elem
        @type  elem: dictionary
        @param elem: the elem input dictionary       
        
        @rtype:   Float
        @return:  the current Float value input for this specific elem
        """       
#        print elem["variable"].get()
        return float(elem["variable"].get())

    def setReal(self,elem,val):
        """ Set the current Float value of the Float input elem
        @type  elem: dictionary
        @param elem: the elem input dictionary       
        @type  val: Float
        @param val: the new Float value
        """                                
        elem["variable"].set(float(val))

    def getBool(self,elem):
        """ Return the current Bool value of the Input elem
        @type  elem: dictionary
        @param elem: the elem input dictionary       
        
        @rtype:   Bool
        @return:  the current Bool value input for this specific elem
        """                        
        return bool(elem["variable"].get())
        
    def setBool(self,elem,val):
        """ Set the current Bool value of the Bool input elem
        @type  elem: dictionary
        @param elem: the elem input dictionary       
        @type  val: Bool
        @param val: the new Bool value
        """                        
        elem["variable"].set(val)

    def getColor(self,elem):
        """ Return the current Color value of the Input elem
        @type  elem: dictionary
        @param elem: the elem input dictionary       
        
        @rtype:   Color
        @return:  the current Color array RGB value input for this specific elem
        """        
        elem["value"] = elem["variable"]        
        return elem["variable"]

    def setColor(self,elem,val):
        """ Set the current Color rgb arrray value of the Color input elem
        @type  elem: dictionary
        @param elem: the elem input dictionary       
        @type  val: Color
        @param val: the new Color value
        """     
        elem["value"] = val
        elem["variable"] = val

    def updateSlider(self,elem,mini,maxi,default,step):
        """ Update the state of the given slider, ie format, min, maxi, step
        @type  elem: dictionary
        @param elem: the slider elem dictionary       
        @type  maxi: int/float
        @param maxi: max value for the item, ie slider
        @type  mini: int/float
        @param mini: min value for the item, ie slider
        @type  default: int/float
        @param default: default value for the item, ie slider
        @type  step: int/float
        @param step: step value for the item, ie slider
        """    
        return
#        if type(step) is int :
#            elem["variable"] = Blender.Draw.Create(0)
#        else :
#            elem["variable"] = Blender.Draw.Create(0.)
#        elem["maxi"] = maxi
#        elem["mini"] = mini
##        elem["default"] = 
#        elem["step"] = step
        
    def updateViewer(self):
        """
        update the 3d windows if any
        """
        pass
        

    def _restore(self,rkey,dkey=None):
        """
        Function used to restore the windows data, usefull for plugin
        @type  rkey: string
        @param rkey: the key to access the data in the registry/storage       
        @type  dkey: string
        @param dkey: wiether we want a particular data from the stored dic
        """
        pass

    def _store(self,rkey,dict):
        """
        Function used to store the windows data, usefull for plugin
        @type  rkey: string
        @param rkey: the key to access the data in the registry/storage       
        @type  dict: dictionary
        @param dict: the storage is done throught a dictionary
        """         
        pass

    def close(self):
        """ Close the windows"""
        if not self.subdialog :
            self.Quit()
        else :
            #should stop drawing it
            self.drawUIblock = False
#
    def drawSubDialog(self,dial,id,callback=None,asynchro = True):
        """
        Draw the given subdialog whit his own element and callback
        
        @type  dial: dialog Object
        @param dial: the dialog object to be draw
        @type  id: int
        @param id: the id of the dialog
        @type  callback: function
        @param callback: the associate callback
        """        
        dial.display()
        #dial.deiconify()
#
    def display(self):
        """ Create and Open the current gui windows """
        print "self.created",self.created
        if not self.created:
            self.CreateLayout()
            self.created = True
        self.deiconify()
        
class dejavuUIDialog(dejavuUI,uiAdaptor):
    def __init__(self,**kw):
        if kw.has_key("master"):
            print "ok master pass",type(kw["master"])
            master = kw["master"]
            if type(master) is dict :
                self.master = master["master"].master
            elif master is None :
                self.master = None
            else :
                self.master = master.master
            print "ok master pass",self.master
        if self.master is not None :
            self.root = Toplevel(self.master)#self.master
            print "ok Toplevel",self.root
        else :
            self.root = self.master = Toplevel()
            print "ok tk", self.root
#            self.root =  Toplevel()

#        self.root.rowconfigure(0, weight=1)            
#        self.root.columnconfigure(0, weight=1)         
#        self.master.rowconfigure(0, weight=1)           
#        self.master.columnconfigure(0, weight=1)        
        
        if kw.has_key("title"):
            self.title= kw["title"]
            self.SetTitle(self.title)
        self.withdraw()
#        self.root.geometry("%ix%i" % (self.w,self.h))
        self.created = False
        print "ok master and root",self.master, self.root
#
#class blenderUISubDialog(blenderUIDialog):
#    def __init__(self,name):
#        blenderUIDialog.__init__(self,)
#        #a subdialog is a popup
#        self.name = name
#        self.elems = []
#        self.result = None
#    
#    def draw(self):
#        self.result = Blender.Draw.PupBlock(self.name, self.elems)
#


