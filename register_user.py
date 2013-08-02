# -*- coding: utf-8 -*-
"""
Created on Fri Oct  7 07:14:08 2011

@author: -
"""
import os
import sys
import socket

try :
    #python 3
    import urllib.parse as urllib
    from http import client as httplib
except :
    import urllib
    import httplib
    
import pickle
import time
import shutil

def internet_on():
    response=urllib.urlopen('http://74.125.113.99')
    if response == 404 :
        return False
    else : 
        return False
    
#from mglutil.util.packageFilePath import getResourceFolderWithVersion
#from mglutil.util.packageFilePath import getResourceFolder
from os.path import expanduser
home = expanduser("~")

try :
    from upy import uiadaptor
    if uiadaptor is None :
        uiadaptor = upy.getUIClass()
except :
    uiadaptor = None


keyword = {"First Name*":"",
             "Last Name*":"",
             "Email*":"",
             "Institution*":"",
             "Institution Type*":"",
             "Position*":' ',
             "Department":"",
             "Address":"",
             "City":"",
             "State":"",
             "PostalCode":"",
             "Country":"",
             "Phone":"",
             "Fax":"",}
order = ["First Name*","Last Name*","Email*","Institution*","Institution Type*","Position*",
             "Department","Address", "City","State","PostalCode", "Country", "Phone",
             "Fax",]   

dicToSend = {'sys_version':'',
             'City': '', 
             'First_Name': '', 
             'Last_Name': '', 
             'Phone': '', 
             'Country': '', 
             'hostname': '', 
             'PlanningToUse': ',PMV', 
             'Fax': '', 
             'Institution': '', 
             'PostalCode': '', 
             'State': '', 
             'version': '', 
             'Institution_Type': 'Academic', 
             'BuildFrom':'Binary', 
             'Address': '', 
             'Department': '', 
             'Position': '', 
             'sys_platfrom': '', 
             'Email': '', 
             'os_name': '',
             '3DHost':''} 

class Register_User:
    """Opens TopLevel Dialog for User Registration"""
    def __init__(self,use="ePMV",where=home):
        self.use=use
        self.where = where
        self.form_dict = keyword.copy()
        from Support.version import __version__
        self.sys_dict = {
             'PlanningToUse':use,
             'BuildFrom':'Binary',
             'version':__version__.split('(')[0],
             'os_name': os.name,
             'sys_platfrom':sys.platform,
             'sys_version':sys.version.replace('\n','')#.split('(')[0],
             #'UserID':'',
             }
        self.form_dict.update(self.sys_dict)
        try:
            hostname = self.gethostname()
            self.form_dict['hostname'] = hostname
        except:
            self.form_dict['hostname'] = "problem"
        self.form_dict['3DHost'] = ""
        
        self.preFill()

    def register(self,):
        self.dictToSend={}
        for i,k in enumerate(order) :
            dk = k
            if i <=5 :
                dk = dk.replace("*","")
                dk = dk.replace(" ","_")
            self.dictToSend[dk] = str(self.form_dict[k]).strip()
            #print (dk,self.dictToSend[dk])
        self.dictToSend.update(self.sys_dict)
        self.dictToSend['hostname'] = self.form_dict['hostname']
        self.dictToSend['3DHost'] = self.form_dict['3DHost']
#        for k in self.dictToSend:
#            print k, self.dictToSend[k]
        params = urllib.urlencode(self.dictToSend)
        #print (params)
        #self.label_message.configure(text = 'Please Wait', fg = 'Red')
        headers = {"Content-type": "application/x-www-form-urlencoded","Accept": "text/plain"}
        conn = httplib.HTTPConnection("www.scripps.edu:80")
        #conn = httplib.HTTPConnection("mgldev.scripps.edu:80")
        try:
            conn.request("POST", "/cgi-bin/sanner/register_mgltools.py", params, headers)
            response = conn.getresponse()
        except :
#            from traceback import print_exc
#            print_exc()
            print ("fail to connect")
            return  False          
        if response.status == 200:
#            getResourceFolder
            reg_file =  os.path.join(self.where,  self.use+'_registration')
#            print (reg_file)
            UserID = response.read().decode("utf8")
