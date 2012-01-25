#python
import sys
import lx  #I know these aren't necessary, 
#but since Python doesn't do anthing if you import 
#something a second time, I figured, eh!
import sys
from os.path import join
from site import addsitedir

userdir = lx.eval('query platformservice path.path ? user')
lx.out(userdir)
addsitedir(join(userdir, 'Scripts', 'MGLToolsPckgs'))
addsitedir(join(userdir, 'Scripts', 'site-packages'))
addsitedir(join(userdir, 'Scripts', 'site-packages','PIL'))

import numpy
import MolKit
import mslib

#TODO in 14 days
#helper.modo
#ui.modo
#adaptor.modo

lx.out()  #This apparently prints an empty line
lx.out( "Python Version: ", sys.version )

#lx.eval('script.run "macro.scriptservice:19601433555:macro"')
#lx.eval('transform.channel pos.X 2.0')
#lx.eval('transform.channel pos.Y 2.0')
#lx.eval('transform.channel pos.Z 2.0')

lx.eval('dialog.setup yesNo')
#style:{info|warning|error|okCancel|yesNo| !	!	!	yesNoCancel|yesNoAll|yesNoToAll|saveOK| !	!	!	fileOpen|fileOpenMulti|fileSave|dir}
lx.eval('dialog.title {Confirm Operation}')
lx.eval('dialog.msg {Perform the operation?}')
#lx.eval('dialog.msg "@table@msg@"') 
lx.eval('dialog.msgArg 1 string "test"')
lx.eval( "dialog.result ok" );

#lx.eval('item.channel color')
try :
    lx.eval('+dialog.open')
    result = lx.eval("dialog.result ?")
    lx.out(result)
    lx.eval('item.create mesh name:Test') #mask:test

except :
    lx.out("no")
#lx.out(result)
#isActive = lx.test( "tool.set prim.cube on" 
#if( result == "no" ) :
#    pass