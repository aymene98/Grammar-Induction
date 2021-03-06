import sys
import re
import nltk
import os
import json
from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import *
from os import listdir
import parsing
import rule_builder
import tagging
import corpus_utils


class App(QMainWindow):

    def __init__(self):
        super().__init__()
        self.title = 'Projet TAL'
        self.left = 0
        self.top = 0
        self.width = 2000
        self.height = 1000
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.table_widget = MyTableWidget(self)
        self.setCentralWidget(self.table_widget)

        self.show()


class MyTableWidget(QWidget):
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        self.layout = QVBoxLayout(self)
        self.dir = ""
        self.lien = ""

        # Initialize tab screen
        self.tabs = QTabWidget()
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tabs.resize(300, 200)

        # Add tabs
        self.tabs.addTab(self.tab1, "Analyse")
        self.tabs.addTab(self.tab2, "Creation d'une nouvelle Grammaire")

        # adding elements
        # Label 1
        self.label1 = QLabel(self)
        self.label1.setText('Lien vers le texte à analyser : ')

        # file name
        self.myTextBox = QTextEdit(self)
        self.myTextBox.setReadOnly(True)

        # Button 1 to get folder path
        self.button1 = QPushButton(self)
        self.button1.setText('Choisir dossier')
        self.button1.clicked.connect(self.getfile)

        # Label 2
        self.label2 = QLabel(self)
        self.label2.setText('Texte : ')

        self.text = QTextEdit(self)

        # Label 2
        self.label3 = QLabel(self)
        self.label3.setText('Analyse : ')

        self.analyse = QTextEdit(self)
        self.analyse.setReadOnly(True)

        self.hidden_label = QLabel(self)
        self.hidden_label.setText('Analyse en cours...')
        self.hidden_label.setVisible(False)

        self.label6 = QLabel(self)
        self.label6.setText('Type de POS-tags a utilisé : ')

        self.cb1 = QComboBox(self)
        tags = ["POS-tag du corpus", "POS-tag modifiés", "POS-tag universels"]
        for name in tags:
            self.cb1.addItem(name)

        # Button 2 to analyse
        self.button2 = QPushButton(self)
        self.button2.setText('Analyser avec grammaire par defaut')
        self.button2.clicked.connect(self.analyser_defaut)

        self.button3 = QPushButton(self)
        self.button3.setText('Analyser avec grammaire générée')
        self.button3.clicked.connect(self.analyser_generee)

        # Create first tab
        self.tab1.layout = QVBoxLayout()
        self.tab1.layout.addWidget(self.label1)
        self.tab1.layout.addWidget(self.myTextBox)
        self.tab1.layout.addWidget(self.button1)
        self.tab1.layout.addWidget(self.label2)
        self.tab1.layout.addWidget(self.text)
        self.tab1.layout.addWidget(self.label3)
        self.tab1.layout.addWidget(self.analyse)
        self.tab1.layout.addWidget(self.hidden_label)
        self.tab1.layout.addWidget(self.label6)
        self.tab1.layout.addWidget(self.cb1)
        self.tab1.layout.addWidget(self.button2)
        self.tab1.layout.addWidget(self.button3)
        self.tab1.setLayout(self.tab1.layout)

        # Label 1
        self.label4 = QLabel(self)
        self.label4.setText('Lien vers le corpus à utiliser : ')

        # file name
        self.lien_nv_corpus = QTextEdit(self)
        self.lien_nv_corpus.setReadOnly(True)

        # Button 1 to get folder path
        self.button4 = QPushButton(self)
        self.button4.setText('Choisir dossier')
        self.button4.clicked.connect(self.getcorpus)

        self.label7 = QLabel(self)
        self.label7.setText('Type de POS-tags a utilisé : ')

        self.cb2 = QComboBox(self)
        tags = ["POS-tag du corpus", "POS-tag modifiés", "POS-tag universels"]
        for name in tags:
            self.cb2.addItem(name)

        self.tagger_label = QLabel(self)
        self.tagger_label.setVisible(False)
        self.label5 = QLabel(self)
        self.label5.setVisible(False)

        self.start_button = QPushButton(self)
        self.start_button.setText('Créer une grammire')
        self.start_button.setEnabled(False)
        self.start_button.clicked.connect(self.start_rule_building)

        # Create second tab
        self.tab2.layout = QVBoxLayout()
        self.tab2.layout.addWidget(self.label4)
        self.tab2.layout.addWidget(self.lien_nv_corpus)
        self.tab2.layout.addWidget(self.button4)
        self.tab2.layout.addWidget(self.label7)
        self.tab2.layout.addWidget(self.cb2)
        self.tab2.layout.addWidget(self.tagger_label)
        self.tab2.layout.addWidget(self.label5)
        self.tab2.layout.addWidget(self.start_button)
        self.tab2.setLayout(self.tab2.layout)

        # Add tabs to widget
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

    def getcorpus(self):
        self.lien = QFileDialog.getExistingDirectory(
            None, 'Select a folder:', './', QFileDialog.ShowDirsOnly)
        self.lien_nv_corpus.setText(self.lien)
        self.start_button.setEnabled(True)

    def start_rule_building(self):
        self.start_button.setEnabled(False)
        name = "_all_new"
        simplify_tags, universal = False, False

        if self.cb2.currentText() == "POS-tag modifiés":
            simplify_tags = True
            name = "_simplified_new"
        if self.cb2.currentText() == "POS-tag universels":
            universal = True
            name = "_universal_new"

        # create tagger
        self.tagger_label.setVisible(True)
        self.tagger_label.setText("Création d'un étiqueteur POS-tag...")
        self.tagger_worker = tagging.TaggerCreator(
            corpus_path=self.lien+"/", filename="tagger"+name+".p", simplify_tags=simplify_tags, universal=universal)
        self.tagger_worker.start()
        self.tagger_worker.finished.connect(self.on_tagger_worker_finish)
        # create grammar
        self.label5.setVisible(True)
        sen_pos_tags = corpus_utils.retrieve_corpus_sen_pos_tags(
            self.lien+'/', sen_limit=100, simplify_tags=simplify_tags, universal=universal)
        self.rule_worker = rule_builder.RuleBuilder(
            sen_pos_tags=sen_pos_tags, filename='./rules/rules'+name+".txt")
        self.rule_worker.start()
        self.rule_worker.progress_update.connect(self.on_rule_worker_progress)
        self.rule_worker.finished.connect(self.on_rule_worker_finish)

    def on_tagger_worker_finish(self):
        self.tagger_label.setText("Étiqueteur POS-tag créé")
        if self.rule_worker.isFinished():
            self.start_button.setEnabled(True)

    def on_rule_worker_finish(self):
        self.label5.setText("Grammaire créée")
        if self.tagger_worker.isFinished():
            self.start_button.setEnabled(True)

    def on_rule_worker_progress(self, val):
        self.label5.setText("Création de la grammaire... %d%%" % val)

    def getfile(self):
        self.dir = QFileDialog.getExistingDirectory(
            None, 'Select a folder:', './', QFileDialog.ShowDirsOnly)
        self.myTextBox.setText(self.dir)
        self.get_text()

    def analyser_defaut(self):
        #self.get_text()
        self.hidden_label.setVisible(True)
        self.button2.setEnabled(False)
        self.button3.setEnabled(False)
        rules_path = "./rules/rules_full_tags.txt"
        if self.cb1.currentText() == "POS-tag modifiés":
            rules_path = "./rules/rules_simplified_tags.txt"
        if self.cb1.currentText() == "POS-tag universels":
            rules_path = "./rules/rules_universal_tags.txt"
        print(self.cb1.currentText())
        print(rules_path)
        g = open(rules_path, "r", encoding="utf-8").read()
        grammar = parsing.get_grammar_string(g)
        self.parser_worker = parsing.Parser(grammar=grammar, text=self.text.toPlainText(
        ), tagger_type=self.cb1.currentText(), new=False)
        # result = parsing.parse(
        #     grammar, self.text.toPlainText(), self.cb1.currentText(), new=False)
        self.parser_worker.start()
        self.parser_worker.sents_and_trees.connect(self.on_parse_finish)
        # self.print_text(result)

    def analyser_generee(self):
        #self.get_text()
        self.hidden_label.setVisible(True)
        self.button2.setEnabled(False)
        self.button3.setEnabled(False)
        # TODO : change the grammar path to match the tags ...
        rules_path = "./rules/rules_all_new.txt"
        if self.cb2.currentText() == "POS-tag modifiés":
            rules_path = "./rules/rules_simplified_new.txt"
        if self.cb2.currentText() == "POS-tag universels":
            rules_path = "./rules/rules_universal_new.txt"

        g = open(rules_path, "r", encoding="utf-8").read()
        grammar = parsing.get_grammar_string(g)
        # result = parsing.parse(
        #     grammar, self.text.toPlainText(), self.cb1.currentText(), new=True)
        # self.print_text(result)
        self.parser_worker = parsing.Parser(grammar=grammar, text=self.text.toPlainText(
        ), tagger_type=self.cb1.currentText(), new=False)
        self.parser_worker.start()
        self.parser_worker.sents_and_trees.connect(self.on_parse_finish)

    def on_parse_finish(self, res):
        self.print_text(res)
        self.hidden_label.setVisible(False)
        self.button2.setEnabled(True)
        self.button3.setEnabled(True)

    def get_text(self):
        corpus = ""
        if self.dir:
            file_names = [file for file in listdir(
                self.dir) if re.match(r'[\w\d]+', file)]
            for name in file_names:
                print(self.dir+"/"+name)
                corpus += open(self.dir+"/"+name, "r", encoding="utf-8").read()

        text = self.text.toPlainText()
        self.text.setText(text + "\n" + corpus)

    def print_text(self, result):
        analyse = ""
        not_parsed = ''
        for sent in result:
            analyse += str(sent[0]) + "\n" + str(sent[1]) + \
                "\n" + str(sent[2]) + "\n"
            if sent[2] == []:
                not_parsed += str(sent[0]) + "\n" + str(sent[1]) + "\n"

        not_parsed_file = open("not_parsed_file.txt", "a")
        not_parsed_file.write(not_parsed)
        not_parsed_file.close()
        self.analyse.setText(analyse)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
