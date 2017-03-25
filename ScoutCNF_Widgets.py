import os
import numpy as np
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import Qt

# Widget for the search line edit
class keyPressQLineEdit(QtWidgets.QLineEdit):
    keyPressed=QtCore.pyqtSignal()

    def __init__(self, parent):
        super(keyPressQLineEdit, self).__init__(parent)
        self.foodDescs=[]
        self.connectList=''
        self.portionList=''
        
    def keyPressEvent(self, event):
        super(keyPressQLineEdit, self).keyPressEvent(event)
        if event.key() == Qt.Key_Return:
            self.searchFoodDescs()
    
    def searchFoodDescs(self):
        self.portionList.clear()
        # Allow having multiple words split by comma
        curTextArr=self.text().lower().split(',')
        self.connectList.clear()
        similarFoodDescs=[]
        # Have to search this way, as some weird characters crash this
        for entry in self.foodDescs:
            try:
                lowCaseEntry=entry.lower()
                found=True
                for text in curTextArr:
                    if text not in lowCaseEntry:
                        found=False
                        break
                if found: similarFoodDescs.append(entry)
            except:
                continue
        # Add wanted items to list
        for entry in sorted(similarFoodDescs):
            self.connectList.addItem(entry)
            
# Widget for the output directory line
class keyPressQLineEdit2(QtWidgets.QLineEdit):
    keyPressed=QtCore.pyqtSignal()

    def __init__(self, parent):
        super(keyPressQLineEdit2, self).__init__(parent)
        
    def keyPressEvent(self, event):
        super(keyPressQLineEdit2, self).keyPressEvent(event)
        if event.key() == Qt.Key_Up:
            name=str(QtWidgets.QFileDialog.getExistingDirectory(self, "Select Folder"))
            if name!='': 
                self.setText(name)
            
# Widget for the analysis page line edits
class keyPressQLineEdit3(QtWidgets.QLineEdit):
    keyPressed=QtCore.pyqtSignal()

    def __init__(self, parent):
        super(keyPressQLineEdit3, self).__init__(parent)
        self.connectList=''
        
    def keyPressEvent(self, event):
        super(keyPressQLineEdit3, self).keyPressEvent(event)
        if event.key() == Qt.Key_Up:
            name=str(QtWidgets.QFileDialog.getExistingDirectory(self, "Select Folder"))
            if name!='': 
                self.setText(name)
        elif event.key() == Qt.Key_Return:
            curText=self.text()
            self.connectList.clear()
            count=0
            for aFile in sorted(os.listdir(curText)):
                if '.csv' not in aFile:
                    continue
                count+=1
                self.connectList.addItem(aFile.replace('\\','/'))
            if count==0:
                'No .csv files located in the specified directory'
            
            
        