from sys import argv as sys_argv, exit as sys_exit
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QTableWidgetItem
import numpy as np

# Initialisation of variables to be used in case that there is no file to open.
from DefaultVariables import DefaultInit as DefaultVariablesInit, Const

Const.RowSize = 25
Const.ColumnSize = 90
Const.MyApp = QtWidgets.QApplication(sys_argv)
Const.DI = DefaultVariablesInit()

VOutput_ForTest = np.array([0])


def ExitFunction():
    print("Exit")
    Const.MyApp.quit()


# InitTable: Init a table with row and column number. Init also the size of table
def InitTable(Table, RowNb, CoulmnNb, CoordX, CoordY):
    # Set row and column number
    Table.setRowCount(RowNb)
    Table.setColumnCount(CoulmnNb)
    # Set rows height
    for row in range(RowNb):
        Table.setRowHeight(row, Const.RowSize)
    # Set column height
    for column in range(CoulmnNb):
        Table.setColumnWidth(column, Const.ColumnSize)
    Table.setGeometry(QtCore.QRect(CoordX, CoordY, CoulmnNb * Const.ColumnSize + 2, RowNb * Const.RowSize + 2))


class TestWindow(QtWidgets.QMainWindow, QtCore.QObject):
    def __init__(self, parent=None):
        from QtUi_test.test import Ui_MainWindow_test
        assert isinstance(parent, object)
        super().__init__(parent)
        QtWidgets.QMainWindow().__init__(self)
        self.ui = Ui_MainWindow_test()
        self.ui.setupUi(self)
        self.ui.Close_test.clicked.connect(ExitFunction)
        self.ui.actionExit.triggered.connect(ExitFunction)
        self.LoadData()
        self.InitAllTab()

    def LoadData(self):
        # Load Default data if there is no file to load.
        self.LoadDefaultData()

    def LoadDefaultData(self):
        self.Vparcelle = Const.DI.Vparcelle_Init
        self.NbParcelle = Const.DI.NbParcelle_Init

        self.VparcelleTaille = Const.DI.VparcelleTaille_Init

        self.VparcelleTypeSol = Const.DI.VparcelleTypeSol_Init
        self.NbParcelleTypeSol = Const.DI.NbParcelleTypeSol_Init

        self.Vculture = Const.DI.Vculture_Init
        self.NbCulture = Const.DI.NbCulture_Init

        self.Vtypesol = Const.DI.Vtypesol_Init
        self.NbTypeSol = Const.DI.NbTypeSol_Init

        self.NbSimuPerYear = Const.DI.NbSimuPerYear_Init

        self.NbAnneeSimulee = Const.DI.NbAnneeSimulee_Init
        self.PailleMin = Const.DI.PailleMin_Init
        self.EnsilageMin = Const.DI.EnsilageMin_Init

        self.VInputN_1 = Const.DI.VInputN_1_Init

    def InitAllTab(self):
        # Init config tab
        self.InitConfigTab()

        # Init Input table:
        self.InitInputTab()

        # Init output tab
        self.InitOutputTab()

        self.WrapperModelInput()

    # InitConfigTab: Init tables in tab "Configuration"
    def InitConfigTab(self):
        ConfCultureTable = self.ui.ConfigCultureTypeTable
        InitTable(ConfCultureTable, 1, self.NbCulture, 0, 25)
        # No Header

        for Culture in range(self.NbCulture):
            # Init Row with culture names
            ConfCultureTable.setItem(0, Culture, QTableWidgetItem(self.Vculture[Culture]))

        self.ui.NbYearSimulationBox.setValue(self.NbAnneeSimulee)
        self.ui.NbSimuPerYearBox.setValue(self.NbSimuPerYear)
        # On change:
        ConfCultureTable.itemChanged.connect(self.OnChange_ConfCultureTable)

    # OnChange_ConfCultureTable: Method called on change event in ConfigCultureTypeTable
    def OnChange_ConfCultureTable(self):
        ConfCultureTable = self.ui.ConfigCultureTypeTable
        row = ConfCultureTable.currentRow()
        col = ConfCultureTable.currentColumn()
        if row == 0:
            # Update culture vector with update
            self.Vculture[col] = ConfCultureTable.item(row, col).text()

            # Update "Entrée" with new Vculture value
            InTable = self.ui.ParcelCultureInputTable
            for Parcelle in range(self.NbParcelle):
                InTable.cellWidget(Parcelle + 1, 1).setItemText(col, self.Vculture[col])

    def FillVInputN_1_ForTest(self):
        culture = 0
        self.VInputN_1.resize(self.NbParcelle)
        for Parcelle in range(self.NbParcelle):
            culture = (culture + 1) % self.NbCulture
            self.VInputN_1[Parcelle] = culture

    # InitInputTab: Init tables in tab "Entrées"
    def InitInputTab(self):
        InTable = self.ui.ParcelCultureInputTable
        InitTable(InTable, self.NbParcelle + 1, 3, 0, 0)
        # Fill Header
        InTable.setItem(0, 0, QTableWidgetItem("Parcelle"))
        InTable.setItem(0, 1, QTableWidgetItem("Culture n-1"))
        InTable.setItem(0, 2, QTableWidgetItem("Taille Parcelle"))

        # self.FillVInputN_1_ForTest()

        for Parcelle in range(self.NbParcelle):
            # Fill Row Header with parcel names
            InTable.setItem(Parcelle + 1, 0, QTableWidgetItem(self.Vparcelle[Parcelle]))
            # Fill first column with input of n-1 year
            # Create list box selection for culture, based on what is in config tab
            combo = QtWidgets.QComboBox()
            for t in self.Vculture:
                combo.addItem(t)
            InTable.setCellWidget(Parcelle + 1, 1, combo)
            InTable.cellWidget(Parcelle + 1, 1).setCurrentIndex(self.VInputN_1[Parcelle])
            InTable.setItem(Parcelle + 1, 2, QTableWidgetItem(str(self.VparcelleTaille[Parcelle])))

        # On change:
        InTable.itemChanged.connect(self.OnChange_InputTable)

    # OnChange_InputTable: Method called on change event in ParcelCultureInputTable
    def OnChange_InputTable(self):
        InTable = self.ui.ParcelCultureInputTable
        row = InTable.currentRow()
        col = InTable.currentColumn()
        if col == 0:
            # Update culture vector with update
            self.Vparcelle[row - 1] = InTable.item(row, col).text()

            # Update "Résultats" with new Vparcelle value
            self.ui.tableWidget.setItem(row, 0, QTableWidgetItem(self.Vparcelle[row - 1]))

    # InitOutputTab: Init tables in tab "Résultats"
    def InitOutputTab(self):
        self.InitCultureOutputTable(self.ui.tableWidget)
        self.FillOutputTable()
        self.InitReportOutputTable(self.ui.tableMarginConstraint)
        self.ui.IndexBestResultBox.setMaximum(self.NbSimuPerYear - 1)
        self.ui.IndexBestResultBox.valueChanged.connect(self.FillOutputTable)

    # InitCultureOutputTable: Init culture output table with header
    def InitCultureOutputTable(self, CultOutTab):
        # Set culture output table
        InitTable(CultOutTab, self.NbParcelle + 1, self.NbAnneeSimulee + 2, 0, 0)
        # Fill Column header with {Parcelle, n-1, n, ..., n + x} with x = NbAnneeSimulee - 1
        CultOutTab.setItem(0, 0, QTableWidgetItem("Parcelle"))
        CultOutTab.setItem(0, 1, QTableWidgetItem("n - 1"))
        CultOutTab.setItem(0, 2, QTableWidgetItem("n"))
        for Year in range(self.NbAnneeSimulee - 1):
            CultOutTab.setItem(0, Year + 3, QTableWidgetItem("n + " + str(Year + 1)))

        for Parcelle in range(self.NbParcelle):
            # Fill Row Header with parcel names
            CultOutTab.setItem(Parcelle + 1, 0, QTableWidgetItem(self.Vparcelle[Parcelle]))
            # Fill first column with input of n-1 year
            CultOutTab.setItem(Parcelle + 1, 1, QTableWidgetItem(self.Vculture[self.VInputN_1[Parcelle]]))

    # InitReportOutputTable: Init report table with header
    def InitReportOutputTable(self, OutReportTab):
        # Set Margin and constraint table
        InitTable(OutReportTab, 3, self.NbAnneeSimulee + 2, 0, (self.NbParcelle + 1) * Const.RowSize + 2)
        # Fill Row header
        OutReportTab.setItem(0, 0, QTableWidgetItem("Marge"))
        OutReportTab.setItem(1, 0, QTableWidgetItem("Qtt paille"))
        OutReportTab.setItem(2, 0, QTableWidgetItem("Qtt ensilage"))

    def FillVOutput_ForTest(self, NbAnnees, NbParcelle, NbBestResult):
        culture = 0
        VOutput_ForTest.resize(NbBestResult, NbAnnees, NbParcelle)
        for NumResult in range(NbBestResult):
            for Year in range(NbAnnees):
                for Parcelle in range(NbParcelle):
                    culture = (culture + 1) % self.NbCulture
                    VOutput_ForTest[NumResult][Year][Parcelle] = culture

    # FillOutputTable: Fill the output table with culture associated with
    def FillOutputTable(self):
        CultOutTab = self.ui.tableWidget
        self.FillVOutput_ForTest(self.NbAnneeSimulee, self.NbParcelle, self.NbSimuPerYear)
        IndexBestResult = self.ui.IndexBestResultBox.value()
        for Year in range(self.NbAnneeSimulee):
            for Parcelle in range(self.NbParcelle):
                index = VOutput_ForTest[IndexBestResult][Year][Parcelle]
                CultOutTab.setItem(Parcelle + 1, Year + 2,
                                   QTableWidgetItem(self.Vculture[index]))


    def WrapperModelInput(self):
        self.ModelInput = {}
        # Format MPCn1
        MPCn1 = np.zeros((self.NbParcelle, self.NbCulture))
        for Parcelle in range(self.NbParcelle):
            MPCn1[Parcelle][self.VInputN_1[Parcelle]] = 1
        self.ModelInput["MPCn1"] = MPCn1
        # print("MPCn1 = ")
        # print(self.ModelInput["MPCn1"])

        # Format MPTS
        MPTS = np.zeros((self.NbParcelle, self.NbTypeSol))
        for Parcelle in range(self.NbParcelle):
            MPTS[Parcelle][self.VparcelleTypeSol[Parcelle]] = 1
        self.ModelInput["MPTS"] = MPTS
        # print("MPCn1 = ")
        # print(self.ModelInput["MPTS"])

        # Format surfaces
        self.ModelInput["surface"] = self.VparcelleTaille
        # print("surface = ")
        # print(self.ModelInput["surface"])

        # Format numPailleMin
        self.ModelInput["numPailleMin"] = self.PailleMin
        # print("numPailleMin = ")
        # print(self.ModelInput["numPailleMin"])

        # Format numEnsilageMin
        self.ModelInput["numEnsilageMin"] = self.EnsilageMin
        # print("numEnsilageMin = ")
        # print(self.ModelInput["numEnsilageMin"])

        # Format numYear
        self.ModelInput["numYear"] = self.NbAnneeSimulee
        # print("numYear = ")
        # print(self.ModelInput["numEnsilageMin"])

        # Format numSolutionYear
        self.ModelInput["numSolutionYear"] = self.NbSimuPerYear
        # print("numSolutionYear = ")
        # print(self.ModelInput["numSolutionYear"])


if __name__ == "__main__":
    # Instantiation du Main
    TestApp = TestWindow()
    TestApp.show()

    sys_exit(Const.MyApp.exec_())
