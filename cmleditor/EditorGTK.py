# Molecule - a chemical reaction puzzle game
# Copyright (C) 2013 Simon Norberg <simon@pthread.se>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#!/usr/bin/env python
import sys
import os
import pygtk
import glob 
import gtk
import gtk.glade
import gobject
import libcml.Cml as Cml
import cml2img
from subprocess import call
import time
class EditorGTK:

    def __init__(self):
        sys.excepthook = self.excepthook    
        self.gladefile = "cmleditor/gui.gtkbuilder"
        self.builder = gtk.Builder()
        self.builder.add_from_file(self.gladefile)
        self.widget = self.builder.get_object
        self.window = self.widget("winMain").show()
        self.widget("fcbOpen").set_current_folder("data/molecule")
        self.builder.connect_signals(self)
        self.folder = "data/molecule/"
        self.init_twStates()

    def init_twStates(self):
        twStates = self.widget("twStates")
        #set what data type twStates shulld contain
        self.modelStates = gtk.ListStore(gobject.TYPE_STRING,\
        gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING)
        twStates.set_model(self.modelStates)
        self.modelStateNames = gtk.ListStore(gobject.TYPE_STRING)
        self.modelStateNames.append(["Solid"])
        self.modelStateNames.append(["Aqueous"])
        self.modelStateNames.append(["Gas"])
        self.modelStateNames.append(["Liquid"])
        cell = gtk.CellRendererText()
        cmbStates = self.widget("cmbStates")
        cmbStates.set_model(self.modelStateNames)
        cmbStates.pack_start(cell, True)
        cmbStates.add_attribute(cell, "text", 0)
        #create columns
        edit0 = gtk.CellRendererText()
        #edit0.set_property('editable', True)
        edit0.connect('edited', self.edited_string, (self.modelStates, 0))
        edit1 = gtk.CellRendererText()
        edit1.set_property('editable', True)
        edit1.connect('edited', self.edited_float, (self.modelStates, 1))
        edit2 = gtk.CellRendererText()
        edit2.set_property('editable', True)
        edit2.connect('edited', self.edited_float, (self.modelStates, 2))
        edit3 = gtk.CellRendererText()
        edit3.set_property('editable', True)
        edit3.connect('edited', self.edited_ions, (self.modelStates, 3))

        col1 = gtk.TreeViewColumn("State", edit0, text=0)
        col2 = gtk.TreeViewColumn("Enthalpy", edit1, text=1)
        col3 = gtk.TreeViewColumn("Entropy", edit2, text=2)
        col4 = gtk.TreeViewColumn("Ions", edit3, text=3)
        twStates.append_column(col1)
        twStates.append_column(col2)
        twStates.append_column(col3)
        twStates.append_column(col4)

    def on_winMain_destroy(self, widget):
        gtk.main_quit()

    def on_btnExit_clicked(self, widget):
        gtk.main_quit()

    def on_btnSave_clicked(self, widget):
        self.molecule.states = dict()
        for col in self.modelStates:
            name = col[0]
            enthalpy = col[1] if col[1] != "" else None
            entropy = col[2] if col[2] != "" else None
            ions = col[3].split(',') if col[3] != "" else None    
            state = Cml.State(name, enthalpy, entropy, ions)
            self.molecule.states[name] = state
        self.molecule.property["Name"] = self.txtMoleculeName.get_text()
        if self.molecule.is_atom:
            self.molecule.property["Weight"] = float(self.txtAtomWeight.get_text())
            self.molecule.property["Radius"] = float(self.txtAtomRadius.get_text())
        self.molecule.write(self.filename)

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

    def update_folder_list(self):
        self.folder_list = glob.glob(self.folder+"/*")
        self.folder_list.sort()


    def on_fcbOpen_file_set(self, widget):
        new_folder = widget.get_current_folder()
        if self.folder != new_folder:
            self.folder = new_folder
            self.update_folder_list()

        self.openFile(widget.get_filename())    

    def openFile(self, filename):
        self.filename = filename
        self.current_pos = self.folder_list.index(filename)
        molecule = Cml.Molecule()
        self.molecule = molecule
        molecule.parse(filename)
        formula = filename.split("/")[-1].split(".cml")[0] 
        state_formula = formula+"(g)"
        cml2img.convert_cml2png(state_formula, "preview.png")
        pixBuffPreview = gtk.gdk.pixbuf_new_from_file("preview.png")
        imgPreview = self.widget("imgPreview")
        imgPreview.set_from_pixbuf(pixBuffPreview)
        
        tableWriteable = self.widget("tableWriteable")
        self.emptyContainer(tableWriteable)
        self.txtMoleculeName = self.createAndAttachTextBox("Name:",
                                   tableWriteable,0)
        self.txtMoleculeName.set_text(str(molecule.property.get("Name", "")))

        if self.molecule.is_atom:
            self.readAtomSettings()
        else:
            pass
        
        self.modelStates.clear()
        for state in molecule.states.values():
            stateList = [state.name, state.enthalpy, state.entropy, state.ions_str]
            stateList = [x if x is not None else "" for x in stateList]
            self.modelStates.append(stateList)
    
    def readAtomSettings(self):
        tableWriteable = self.widget("tableWriteable")
        molecule = self.molecule
        self.txtAtomWeight = self.createAndAttachTextBox("Weight:",
                                   tableWriteable,1)        
        self.txtAtomWeight.set_text(str(molecule.property.get("Weight","")))
        self.txtAtomRadius = self.createAndAttachTextBox("Radius:",
                                   tableWriteable,2)        
        self.txtAtomRadius.set_text(str(molecule.property.get("Radius","")))

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

    def edited_string(self, cell, path, new_text, userdata):
        model, col_num = userdata
        iter = model.get_iter(path)
        model.set(iter, col_num,new_text)

    def edited_float(self, cell, path, new_text, userdata):
        if new_text != "":
            new_text = "%.1f" % float(new_text)
        model, col_num = userdata
        iter = model.get_iter(path)
        model.set(iter, col_num,new_text)

    def edited_ions(self, cell, path, new_text, userdata):
        model, col_num = userdata
        iter = model.get_iter(path)
        model.set(iter, col_num,new_text)

    def on_btnAddState_clicked(self, widget):
        new_state = self.widget("cmbStates").get_active_text()
        if not self.state_already_added(new_state):
            self.modelStates.append([new_state, "", "", ""])    

    def state_already_added(self, statename):
        for state in self.modelStates:
            if state[0] == statename:
                return True
        return False
    
    def on_twStates_key_press_event(self,widget, userdata):
        if gtk.gdk.keyval_name(userdata.keyval) == "Delete":
            model, iter = self.widget("twStates").get_selection().get_selected()
            if iter:
                model.remove(iter)

    def on_btnNewMolecule_clicked(self, widget):
        answers = InputBox("Molecule", ["Formula:", "SMILES:"])
        print(answers)
        if answers is None:
            return
        formula, smiles = answers
        path = "data/molecule/%s.cml" % formula
        if os.path.isfile(path):
            res = YesNo("Molecule already exist, do you want to overwrite?")
            if res == "No":
                return
        ret = call(["obabel", "-:%s" % smiles, "-h", "--gen2d", "-ocml", "-O", path])
        MsgBox("Creating molecule...")
        self.update_folder_list()
        self.widget("fcbOpen").set_filename(path)    
        self.on_fcbOpen_file_set(self.widget("fcbOpen"))

    def excepthook(self, type, value, traceback):
        MsgBox("Error:"+ str(type) +"\n"+ str(value))
        sys.__excepthook__(type, value, traceback)

        


