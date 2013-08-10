#!/usr/bin/env python
import sys
import pygtk
import glob 
import gtk
import gtk.glade
import gobject
import libcml.Cml as Cml
import cml2img

class EditorGTK:

	def __init__(self):	
		#Set the Glade file
		#self.gladefile = "cmleditor/gui.glade" 
	        #self.wTree = gtk.glade.XML(self.gladefile, "winMain") 
		#self.wTree.signal_autoconnect(self)
		#self.widget = self.wTree.get_widget
		self.gladefile = "cmleditor/gui.gtkbuilder"
		self.builder = gtk.Builder()
		self.builder.add_from_file(self.gladefile)
		self.widget = self.builder.get_object
		self.window = self.widget("winMain").show()
		print self.widget("fcbOpen").set_current_folder("data/molecule")
		self.builder.connect_signals(self)
		self.folder = None

	def on_winMain_destroy(self, widget):
		gtk.main_quit()

	def on_btnExit_clicked(self, widget):
		gtk.main_quit()

	def on_btnSave_clicked(self, widget):
		print "saving file..."

	def on_btnNext_clicked(self, widget):
		self.switch_molecule(1)

	def on_btnPrev_clicked(self, widget):
		self.switch_molecule(-1)

	def switch_molecule(self, relative):
		new_index = (self.current_pos + relative)
		if new_index > len(self.folder_list)-1:
			new_index = 0
		elif new_index < 0:
			new_index = len(self.folder_list)-1
		newFile = self.folder_list[new_index]
		self.widget("fcbOpen").set_filename(newFile)
		self.openFile(newFile)

	def on_fcbOpen_file_set(self, widget):
		new_folder = widget.get_current_folder()
		if self.folder != new_folder:
			self.folder = new_folder
			self.folder_list = glob.glob(self.folder+"/*")
			self.folder_list.sort()

		self.openFile(widget.get_filename())
		

	def openFile(self, filename):
		self.current_pos = self.folder_list.index(self.widget("fcbOpen").get_filename())
		molecule = Cml.Molecule()
		molecule.parse(filename)
		cml2img.convert_cml2png(filename, "preview.png")
		pixBuffPreview = gtk.gdk.pixbuf_new_from_file("preview.png")
		imgPreview = self.widget("imgPreview")
		imgPreview.set_from_pixbuf(pixBuffPreview)
		tableReadOnly = self.widget("tableReadOnly")
		self.emptyContainer(tableReadOnly)
		row = 0
		for bond in molecule.bonds:
			self.createAndAttachLabel("from:"+bond.atomA.id, tableReadOnly, 0, row)
			self.createAndAttachLabel("to:"+bond.atomB.id, tableReadOnly, 1, row)
			self.createAndAttachLabel("Bonds:"+str(bond.bonds), tableReadOnly, 2, row)
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