#            print (UserID)
            if UserID:
                self.form_dict['UserID'] = UserID
                file = open(reg_file,'wb')
                pickle.dump(self.form_dict, file)
                file.close()
                #c_reg_file = os.path.join(self.where,  self.use+'_registration.'+UserID)
                #shutil.copy(reg_file, c_reg_file)
                #file = open(c_reg_file,'wb')
                #pickle.dump(self.form_dict, file)
                #file.close()
            else:
                print ("Registration failed to create User.")
                return  False
        else:
            print ("Unable to connect to Registration Database" )
            return  False
        conn.close()        
        return  True
        
    def preFill(self):
        #old_rc = getResourceFolder()
        regfile = os.path.join(self.where, self.use+'_registration')
        if os.path.exists(regfile):
            try :
                form_dict =  pickle.load(open(regfile, 'rb'))
            except :
                return
            print(form_dict)
            for i,k in enumerate(order) :
                dk = k
                if i <=5 :
                    if dk not in form_dict :
                        dk = dk.replace("*","")
                        dk = dk.replace(" ","_")
                self.form_dict[k] = str(form_dict[dk]).strip()
            
    def gethostname(self):
        fullname = socket.gethostname()
        if '.' not in fullname:
            fullname = resolve(fullname)
        return fullname 

class Register_User_ui (uiadaptor) :
    def setup(self,sub=True,r=None,id=2000,use="ePMV",where=home):
        self.h = 350
        self.w = 300
        self.subdialog = sub
        self.title = "Register "+use
        self.SetTitle(self.title)
        if self.subdialog:
            self.block = True
        witdh=350
        if id is not None :
            id=id
        else:
            id = self.bid        
        if r is None :
            self.reg = Register_User(use=use,where=where)
        else :
            self.reg = r
        self.initWidget()
        self.setupLayout()
        self.registered = False
        return True
    
    def initWidget(self):
        self.widget_form = {}
        self.label_form = {}
        self.liste_institution = ["Academic", "Government", "Commercial"]
        for k in order :
            if k == "Institution Type*":
                self.label_form[k] = self._addElemt(label=k+' Academic, Government, Commercial',
                    width=120)
                #pullDownMenu
                self.widget_form[k] = self._addElemt(name=k,
                                    value=self.liste_institution,
                                    width=100,height=10,action=None,
                                    variable=self.addVariable("int",0),
                                    type="pullMenu",)
            else :
                self.label_form[k] = self._addElemt(label=k,width=120)
                self.widget_form[k] = self._addElemt(name=k,width=100,height=10,
                                              action=None,type="inputStr",
                                              value=self.reg.form_dict[k],
                                              variable=self.addVariable("str",""))
        self.label_message = self._addElemt(label="Registration Form. * are required",width=120)
        self.regButton =  self._addElemt(name="Register",width=50,height=10,
                         action=self.Register,type="button")
        self.cancelButton  = self._addElemt(name="Cancel",width=50,height=10,
                         action=self.close,type="button")

    def setupLayout(self):
        self._layout = []
        for k in order :
            self._layout.append([self.label_form[k],self.widget_form[k]])
        self._layout.append([self.label_message,]) 
        self._layout.append([self.regButton,self.cancelButton])

    def checkForm(self):
        for i in range(5):
            if not self.reg.form_dict[order[i]]:
                self.setString(self.label_message,str(order[i]+' is missing or invalid'))
                return False
        self.setString(self.label_message,'')
        return True
        
    def Register(self,*args):
        #get the value in the widget, and send
        for k in keyword :
            self.reg.form_dict[k] = self.getVal(self.widget_form[k])
        res = self.checkForm()
        print(("check",res))
        print((self.reg.form_dict))
        if not res :
            return
        print ('Submitting the Registration Form\nPlease Wait')
        self.setVal(self.label_message, 'Submitting the Registration Form\nPlease Wait')
        self.reg.form_dict["3DHost"] = self.host
        res = self.reg.register()
        if not res :
            self.drawMessage(title="ERROR",
                             message="Registration failed to create User.\nPlease contact mgltools@scripps.edu")
            self.registered=False
            self.close()
        else :
            self.drawMessage(title="SUCCESS",
                             message="Registration success\n")
            self.registered=True
            self.close()
            
    def CreateLayout(self):
        self._createLayout()
        return True
        
    def Command(self,*args):
#        print args
        self._command(args)
        return True
             