def MsgBox(message):
        dialog = gtk.MessageDialog(None,
                gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                gtk.MESSAGE_INFO, gtk.BUTTONS_OK,
                message)
        dialog.run()
        dialog.destroy()

def YesNo(message):
        dialog = gtk.MessageDialog(None,
                gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                gtk.MESSAGE_QUESTION, gtk.BUTTONS_YES_NO,
                message)
        response = dialog.run()
        dialog.destroy()
        if response == -8:
                return "Yes"
        else:
                return "No"

def responseToDialog(entry, dialog, response):
    dialog.response(response)
    
def InputBox(title, questions):
    dialog = gtk.Dialog(title, None, 0,
    (gtk.STOCK_OK, gtk.RESPONSE_OK,
    "Cancel", gtk.RESPONSE_CANCEL))
    dialog.set_resizable(False)
    hbox = gtk.HBox(False, 8)
    hbox.set_border_width(8)
    dialog.vbox.pack_start(hbox, False, False, 0)

    stock = gtk.image_new_from_stock(
            gtk.STOCK_DIALOG_QUESTION,
            gtk.ICON_SIZE_DIALOG)
    hbox.pack_start(stock, False, False, 0)
    table = gtk.Table(2, 2)
    table.set_row_spacings(4)
    table.set_col_spacings(4)
    hbox.pack_start(table, True, True, 0)
    entryBoxes = list()
    pos = 0
    for question in questions:
        label = gtk.Label(question)
        label.set_use_underline(True)
        table.attach(label, 0, 1, pos, pos+1)
        entry = gtk.Entry()
        entry.connect("activate", responseToDialog, dialog, gtk.RESPONSE_OK)
        table.attach(entry, 1, 2, pos, pos+1)
        label.set_mnemonic_widget(entry)
        entryBoxes.append(entry)
        pos += 1
        
    dialog.show_all()
    response = dialog.run()
    if response == gtk.RESPONSE_OK:
            answers = list()
    else:
        dialog.destroy()
        return None
    
    for entryBox in entryBoxes:
        answers.append(entryBox.get_text())
    dialog.destroy()
    return answers
