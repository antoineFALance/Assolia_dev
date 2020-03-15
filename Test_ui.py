import datetime
import sqlite3 as sql
import time
from sys import argv as sys_arg, exit as sys_exit

import numpy as np
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QTableWidgetItem, QFileDialog, QWidget

# Initialisation of variables to be used in case that there is no file to open.
from DefaultVariables import DefaultInit as DefaultVariablesInit, Const
import Assolia_Solver as A_solver

Const.RowSize = 25
Const.ColumnSize = 90
Const.MyApp = QtWidgets.QApplication(sys_arg)
Const.DI = DefaultVariablesInit()
Const.Verbose = False

Const.Version = "V030"


def DebugFctnBreakPoint():
    print("BreakPoint here")


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


def DummyCalculation(**InputDictionary):
    NbBestResult = InputDictionary.get("numBestResult", Const.DI.NbBestResult_Init)
    NbYear = InputDictionary.get("numYear", Const.DI.NbAnneeSimulee_Init)
    VparcelleCulture = InputDictionary.get("MPCn1", Const.DI.VparcelleCulture_N_1_Init)
    NbParcelle = len(VparcelleCulture)
    NbCulture = len(VparcelleCulture[0])
    MinPaille = InputDictionary.get("numPailleMin", Const.DI.QttPailleMin_Init)
    MinEnsilage = InputDictionary.get("numEnsilageMin", Const.DI.QttEnsilageMin_Init)
    MinLuzerne = InputDictionary.get("numLuzerneMin", Const.DI.QttLuzerneMin_Init)
    CultureSimu = 1
    Marge = 50000
    StepMarge = 1
    Ift = 3.0
    StepIft = -0.01

    OutputStructure = []
    for Result in range(NbBestResult):
        result_n_year = []

        for Year in range(NbYear):
            result_1_year_assol = np.zeros(NbParcelle)
            for Parcelle in range(NbParcelle):
                result_1_year_assol[Parcelle] = CultureSimu
                CultureSimu = (CultureSimu + 1) % NbCulture
            result_1_year_other = np.array([Marge, Ift, MinPaille, MinEnsilage, MinLuzerne])
            Marge += StepMarge
            Ift += StepIft
            result_1_year = [result_1_year_assol, result_1_year_other]

            result_n_year.append(result_1_year)
        result_n_year_other_average = np.array([Marge, Ift, MinPaille, MinEnsilage, MinLuzerne])
        Marge += StepMarge
        Ift += StepIft
        result_n_year_with_average = [result_n_year, result_n_year_other_average]

        OutputStructure.append(result_n_year_with_average)
        # print(OutputStructure[Result])

    return OutputStructure


def fetchall_column(rows):
    Column = []
    for row in rows:
        Column.append(row[0])
    return Column


def GetIndexFromId(Vid, Id):
    for index in range(len(Vid)):
        if Id == Vid[index]:
            return index
    return -1


