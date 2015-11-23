
"""
    Copyright (C) <2010>  Autin L. TSRI
    
    This file git_upy/houdini/testQt.py is part of upy.

    upy is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    upy is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with upy.  If not, see <http://www.gnu.org/licenses/gpl-3.0.html>.
"""
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 29 16:52:28 2011

@author: -
"""
# This example is from the PyQt4 tutorial and is slightly modified to
# illustrate how to integrate PyQt4 with Houdini.

from PyQt4 import QtCore
from PyQt4 import QtGui
from pyubic.houdini import hou_pyqt_helper as pyqt_houdini

class FontDialog(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        hbox = QtGui.QHBoxLayout()

        self.setGeometry(500, 300, 250, 110)
        self.setWindowTitle('FontDialog')

        button = QtGui.QPushButton('Change Font...', self)
        button.setFocusPolicy(QtCore.Qt.NoFocus)
        button.move(20, 20)

        hbox.addWidget(button)

        self.connect(button, QtCore.SIGNAL('clicked()'), self.showDialog)

        self.label = QtGui.QLabel('This is some Sample Text', self)
        self.label.move(130, 20)

        hbox.addWidget(self.label, 1)
        self.setLayout(hbox)

    def showDialog(self):
        font, ok = QtGui.QFontDialog.getFont()
        if ok:
            self.label.setFont(font)

app = QtGui.QApplication(['houdini'])
dialog = FontDialog()
dialog.show()

# The main difference from a normal PyQt application is that instead of calling
# app.exec_() you call pyqt_houdini.exec_(app, dialog1, ...).
pyqt_houdini.exec_(app, dialog)
