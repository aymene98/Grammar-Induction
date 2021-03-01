import sys
import re, nltk
from PyQt5.QtWidgets import *
from os import listdir
import parsing

class App(QMainWindow):

    def __init__(self):
        super().__init__()
        self.title = 'Projet vision'
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
        self.label1.setText('Lien vers corpus à analyser : ')

        # file name
        self.myTextBox = QTextEdit(self)
        self.myTextBox.setReadOnly(True)

        # Button 1 to get folder path
        self.button1 = QPushButton(self)
        self.button1.setText('Choisir dossier')
        self.button1.clicked.connect(self.getfile)

        # Label 2
        self.label2 = QLabel(self)
        self.label2.setText('Text : ')

        self.text = QTextEdit(self)

        # Label 2
        self.label3 = QLabel(self)
        self.label3.setText('Analyse : ')

        self.analyse = QTextEdit(self)
        self.analyse.setReadOnly(True)

        # Button 2 to analyse
        self.button2 = QPushButton(self)
        self.button2.setText('Analyser avec grammaire par defaut')
        self.button2.clicked.connect(self.analyser)

        self.button3 = QPushButton(self)
        self.button3.setText('Analyser avec grammaire génerée')
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

        self.label5 = QLabel(self)
        self.label5.setText('')

        # Create second tab
        self.tab2.layout = QVBoxLayout()
        self.tab2.layout.addWidget(self.label4)
        self.tab2.layout.addWidget(self.lien_nv_corpus)
        self.tab2.layout.addWidget(self.button4)
        self.tab2.setLayout(self.tab2.layout)
        
        # Add tabs to widget
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

    def getcorpus(self):
        self.lien = QFileDialog.getExistingDirectory(
            None, 'Select a folder:', './', QFileDialog.ShowDirsOnly)
        self.lien_nv_corpus.setText(self.lien)
        self.label5.setText("Création de la grammaire")
        # have to create the grammar here and save it to the path './grammar_generee.cfg'
        self.label5.setText("Grammaire créée")
    
    def getfile(self):
        self.dir = QFileDialog.getExistingDirectory(
            None, 'Select a folder:', './', QFileDialog.ShowDirsOnly)
        self.myTextBox.setText(self.dir)

    def analyser(self):
        corpus = ""
        if self.dir:
            file_names = [file for file in listdir(self.dir)]
            for name in file_names:
                corpus+= open(self.dir+"/"+name, "r").read()
        
        text = self.text.toPlainText()
        self.text.setText(text + corpus)
        
        g = open('./rules.txt', "r").read()
        grammar = parsing.get_grammar_string(g)
        
        result = parsing.parse(grammar, self.text.toPlainText())
        analyse = ""
        not_parsed = ''
        for sent in result:
            analyse += str(sent[0]) + "\n" + str(sent[1]) + "\n" + str(sent[2]) + "\n"
            if sent[2] == []:
                not_parsed += str(sent[0]) + "\n" + str(sent[1]) + "\n"
        
        not_parsed_file = open("not_parsed_file.txt", "a")
        not_parsed_file.write(not_parsed)
        not_parsed_file.close()
        self.analyse.setText(analyse)
    
    def analyser_generee(self):
        file_names = [file for file in listdir(self.dir)]
        corpus = ""
        for name in file_names:
            corpus+= open(self.dir+"/"+name, "r").read()

        grammar = parsing.get_grammar_path('./grammar_generee.cfg')
        result = parsing.parse(grammar, corpus)
        # needs some processing before print ...
        self.analyse.setText(str(result))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
