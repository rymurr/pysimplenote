
import sys
import simplenote
from PyQt4.QtCore import *
from PyQt4.QtGui import *

#sort items in content list by modifydate
#remove deleted items from screen
#store copy of data offline --- another class which stores and such?
#use proper security measures 
#set up to sync every X seconds
#sync before shutting down
#add button for new note
#add search
#add option to rename title
#remove title from content before being displayed
#add columns
#add tagging and revisions
#add views and stuff similar to notational velocity
#add to revision control and send to simple note mailing list
#make website and integrate into general me-site
#make packages for OSs and set up on linux box

class Form(QDialog):

    def __init__(self, parent=None):
        super(Form,self).__init__(parent)

        email='rymurr@gmail.com'
        password = 
        self.notes=simplenote.Simplenote(email,password)
        self.titles,self.content = self.notes.get_content()
        self.rtitles = dict((v,k) for k, v in self.titles.iteritems())
        tList = [v for k, v in self.titles.iteritems()]
        #tList = [1,2,3,4]

        self.titleList = QListWidget()
        self.titleList.addItems(QStringList(map(QString, tList)))
        self.noteEdit = QTextEdit()


        layout = QHBoxLayout()
        layout.addWidget(self.titleList,1)
        layout.addWidget(self.noteEdit,4)
        self.setLayout(layout)
        self.setWindowTitle("QSnote")
        self.connect(self.titleList,SIGNAL("itemSelectionChanged()"),self.print_item)

    def print_item(self):
        item=self.titleList.currentItem()
        self.noteEdit.clear()
        self.noteEdit.setText(QString(self.content[self.rtitles[str(item.text())]]['content']))

app = QApplication(sys.argv)
form = Form()
form.show()
app.exec_()
