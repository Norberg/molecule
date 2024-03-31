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
import gi
import glob
from itertools import product

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository.GdkPixbuf import Pixbuf
from gi.repository import GObject
import libcml.Cml as Cml
import cml2img
from subprocess import call
from libcml import CachedCml
from libreact.Reaction import Reaction, list_without_state
from libreact.Reactor import Reactor
import subprocess
from cmleditor import wiki_fetch

class EditorGTK:

    def __init__(self):
        sys.excepthook = self.excepthook
        self.gladefile = "cmleditor/gui.gtkbuilder"
        self.builder = Gtk.Builder()
        self.builder.add_from_file(self.gladefile)
        self.widget = self.builder.get_object
        self.window = self.widget("winMain").show()
        self.widget("fcbOpen").set_current_folder("data/molecule")
        self.builder.connect_signals(self)
        self.folder = "data/molecule/"
        self.init_twStates()
        self.init_twReactions()
        self.init_reactions()
        self.handle_command_arguments()

    def init_reactions(self):
        cml = Cml.Reactions()
        cml.parse("data/reactions.cml")
        self.reactor = Reactor(cml.reactions)

    def init_twReactions(self):
        twReactions = self.widget("twReactions")
        #set what data type twStates twReactions should contain
        self.reactionStates = Gtk.ListStore(str, str, str)
        twReactions.set_model(self.reactionStates)
        #create columns
        edit0 = Gtk.CellRendererText()
        edit1 = Gtk.CellRendererText()
        edit2 = Gtk.CellRendererText()

        col1 = Gtk.TreeViewColumn("Reactants", edit0, text=0)
        col2 = Gtk.TreeViewColumn("Products", edit1, text=1)
        col3 = Gtk.TreeViewColumn("Temperature (K)", edit2, text=2)
        twReactions.append_column(col1)
        twReactions.append_column(col2)
        twReactions.append_column(col3)

    def init_twStates(self):
        twStates = self.widget("twStates")
        #set what data type twStates shulld contain
        self.modelStates = Gtk.ListStore(str, str, str, str)
        twStates.set_model(self.modelStates)
        self.modelStateNames = Gtk.ListStore(str)
        self.modelStateNames.append(["Solid"])
        self.modelStateNames.append(["Aqueous"])
        self.modelStateNames.append(["Gas"])
        self.modelStateNames.append(["Liquid"])
        cell = Gtk.CellRendererText()
        cmbStates = self.widget("cmbStates")
        cmbStates.set_model(self.modelStateNames)
        cmbStates.pack_start(cell, True)
        cmbStates.add_attribute(cell, "text", 0)
        #init licenses
        self.widget("cmbLicense").pack_start(cell, True)
        self.widget("cmbLicense").add_attribute(cell, "text", 0)
        #create columns
        edit0 = Gtk.CellRendererText()
        #edit0.set_property('editable', True)
        #edit0.connect('edited', self.edited_string, (self.modelStates, 0))
        edit1 = Gtk.CellRendererText()
        edit1.set_property('editable', True)
        edit1.connect('edited', self.edited_float, (self.modelStates, 1))
        edit2 = Gtk.CellRendererText()
        edit2.set_property('editable', True)
        edit2.connect('edited', self.edited_float, (self.modelStates, 2))
        edit3 = Gtk.CellRendererText()
        edit3.set_property('editable', True)
        edit3.connect('edited', self.edited_ions, (self.modelStates, 3))

        col1 = Gtk.TreeViewColumn("State", edit0, text=0)
        col2 = Gtk.TreeViewColumn("Enthalpy", edit1, text=1)
        col3 = Gtk.TreeViewColumn("Entropy", edit2, text=2)
        col4 = Gtk.TreeViewColumn("Ions", edit3, text=3)
        twStates.append_column(col1)
        twStates.append_column(col2)
        twStates.append_column(col3)
        twStates.append_column(col4)

    def on_winMain_destroy(self, widget):
        Gtk.main_quit()

    def on_btnExit_clicked(self, widget):
        Gtk.main_quit()

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
        textbuffer = self.widget("textbufferDescription")
        start_iter = textbuffer.get_start_iter()
        end_iter = textbuffer.get_end_iter()
        description = textbuffer.get_text(start_iter, end_iter, True)
        self.molecule.property["Description"] = description
        self.molecule.property["DescriptionAttribution"] = self.widget("txtAttribution").get_text()
        self.molecule.property["DescriptionLicense"] = get_active_text(self.widget("cmbLicense"))
        if self.molecule.is_atom:
            self.molecule.property["Weight"] = float(self.txtAtomWeight.get_text())
            self.molecule.property["Radius"] = float(self.txtAtomRadius.get_text())
        self.molecule.write(self.filename)
        CachedCml.evictFromCache(self.formula)
        self.updateReactions(self.formula)

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
        self.formula = filename.split("/")[-1].split(".cml")[0]
        state_formula = self.formula+"(aq)"
        cml2img.convert_cml2png(state_formula, "preview.png")
        pixBuffPreview = Pixbuf.new_from_file("preview.png")
        imgPreview = self.widget("imgPreview")
        imgPreview.set_from_pixbuf(pixBuffPreview)

        self.txtMoleculeName = self.widget("txtName")
        self.txtAtomWeight = self.widget("txtWeight")
        self.txtAtomRadius = self.widget("txtRadius")

        self.txtMoleculeName.set_text(str(molecule.property.get("Name", "")))
        self.widget("txtAttribution").set_text(
                molecule.property.get("DescriptionAttribution", ""))
        self.widget("textbufferDescription").set_text(
                molecule.property.get("Description", ""))

        if self.molecule.is_atom:
            self.setAtomSettings()
        else:
            self.txtAtomWeight.set_text("")
            self.txtAtomWeight.set_sensitive(False)
            self.txtAtomRadius.set_text("")
            self.txtAtomRadius.set_sensitive(False)

        self.modelStates.clear()
        for state in molecule.states.values():
            stateList = [state.name, state.enthalpy, state.entropy, state.ions_str]
            stateList = [str(x) if x is not None else "" for x in stateList]
            self.modelStates.append(stateList)

        self.setLicense(molecule.property.get("DescriptionLicense", "N/A"))
        self.updateReactions(self.formula)

    def setLicense(self, selectedLicense):
        self.widget("cmbLicense").set_active(-1)
        index = 0
        for license in self.widget("liststoreLicenses"):
            if license[0] == selectedLicense:
                self.widget("cmbLicense").set_active(index)
                break
            index += 1

    def updateReactions(self, formula):
        #Refresh the reactions in case the reaction file have been changed
        self.init_reactions()
        self.reactionStates.clear()
        for reaction in self.reactor.reactions:
            if formula not in reaction.reactants and formula not in list_without_state(reaction.products):
                 continue
            state_permutations = addStatePermutations(reaction.reactants)
            for reactants in state_permutations:
                expected_products = reaction.products
                reactions = self.findReactingTemperatures(reactants, expected_products)
                if len(reactions) == 0:
                    reactingTemp_str = "Never occurs"
                    reactants_str = " + ".join(reactants)
                    expected_products_str = " + ".join(expected_products)
                    self.reactionStates.append([str(reactants_str), str(expected_products_str), str(reactingTemp_str)])

                for reaction in reactions.values():
                    reactants_str = " + ".join(reaction.reactants)
                    expected_products_str = " + ".join(reaction.products)
                    reactingTemp_str = " , ".join([str(temp) for temp in reaction.temperatures])
                    self.reactionStates.append([str(reactants_str), str(expected_products_str), str(reactingTemp_str)])

    def findReactingTemperatures(self, reactants, expected_products, trace = False):
        if trace:
            print("\nFinding reacting temperatures for:", reactants, expected_products)
        tempranges = [0, 50, 298, 773, 1000, 2000, 4000, 8000]
        result = None
        reactions = dict()
        for temp in tempranges:
            result = self.reactor.react(reactants, temp, trace=trace)
            if result is not None and expected_products == result.products:
                reaction = ReactionInfo(result)
                if reactions.get(reaction.key) is None:
                    reactions[reaction.key] = ReactionInfo(result)
                reactions[reaction.key].temperatures.append(temp)
        return reactions



    def setAtomSettings(self):
        self.txtAtomWeight.set_sensitive(True)
        self.txtAtomRadius.set_sensitive(True)
        molecule = self.molecule
        self.txtAtomWeight.set_text(str(molecule.property.get("Weight","")))
        self.txtAtomRadius.set_text(str(molecule.property.get("Radius","")))

    def emptyContainer(self, container):
        for child in container.get_children():
            child.destroy()

    def createAndAttachLabel(self, text, table, col, row):
        label = Gtk.Label(label=text)
        table.attach(label, col, row, col+1, row+1)
        label.set_visible(True)

    def createAndAttachTextBox(self,text,table, row):
        self.createAndAttachLabel(text, table, 0, row)
        entry = Gtk.Entry()
        table.attach(entry, 1, row, 2, row+1)
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
        cmbStates = self.widget("cmbStates")
        new_state = get_active_text(cmbStates)
        if not self.state_already_added(new_state):
            self.modelStates.append([new_state, "","", ""])

    def state_already_added(self, statename):
        for state in self.modelStates:
            if state[0] == statename:
                return True
        return False

    def on_twStates_key_press_event(self,widget, userdata):
        if Gdk.keyval_name(userdata.keyval) == "Delete":
            model, iter = self.widget("twStates").get_selection().get_selected()
            if iter:
                model.remove(iter)

    def on_twReactions_key_press_event(self, widget, userdata):
        #if pressed t/T trace the reaction
        if Gdk.keyval_name(userdata.keyval) == "t" or Gdk.keyval_name(userdata.keyval) == "T":
            model, iter = self.widget("twReactions").get_selection().get_selected()
            if iter:
                reactants = model[iter][0].split(" + ")
                products = model[iter][1].split(" + ")
                self.findReactingTemperatures(reactants, products, trace = True)

    def on_twReactions_row_activated(self, widget, path, column):
        """When a cell is double clicked allow user to select bettween the molecules in that cell to open in the editor"""
        if column.get_title() == "Temperature (K)":
            return
        model = widget.get_model()
        iter = model.get_iter(path)    
        columns = widget.get_columns()
        column_index = columns.index(column)
        molecules = model.get_value(iter, column_index).split(" + ")
        molecules = list_without_state(molecules)
        if len(molecules) == 1:
            self.widget("fcbOpen").set_filename("data/molecule/"+molecules[0]+".cml")
            self.openFile("data/molecule/"+molecules[0]+".cml")
        else:
            dialog = Gtk.Dialog(title="Select molecule to open", parent=self.widget("winMain"), flags=0)
            dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK)
            dialog.set_default_response(Gtk.ResponseType.OK)

            combo = Gtk.ComboBoxText()
            for mol in molecules:
                combo.append_text(mol)
            combo.set_active(0)
            
            box = dialog.get_content_area()
            box.add(combo)
            dialog.show_all()

            response = dialog.run()
            if response == Gtk.ResponseType.OK:
                selected_molecule = combo.get_active_text()
                self.widget("fcbOpen").set_filename(f"data/molecule/{selected_molecule}.cml")
                self.openFile(f"data/molecule/{selected_molecule}.cml")
            dialog.destroy()

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
        result = subprocess.run(["obabel", "-:%s" % smiles.strip(), "-h", "--gen2d", "-ocml", "-O", path], capture_output=True, text=True)
        print("Obabel response:", result.stdout)
        print(result.stderr)
        if ("0 molecule"  in result.stderr):
            MsgBox("Could not create molecule from SMILES " + result.stderr)
            return
        MsgBox("Creating molecule...")
        self.update_folder_list()
        self.widget("fcbOpen").set_filename(path)
        self.on_fcbOpen_file_set(self.widget("fcbOpen"))
    
    def on_btnNewMoleculeFromWiki_clicked(self, widget):
        answers = InputBox("Molecule", ["Wikipedia link:"])
        print(answers)
        if answers is None:
            return
        url = answers[0]
        wiki = wiki_fetch.extract_wikipedia_info(url)

        formula = wiki.chemical_formula
        smiles = wiki.smiles
        path = "data/molecule/%s.cml" % formula
        if os.path.isfile(path):
            res = YesNo(f"Molecule {formula} already exist, do you want to overwrite?")
            if res == "No":
                return
        result = subprocess.run(["obabel", "-:%s" % smiles.strip(), "-h", "--gen2d", "-ocml", "-O", path], capture_output=True, text=True)
        print("Obabel response:", result.stdout)
        print(result.stderr)
        if ("0 molecule"  in result.stderr):
            MsgBox("Could not create molecule from SMILES " + result.stderr)
            return
        MsgBox("Creating molecule...")
        self.update_folder_list()
        self.widget("fcbOpen").set_filename(path)
        self.on_fcbOpen_file_set(self.widget("fcbOpen"))
        self.txtMoleculeName.set_text(wiki.name)
        self.setLicense("CC BY-SA 3.0")
        self.widget("txtAttribution").set_text(url)

        self.widget("textbufferDescription").set_text(wiki.summary + "\nEnthalpy:" + str(wiki.std_enthalpy_of_formation) + "\nEntropy:" + str(wiki.std_molar_entropy))

    def excepthook(self, type, value, traceback):
        MsgBox("Error:"+ str(type) +"\n"+ str(value))
        sys.__excepthook__(type, value, traceback)

    def handle_command_arguments(self):
        """Handle command line arguments with parseargs"""
        import argparse
        parser = argparse.ArgumentParser(description="Molecule editor")
        parser.add_argument("-m", "--molecule", help="Open a molecule file")
        args = parser.parse_args()
        if args.molecule:
            self.update_folder_list()
            self.widget("fcbOpen").set_filename("data/molecule/"+args.molecule + ".cml")
            self.openFile("data/molecule/"+args.molecule + ".cml")

