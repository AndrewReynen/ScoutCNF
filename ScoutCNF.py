import sys
import numpy as np
import sip
import csv
sip.setapi('QVariant', 2)
sip.setapi('QString', 2)
from PyQt5 import QtWidgets
from ScoutCNF_UI2 import Ui_MainWindow

# Version: 0.0.3
# Author: Andrew Reynen

# Main window class
class ScoutCNF(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.loadDataBase()
        self.setFunctionality()
        # Will hold information of item just added to portion list
        self.curItem={'Factor':0.0,'Desc':'Nothing!','FoodID':-1}
        # Will hold all information of items which have been added to selected food list
        self.curSelection=[]
        
    def loadDataBase(self):
        # Load the food categories        
        self.loadFoodGroups()
        # Load all the foods
        self.loadFoodItems()
        # Load the measurement units
        self.loadMeasureAndConversion()
        # Load nutrient information
        self.loadNutrientConversion()
        
    # Start setting up some functionality to the UI
    def setFunctionality(self):
        # Give function to the food category list
        self.foodCategoryList.itemDoubleClicked.connect(self.showFoodGroup)
        # Give function to the searched food list
        self.specFoodList.itemDoubleClicked.connect(self.showFoodPortions)
        # Give function to the add selected item button
        self.addSelectionButton.clicked.connect(self.addCurItem)
        # Give function to the selected item list
        self.selectedFoodList.itemDoubleClicked.connect(self.removeItemSelectedList)
        # Give function to the save selected items button
        self.saveSelectionButton.clicked.connect(self.saveCurSelection)
        # Give function to the analysis page widgets
        self.RDI_DirLineEntry.connectList=self.RDI_SummaryList
        self.subjectDirLineEntry.connectList=self.subjectSummaryList
        self.subjectSummaryList.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.compareButton.clicked.connect(self.compareSummaries)

    # Make the list of food categories to choose from
    def loadFoodGroups(self):
        info=loadQuotedCSV('./cnf-fcen-csv/FOOD GROUP.csv',skip_header=1)
        # Add items to the internal dictionary
        self.foodGroup={}
        for aEntry in info:
            self.foodGroup[aEntry[2]]=int(aEntry[0])
        # Add items to the GUI
        self.updateList(self.foodCategoryList,info[:,2])
    
    # Load all of the foods present in the database
    def loadFoodItems(self):
        info=loadQuotedCSV('./cnf-fcen-csv/FOOD NAME.csv',skip_header=1)
        self.foodItems={}
        self.foodItems['ID']=info[:,0].astype(int)
        self.foodItems['GroupID']=info[:,2].astype(int)
        self.foodItems['Desc']=info[:,4].astype(str)
        # Add this to the search line edit variable
        self.searchEntryLine.foodDescs=self.foodItems['Desc']
        self.searchEntryLine.connectList=self.specFoodList
        self.searchEntryLine.portionList=self.foodPortionList
        
    # Load all of the measurement types and conversion factors
    def loadMeasureAndConversion(self):
        info=loadQuotedCSV('./cnf-fcen-csv/MEASURE NAME.csv',skip_header=1)
        self.measure={}
        self.measure['ID']=info[:,0].astype(int)
        self.measure['Desc']=info[:,1].astype(str)
        info=loadQuotedCSV('./cnf-fcen-csv/CONVERSION FACTOR.csv',skip_header=1)
        self.conv={}
        self.conv['FoodID']=info[:,0].astype(int)
        self.conv['MeasID']=info[:,1].astype(int)
        self.conv['Factor']=info[:,2].astype(float)
    
    # Load in the nutrient conversions, and labels
    def loadNutrientConversion(self):
        info=loadQuotedCSV('./cnf-fcen-csv/NUTRIENT AMOUNT.csv',skip_header=1)
        self.nutrAmount={}
        self.nutrAmount['FoodID']=info[:,0].astype(int)
        self.nutrAmount['NutrID']=info[:,1].astype(int)
        self.nutrAmount['Value']=info[:,2].astype(float)
        info=loadQuotedCSV('./cnf-fcen-csv/NUTRIENT NAME.csv',skip_header=1)
        self.nutrients={}
        self.nutrients['ID']=list(info[:,0].astype(int))
        self.nutrients['Unit']=info[:,3].astype(str)
        self.nutrients['Name']=['"'+aName+'"' for aName in info[:,2].astype(str)]
        
    # If double clicked on a category, list out the category
    def showFoodGroup(self):
        foodGroupID=self.foodGroup[self.foodCategoryList.currentItem().text()]
        self.updateList(self.specFoodList,self.foodItems['Desc'][np.where(self.foodItems['GroupID']==foodGroupID)])
            
    def showFoodPortions(self):
        # Get the current food item selected
        item=str(self.specFoodList.currentItem().text())
        foodID=self.foodItems['ID'][np.where(self.foodItems['Desc']==item)[0][0]]
        # Get its conversion factors, and the names of the conversion
        convArgs=np.where(self.conv['FoodID']==foodID)
#        print(foodID) ## ##
        measIDs=self.conv['MeasID'][convArgs]
        convFactors=self.conv['Factor'][convArgs]
        # Not all conversion factors are seen, take which are
        portionDescr=[]
        usedConvFactors=[]
        for i,aID in enumerate(measIDs):
            wantArg=np.where(self.measure['ID']==aID)[0]
            if len(wantArg)==0:
                continue
            usedConvFactors.append(convFactors[i])
            portionDescr.append(self.measure['Desc'][wantArg][0])
        if len(portionDescr)==0:
            print 'Measurement IDs were not properly linked in the database'
        self.updateList(self.foodPortionList,portionDescr)
        # Update the current item information (if it is to be added)
        self.curItem['Factor']=usedConvFactors
        self.curItem['PortionDesc']=portionDescr
        self.curItem['Desc']=item
        self.curItem['FoodID']=foodID
    
    # Add current item with given portion, to selected item list
    def addCurItem(self):
        try: 
            curPortion=float(self.portionEntryLine.text())
        except:
            print 'Enter a number into the portion line'
            return
        # See which measurement unit was selected
        curPorIdx=self.foodPortionList.currentRow()
        if curPorIdx==-1:
            print 'Select a measurement unit'
            return
        curMeasUnit=self.foodPortionList.currentItem().text()
        # Give a name to the current selection
        selectString=str(curPortion)+' _x_ '+curMeasUnit+' # '+self.curItem['Desc']
        # Add the item to the internal list & GUI list (if not already there)
        if selectString in [self.selectedFoodList.item(i).text() for 
                            i in range(self.selectedFoodList.count())]:
            print 'Item is already in the selected list'
        else:
            cnfPortionFactor=self.curItem['Factor'][self.curItem['PortionDesc'].index(curMeasUnit)]
            self.curSelection.append([self.curItem['Desc'],self.curItem['FoodID'],cnfPortionFactor*curPortion,selectString])
            self.selectedFoodList.addItem(selectString)
        
    # Remove an item from the selected list if double clicked
    def removeItemSelectedList(self):
        removeItem=self.selectedFoodList.currentItem().text()
        self.selectedFoodList.takeItem(self.selectedFoodList.currentRow())
        for i in range(len(self.curSelection)):
            if self.curSelection[i][3]==removeItem:
                self.curSelection.pop(i)
                break

    # Save the current selection to wanted output directory
    def saveCurSelection(self):
        if len(self.curSelection)==0:
            print 'No foods have been added to the selected list'
            return
        outLoc=self.outputDirEntryLine.text().replace('\\','/')
        if outLoc=='':
            print 'Output file location line is empty'
            return
        outArr=[]
        # Collect all of the nutrients relating to each
        for aEntry in self.curSelection:
            aFoodDesc,aFoodID,aPortion=aEntry[0:3]
            aFoodQuant,aFoodUnit=(aEntry[3].split(' # ')[0]).split(' _x_ ')
#            print aFoodDesc,aFoodID,aPortion,aFoodQuant,aFoodUnit ## ##
            # Look for the nutrient amounts for this FoodID
            nutrAmountArgs=np.where(self.nutrAmount['FoodID']==aFoodID)[0]
            nutrIDs=self.nutrAmount['NutrID'][nutrAmountArgs]
            nutrAmounts=self.nutrAmount['Value'][nutrAmountArgs]
            # For each nutrient, get its amount from this food, and add to output array
            for aNutrID,aNutrAmount in zip(nutrIDs,nutrAmounts):
                nutrArg=self.nutrients['ID'].index(aNutrID)
                nutrName=self.nutrients['Name'][nutrArg]
                nutrUnit=self.nutrients['Unit'][nutrArg]
                outArr.append([aFoodID,aFoodDesc,nutrName,nutrUnit,aNutrAmount*aPortion,aFoodQuant,aFoodUnit])
        # Replace any weird quotes
        for i in range(len(outArr)):
            for j in range(len(outArr[i])):
                outArr[i][j]=str(outArr[i][j]).replace('"','')
        outArr=np.array(outArr,dtype=str)
        sumArr=[]
        seenNutr=np.unique(outArr[:,2])
        # For each nutrient, sum up contribution
        for aNutr in seenNutr:
            wantArgs=np.where(outArr[:,2]==aNutr)[0]
            nutrSum=np.sum(outArr[wantArgs,4].astype(float))
            sumArr.append([-999,'SUMMARY',aNutr,outArr[wantArgs[0]][3],nutrSum,'NAN','NAN'])
        saveArr=np.vstack((outArr,np.array(sumArr,dtype=str)))
        # Save the array
        np.savetxt(outLoc+'.csv',saveArr,delimiter=';',fmt='%s')
            
    # Generic function to update a list
    def updateList(self,listWidget,listEntries):
        listWidget.clear()
        for aEntry in sorted(listEntries):
            listWidget.addItem(aEntry)
    
    # Compare the two summaries, and print out comparison
    def compareSummaries(self):
        # Initial checks to make sure inputs are present
        if self.RDI_SummaryList.currentRow()==-1:
            print 'No RDI file is selected'
            return
        if self.subjectSummaryList.currentRow()==-1:
            print 'No subject file is selected'
            return
        if self.outputDirEntryLine_2.text()=='':
            print 'Enter the output comparison file location'
            return
        try:
            numDays=float(self.numDaysLineEntry.text())
        except:
            print 'Enter the number of days'
            return
        # Load in the reference summaries
        refFile=self.RDI_SummaryList.currentItem().text()
        refInfo=loadSemiCSV(self.RDI_DirLineEntry.text()+'/'+refFile,skip_header=0)
        ## Could sort the ref file here for the nutrients names ##
        # Load in the subject summaries
        subjInfos=[]
        subjFiles=[]
        for aItem in self.subjectSummaryList.selectedItems():
            subjFiles.append(aItem.text())
            subjInfos.append(loadSemiCSV(self.subjectDirLineEntry.text()+'/'+aItem.text(),skip_header=0))
        subjInfos=np.array(subjInfos)
        seenNutr=refInfo[:,2]
        seenNutrUnits=refInfo[:,3]
        if len(seenNutr)!=len(np.unique(refInfo[:,2])):
            print 'Some nutrients have multiple entries in the reference summary'
            return
        # Start generating the output array...
        # ... make the header
        Header=['','Quantity','Units']
        for aNutr,aUnit in zip(seenNutr,seenNutrUnits):
            Header.append('"'+aNutr+' '+aUnit+'"')
        # ... make the reference total
        refTotalLine=['RDI Total','','']
        for i in range(len(seenNutr)):
            refTotalLine.append(float(refInfo[i,4]))
        # ...make the subject total, as well as the header lines
        subjTotalLine=['Subject Average','','']
        subjHeaderLines=[[aFile.replace('.csv',''),'',''] for aFile in subjFiles]
        for aNutr in seenNutr:
            # sum up all the values for this nutrient (dont assume it has summary lines)
            nutrSum=0.0
            for i,anArr in enumerate(subjInfos):
                wantRows=np.where((anArr[:,2]==aNutr)&(anArr[:,1]!='SUMMARY'))[0]
                if len(wantRows)==0:
                    thisArrSum=0
                else:
                    thisArrSum=np.sum(anArr[wantRows,4].astype(float))
                subjHeaderLines[i].append(thisArrSum)
                nutrSum+=thisArrSum/numDays # Divide when looking at the total
            subjTotalLine.append(nutrSum)
        # ... make the percentage of subject vs. RDI
        percLine=['% of RDI','','']
        noteLine=['Note','','']
        for i in range(len(seenNutr)):
            aPerc=100.0*subjTotalLine[i+3]/refTotalLine[i+3]
            percLine.append(aPerc)
            if aPerc>=150.0:
                noteLine.append('H')
            elif aPerc<=75.0:
                noteLine.append('L')
            else:
                noteLine.append('')
        # ... make lines for each input subject file
        subjFullLines=[]
        for i,anArr in enumerate(subjInfos):
            subjFullLines.append(subjHeaderLines[i])
            foodDescFull=np.array([aEntry[0]+aEntry[5]+aEntry[6] for aEntry in anArr])
            # For each unique description, get the nutrient values in order...
            for aUnqDescr in np.unique(foodDescFull):
                wantArgs=np.where(foodDescFull==aUnqDescr)[0]
                # Skip if this is a summary line
                if anArr[wantArgs[0],1]=='SUMMARY':
                    continue
                subjFullLines.append(['"'+anArr[wantArgs[0],1]+'"',
                                      anArr[wantArgs[0],5],anArr[wantArgs[0],6]])
                wantArr=anArr[wantArgs]
                for aNutr in seenNutr:
                    nutrArgs=np.where(wantArr[:,2]==aNutr)[0]
                    if len(nutrArgs)==0:
                        subjFullLines[-1].append('')
                        continue
                    subjFullLines[-1].append(wantArr[nutrArgs[0],4])       
                
        # Output the file
#        print np.array(Header).shape
#        print np.array(refTotalLine).shape
#        print np.array(subjTotalLine).shape
#        print np.array(percLine).shape
#        print np.array(noteLine).shape
#        print np.array(subjFullLines).shape
        outArr=np.array([Header,refTotalLine,subjTotalLine,percLine,noteLine]+
                         subjFullLines,dtype=str)
        np.savetxt(self.outputDirEntryLine_2.text()+'.csv',outArr,fmt='%s',delimiter=';')
            
# Load a CSV with quotes
def loadQuotedCSV(csvFileLoc,skip_header=1):
    with open(csvFileLoc, 'rb') as f:
        reader = csv.reader(f)
        ignoreRange=range(0,skip_header)
        info=np.array([row for i,row in enumerate(reader) if i not in ignoreRange])
    return info

def loadSemiCSV(csvFileLoc,skip_header=1):
    info=np.genfromtxt(csvFileLoc,delimiter=';',dtype=str,skip_header=skip_header)
    return info

def my_excepthook(type, value, tback):
    # log the exception here
    print tback
    # then call the default handler
    sys.__excepthook__(type, value, tback)

# Start up the logging and UI
if __name__ == "__main__":
    sys.excepthook = my_excepthook
#    loadQuotedCSV('./testDir/andrewBF.csv')
#    loadQuotedCSV('./referenceDir/reference.csv')
#    quit()
    # Start up the UI
    app = QtWidgets.QApplication(sys.argv)
    window = ScoutCNF()
    window.show()
    sys.exit(app.exec_())