class TestWindow(QtWidgets.QMainWindow, QtCore.QObject):
    def __init__(self, parent=None):
        from QtUi_test.test import Ui_Assolia_MainWindow
        assert isinstance(parent, object)
        super().__init__(parent)
        # QtWidgets.QMainWindow().__init__(self)
        self.ui = Ui_Assolia_MainWindow()
        self.ui.setupUi(self)

        # Default data loading
        self.Vusers = []
        self.VusersId = []
        self.NbUsers = 0

        self.Vparcelle = Const.DI.Vparcelle_Init
        self.VparcelleId = []
        self.NbParcelle = Const.DI.NbParcelle_Init

        self.VparcelleTaille = Const.DI.VparcelleTaille_Init

        self.VparcelleTypeSol = Const.DI.VparcelleTypeSol_Init
        self.NbParcelleTypeSol = Const.DI.NbParcelleTypeSol_Init

        self.Vculture = Const.DI.Vculture_Init
        self.VcultureId = []
        self.NbCulture = Const.DI.NbCulture_Init
        self.VredementCulture = Const.DI.VredementCulture_Init
        self.VculturePrice = Const.DI.VculturePrice_Init
        self.VcultureProdPrice = Const.DI.VcultureProdPrice_Init
        self.VredementCulturePaille = Const.DI.VredementCulturePaille_Init
        self.VredementCultureEnsilage = Const.DI.VredementCultureEnsilage_Init
        self.VredementCultureLuzerne = Const.DI.VredementCultureLuzerne_Init
        self.VcultureIft = Const.DI.VcultureIft_Init

        self.Vtypesol = Const.DI.Vtypesol_Init
        self.VtypesolId = []
        self.NbTypeSol = Const.DI.NbTypeSol_Init
        self.VcultureSol = Const.DI.VcultureSol_Init

        self.VRotationN_1 = Const.DI.VRotationN_1_Init

        self.QttPailleMin = Const.DI.QttPailleMin_Init
        self.QttEnsilageMin = Const.DI.QttEnsilageMin_Init
        self.QttLuzerneMin = Const.DI.QttLuzerneMin_Init

        self.NbSimuPerYear = Const.DI.NbSimuPerYear_Init
        self.NbAnneeSimulee = Const.DI.NbAnneeSimulee_Init
        self.NbBestResult = Const.DI.NbBestResult_Init

        self.ActualYear = int(datetime.datetime.today().strftime('%Y'))
        self.VparcelleCulture_N_X = [Const.DI.VparcelleCulture_N_1_Init]
        self.VanneeCultureParcelle = [1]
        self.NbAnneeCultureParcelle = len(self.VanneeCultureParcelle)

        self.NbAnneeLuzerne = Const.DI.NbAnneeLuzerne_Init

        self.WeightIFT = Const.DI.WeightIFT_Init
        self.WeightMB = Const.DI.WeightMB_Init

        self.solverMode = 'constrained IFT'
        self.kIFT = 0.0

        self.ConfigParameterTab = self.ui.tabWidget.widget(2)

        # start with empty dictionary for the input of the model
        self.ModelInput = {}
        self.WrapperModelInput()
        self.solver = A_solver.objectSolver(**self.ModelInput)
        self.ModelOutput = []

        self.ActualUserName = "Default"
        self.ActualUserId = 1

        self.db = sql.connect('Assolia_Default.db')
        self.LoadDataBase()

        self.FirstInit = True
        self.InitMenu()
        self.InitAllTab()
        self.FirstInit = False

    def Debug_PrintVariables(self):
        try:
            print("users  = ")
            print(self.Vusers)
            print(self.NbUsers)
            print("type sol = ")
            print(self.Vtypesol)
            print(self.NbTypeSol)
            print("Parcelle = ")
            print(self.Vparcelle)
            print(self.NbParcelle)
            print("Parcelle type sol = ")
            print(self.VparcelleTypeSol)
            print("Parcelle taille = ")
            print(self.VparcelleTaille)
            print("Culture = ")
            print(self.Vculture)
            print(self.NbCulture)
            print("Prix vente = ")
            print(self.VculturePrice)
            print("Cout = ")
            print(self.VcultureProdPrice)
            print("Rendement = ")
            print(self.VredementCulture)
            print("Paille = ")
            print(self.VredementCulturePaille)
            print("Ensilage = ")
            print(self.VredementCultureEnsilage)
            print("Luzerne = ")
            print(self.VredementCultureLuzerne)
            print("Ift = ")
            print(self.VcultureIft)
            print("VparcelleCulture_N_X = ")
            print(self.VparcelleCulture_N_X)
            print("VcultureSol = ")
            print(self.VcultureSol)
            print("VRotationN_1 = ")
            print(self.VRotationN_1)
            return True

        except:
            DebugFctnBreakPoint()
            return False

    def Debug_PrintDictionary(self):
        try:
            print("MPCn1 = ")
            print(self.ModelInput["MPCn1"])
            print("MPTS = ")
            print(self.ModelInput["MPTS"])
            print("surface = ")
            print(self.ModelInput["surface"])
            print("constraintPaille = ")
            print(self.ModelInput["constraintPaille"])
            print("constraintEnsilage = ")
            print(self.ModelInput["constraintEnsilage"])
            print("constraintLuzerne = ")
            print(self.ModelInput["constraintLuzerne"])
            print("numYear = ")
            print(self.ModelInput["numYear"])
            print("numSolutionYear = ")
            print(self.ModelInput["numSolutionYear"])
            # print("numBestResult = ")
            # print(self.ModelInput["numBestResult"])
            print("eta = ")
            print(self.ModelInput["eta"])
            print("prixVenteCulture = ")
            print(self.ModelInput["prixVenteCulture"])
            print("coutProdCulture = ")
            print(self.ModelInput["coutProdCulture"])
            # print("etaPaille = ")
            # print(self.ModelInput["etaPaille"])
            # print("etaEnsilage = ")
            # print(self.ModelInput["etaEnsilage"])
            # print("etaLuzerne = ")
            # print(self.ModelInput["etaLuzerne"])
            print("ift = ")
            print(self.ModelInput["ift"])
            print("R1 = ")
            print(self.ModelInput["R1"])
            print("R2 = ")
            print(self.ModelInput["R2"])
            print("solverMode = ")
            print(self.ModelInput["solverMode"])
            print("kIFT = ")
            print(self.ModelInput["kIFT"])
            print("cultureList = ")
            print(self.ModelInput["cultureList"])
            print("parcelleList = ")
            print(self.ModelInput["parcelleList"])
            return True

        except:
            DebugFctnBreakPoint()
            return False

    def Debug_PrintOutput(self):
        try:
            print(self.solver.dfMBSolution)
            print(self.solver.dfIFTSolution)
            print(self.solver.yearAssolementConfig)
            print(self.solver.yearMB)
            print(self.solver.yearQtePaille)
            print(self.solver.yearQteEnsilage)
            print(self.ModelOutput)
            return True

        except:
            DebugFctnBreakPoint()
            return False

    def SuspendAllConnections(self, bloqued=True):
        # Menu
        self.ui.Close_test.blockSignals(bloqued)
        self.ui.actionParametre_administrateur.blockSignals(bloqued)
        self.ui.actionOuvrir.blockSignals(bloqued)
        # TODO: décommenter ceci pour autoriser la sauvegarde dans un fichier.
        # self.ui.actionEnregistrer.blockSignals(bloqued)
        self.ui.actionExit.blockSignals(bloqued)
        self.ui.StartCalculation.blockSignals(bloqued)

        # ConfigTab
        self.ui.ConfigCultureTypeTable.blockSignals(bloqued)
        self.ui.ConfigSolTypeTable.blockSignals(bloqued)
        self.ui.NbSimuPerYearBox.blockSignals(bloqued)
        self.ui.NbYearSimulationBox.blockSignals(bloqued)
        self.ui.NbBestResultBox.blockSignals(bloqued)
        self.ui.NbYearLuzerneBox.blockSignals(bloqued)
        self.ui.ConfigOptiMbIft_Slider.blockSignals(bloqued)

        # HiddenConfigTab
        self.ui.ConfigCultureSolTable.blockSignals(bloqued)
        self.ui.ConfigRotationCultureN_1Table.blockSignals(bloqued)

        # InputTab
        self.ui.ParcelCultureInputTable.blockSignals(bloqued)
        self.ui.QttPailleMinBox.blockSignals(bloqued)
        self.ui.QttEnsilageMinBox.blockSignals(bloqued)
        self.ui.QttLuzerneMinBox.blockSignals(bloqued)
        self.ui.UserNameComboBox.blockSignals(bloqued)
        self.ui.ValindInput.blockSignals(bloqued)
        self.ui.IndexBestResultBox.blockSignals(bloqued)

    def LoadDataBase(self):
        try:
            start_time_2 = time.clock()

            if Const.Verbose:
                self.Debug_PrintVariables()

            # Load data base
            self.db.row_factory = sql.Row
            cursor = self.db.cursor()

            # Get ref users
            cursor.execute("SELECT lb_users FROM ref_users")
            self.Vusers = fetchall_column(cursor.fetchall())
            self.NbUsers = len(self.Vusers)

            cursor.execute("SELECT id_users FROM ref_users")
            self.VusersId = fetchall_column(cursor.fetchall())

            # Get ref Type sol
            cursor.execute("SELECT lb_type_sol FROM ref_type_sol")
            self.Vtypesol = fetchall_column(cursor.fetchall())
            self.NbTypeSol = len(self.Vtypesol)

            cursor.execute("SELECT id_type_sol FROM ref_type_sol")
            self.VtypesolId = fetchall_column(cursor.fetchall())

            # Get parcels name
            cursor.execute("SELECT lb_parcelle FROM ref_parcelle WHERE id_users = ?", (self.ActualUserId,))
            self.Vparcelle = fetchall_column(cursor.fetchall())
            self.NbParcelle = len(self.Vparcelle)

            cursor.execute("SELECT id_parcelle FROM ref_parcelle WHERE id_users = ?", (self.ActualUserId,))
            self.VparcelleId = fetchall_column(cursor.fetchall())

            cursor.execute("SELECT id_type_sol FROM ref_parcelle WHERE id_users = ?", (self.ActualUserId,))
            VparcelleTypeSolId = fetchall_column(cursor.fetchall())
            self.VparcelleTypeSol = np.zeros(self.NbParcelle, dtype=int)
            for i in range(self.NbParcelle):
                self.VparcelleTypeSol[i] = GetIndexFromId(self.VtypesolId, VparcelleTypeSolId[i])

            cursor.execute("SELECT num_surface FROM ref_parcelle WHERE id_users = ?", (self.ActualUserId,))
            self.VparcelleTaille = np.array(fetchall_column(cursor.fetchall()))
            # TODO: demander pourquoi sans le np.array ça pose problème à la ligne 418 de Assolia_Solver.py

            # Get cultures
            cursor.execute("SELECT lb_culture FROM ref_culture")
            self.Vculture = fetchall_column(cursor.fetchall())
            self.NbCulture = len(self.Vculture)

            cursor.execute("SELECT id_culture FROM ref_culture")
            self.VcultureId = fetchall_column(cursor.fetchall())

            cursor.execute("SELECT num_prix_vente FROM ref_culture")
            self.VculturePrice = fetchall_column(cursor.fetchall())

            cursor.execute("SELECT num_cout FROM ref_culture")
            self.VcultureProdPrice = fetchall_column(cursor.fetchall())

            cursor.execute("SELECT Rendement FROM ref_culture")
            self.VredementCulture = fetchall_column(cursor.fetchall())

            cursor.execute("SELECT Paille FROM ref_culture")
            self.VredementCulturePaille = fetchall_column(cursor.fetchall())

            cursor.execute("SELECT Ensilage FROM ref_culture")
            self.VredementCultureEnsilage = fetchall_column(cursor.fetchall())

            cursor.execute("SELECT Luzerne FROM ref_culture")
            self.VredementCultureLuzerne = fetchall_column(cursor.fetchall())

            cursor.execute("SELECT Ift FROM ref_culture")
            self.VcultureIft = fetchall_column(cursor.fetchall())

            # Get repartition culture
            cursor.execute("SELECT * FROM lnk_ref_repartition_culture WHERE id_users = ?", (self.ActualUserId,))
            rows = cursor.fetchall()
            self.VanneeCultureParcelle = []
            for row in rows:
                N_X = self.ActualYear - int(row['date_repartition'])
                Already = False
                for Already_N_X in self.VanneeCultureParcelle:
                    if Already_N_X == N_X:
                        Already = True
                if not Already:
                    self.VanneeCultureParcelle.append(N_X)
            self.NbAnneeCultureParcelle = len(self.VanneeCultureParcelle)

            self.VparcelleCulture_N_X = np.zeros((self.NbAnneeCultureParcelle, self.NbParcelle), dtype=int)
            for row in rows:
                index_culture = GetIndexFromId(self.VcultureId, row['id_culture'])
                index_parcelle = GetIndexFromId(self.VparcelleId, row['id_parcelle'])
                annee = int(row['date_repartition'])
                self.VparcelleCulture_N_X[
                    GetIndexFromId(self.VanneeCultureParcelle, self.ActualYear - annee)][
                    index_parcelle] \
                    = index_culture

            # Get rendement culture sol
            cursor.execute("SELECT * FROM lnk_ref_rendement_culture_sol")
            rows = cursor.fetchall()
            self.VcultureSol = np.zeros((self.NbCulture, self.NbTypeSol))
            for row in rows:
                index_culture = GetIndexFromId(self.VcultureId, row['id_culture'])
                index_type_sol = GetIndexFromId(self.VtypesolId, row['id_type_sol'])
                num_rendement = row['num_rendement']
                self.VcultureSol[index_culture][index_type_sol] = num_rendement

            # Get rotation culture n-1
            cursor.execute("SELECT * FROM lnk_ref_rotation_culture_n_1")
            rows = cursor.fetchall()
            self.VRotationN_1 = np.zeros((self.NbCulture, self.NbCulture))
            for row in rows:
                index_culture_n_1 = GetIndexFromId(self.VcultureId, row['id_culture_n_1'])
                index_culture_n = GetIndexFromId(self.VcultureId, row['id_culture_n'])
                num_rotation_ratio = row['num_rotation_ration']
                self.VRotationN_1[index_culture_n][index_culture_n_1] = num_rotation_ratio

            # Get user config
            cursor.execute("SELECT * FROM ref_conf WHERE id_users = ?", (self.ActualUserId,))
            rows = cursor.fetchall()
            row = rows[0]
            self.QttPailleMin = row['num_qtt_paille_min']
            self.QttEnsilageMin = row['num_qtt_ensilage_min']
            self.QttLuzerneMin = row['num_qtt_luzerne_min']
            self.NbAnneeSimulee = row['num_nb_annee_simu']
            self.NbSimuPerYear = row['num_nb_simu_par_an']
            self.NbBestResult = row['num_nb_resultats_finaux']
            self.NbBestResult = 1
            self.NbAnneeLuzerne = row['num_nb_annee_luzerne']

            if Const.Verbose:
                self.Debug_PrintVariables()

            print("Db loaded in :")
            print(time.clock() - start_time_2)
            return True

        except:
            DebugFctnBreakPoint()
            return False

    def SaveDataBase(self):
        try:
            # Save database
            print("Saving..")

            cursor = self.db.cursor()

            for index in range(self.NbTypeSol):
                cursor.execute("UPDATE ref_type_sol SET lb_type_sol = ? WHERE id_type_sol = ?",
                               (self.Vtypesol[index], str(self.VtypesolId[index]),))
            # cursor.execute("UPDATE ref_type_sol SET lb_type_sol = ?", (self.Vtypesol, ))

            for index in range(self.NbParcelle):
                cursor.execute("UPDATE ref_parcelle SET lb_parcelle = ? WHERE id_parcelle = ?",
                               (self.Vparcelle[index], str(self.VparcelleId[index]),))
                cursor.execute("UPDATE ref_parcelle SET id_type_sol = ? WHERE id_parcelle = ?",
                               (self.VtypesolId[self.VparcelleTypeSol[index]], str(self.VparcelleId[index]),))
                cursor.execute("UPDATE ref_parcelle SET num_surface = ? WHERE id_parcelle = ?",
                               (self.VparcelleTaille[index], str(self.VparcelleId[index]),))
                cursor.execute("UPDATE lnk_ref_repartition_culture SET id_culture = ? WHERE id_parcelle = ?",
                               (self.VcultureId[self.VparcelleCulture_N_X[0][index]], str(self.VparcelleId[index]),))

            for index in range(self.NbCulture):
                cursor.execute("UPDATE ref_culture SET lb_culture = ? WHERE id_culture = ?",
                               (self.Vculture[index], str(self.VparcelleId[index]),))
                cursor.execute("UPDATE ref_culture SET num_prix_vente = ? WHERE id_culture = ?",
                               (self.VculturePrice[index], str(self.VparcelleId[index]),))
                cursor.execute("UPDATE ref_culture SET num_cout = ? WHERE id_culture = ?",
                               (self.VcultureProdPrice[index], str(self.VparcelleId[index]),))
                cursor.execute("UPDATE ref_culture SET Rendement = ? WHERE id_culture = ?",
                               (self.VredementCulture[index], str(self.VparcelleId[index]),))
                cursor.execute("UPDATE ref_culture SET Paille = ? WHERE id_culture = ?",
                               (self.VredementCulturePaille[index], str(self.VparcelleId[index]),))
                cursor.execute("UPDATE ref_culture SET Ensilage = ? WHERE id_culture = ?",
                               (self.VredementCultureEnsilage[index], str(self.VparcelleId[index]),))
                cursor.execute("UPDATE ref_culture SET Luzerne = ? WHERE id_culture = ?",
                               (self.VredementCultureLuzerne[index], str(self.VparcelleId[index]),))
                cursor.execute("UPDATE ref_culture SET Ift = ? WHERE id_culture = ?",
                               (self.VcultureIft[index], str(self.VparcelleId[index]),))
                for index_sol in range(self.NbTypeSol):
                    cursor.execute("UPDATE lnk_ref_rendement_culture_sol SET num_rendement = ? "
                                   "WHERE id_culture = ? AND id_type_sol = ?",
                                   (self.VcultureSol[index][index_sol],
                                    str(self.VcultureId[index]), str(self.VtypesolId[index_sol]),))

                for index_n_1 in range(self.NbCulture):
                    cursor.execute("UPDATE lnk_ref_rotation_culture_n_1 SET num_rotation_ration = ? "
                                   "WHERE id_culture_n = ? AND id_culture_n_1 = ?",
                                   (self.VRotationN_1[index][index_n_1],
                                    str(self.VcultureId[index]), str(self.VcultureId[index_n_1]),))

            self.db.commit()
            print("Saved")
            return True

        except:
            DebugFctnBreakPoint()
            return False

    def InitMenu(self):
        try:
            self.ui.Close_test.clicked.connect(self.ExitFunction)
            self.ui.actionParametre_administrateur.triggered.connect(self.AdminRequested)
            self.ui.actionOuvrir.triggered.connect(self.OnClick_OpenDataBase)
            # TODO: décommenter ceci pour autoriser la sauvegarde dans un fichier.
            # self.ui.actionEnregistrer.triggered.connect(self.SaveDataBase)
            self.ui.actionExit.triggered.connect(self.ExitFunction)
            self.ui.StartCalculation.clicked.connect(self.OnClick_StartCalculation)
            return True

        except:
            DebugFctnBreakPoint()
            return False

    def AdminRequested(self):
        try:
            self.ui.tabWidget.addTab(self.ConfigParameterTab, "Configuration cachée")
            return True

        except:
            DebugFctnBreakPoint()
            return False

    # noinspection PyArgumentList,PyArgumentList
    def OnClick_OpenDataBase(self):
        try:
            fileName = QFileDialog.getOpenFileName(
                parent=self,
                caption="Ouvrir un fichier d'image",
                directory='',
                filter="Base de donnée (*.db)"
            )
            if fileName:
                self.db.close()
                self.db = sql.connect(fileName[0])

                self.LoadDataBase()
                self.SuspendAllConnections(True)
                self.InitAllTab()
                self.SuspendAllConnections(False)
            return True

        except:
            DebugFctnBreakPoint()
            return False

    # InitAllTab: Init all tab ("Entrées", "Configuration", "Résultats", "Configurations cachées")
    def InitAllTab(self):
        try:
            # Init config tab
            self.InitConfigTab()

            # Init hidden config tab
            self.InitHiddenConfigTab()

            # Init Input table:
            self.InitInputTab()

            # Init output tab
            self.InitOutputTab()
            return True

        except:
            DebugFctnBreakPoint()
            return False

    # InitConfigTab: Init tables in tab "Configuration"
    def InitConfigTab(self):
        try:
            # ConfCultureTable
            ConfCultureTable = self.ui.ConfigCultureTypeTable
            NbRow = 8
            InitTable(ConfCultureTable, NbRow, self.NbCulture + 1, 0, 25)
            Geometrie = ConfCultureTable.geometry()
            Geometrie.setWidth(Geometrie.width() + 150 - Const.ColumnSize)
            ConfCultureTable.setGeometry(Geometrie)
            ConfCultureTable.setColumnWidth(0, 150)
            # Header
            ConfCultureTable.setItem(0, 0, QTableWidgetItem("Culture"))
            ConfCultureTable.setItem(1, 0, QTableWidgetItem("Rdt (t/ha)"))
            ConfCultureTable.setItem(2, 0, QTableWidgetItem("Prix de vente (€/t)"))
            ConfCultureTable.setItem(3, 0, QTableWidgetItem("Cout de production (€/t)"))
            ConfCultureTable.setItem(4, 0, QTableWidgetItem("Paille (oui/non)"))
            ConfCultureTable.setItem(5, 0, QTableWidgetItem("Ensilage (oui/non)"))
            ConfCultureTable.setItem(6, 0, QTableWidgetItem("Luzerne (oui/non)"))
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
            self.ui.NbYearLuzerneBox.setValue(self.NbAnneeLuzerne)
            # On change:
            ConfCultureTable.itemChanged.connect(self.OnChange_ConfCultureTable)
            ConfTypeSolTable.itemChanged.connect(self.OnChange_ConfTypeSolTable)
            self.ui.NbYearSimulationBox.valueChanged.connect(self.OnChange_NbYearSimulationBox)
            self.ui.NbSimuPerYearBox.valueChanged.connect(self.OnChange_NbSimuPerYearBox)
            self.ui.NbBestResultBox.valueChanged.connect(self.OnChange_NbBestResultBox)
            self.ui.NbYearLuzerneBox.valueChanged.connect(self.OnChange_NbYearLuzerneBox)
            self.ui.ConfigOptiMbIft_Slider.valueChanged.connect(self.OnChange_ConfigOptiMbIft_Slider)
            return True

        except:
            DebugFctnBreakPoint()
            return False

    # OnChange_ConfCultureTable: Method called on change event in ConfigCultureTypeTable
    def OnChange_ConfCultureTable(self):
        try:
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
                self.VredementCulture[col - 1] = float(ConfCultureTable.item(row, col).text())
            if row == 2:
                # Update culturePrice vector with update
                self.VculturePrice[col - 1] = float(ConfCultureTable.item(row, col).text())
            if row == 3:
                # Update culturePrice vector with update
                self.VcultureProdPrice[col - 1] = float(ConfCultureTable.item(row, col).text())
            if row == 4:
                # Update culturePrice vector with update
                self.VredementCulturePaille[col - 1] = int(float(ConfCultureTable.item(row, col).text()))
            if row == 5:
                # Update culturePrice vector with update
                self.VredementCultureEnsilage[col - 1] = int(float(ConfCultureTable.item(row, col).text()))
            if row == 6:
                # Update culturePrice vector with update
                self.VredementCultureLuzerne[col - 1] = int(float(ConfCultureTable.item(row, col).text()))
            if row == 7:
                # Update culturePrice vector with update
                self.VcultureIft[col - 1] = float(ConfCultureTable.item(row, col).text())
            return True

        except:
            DebugFctnBreakPoint()
            return False

    # OnChange_ConfTypeSolTable: Method called on change event in ConfigSolTypeTable
    def OnChange_ConfTypeSolTable(self):
        try:
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
            return True

        except:
            DebugFctnBreakPoint()
            return False

    # OnChange_NbSimuPerYearBox: Method called on change event in NbSimuPerYearBox
    def OnChange_NbSimuPerYearBox(self):
        try:
            self.NbSimuPerYear = self.ui.NbSimuPerYearBox.value()
            return True

        except:
            DebugFctnBreakPoint()
            return False

    # OnChange_NbYearSimulationBox: Method called on change event in NbYearSimulationBox
    def OnChange_NbYearSimulationBox(self):
        try:
            self.NbAnneeSimulee = self.ui.NbYearSimulationBox.value()
            self.InitCultureOutputTable(self.ui.OutputCultureTable)
            self.InitReportOutputTable(self.ui.tableMarginConstraint, self.ui.tableMeanPerYear)
            return True

        except:
            DebugFctnBreakPoint()
            return False

    # OnChange_NbBestResultBox: Method called on change event in NbBestResultBox
    def OnChange_NbBestResultBox(self):
        try:
            self.NbBestResult = self.ui.NbBestResultBox.value()
            self.ui.IndexBestResultBox.setMaximum(self.NbBestResult - 1)
            return True

        except:
            DebugFctnBreakPoint()
            return False

    # OnChange_NbYearLuzerneBox: Method called on change event in NbYearLuzerneBox
    def OnChange_NbYearLuzerneBox(self):
        try:
            self.NbAnneeLuzerne = self.ui.NbYearLuzerneBox.value()
            return True

        except:
            DebugFctnBreakPoint()
            return False

    # OnChange_ConfigOptiMbIft_Slider: Method called on change event in ConfigOptiMbIft_Slider
    def OnChange_ConfigOptiMbIft_Slider(self):
        try:
            ConfigOptiMbIft = self.ui.ConfigOptiMbIft_Slider.value()
            if ConfigOptiMbIft == 0:
                self.WeightIFT = 0.0
                self.WeightMB = 1.0 - self.WeightIFT
                self.solverMode = 'unconstrained IFT'
                self.kIFT = 0.0
            elif ConfigOptiMbIft == 1:
                self.WeightIFT = 0.5
                self.WeightMB = 1.0 - self.WeightIFT
                self.solverMode = 'constrained IFT'
                self.kIFT = 0.0
            elif ConfigOptiMbIft == 2:
                self.WeightIFT = 0.5
                self.WeightMB = 1.0 - self.WeightIFT
                self.solverMode = 'constrained decreasing IFT'
                self.kIFT = 0.01

            return True

        except:
            DebugFctnBreakPoint()
            return False

    # InitHiddenConfigTab: Init hidden config tab
    def InitHiddenConfigTab(self):
        try:
            ConfigCultureSolTable = self.ui.ConfigCultureSolTable
            InitTable(ConfigCultureSolTable, self.NbTypeSol + 1, self.NbCulture + 1, 0, 25)
            Geometrie = ConfigCultureSolTable.geometry()
            Geometrie.setWidth(Geometrie.width() + 150 - Const.ColumnSize)
            ConfigCultureSolTable.setGeometry(Geometrie)
            ConfigCultureSolTable.setColumnWidth(0, 150)
            # Header
            for Sol in range(self.NbTypeSol):
                ConfigCultureSolTable.setItem(Sol + 1, 0, QTableWidgetItem(self.Vtypesol[Sol]))
            for Culture in range(self.NbCulture):
                ConfigCultureSolTable.setItem(0, Culture + 1, QTableWidgetItem(self.Vculture[Culture]))

            for Sol in range(self.NbTypeSol):
                for Culture in range(self.NbCulture):
                    ConfigCultureSolTable.setItem(Sol + 1, Culture + 1,
                                                  QTableWidgetItem(str(self.VcultureSol[Culture][Sol])))

            # ConfigRotationCultureN_1Text
            Geometrie = self.ui.ConfigRotationCultureN_1Text.geometry()
            Geometrie.setY(25 * (self.NbTypeSol + 2) + 12)
            Geometrie.setHeight(25)
            self.ui.ConfigRotationCultureN_1Text.setGeometry(Geometrie)
            # ConfTypeSolTable
            RotationCultureN_1Table = self.ui.ConfigRotationCultureN_1Table
            InitTable(RotationCultureN_1Table, self.NbCulture + 1, self.NbCulture + 1,
                      0, 25 * (self.NbTypeSol + 3) + 12)

            # Header row and column with culture names
            for Culture in range(self.NbCulture):
                RotationCultureN_1Table.setItem(0, Culture + 1, QTableWidgetItem("n " + self.Vculture[Culture]))
                RotationCultureN_1Table.setItem(Culture + 1, 0, QTableWidgetItem("n-1 " + self.Vculture[Culture]))

            # Init table
            for CultureN in range(self.NbCulture):
                for CultureN_1 in range(self.NbCulture):
                    RotationCultureN_1Table.setItem(CultureN + 1, CultureN_1 + 1,
                                                    QTableWidgetItem(str(self.VRotationN_1[CultureN][CultureN_1])))

            # On change
            ConfigCultureSolTable.itemChanged.connect(self.OnChange_ConfigCultureSolTable)
            RotationCultureN_1Table.itemChanged.connect(self.OnChange_RotationCultureN_1Table)

            # self.ui.tabWidget.setTabEnabled(2, False)
            page = self.ui.tabWidget.findChild(QWidget, "HiddenConfigTab")
            index = self.ui.tabWidget.indexOf(page)
            if index != -1:
                self.ui.tabWidget.removeTab(index)
            return True

        except:
            DebugFctnBreakPoint()
            return False

    # OnChange_ConfigCultureSolTable: Method called on change event on ConfigCultureSolTable
    def OnChange_ConfigCultureSolTable(self):
        try:
            ConfigCultureSolTable = self.ui.ConfigCultureSolTable
            row = ConfigCultureSolTable.currentRow()
            col = ConfigCultureSolTable.currentColumn()
            if row > 0 and col > 0:
                self.VcultureSol[col - 1][row - 1] = float(ConfigCultureSolTable.item(row, col).text())
            return True

        except:
            DebugFctnBreakPoint()
            return False

    # OnChange_RotationCultureN_1Table: Method called on change event on ConfigRotationCultureN_1Table
    def OnChange_RotationCultureN_1Table(self):
        try:
            RotationCultureN_1Table = self.ui.ConfigRotationCultureN_1Table
            row = RotationCultureN_1Table.currentRow()
            col = RotationCultureN_1Table.currentColumn()
            if row > 0 and col > 0:
                self.VRotationN_1[row - 1][col - 1] = float(RotationCultureN_1Table.item(row, col).text())
            return True

        except:
            DebugFctnBreakPoint()
            return False

    # InitInputTab: Init tables in tab "Entrées"
    def InitInputTab(self):
        try:
            # Init user selection
            if self.FirstInit:
                self.ui.UserNameComboBox.addItems(self.Vusers)
            else:
                self.SuspendAllConnections(True)
                self.ui.UserNameComboBox.clear()
                self.ui.UserNameComboBox.addItems(self.Vusers)
                self.ui.UserNameComboBox.setCurrentIndex(GetIndexFromId(self.VusersId, self.ActualUserId))
                self.SuspendAllConnections(False)

            # Init parcelle culture input table
            InTable = self.ui.ParcelCultureInputTable
            InTable.clear()
            InitTable(InTable, self.NbParcelle + 1, self.NbAnneeCultureParcelle + 3, 0, 25)
            # Fill Header
            InTable.setItem(0, 0, QTableWidgetItem("Parcelle"))
            for Annee in range(self.NbAnneeCultureParcelle):
                InTable.setItem(0, self.NbAnneeCultureParcelle - Annee,
                                QTableWidgetItem("Culture n-" + str(self.VanneeCultureParcelle[Annee])))
            InTable.setItem(0, self.NbAnneeCultureParcelle + 1, QTableWidgetItem("Taille Parcelle (ha)"))
            InTable.setItem(0, self.NbAnneeCultureParcelle + 2, QTableWidgetItem("Type Sol"))

            for Parcelle in range(self.NbParcelle):
                # Fill Row Header with parcel names
                InTable.setItem(Parcelle + 1, 0, QTableWidgetItem(self.Vparcelle[Parcelle]))
                # Fill first column with input of n-1 year
                # Create list box selection for culture, based on what is in config tab
                for Annee in range(self.NbAnneeCultureParcelle):
                    comboCulture = QtWidgets.QComboBox()
                    comboCulture.addItems(self.Vculture)
                    InTable.setCellWidget(Parcelle + 1, self.NbAnneeCultureParcelle - Annee, comboCulture)
                    InTable.cellWidget(Parcelle + 1, self.NbAnneeCultureParcelle - Annee). \
                        setCurrentIndex(self.VparcelleCulture_N_X[Annee][Parcelle])
                InTable.setItem(Parcelle + 1,
                                self.NbAnneeCultureParcelle + 1, QTableWidgetItem(str(self.VparcelleTaille[Parcelle])))
                comboTypeSol = QtWidgets.QComboBox()
                comboTypeSol.addItems(self.Vtypesol)
                InTable.setCellWidget(Parcelle + 1, self.NbAnneeCultureParcelle + 2, comboTypeSol)
                InTable.cellWidget(Parcelle + 1,
                                   self.NbAnneeCultureParcelle + 2).setCurrentIndex(self.VparcelleTypeSol[Parcelle])

            # Init Qtt min
            self.ui.QttPailleMinBox.setValue(self.QttPailleMin)
            self.ui.QttEnsilageMinBox.setValue(self.QttEnsilageMin)
            self.ui.QttLuzerneMinBox.setValue(self.QttLuzerneMin)
            # On change:
            InTable.itemChanged.connect(self.OnChange_InputTable)
            self.ui.QttPailleMinBox.valueChanged.connect(self.OnChange_QttPailleMinBox)
            self.ui.QttEnsilageMinBox.valueChanged.connect(self.OnChange_QttEnsilageMinBox)
            self.ui.QttLuzerneMinBox.valueChanged.connect(self.OnChange_QttLuzerneMinBox)
            self.ui.UserNameComboBox.currentTextChanged.connect(self.OnChange_UserNameComboBox)
            # On clicks:
            self.ui.ValindInput.clicked.connect(self.OnClick_ValidInput)
            return True

        except:
            DebugFctnBreakPoint()
            return False

    # OnClick_ValidInput: Method called on click event on ValidInput
    def OnClick_ValidInput(self):
        try:
            InTable = self.ui.ParcelCultureInputTable
            # Update Input n-1
            for Row in range(self.NbParcelle):
                # Get VparcelleCulture_N_X value
                for Year in range(self.NbAnneeCultureParcelle):
                    self.VparcelleCulture_N_X[Year][Row] = \
                        InTable.cellWidget(Row + 1, self.NbAnneeCultureParcelle - Year).currentIndex()
                # Get VparcelleTypeSol value
                self.VparcelleTypeSol[Row] = InTable.cellWidget(Row + 1, self.NbAnneeCultureParcelle + 2).currentIndex()
                # Set VparcelleCulture_N_X in OutputTable
                OCT = self.ui.OutputCultureTable
                OCT.setItem(Row + 1, 1, QTableWidgetItem(self.Vculture[self.VparcelleCulture_N_X[0][Row]]))
            return True

        except:
            DebugFctnBreakPoint()
            return False

    # OnChange_InputTable: Method called on change event in ParcelCultureInputTable
    def OnChange_InputTable(self):
        try:
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
            return True

        except:
            DebugFctnBreakPoint()
            return False

    # OnChange_QttPailleMinBox: Method called on change event in QttPailleMinBox
    def OnChange_QttPailleMinBox(self):
        try:
            self.QttPailleMin = self.ui.QttPailleMinBox.value()
            return True

        except:
            DebugFctnBreakPoint()
            return False

    # OnChange_QttLuzerneMinBox: Method called on change event in QttLuzerneMinBox
    def OnChange_QttLuzerneMinBox(self):
        try:
            self.QttLuzerneMin = self.ui.QttLuzerneMinBox.value()
            return True

        except:
            DebugFctnBreakPoint()
            return False

    # OnChange_QttEnsilageMinBox: Method called on change event in QttEnsilageMinBox
    def OnChange_QttEnsilageMinBox(self):
        try:
            self.QttEnsilageMin = self.ui.QttEnsilageMinBox.value()
            return True

        except:
            DebugFctnBreakPoint()
            return False

    # OnChange_UserNameTab: Method called on change event in UserNameTab
    def OnChange_UserNameComboBox(self):
        try:
            Index = self.ui.UserNameComboBox.currentIndex()
            self.ActualUserName = self.Vusers[Index]
            self.ActualUserId = self.VusersId[Index]
            self.LoadDataBase()
            self.InitAllTab()
            return True

        except:
            DebugFctnBreakPoint()
            return False

    # InitOutputTab: Init tables in tab "Résultats"
    def InitOutputTab(self):
        try:
            self.InitCultureOutputTable(self.ui.OutputCultureTable)
            self.InitReportOutputTable(self.ui.tableMarginConstraint, self.ui.tableMeanPerYear)
            self.ui.IndexBestResultBox.setMaximum(self.NbBestResult - 1)
            self.ui.IndexBestResultBox.valueChanged.connect(self.FillOutputTable)
            return True

        except:
            DebugFctnBreakPoint()
            return False

    # InitCultureOutputTable: Init culture output table with header
    def InitCultureOutputTable(self, CultOutTab):
        try:
            # Set culture output table
            InitTable(CultOutTab, self.NbParcelle + 1, self.NbAnneeSimulee + 2, 0, 25)
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
                CultOutTab.setItem(Parcelle + 1, 1,
                                   QTableWidgetItem(self.Vculture[self.VparcelleCulture_N_X[0][Parcelle]]))
            return True

        except:
            DebugFctnBreakPoint()
            return False

    # InitReportOutputTable: Init report table with header
    def InitReportOutputTable(self, OutReportTab, OutMeanPerYearTab):
        try:
            # Set Margin and constraint table
            InitTable(OutReportTab, 5, self.NbAnneeSimulee + 2, 0, (self.NbParcelle + 2) * Const.RowSize + 2)
            # Fill Row header
            OutReportTab.setItem(0, 0, QTableWidgetItem("Marge"))
            OutReportTab.setItem(1, 0, QTableWidgetItem("Ift"))
            OutReportTab.setItem(2, 0, QTableWidgetItem("Qtt paille"))
            OutReportTab.setItem(3, 0, QTableWidgetItem("Qtt ensilage"))
            OutReportTab.setItem(4, 0, QTableWidgetItem("Qtt luzerne"))
            InitTable(OutMeanPerYearTab, 6, 1, (self.NbAnneeSimulee + 2) * Const.ColumnSize + 2,
                      (self.NbParcelle + 1) * Const.RowSize + 2)
            OutMeanPerYearTab.setItem(0, 0, QTableWidgetItem("Moyenne/an"))
            return True

        except:
            DebugFctnBreakPoint()
            return False

    # FillOutputTable: Fill the output table with culture associated with
    def FillOutputTable(self):
        CultOutTab = self.ui.OutputCultureTable
        MarginConstraintTable = self.ui.tableMarginConstraint
        MeanPerYearTable = self.ui.tableMeanPerYear
        IndexBestResult = self.ui.IndexBestResultBox.value()
        for Year in range(self.NbAnneeSimulee):
            for Parcelle in range(self.NbParcelle):
                index = int(self.ModelOutput[IndexBestResult][0][Year][0][Parcelle])
                if index != -1:
                    CultOutTab.setItem(Parcelle + 1, Year + 2,
                                   QTableWidgetItem(self.Vculture[index]))
                else:
                    CultOutTab.setItem(Parcelle + 1, Year + 2,
                                       QTableWidgetItem("-"))
            for i in range(5):
                value = str(round(self.ModelOutput[IndexBestResult][0][Year][1][i], 2))
                MarginConstraintTable.setItem(i, Year + 2, QTableWidgetItem(value))

        for i in range(5):
                value = str(round(self.ModelOutput[IndexBestResult][1][i], 2))
                MeanPerYearTable.setItem(0, i + 1, QTableWidgetItem(value))

    # OnClick_StartCalculation: Method to start calculation.
    def OnClick_StartCalculation(self):
        Status = True
        start_time_2 = time.clock()
        if Status:
            Status = self.WrapperModelInput()
        print(time.clock() - start_time_2)

        if Status:
            self.solver.__init__(**self.ModelInput)
            Status = self.solver.solve()
        print(time.clock() - start_time_2)

        # Choix du mode de selection: 'MB' ou 'MCDA'
        if Status:
            maxProgressBarIter = (1 - self.NbSimuPerYear ** (self.NbAnneeSimulee + 1)) / (1 - self.NbSimuPerYear) - 1
            self.ui.CalculationProgressBar.setMaximum(maxProgressBarIter)
            Status = self.solver.resultSelection(selectionMode='MCDA', weightIFT=self.WeightIFT, weightMB=self.WeightMB)
            self.ui.CalculationProgressBar.setValue(maxProgressBarIter)
            # if Status != False:
            Status = self.solver.assolement()
        print(time.clock() - start_time_2)

        if Status:
            self.WrapperModelOutput()
        else:
            self.ModelOutput = DummyCalculation(**self.ModelInput)

        if Const.Verbose:
            self.Debug_PrintOutput()
        self.FillOutputTable()
        print(time.clock() - start_time_2)

    def WrapperModelInput(self):
        try:
            # Format MPCn1
            MPCn1 = np.zeros((self.NbParcelle, self.NbCulture))
            for Parcelle in range(self.NbParcelle):
                MPCn1[Parcelle][self.VparcelleCulture_N_X[0][Parcelle]] = 1
            self.ModelInput["MPCn1"] = MPCn1

            # Format MPTS
            MPTS = np.zeros((self.NbParcelle, self.NbTypeSol))
            for Parcelle in range(self.NbParcelle):
                MPTS[Parcelle][self.VparcelleTypeSol[Parcelle]] = 1
            self.ModelInput["MPTS"] = MPTS

            # Format surfaces
            self.ModelInput["surface"] = self.VparcelleTaille

            # Format numPailleMin
            self.ModelInput["constraintPaille"] = self.QttPailleMin

            # Format numEnsilageMin
            self.ModelInput["constraintEnsilage"] = self.QttEnsilageMin

            # Format numLuzerneMin
            self.ModelInput["constraintLuzerne"] = self.QttLuzerneMin

            # Format numYear
            self.ModelInput["numYear"] = self.NbAnneeSimulee

            # Format numSolutionYear
            self.ModelInput["numSolutionYear"] = self.NbSimuPerYear

            # Format numSolutionYear
            self.ModelInput["yearRollLuzerne"] = self.NbAnneeLuzerne

            # Format number best results
            # TODO: décommenter cette ligne après intégration dans le modèle:
            #  self.ModelInput["numBestResult"] = self.NbBestResult

            # Format rendement
            self.ModelInput["eta"] = self.VredementCulture

            # Format prix culture
            self.ModelInput["prixVenteCulture"] = self.VculturePrice

            # Format cout de prod culture
            self.ModelInput["coutProdCulture"] = self.VcultureProdPrice

            # Format rendement paille culture
            # TODO: décommenter cette ligne après intégration dans le modèle:
            #  self.ModelInput["etaPaille"] = self.VredementCulturePaille  # TODO: Name to be defined!!

            # Format rendement ensilage culture
            # TODO: décommenter cette ligne après intégration dans le modèle:
            #  self.ModelInput["etaEnsilage"] = self.VredementCultureEnsilage  # TODO: Name to be defined!!

            # Format rendement luzerne culture
            # TODO: décommenter cette ligne après intégration dans le modèle:
            #  self.ModelInput["etaLuzerne"] = self.VredementCultureLuzerne  # TODO: Name to be defined!!

            # Format IFT culture
            self.ModelInput["ift"] = self.VcultureIft

            # Format impact of sol on culture
            self.ModelInput["R1"] = self.VcultureSol

            # Format culture rotation n-1
            self.ModelInput["R2"] = self.VRotationN_1

            # Format
            self.ModelInput["solverMode"] = self.solverMode

            # Format
            self.ModelInput["kIFT"] = self.kIFT

            # Format culture names
            # TODO: to be removed
            self.ModelInput["cultureList"] = self.Vculture

            # Format parcel names
            # TODO: to be removed
            self.ModelInput["parcelleList"] = self.Vparcelle

            if Const.Verbose:
                self.Debug_PrintDictionary()

            return True

        except:
            DebugFctnBreakPoint()
            return False

    def WrapperModelOutput(self):
        try:
            self.ModelOutput = []
            for Result in range(self.NbBestResult):
                result_n_year = []
                TotalMb = 0
                TotalIft = 0
                TotalQtePaille = 0
                TotalQteEnsilage = 0
                TotalQteLuzerne = 0
                for Year in range(self.NbAnneeSimulee):
                    result_1_year_assol = np.zeros(self.NbParcelle)
                    for Parcelle in range(self.NbParcelle):
                        CultureNotFound = True
                        for Culture in range(self.NbCulture):
                            if self.solver.yearAssolementConfig[Year][Parcelle][Culture] == 1:
                                result_1_year_assol[Parcelle] = Culture
                                CultureNotFound = False
                        if CultureNotFound:
                            result_1_year_assol[Parcelle] = -1
                    result_1_year_other = np.array([self.solver.yearMB[Year],
                                                    self.solver.yearIFT[Year],
                                                    self.solver.yearQtePaille[Year],
                                                    self.solver.yearQteEnsilage[Year],
                                                    self.solver.yearQteLuzerne[Year]])
                    TotalMb += self.solver.yearMB[Year]
                    TotalIft += self.solver.yearIFT[Year]
                    TotalQtePaille += self.solver.yearQtePaille[Year]
                    TotalQteEnsilage += self.solver.yearQteEnsilage[Year]
                    TotalQteLuzerne += self.solver.yearQteLuzerne[Year]
                    result_1_year = [result_1_year_assol, result_1_year_other]
                    result_n_year.append(result_1_year)
                AverageMb = TotalMb / self.NbAnneeSimulee
                AverageIft = TotalIft / self.NbAnneeSimulee
                AverageQtePaille = TotalQtePaille / self.NbAnneeSimulee
                AverageQteEnsilage = TotalQteEnsilage / self.NbAnneeSimulee
                AverageQteLuzerne = TotalQteLuzerne / self.NbAnneeSimulee
                result_n_year_other_average = np.array([AverageMb,
                                                        AverageIft,
                                                        AverageQtePaille,
                                                        AverageQteEnsilage,
                                                        AverageQteLuzerne])
                result_n_year_with_average = [result_n_year, result_n_year_other_average]

                self.ModelOutput.append(result_n_year_with_average)
            return True

        except:
            DebugFctnBreakPoint()
            return False

    def ExitFunction(self):
        self.db.close()
        print("Exit")
        Const.MyApp.quit()


if __name__ == "__main__":
    # Instantiation du Main
    TestApp = TestWindow()
    TestApp.setWindowTitle("Assolia " + Const.Version)
    TestApp.show()

    sys_exit(Const.MyApp.exec_())
