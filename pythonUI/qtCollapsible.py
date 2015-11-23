
"""
    Copyright (C) <2010>  Autin L. TSRI
    
    This file git_upy/pythonUI/qtCollapsible.py is part of upy.

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
#'''PyQt collapsible GroupBox
#
#http://code.google.com/p/blur-dev/
#'''
#
##
#	\namespace	blurdev.gui.widgets.accordianwidget.accordianitem
#
#	\remarks	The container class for a widget that is collapsible within the accordian widget system
#
#	\author		beta@blur.com
#	\author		Blur Studio
#	\date		04/29/10
#
#

#from PyQt4.QtGui 	import QGroupBox
try :
    from PyQt4 import QtGui,QtCore
    from PyQt4.QtCore import pyqtSignal, pyqtProperty,QEvent
    QtCore.Signal = QtCore.pyqtSignal
    QtCore.Slot = QtCore.pyqtSlot    
    from PyQt4.QtGui	import QPainter, QPainterPath, QPalette, QPixmap, QPen,QCursor,QScrollArea,QWidget,QApplication,QMatrix
except :
    try :
        from PySide import QtGui,QtCore
        from PySide.QtCore import QEvent
        pyqtSignal= QtCore.Signal
        pyqtProperty=QtCore.Property
        from PySide.QtGui	import QPainter, QPainterPath, QPalette, QPixmap, QPen,QCursor,QScrollArea,QWidget,QApplication,QMatrix
    except :
        print ("noQt support ")
Qt = QtCore.Qt
QVBoxLayout = QtGui.QVBoxLayout
#QPixmap = QtGui.QPixmap
QRect = QtCore.QRect
QMimeData = QtCore.QMimeData
QDrag = QtGui.QDrag

class AccordianItem( QtGui.QGroupBox ):
	def __init__( self, accordian, title, widget ):
		QtGui.QGroupBox.__init__( self, accordian )

		# create the layout

		layout = QVBoxLayout()
		layout.setContentsMargins( 6, 6, 6, 6 )
		layout.setSpacing( 0 )
		layout.addWidget( widget )

		self._accordianWidget = accordian
		self._rolloutStyle = 2
		self._dragDropMode = 0

		self.setAcceptDrops(True)
		self.setLayout( layout )
		self.setContextMenuPolicy( Qt.CustomContextMenu )
		self.customContextMenuRequested.connect( self.showMenu )

		# create custom properties
		self._widget		= widget
		self._collapsed		= False
		self._collapsible	= True
		self._clicked		= False
		self._customData	= {}

#		from PyQt4.QtGui import QPixmap
		import os.path
		self._pixmap = QPixmap( os.path.split( __file__ )[0] + '/triangle.png' )
		print( os.path.split( __file__ )[0] + '/triangle.png' )
		# set common properties
		self.setTitle( title )

	def accordianWidget( self ):
		"""
			\remarks	grabs the parent item for the accordian widget
			\return		<blurdev.gui.widgets.accordianwidget.AccordianWidget>
		"""
		return self._accordianWidget

	def customData( self, key, default = None ):
		"""
			\remarks	return a custom pointer to information stored with this item
			\param		key			<str>
			\param		default		<variant>	default value to return if the key was not found
			\return		<variant> data
		"""
		return self._customData.get( str(key), default )

	def dragEnterEvent( self, event ):
		if ( not self._dragDropMode ):
			return

		source = event.source()
		if ( source != self and source.parent() == self.parent() and isinstance( source, AccordianItem ) ):
			event.acceptProposedAction()

	def dragDropRect( self ):
#		from PyQt4.QtCore import QRect
		return QRect( 25, 7, 10, 6 )

	def dragDropMode( self ):
		return self._dragDropMode

	def dragMoveEvent( self, event ):
		if ( not self._dragDropMode ):
			return

		source = event.source()
		if ( source != self and source.parent() == self.parent() and isinstance( source, AccordianItem ) ):
			event.acceptProposedAction()

	def dropEvent( self, event ):
		widget = event.source()
		layout = self.parent().layout()
		layout.insertWidget( layout.indexOf(self), widget )
		self._accordianWidget.emitItemsReordered()

	def expandCollapseRect( self ):
#		from PyQt4.QtCore import QRect
		return QRect( 0, 0, self.width(), 20 )

	def enterEvent( self, event ):
		self.accordianWidget().leaveEvent( event )
		event.accept()

	def leaveEvent( self, event ):
		self.accordianWidget().enterEvent( event )
		event.accept()

	def mouseReleaseEvent( self, event ):
		if ( self._clicked and self.expandCollapseRect().contains( event.pos() ) ):
			self.toggleCollapsed()
			event.accept()
		else:
			event.ignore()

		self._clicked = False

	def mouseMoveEvent( self, event ):
		event.ignore()

	def mousePressEvent( self, event ):
		# handle an internal move
#		from PyQt4.QtCore import Qt

		# start a drag event
		if ( event.button() == Qt.LeftButton and self.dragDropRect().contains( event.pos() ) ):
#			from PyQt4.QtCore import QMimeData
#			from PyQt4.QtGui import QDrag, QPixmap

			# create the pixmap
			pixmap = QPixmap.grabWidget( self, self.rect() )

			# create the mimedata
			mimeData = QMimeData()
			mimeData.setText( 'ItemTitle::%s' % (self.title()) )

			# create the drag
			drag = QDrag(self)
			drag.setMimeData( mimeData )
			drag.setPixmap( pixmap )
			drag.setHotSpot( event.pos() )

			if ( not drag.exec_() ):
				self._accordianWidget.emitItemDragFailed(self)

			event.accept()

		# determine if the expand/collapse should occur
		elif ( event.button() == Qt.LeftButton and self.expandCollapseRect().contains( event.pos() ) ):
			self._clicked = True
			event.accept()

		else:
			event.ignore()

	def isCollapsed( self ):
		return self._collapsed

	def isCollapsible( self ):
		return self._collapsible

	def paintEvent( self, event ):
#		from PyQt4.QtCore 	import Qt
#		from PyQt4.QtGui	import QPainter, QPainterPath, QPalette, QPixmap, QPen

		painter = QPainter()
		painter.begin( self )
		painter.setRenderHint( painter.Antialiasing )

		x = self.rect().x()
		y = self.rect().y()
		w = self.rect().width() - 1
		h = self.rect().height() - 1
		r = 8

		# draw a rounded style
		if ( self._rolloutStyle == 2 ):

			# draw the text
			painter.drawText( x + 22, y + 3, w, 16, Qt.AlignLeft | Qt.AlignTop, self.title() )

			# draw the triangle
			pixmap = self._pixmap
			if ( not self.isCollapsed() ):
#				from PyQt4.QtGui import QMatrix
				pixmap = pixmap.transformed( QMatrix().rotate(90) )

			painter.drawPixmap( x + 7, y + 4, pixmap )

			# draw the borders
			pen = QPen( self.palette().color( QPalette.Light ) )
			pen.setWidthF( 0.6 )
			painter.setPen( pen )

			painter.drawRoundedRect( x + 1, y + 1, w - 1, h - 1, r, r )

			pen.setColor( self.palette().color( QPalette.Shadow ) )
			painter.setPen( pen )

			painter.drawRoundedRect( x, y, w - 1, h - 1, r, r )

		# draw a boxed style
		elif ( self._rolloutStyle == 1 ):
#			from PyQt4.QtCore import QRect
			if ( self.isCollapsed() ):
				arect 	= QRect( x + 1, y + 9, w - 1, 4 )
				brect 	= QRect( x, y + 8, w - 1, 4 )
				text 	= '+'
			else:
				arect	= QRect( x + 1, y + 9, w - 1, h - 9 )
				brect 	= QRect( x, y + 8, w - 1, h - 9 )
				text	= '-'

			# draw the borders
			pen = QPen( self.palette().color( QPalette.Light ) )
			pen.setWidthF( 0.6 )
			painter.setPen( pen )

			painter.drawRect( arect )

			pen.setColor( self.palette().color( QPalette.Shadow ) )
			painter.setPen( pen )

			painter.drawRect( brect )

			painter.setRenderHint( painter.Antialiasing, False )
			painter.setBrush( self.palette().color( QPalette.Window ).darker( 120 ) )
			painter.drawRect( x + 10, y + 1, w - 20, 16 )
			painter.drawText( x + 16, y + 1, w - 32, 16, Qt.AlignLeft | Qt.AlignVCenter, text )
			painter.drawText( x + 10, y + 1, w - 20, 16, Qt.AlignCenter, self.title() )

		if ( self.dragDropMode() ):
			rect 	= self.dragDropRect()

			# draw the lines
			l		= rect.left()
			r		= rect.right()
			cy		= rect.center().y()

			for y in (cy - 3, cy, cy + 3):
				painter.drawLine( l, y, r, y )

		painter.end()

	def setCollapsed( self, state = True ):
		if ( self.isCollapsible() ):
			accord = self.accordianWidget()
			accord.setUpdatesEnabled(False)

			self._collapsed = state

			if ( state ):
				self.setMinimumHeight( 22 )
				self.setMaximumHeight( 22 )
				self.widget().setVisible( False )
			else:
				self.setMinimumHeight( 0 )
				self.setMaximumHeight( 1000000 )
				self.widget().setVisible( True )

			self._accordianWidget.emitItemCollapsed( self )
			accord.setUpdatesEnabled(True)

	def setCollapsible( self, state = True ):
		self._collapsible = state

	def setCustomData( self, key, value ):
		"""
			\remarks	set a custom pointer to information stored on this item
			\param		key		<str>
			\param		value	<variant>
		"""
		self._customData[ str(key) ] = value

	def setDragDropMode( self, mode ):
		self._dragDropMode = mode

	def setRolloutStyle( self, style ):
		self._rolloutStyle = style

	def showMenu( self ):
#		from PyQt4.QtCore import QRect
#		from PyQt4.QtGui import QCursor
		if ( QRect( 0, 0, self.width(), 20 ).contains( self.mapFromGlobal( QCursor.pos() ) ) ):
			self._accordianWidget.emitItemMenuRequested( self )

	def rolloutStyle( self ):
		return self._rolloutStyle

	def toggleCollapsed( self ):
		self.setCollapsed( not self.isCollapsed() )

	def widget( self ):
		return self._widget

##
#	\namespace	trax.gui.widgets.accordianwidget
#
#	\remarks	A container widget for creating expandable and collapsible components
#
#	\author		beta@blur.com
#	\author		Blur Studio
#	\date		04/29/10
#
#

#from PyQt4.QtCore import pyqtSignal, pyqtProperty
#from PyQt4.QtGui 	import QScrollArea
#from accordianitem	import AccordianItem

class AccordianWidget( QScrollArea ):
	itemCollapsed 		= pyqtSignal(AccordianItem)
	itemMenuRequested	= pyqtSignal(AccordianItem)
	itemDragFailed		= pyqtSignal(AccordianItem)
	itemsReordered		= pyqtSignal()

	Boxed 		= 1
	Rounded 	= 2

	NoDragDrop 		= 0
	InternalMove	= 1

	def __init__( self, parent ):
		QScrollArea.__init__( self, parent )

		#self.setFrameShape( QScrollArea.NoFrame )
		self.setAutoFillBackground( False )
		self.setWidgetResizable( True )
		self.setMouseTracking(True)
		self.verticalScrollBar().setMaximumWidth(10)

#		from PyQt4.QtGui import QWidget
		widget = QWidget( self )

		# define custom properties
		self._rolloutStyle 	= AccordianWidget.Rounded
		self._dragDropMode 	= AccordianWidget.NoDragDrop
		self._scrolling		= False
		self._scrollInitY	= 0
		self._scrollInitVal	= 0
		self._itemClass		= AccordianItem

		# create the layout
#		from PyQt4.QtGui import QVBoxLayout

		layout = QVBoxLayout()
		layout.setContentsMargins( 3, 3, 3, 3 )
		layout.setSpacing( 3 )
		layout.addStretch(1)

		widget.setLayout( layout )

		self.setWidget( widget )
          
	def addItem( self, title, widget, collapsed = False ):
		self.setUpdatesEnabled(False)
		item 	= self._itemClass( self, title, widget )
		item.setRolloutStyle( self.rolloutStyle() )
		item.setDragDropMode( self.dragDropMode() )
		layout	= self.widget().layout()
		layout.insertWidget( layout.count() - 1, item )
		layout.setStretchFactor( item, 0 )

		if ( collapsed ):
			item.setCollapsed(collapsed)

		self.setUpdatesEnabled(True)
		return item

	def clear( self ):
		self.setUpdatesEnabled(False)
		layout = self.widget().layout()
		while ( layout.count() > 1 ):
			item = layout.itemAt(0)

			# remove the item from the layout
			w = item.widget()
			layout.removeItem( item )

			# close the widget and delete it
			w.close()
			w.deleteLater()

		self.setUpdatesEnabled(True)

	def eventFilter( self, object, event ):
#		from PyQt4.QtCore import QEvent

		if ( event.type() == QEvent.MouseButtonPress ):
			self.mousePressEvent( event )
			return True

		elif ( event.type() == QEvent.MouseMove ):
			self.mouseMoveEvent( event )
			return True

		elif ( event.type() == QEvent.MouseButtonRelease ):
			self.mouseReleaseEvent( event )
			return True

		return False

	def canScroll( self ):
		return self.verticalScrollBar().maximum() > 0

	def count( self ):
		return self.widget().layout().count() - 1

	def dragDropMode( self ):
		return self._dragDropMode

	def indexOf(self, widget):
		"""
			\remarks	Searches for widget(not including child layouts).
						Returns the index of widget, or -1 if widget is not found
			\return		<int>
		"""
		layout = self.widget().layout()
		for index in range(layout.count()):
			if layout.itemAt(index).widget().widget() == widget:
				return index
		return -1

	def isBoxedMode( self ):
		return self._rolloutStyle == AccordianWidget.Boxed

	def itemClass( self ):
		return self._itemClass

	def itemAt( self, index ):
		layout = self.widget().layout()
		if ( 0 <= index and index < layout.count() - 1 ):
			return layout.itemAt( index ).widget()
		return None

	def emitItemCollapsed( self, item ):
		if ( not self.signalsBlocked() ):
			self.itemCollapsed.emit(item)

	def emitItemDragFailed( self, item ):
		if ( not self.signalsBlocked() ):
			self.itemDragFailed.emit(item)

	def emitItemMenuRequested( self, item ):
		if ( not self.signalsBlocked() ):
			self.itemMenuRequested.emit(item)

	def emitItemsReordered( self ):
		if ( not self.signalsBlocked() ):
			self.itemsReordered.emit()

	def enterEvent( self, event ):
		if ( self.canScroll() ):
#			from PyQt4.QtCore import Qt
#			from PyQt4.QtGui import QApplication
			QApplication.setOverrideCursor( Qt.OpenHandCursor )

	def leaveEvent( self, event ):
		if ( self.canScroll() ):
#			from PyQt4.QtGui import QApplication
			QApplication.restoreOverrideCursor()

	def mouseMoveEvent( self, event ):
		if ( self._scrolling ):
			sbar 	= self.verticalScrollBar()
			smax	= sbar.maximum()

			# calculate the distance moved for the moust point
			dy 			= event.globalY() - self._scrollInitY

			# calculate the percentage that is of the scroll bar
			dval		= smax * ( dy / float(sbar.height()) )

			# calculate the new value
			sbar.setValue( self._scrollInitVal - dval )

		event.accept()

	def mousePressEvent( self, event ):
		# handle a scroll event
#		from PyQt4.QtCore import Qt
#		from PyQt4.QtGui import QApplication

		if ( event.button() == Qt.LeftButton and self.canScroll() ):
			self._scrolling 		= True
			self._scrollInitY		= event.globalY()
			self._scrollInitVal 	= self.verticalScrollBar().value()

			QApplication.setOverrideCursor( Qt.ClosedHandCursor )

		event.accept()

	def mouseReleaseEvent( self, event ):
#		from PyQt4.QtCore 	import Qt
#		from PyQt4.QtGui 	import QApplication

		if ( self._scrolling ):
			QApplication.restoreOverrideCursor()

		self._scrolling 		= False
		self._scrollInitY		= 0
		self._scrollInitVal		= 0
		event.accept()

	def moveItemDown(self, index):
		layout = self.widget().layout()
		if (layout.count() - 1) > (index + 1):
			widget = layout.takeAt(index).widget()
			layout.insertWidget(index + 1, widget)

	def moveItemUp(self, index):
		if index > 0:
			layout = self.widget().layout()
			widget = layout.takeAt(index).widget()
			layout.insertWidget(index - 1, widget)

	def setBoxedMode( self, state ):
		if ( state ):
			self._rolloutStyle = AccordianWidget.Boxed
		else:
			self._rolloutStyle = AccordianWidget.Rounded

	def setDragDropMode( self, dragDropMode ):
		self._dragDropMode = dragDropMode

		for item in self.findChildren( AccordianItem ):
			item.setDragDropMode( self._dragDropMode )

	def setItemClass( self, itemClass ):
		self._itemClass = itemClass

	def setRolloutStyle( self, rolloutStyle ):
		self._rolloutStyle = rolloutStyle

		for item in self.findChildren( AccordianItem ):
			item.setRolloutStyle( self._rolloutStyle )

	def rolloutStyle( self ):
		return self._rolloutStyle

	def takeAt( self, index ):
		self.setUpdatesEnabled(False)
		layout = self.widget().layout()
		widget = None
		if ( 0 <= index and index < layout.count() - 1 ):
			item = layout.itemAt(index)
			widget = item.widget()

			layout.removeItem(item)
			widget.close()
		self.setUpdatesEnabled(True)
		return widget

	def widgetAt( self, index ):
		item = self.itemAt( index )
		if ( item ):
			return item.widget()
		return None

	pyBoxedMode = pyqtProperty( 'bool', isBoxedMode, setBoxedMode )

#from PyQt4 import QtGui

def demoGui(GroupBox):
	GroupBox.setFlat(True)
	verticalLayout = QtGui.QVBoxLayout(GroupBox)

	formLayout = QtGui.QFormLayout()
	formLayout.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)

	monkey1Label = QtGui.QLabel(GroupBox)

	formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, monkey1Label)
	monkey1LineEdit = QtGui.QLineEdit(GroupBox)

	formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, monkey1LineEdit)
	monnkey2Label = QtGui.QLabel(GroupBox)

	formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, monnkey2Label)
	monkey3Label = QtGui.QLabel(GroupBox)

	formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, monkey3Label)
	happyCheckBoxLabel = QtGui.QLabel(GroupBox)

	formLayout.setWidget(3, QtGui.QFormLayout.LabelRole, happyCheckBoxLabel)
	happyCheckBoxCheckBox = QtGui.QCheckBox(GroupBox)

	formLayout.setWidget(3, QtGui.QFormLayout.FieldRole, happyCheckBoxCheckBox)
	comboBox = QtGui.QComboBox(GroupBox)

	comboBox.addItem('')
	comboBox.addItem('')
	comboBox.addItem('')
	comboBox.addItem('')
	formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, comboBox)
	spinBox = QtGui.QSpinBox(GroupBox)

	formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, spinBox)
	verticalLayout.addLayout(formLayout)

	GroupBox.setWindowTitle(QtGui.QApplication.translate("GroupBox", "GroupBox", None, QtGui.QApplication.UnicodeUTF8))
	monkey1Label.setText(QtGui.QApplication.translate("GroupBox", "Text", None, QtGui.QApplication.UnicodeUTF8))
	monnkey2Label.setText(QtGui.QApplication.translate("GroupBox", "Combo", None, QtGui.QApplication.UnicodeUTF8))
	monkey3Label.setText(QtGui.QApplication.translate("GroupBox", "Spin", None, QtGui.QApplication.UnicodeUTF8))
	happyCheckBoxLabel.setText(QtGui.QApplication.translate("GroupBox", "CheckBox", None, QtGui.QApplication.UnicodeUTF8))
	comboBox.setItemText(0, QtGui.QApplication.translate("GroupBox", "a", None, QtGui.QApplication.UnicodeUTF8))
	comboBox.setItemText(1, QtGui.QApplication.translate("GroupBox", "b", None, QtGui.QApplication.UnicodeUTF8))
	comboBox.setItemText(2, QtGui.QApplication.translate("GroupBox", "c", None, QtGui.QApplication.UnicodeUTF8))
	comboBox.setItemText(3, QtGui.QApplication.translate("GroupBox", "d", None, QtGui.QApplication.UnicodeUTF8))
	return GroupBox

class test(QtGui.QDialog):
    def __init__(self,parent=None):
        QtGui.QDialog.__init__(self,parent)
        self.resize(400,400)
        self.setWindowTitle("test")
        self.sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        self.setSizeGripEnabled(True)
        #self.setWidgetResizable( True )
        layout = QVBoxLayout(self)
        self.setLayout(layout)
        #layout.setWidgetResizable( True )
        dlg = AccordianWidget(self)
        dlg.addItem('a', demoGui(QtGui.QGroupBox()))
        dlg.addItem('b', demoGui(QtGui.QGroupBox()))
        dlg.addItem('c', demoGui(QtGui.QGroupBox()))
        layout.addWidget(dlg)
        
if __name__ == '__main__':
	#from PyQt4.QtGui import QApplication
	app = QApplication([])
	#app.setStyle( 'Plastique' )
	p=test()
	p.show()
	#p.adjustSize()
	app.exec_()