def addStatePermutations(stateless):
    states_per_molecule = []
    for formula in stateless:
        m = CachedCml.getMolecule(formula)
        available_states = []
        for state in ["Aqueous", "Gas", "Liquid", "Solid"]:
            if state in m.states and m.states[state].ions is None:
                available_states.append(m.states[state].short)
        if not available_states:
            print(f"No state found for {formula}")
            return []
        states_per_molecule.append([f"{formula}({state})" for state in available_states])

    all_permutations = product(*states_per_molecule)

    unique_permutations_set = set()
    unique_permutations = []

    for permutation in all_permutations:
        sorted_permutation = sorted(permutation)
        if (str(sorted_permutation) in unique_permutations_set):
            continue
        unique_permutations_set.add(str(sorted_permutation))
        unique_permutations.append(sorted_permutation)

    return unique_permutations

def get_active_text(cmb):
    tree_iter = cmb.get_active_iter()
    model = cmb.get_model()
    return model[tree_iter][0]

def MsgBox(message):
        dialog = Gtk.MessageDialog(None,
                Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                Gtk.MessageType.INFO, Gtk.ButtonsType.OK,
                message)
        dialog.run()
        dialog.destroy()

def YesNo(message):
        dialog = Gtk.MessageDialog(None,
                Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                Gtk.MessageType.QUESTION, Gtk.ButtonsType.YES_NO,
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
    dialog = Gtk.Dialog(title, None, 0,
    (Gtk.STOCK_OK, Gtk.ResponseType.OK,
    "Cancel", Gtk.ResponseType.CANCEL))
    dialog.set_resizable(False)
    hbox = Gtk.HBox(False, 8)
    hbox.set_border_width(8)
    dialog.vbox.pack_start(hbox, False, False, 0)

    stock = Gtk.Image.new_from_stock(
            Gtk.STOCK_DIALOG_QUESTION,
            Gtk.IconSize.DIALOG)
    hbox.pack_start(stock, False, False, 0)
    table = Gtk.Table(2, 2)
    table.set_row_spacings(4)
    table.set_col_spacings(4)
    hbox.pack_start(table, True, True, 0)
    entryBoxes = list()
    pos = 0
    for question in questions:
        label = Gtk.Label(label=question)
        label.set_use_underline(True)
        table.attach(label, 0, 1, pos, pos+1)
        entry = Gtk.Entry()
        entry.connect("activate", responseToDialog, dialog, Gtk.ResponseType.OK)
        table.attach(entry, 1, 2, pos, pos+1)
        label.set_mnemonic_widget(entry)
        entryBoxes.append(entry)
        pos += 1

    dialog.show_all()
    response = dialog.run()
    if response == Gtk.ResponseType.OK:
            answers = list()
    else:
        dialog.destroy()
        return None

    for entryBox in entryBoxes:
        answers.append(entryBox.get_text())
    dialog.destroy()
    return answers

class ReactionInfo:
    def __init__(self, reaction):
        self.reaction = reaction
        self.temperatures = list()
        self.reactants = reaction.reactants
        self.products = reaction.products

    @property
    def key(self):
        return str(self.reaction.reactants)+ "->" + str(self.reaction.products)