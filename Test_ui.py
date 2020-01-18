from sys import argv as sys_argv, exit as sys_exit
import numpy as np
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QTableWidgetItem

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
        # QtWidgets.QMainWindow().__init__(self)
        self.ui = Ui_MainWindow_test()
        self.ui.setupUi(self)

        # Default data loading
        self.Vparcelle = Const.DI.Vparcelle_Init
        self.NbParcelle = Const.DI.NbParcelle_Init

        self.VparcelleTaille = Const.DI.VparcelleTaille_Init

        self.VparcelleTypeSol = Const.DI.VparcelleTypeSol_Init
        self.NbParcelleTypeSol = Const.DI.NbParcelleTypeSol_Init

        self.Vculture = Const.DI.Vculture_Init
        self.NbCulture = Const.DI.NbCulture_Init
        self.VredementCulture = Const.DI.VredementCulture_Init
        self.VculturePrice = Const.DI.VculturePrice_Init
        self.VcultureProdPrice = Const.DI.VcultureProdPrice_Init
        self.VredementCulturePaille = Const.DI.VredementCulturePaille_Init
        self.VredementCultureEnsilage = Const.DI.VredementCultureEnsilage_Init
        self.VredementCultureLuzerne = Const.DI.VredementCultureLuzerne_Init
        self.VcultureIft = Const.DI.VcultureIft_Init

        self.Vtypesol = Const.DI.Vtypesol_Init
        self.NbTypeSol = Const.DI.NbTypeSol_Init

        self.QttPailleMin = Const.DI.QttPailleMin_Init
        self.QttEnsilageMin = Const.DI.QttEnsilageMin_Init
        self.QttLuzerneMin = Const.DI.QttLuzerneMin_Init

        self.NbSimuPerYear = Const.DI.NbSimuPerYear_Init
        self.NbAnneeSimulee = Const.DI.NbAnneeSimulee_Init
        self.NbBestResult = Const.DI.NbBestResult_Init

        self.VparcelleCulture_N_1 = Const.DI.VparcelleCulture_N_1_Init

        # start with empty dictionary for the input of the model
        self.ModelInput = {}

        self.InitMenu()
        self.InitAllTab()

    def InitMenu(self):
        self.ui.Close_test.clicked.connect(ExitFunction)
        self.ui.actionExit.triggered.connect(ExitFunction)
        self.ui.StartCalculation.clicked.connect(self.OnClick_StartCalculation)

    def InitAllTab(self):
        # Init config tab
        self.InitConfigTab()

        # Init Input table:
        self.InitInputTab()

        # Init output tab
        self.InitOutputTab()

    # InitConfigTab: Init tables in tab "Configuration"
    def InitConfigTab(self):
        # ConfCultureTable
        ConfCultureTable = self.ui.ConfigCultureTypeTable
        NbRow = 8
        InitTable(ConfCultureTable, NbRow, self.NbCulture + 1, 0, 25)
        Geometrie = ConfCultureTable.geometry()
        Geometrie.setWidth(Geometrie.width() + 150 - Const.ColumnSize)
        ConfCultureTable.setGeometry(Geometrie)
        # Header
        ConfCultureTable.setColumnWidth(0, 150)
        ConfCultureTable.setItem(0, 0, QTableWidgetItem("Culture"))
        ConfCultureTable.setItem(1, 0, QTableWidgetItem("Rdt (t/ha)"))
        ConfCultureTable.setItem(2, 0, QTableWidgetItem("Prix de vente (€/t)"))
        ConfCultureTable.setItem(3, 0, QTableWidgetItem("Cout de production (€/t)"))
        ConfCultureTable.setItem(4, 0, QTableWidgetItem("Rdt Paille (t/ha)"))
        ConfCultureTable.setItem(5, 0, QTableWidgetItem("Rdt Ensilage (t/ha)"))
        ConfCultureTable.setItem(6, 0, QTableWidgetItem("Rdt Luzerne (t/ha)"))
        ConfCultureTable.setItem(7, 0, QTableWidgetItem("IFT (/ha)"))
        for Culture in range(self.NbCulture):
            # Init Row with culture names
            ConfCultureTable.setItem(0, Culture + 1, QTableWidgetItem(self.Vculture[Culture]))
            ConfCultureTable.setItem(1, Culture + 1, QTableWidgetItem(str(self.VredementCulture[Culture])))
            ConfCultureTable.setItem(2, Culture + 1, QTableWidgetItem(str(self.VculturePrice[Culture])))
            ConfCultureTable.setItem(3, Culture + 1, QTableWidgetItem(str(self.VcultureProdPrice[Culture])))
            ConfCultureTable.setItem(4, Culture + 1, QTableWidgetItem(str(self.VredementCulturePaille[Culture])))
            ConfCultureTable.setItem(5, Culture + 1, QTableWidgetItem(str(self.VredementCultureEnsilage[Culture])))
            ConfCultureTable.setItem(6, Culture + 1, QTableWidgetItem(str(self.VredementCultureLuzerne[Culture])))
            ConfCultureTable.setItem(7, Culture + 1, QTableWidgetItem(str(self.VcultureIft[Culture])))

        # ConfigTypeSolText
        Geometrie = self.ui.ConfigSolTypeText.geometry()
        Geometrie.setY(25 * (NbRow + 1) + 12)
        self.ui.ConfigSolTypeText.setGeometry(Geometrie)
        # ConfTypeSolTable
        ConfTypeSolTable = self.ui.ConfigSolTypeTable
        InitTable(ConfTypeSolTable, 1, self.NbTypeSol, 0, 25 * (NbRow + 2) + 12)
        # No Header
        for Sol in range(self.NbTypeSol):
            # Init Row with culture names
            ConfTypeSolTable.setItem(0, Sol, QTableWidgetItem(self.Vtypesol[Sol]))

        self.ui.NbYearSimulationBox.setValue(self.NbAnneeSimulee)
        self.ui.NbSimuPerYearBox.setValue(self.NbSimuPerYear)
        self.ui.NbBestResultBox.setValue(self.NbBestResult)
        # On change:
        ConfCultureTable.itemChanged.connect(self.OnChange_ConfCultureTable)
        ConfTypeSolTable.itemChanged.connect(self.OnChange_ConfTypeSolTable)
        self.ui.NbSimuPerYearBox.valueChanged.connect(self.OnChange_NbSimuPerYearBox)
        self.ui.NbYearSimulationBox.valueChanged.connect(self.OnChange_NbYearSimulationBox)
        self.ui.NbBestResultBox.valueChanged.connect(self.OnChange_NbBestResultBox)

    # OnChange_ConfCultureTable: Method called on change event in ConfigCultureTypeTable
    def OnChange_ConfCultureTable(self):
        ConfCultureTable = self.ui.ConfigCultureTypeTable
        row = ConfCultureTable.currentRow()
        col = ConfCultureTable.currentColumn()
        if row == 0:
            # Update culture vector with update
            self.Vculture[col - 1] = ConfCultureTable.item(row, col).text()

            # Update "Entrée" with new Vculture value
            InTable = self.ui.ParcelCultureInputTable
            for Parcelle in range(self.NbParcelle):
                InTable.cellWidget(Parcelle + 1, 1).setItemText(col - 1, self.Vculture[col - 1])
        if row == 1:
            # Update rendement vector with update
            self.VredementCulture[col - 1] = int(ConfCultureTable.item(row, col).text())
        if row == 2:
            # Update culturePrice vector with update
            self.VculturePrice[col - 1] = int(ConfCultureTable.item(row, col).text())
        if row == 3:
            # Update culturePrice vector with update
            self.VcultureProdPrice[col - 1] = int(ConfCultureTable.item(row, col).text())
        if row == 4:
            # Update culturePrice vector with update
            self.VredementCulturePaille[col - 1] = int(ConfCultureTable.item(row, col).text())
        if row == 5:
            # Update culturePrice vector with update
            self.VredementCultureEnsilage[col - 1] = int(ConfCultureTable.item(row, col).text())
        if row == 6:
            # Update culturePrice vector with update
            self.VredementCultureLuzerne[col - 1] = int(ConfCultureTable.item(row, col).text())
        if row == 7:
            # Update culturePrice vector with update
            self.VcultureIft[col - 1] = int(ConfCultureTable.item(row, col).text())

    # OnChange_ConfTypeSolTable: Method called on change event in ConfigSolTypeTable
    def OnChange_ConfTypeSolTable(self):
        ConfTypeSolTable = self.ui.ConfigSolTypeTable
        row = ConfTypeSolTable.currentRow()
        col = ConfTypeSolTable.currentColumn()
        if row == 0:
            # Update culture vector with update
            self.Vtypesol[col] = ConfTypeSolTable.item(row, col).text()

            # Update "Entrée" with new Vculture value
            InTable = self.ui.ParcelCultureInputTable
            for Parcelle in range(self.NbParcelle):
                InTable.cellWidget(Parcelle + 1, 3).setItemText(col, self.Vtypesol[col])

    # OnChange_NbSimuPerYearBox: Method called on change event in NbSimuPerYearBox
    def OnChange_NbSimuPerYearBox(self):
        self.NbSimuPerYear = self.ui.NbSimuPerYearBox.value()

    # OnChange_NbYearSimulationBox: Method called on change event in NbYearSimulationBox
    def OnChange_NbYearSimulationBox(self):
        self.NbAnneeSimulee = self.ui.NbYearSimulationBox.value()

    # OnChange_NbBestResultBox: Method called on change event in NbBestResultBox
    def OnChange_NbBestResultBox(self):
        self.NbBestResult = self.ui.NbBestResultBox.value()
        self.ui.IndexBestResultBox.setMaximum(self.NbBestResult - 1)

    def FillVparcelleCulture_N_1_ForTest(self):
        Culture = 0
        self.VparcelleCulture_N_1.resize(self.NbParcelle)
        for Parcelle in range(self.NbParcelle):
            Culture = (Culture + 1) % self.NbCulture
            self.VparcelleCulture_N_1[Parcelle] = Culture

    # InitInputTab: Init tables in tab "Entrées"
    def InitInputTab(self):
        # Init parcelle culture input table
        InTable = self.ui.ParcelCultureInputTable
        InitTable(InTable, self.NbParcelle + 1, 4, 0, 0)
        # Fill Header
        InTable.setItem(0, 0, QTableWidgetItem("Parcelle"))
        InTable.setItem(0, 1, QTableWidgetItem("Culture n-1"))
        InTable.setItem(0, 2, QTableWidgetItem("Taille Parcelle"))
        InTable.setItem(0, 3, QTableWidgetItem("Type Sol"))

        for Parcelle in range(self.NbParcelle):
            # Fill Row Header with parcel names
            InTable.setItem(Parcelle + 1, 0, QTableWidgetItem(self.Vparcelle[Parcelle]))
            # Fill first column with input of n-1 year
            # Create list box selection for culture, based on what is in config tab
            comboCulture = QtWidgets.QComboBox()
            comboCulture.addItems(self.Vculture)
            InTable.setCellWidget(Parcelle + 1, 1, comboCulture)
            InTable.cellWidget(Parcelle + 1, 1).setCurrentIndex(self.VparcelleCulture_N_1[Parcelle])
            InTable.setItem(Parcelle + 1, 2, QTableWidgetItem(str(self.VparcelleTaille[Parcelle])))
            comboTypeSol = QtWidgets.QComboBox()
            comboTypeSol.addItems(self.Vtypesol)
            InTable.setCellWidget(Parcelle + 1, 3, comboTypeSol)
            InTable.cellWidget(Parcelle + 1, 3).setCurrentIndex(self.VparcelleTypeSol[Parcelle])

        # Init Qtt min
        self.ui.QttPailleMinBox.setValue(self.QttPailleMin)
        self.ui.QttEnsilageMinBox.setValue(self.QttEnsilageMin)
        self.ui.QttLuzerneMinBox.setValue(self.QttLuzerneMin)
        # On change:
        InTable.itemChanged.connect(self.OnChange_InputTable)
        self.ui.QttPailleMinBox.valueChanged.connect(self.OnChange_QttPailleMinBox)
        self.ui.QttEnsilageMinBox.valueChanged.connect(self.OnChange_QttEnsilageMinBox)
        self.ui.QttLuzerneMinBox.valueChanged.connect(self.OnChange_QttLuzerneMinBox)
        # On clicks:
        self.ui.ValindInput.clicked.connect(self.OnClick_ValidInput)

    # OnClick_ValidInput: Method called on click event on ValidInput
    def OnClick_ValidInput(self):
        InTable = self.ui.ParcelCultureInputTable
        # Update Input n-1
        for Row in range(self.NbParcelle):
            # Get VparcelleCulture_N_1 value
            self.VparcelleCulture_N_1[Row] = InTable.cellWidget(Row + 1, 1).currentIndex()
            # Get VparcelleTypeSol value
            self.VparcelleTypeSol[Row] = InTable.cellWidget(Row + 1, 3).currentIndex()
            # Set VparcelleCulture_N_1 in OutputTable
            OCT = self.ui.OutputCultureTable
            OCT.setItem(Row + 1, 1, QTableWidgetItem(self.Vculture[self.VparcelleCulture_N_1[Row]]))

    # OnChange_InputTable: Method called on change event in ParcelCultureInputTable
    def OnChange_InputTable(self):
        InTable = self.ui.ParcelCultureInputTable
        row = InTable.currentRow()
        col = InTable.currentColumn()
        if col == 0:
            # Update Parcelle vector with update
            self.Vparcelle[row - 1] = InTable.item(row, col).text()

            # Update "Résultats" with new Vparcelle value
            self.ui.OutputCultureTable.setItem(row, 0, QTableWidgetItem(self.Vparcelle[row - 1]))

        if col == 2:
            # Update Input n-1
            # text = InTable.item(row, col).text()
            self.VparcelleTaille[row - 1] = int(InTable.item(row, col).text())

    # OnChange_QttPailleMinBox: Method called on change event in QttPailleMinBox
    def OnChange_QttPailleMinBox(self):
        self.QttPailleMin = self.ui.QttPailleMinBox.value()

    # OnChange_QttLuzerneMinBox: Method called on change event in QttLuzerneMinBox
    def OnChange_QttLuzerneMinBox(self):
        self.QttLuzerneMin = self.ui.QttLuzerneMinBox.value()

    # OnChange_QttEnsilageMinBox: Method called on change event in QttEnsilageMinBox
    def OnChange_QttEnsilageMinBox(self):
        self.QttEnsilageMin = self.ui.QttEnsilageMinBox.value()

    # InitOutputTab: Init tables in tab "Résultats"
    def InitOutputTab(self):
        self.InitCultureOutputTable(self.ui.OutputCultureTable)
        self.FillOutputTable()  # TODO: Remove this line as soon as calculation algorithm is connected.
        self.InitReportOutputTable(self.ui.tableMarginConstraint)
        self.ui.IndexBestResultBox.setMaximum(self.NbBestResult - 1)
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
            CultOutTab.setItem(Parcelle + 1, 1, QTableWidgetItem(self.Vculture[self.VparcelleCulture_N_1[Parcelle]]))

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
        VOutput_ForTest.resize((NbBestResult, NbAnnees, NbParcelle))
        for NumResult in range(NbBestResult):
            for Year in range(NbAnnees):
                for Parcelle in range(NbParcelle):
                    culture = (culture + 1) % self.NbCulture
                    VOutput_ForTest[NumResult][Year][Parcelle] = culture

    # FillOutputTable: Fill the output table with culture associated with
    def FillOutputTable(self):
        CultOutTab = self.ui.OutputCultureTable
        self.FillVOutput_ForTest(self.NbAnneeSimulee, self.NbParcelle, self.NbBestResult)
        IndexBestResult = self.ui.IndexBestResultBox.value()
        for Year in range(self.NbAnneeSimulee):
            for Parcelle in range(self.NbParcelle):
                index = VOutput_ForTest[IndexBestResult][Year][Parcelle]
                CultOutTab.setItem(Parcelle + 1, Year + 2,
                                   QTableWidgetItem(self.Vculture[index]))

    # OnClick_StartCalculation: Method to start calculation.
    def OnClick_StartCalculation(self):
        self.WrapperModelInput()

    def WrapperModelInput(self):
        # Format MPCn1
        MPCn1 = np.zeros((self.NbParcelle, self.NbCulture))
        for Parcelle in range(self.NbParcelle):
            MPCn1[Parcelle][self.VparcelleCulture_N_1[Parcelle]] = 1
        self.ModelInput["MPCn1"] = MPCn1
        # print("MPCn1 = ")
        # print(self.ModelInput["MPCn1"])

        # Format MPTS
        MPTS = np.zeros((self.NbParcelle, self.NbTypeSol))
        for Parcelle in range(self.NbParcelle):
            MPTS[Parcelle][self.VparcelleTypeSol[Parcelle]] = 1
        self.ModelInput["MPTS"] = MPTS
        # print("MPTS = ")
        # print(self.ModelInput["MPTS"])

        # Format surfaces
        self.ModelInput["surface"] = self.VparcelleTaille
        # print("surface = ")
        # print(self.ModelInput["surface"])

        # Format numPailleMin
        self.ModelInput["numPailleMin"] = self.QttPailleMin
        # print("numPailleMin = ")
        # print(self.ModelInput["numPailleMin"])

        # Format numEnsilageMin
        self.ModelInput["numEnsilageMin"] = self.QttEnsilageMin
        # print("numEnsilageMin = ")
        # print(self.ModelInput["numEnsilageMin"])

        # Format numLuzerneMin
        self.ModelInput["numLuzerneMin"] = self.QttLuzerneMin
        # print("numLuzerneMin = ")
        # print(self.ModelInput["numLuzerneMin"])

        # Format numYear
        self.ModelInput["numYear"] = self.NbAnneeSimulee
        # print("numYear = ")
        # print(self.ModelInput["numYear"])

        # Format numSolutionYear
        self.ModelInput["numSolutionYear"] = self.NbSimuPerYear
        # print("numSolutionYear = ")
        # print(self.ModelInput["numSolutionYear"])

        # Format number best results
        self.ModelInput["numBestResult"] = self.NbBestResult
        # print("numBestResult = ")
        # print(self.ModelInput["numBestResult"])

        # Format rendement
        self.ModelInput["eta"] = self.VredementCulture
        # print("eta = ")
        # print(self.ModelInput["eta"])

        # Format prix culture
        self.ModelInput["prixVenteCulture"] = self.VculturePrice
        # print("prixVenteCulture = ")
        # print(self.ModelInput["prixVenteCulture"])

        # Format cout de prod culture
        self.ModelInput["coutProdCulture"] = self.VcultureProdPrice
        # print("coutProdCulture = ")
        # print(self.ModelInput["coutProdCulture"])

        # Format rendement paille culture
        self.ModelInput["etaPaille"] = self.VredementCulturePaille  # TODO: Name to be defined!!
        # print("etaPaille = ")
        # print(self.ModelInput["etaPaille"])

        # Format rendement ensilage culture
        self.ModelInput["etaEnsilage"] = self.VredementCultureEnsilage  # TODO: Name to be defined!!
        # print("etaEnsilage = ")
        # print(self.ModelInput["etaEnsilage"])

        # Format rendement luzerne culture
        self.ModelInput["etaLuzerne"] = self.VredementCultureLuzerne  # TODO: Name to be defined!!
        # print("etaLuzerne = ")
        # print(self.ModelInput["etaLuzerne"])

        # Format IFT culture
        self.ModelInput["IftCulture"] = self.VcultureIft  # TODO: Name to be defined!!
        # print("IftCulture = ")
        # print(self.ModelInput["IftCulture"])


if __name__ == "__main__":
    # Instantiation du Main
    TestApp = TestWindow()
    TestApp.show()

    sys_exit(Const.MyApp.exec_())
