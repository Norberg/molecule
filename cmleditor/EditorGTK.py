#!/usr/bin/env python
import sys
import pygtk
pygtk.require("2.0")
import gtk
import gtk.glade
import gobject
import libcml.Cml as Cml

class EditorGTK:

	def __init__(self):	
		#Set the Glade file
		self.gladefile = "gui.glade" 
	        self.wTree = gtk.glade.XML(self.gladefile, "winMain") 
		self.wTree.signal_autoconnect(self)
		self.widget = self.wTree.get_widget
	def on_winMain_destroy(self, widget):
		gtk.main_quit()

	def on_btnExit_clicked(self, widget):
		gtk.main_quit()

	def on_btnSave_clicked(self, widget):
		print "saving file..."

	def on_fcbOpen_file_set(self, widget):
		self.openFile(widget.get_filename())

	def openFile(self, filename):
		molecule = Cml.Molecule()
		molecule.parse(filename)
		molecule.printer()
		tableReadOnly = self.widget("tableReadOnly")
		self.emptyContainer(tableReadOnly)
		row = 0
		for atom in molecule.atoms_sorted:
			self.createAndAttachLabel("id:"+atom.id, tableReadOnly, 0, row)
			self.createAndAttachLabel("elementType:"+atom.elementType,
			                                         tableReadOnly, 1, row)
			self.createAndAttachLabel("X:"+atom.x_str, tableReadOnly, 2, row)
			self.createAndAttachLabel("Y:"+atom.y_str, tableReadOnly, 3, row)
			row += 1
		
		for bond in molecule.bonds:
			self.createAndAttachLabel("from:"+bond.atomA.id, tableReadOnly, 0, row)
			self.createAndAttachLabel("to:"+bond.atomB.id, tableReadOnly, 1, row)
			self.createAndAttachLabel("Bonds:"+bond.bonds, tableReadOnly, 2, row)
			row += 1
		
		tableWriteable = self.widget("tableWriteable")
		self.emptyContainer(tableWriteable)
		self.txtMoleculeName = self.createAndAttachTextBox("Molecule:",
                                                                   tableWriteable,0)		
	
	def emptyContainer(self, container):
		for child in container.get_children():
			child.destroy()

	def createAndAttachLabel(self, text, table, col, row):
		label = gtk.Label(text)
		table.attach(label, col, col+1, row, row+1)
		label.set_visible(True)
		
	def createAndAttachTextBox(self,text,table, row):
		self.createAndAttachLabel(text, table, 0, row)
		entry = gtk.Entry()
		table.attach(entry, 1, 2, row, row+1)
		entry.set_visible(True)
		return entry
		
		

if __name__ == "__main__":
	GUI = EditorGTK()
	gtk.main()
