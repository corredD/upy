/*
 * Copyright (c) 2010
 *	Side Effects Software Inc.  All rights reserved.
 *
 * Redistribution and use of Houdini Development Kit samples in source and
 * binary forms, with or without modification, are permitted provided that the
 * following conditions are met:
 * 1. Redistributions of source code must retain the above copyright notice,
 *    this list of conditions and the following disclaimer.
 * 2. The name of Side Effects Software may not be used to endorse or
 *    promote products derived from this software without specific prior
 *    written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY SIDE EFFECTS SOFTWARE `AS IS' AND ANY EXPRESS
 * OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
 * OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.  IN
 * NO EVENT SHALL SIDE EFFECTS SOFTWARE BE LIABLE FOR ANY DIRECT, INDIRECT,
 * INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
 * LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
 * OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
 * LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
 * NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
 * EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 *----------------------------------------------------------------------------
 */

/// @file cmd_ui.C
/// @brief Example for creating a native UI dialog.
///
/// This file provides a sample command that launches an HDK-based GUI dialog.
/// When launched as the 'cmd_ui' command from the hscript textport, it simply
/// brings up a dialog with some UI gadgets that do nothing.
/// 
/// It uses a cmd_ui.ui file that can found in the same place as this file.
/// For all platforms *except* OSX, cmd_ui. should be installed to:
/// @code
///	$HOME/houdiniX.Y/config/Applications/cmd_ui/
/// @endcode
/// On OSX, it should be installed to:
/// @code
///	$HOME/Library/Preferences/houdini/X.Y/config/Applications/cmd_ui/
/// @endcode
/// 

#include <stdio.h>
#include <UT/UT_DSOVersion.h>
#include <CMD/CMD_Manager.h>
#include <CMD/CMD_Args.h>

#include <UI/UI_Value.h>
#include <SI/AP_Interface.h>

#include <time.h>

/// Used to wrap around callback functions responding to UI_Value changes
#define MYDIALOG_CB(method)	((UI_EventMethod)&MyDialog::method)

///
/// Example dialog class. It should be derived from AP_Interface.
///
namespace HDK_Sample {

class MyDialog : public AP_Interface
{
public:
    MyDialog();

    /// Launch the UI dialog
    bool	open();

    /// Close the UI dialog
    void	close();

private:
    /// Parses the supplied cmd_ui.ui file
    bool	parseDialog();

    /// Example callback from UI_Value changes
    // @{
    void	handleImport(UI_Event *event);
    void	handleOpenOrClose(UI_Event *event);
    // @}

private:
    UI_Value	myOpenValue;	    /// Bound to value for dialog open/close
    UI_Value	myStatusValue;	    /// Bound to status value
    bool	myParsedDialog;	    /// Flag to keep track if we've been parsed
    bool	myIsOpen;	    /// Keep track if we're open
};

} // namespace HDK_Sample

using namespace HDK_Sample;

MyDialog::MyDialog()
    : myParsedDialog(false)
    , myIsOpen(false)
{
}

bool
MyDialog::parseDialog()
{
    // These bind the named UI values with the given objects.
    // It's not strictly necessary but is more readable than using
    // getValueSymbol() after calling parseUI().
    setValueSymbol("dlg.val", &myOpenValue);
    setValueSymbol("status.val", &myStatusValue);

    // The search path used will be defined by HOUDINI_UI_APP_PATH environment
    // variable. The default is $HFS/houdini/config/Applications
    if (!parseUI("cmd_ui/cmd_ui.ui"))
	return false;	// error parsing

    // Add interest on when a UI_Value changes
    myOpenValue.addInterest(this, MYDIALOG_CB(handleOpenOrClose));
    // We can also directly add interest on an unbound but named UI_Value
    getValueSymbol("import.val")->addInterest(this, MYDIALOG_CB(handleImport));

    return true;
}

bool
MyDialog::open()
{
    // Only parse the dialog once
    if (!myParsedDialog)
    {
	if (!parseDialog())
	    return false;
	myParsedDialog = true;
    }

    myStatusValue = "";

    myOpenValue = true;
    myOpenValue.changed(this);	    // notify window to open
    return true;
}

void
MyDialog::close()
{
    myOpenValue = false;
    myOpenValue.changed(this);	    // notify window to close
}

void
MyDialog::handleOpenOrClose(UI_Event *event)
{
    // guard against potential multiple events
    if (myIsOpen == (bool)myOpenValue)
	return;
    myIsOpen = (bool)myOpenValue;

    if (myIsOpen)
    {
	printf("dialog was opened\n");
    }
    else
    {
	printf("dialog was closed\n");
    }
}

void
MyDialog::handleImport(UI_Event *event)
{
    // UI_Value objects can store data of several types. It has cast operators
    // for retrieving the data.
    printf("Filename %s\n", (const char *)*getValueSymbol("filename.val"));
    printf("Menu index %d\n", (int)*getValueSymbol("mymenu.val"));
    printf("Cameras %d\n", (bool)*getValueSymbol("cameras.val"));
    printf("Lights %d\n", (bool)*getValueSymbol("lights.val"));
    printf("Geometry %d\n", (bool)*getValueSymbol("geometry.val"));
    printf("Animation %d\n", (bool)*getValueSymbol("animation.val"));
    printf("Attributes %d\n", (int)*getValueSymbol("attrib.val"));

    //close();
    myStatusValue = "Import Successful!";
    myStatusValue.changed(this);
}


/// cmd_ui()
///
/// Callback function for the new 'cmd_ui' command
static void
cmd_ui( CMD_Args &args )
{
    static MyDialog dlg;

    if (!dlg.open())
	args.err() << "Could not parse cmd_ui.ui file" << endl;
    else
	args.out() << "Successfully launched dialog" << endl;
}

/// This function gets called once during Houdini initialization to register
/// the 'cmd_ui' hscript command.
void
CMDextendLibrary( CMD_Manager *cman )
{
    // install the cmd_ui command into the command manager
    cman->installCommand("cmd_ui", "", cmd_ui);
}

