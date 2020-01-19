from BouiBouiTools import Const as Const
import numpy as np

# Initialisation of variables to be used in case that there is no file to open.
Const.Vparcelle_Init = ['Souleilla', 'Paguère', '4 chemins', 'Champ long', 'Lougeas', 'Labourdette']
Const.NbParcelle_Init = len(Const.Vparcelle_Init)

Const.VparcelleTaille_Init = np.array([10, 10, 10, 20, 20, 20])
Const.NbParcelleTaille_Init = len(Const.VparcelleTaille_Init)
assert Const.NbParcelleTaille_Init == Const.NbParcelle_Init

Const.VparcelleTypeSol_Init = np.array([0, 0, 0, 3, 3, 3])
Const.NbParcelleTypeSol_Init = len(Const.VparcelleTypeSol_Init)
assert Const.NbParcelleTypeSol_Init == Const.NbParcelle_Init

Const.Vculture_Init = ['Soja', 'Blé de force', 'Orge', 'Maïs', 'Tournesol']
Const.NbCulture_Init = len(Const.Vculture_Init)
Const.VredementCulture_Init = np.array([4, 8, 7, 13, 3.4])
assert len(Const.VredementCulture_Init) == Const.NbCulture_Init
Const.VculturePrice_Init = np.array([350, 200, 150, 150, 400])
assert len(Const.VculturePrice_Init) == Const.NbCulture_Init
Const.VcultureProdPrice_Init = np.array([400, 600, 400, 1200, 300])
assert len(Const.VcultureProdPrice_Init) == Const.NbCulture_Init
Const.VredementCulturePaille_Init = np.array([0, 1, 1, 0, 0])
assert len(Const.VredementCulturePaille_Init) == Const.NbCulture_Init
Const.VredementCultureEnsilage_Init = np.array([0, 0, 0, 1, 0])
assert len(Const.VredementCulturePaille_Init) == Const.NbCulture_Init
Const.VredementCultureLuzerne_Init = np.array([0, 0, 0, 0, 0])
assert len(Const.VredementCultureLuzerne_Init) == Const.NbCulture_Init
Const.VcultureIft_Init = np.array([0.7, 2.3, 1.6, 1.1, 1.7])
assert len(Const.VcultureIft_Init) == Const.NbCulture_Init

Const.Vtypesol_Init = ['Coteaux', 'Plaines argilo-calcaires', 'Plaines boulbènes', 'Plaines irrigués']
Const.NbTypeSol_Init = len(Const.Vtypesol_Init)

Const.VcultureSol_Init = np.array([[50, 15, 30, 5],
                                   [15, 15, 25, 5],
                                   [15, 15, 25, 5],
                                   [25, 10, 25, 5],
                                   [15, 10, 25, 5]])
assert len(Const.VcultureSol_Init) == Const.NbCulture_Init
assert len(Const.VcultureSol_Init[0]) == Const.NbTypeSol_Init

Const.VRotationN_1_Init = np.array([[50,  100, 100, 95,  95],
                                    [100, 30,  70,  100, 100],
                                    [100, 50,  50,  100, 100],
                                    [100, 80,  80,  80,  80],
                                    [100, 95,  95,  95,  95]])
assert len(Const.VRotationN_1_Init) == Const.NbCulture_Init
assert len(Const.VRotationN_1_Init[0]) == Const.NbCulture_Init

Const.QttPailleMin_Init = 200
Const.QttEnsilageMin_Init = 250
Const.QttLuzerneMin_Init = 0

Const.NbSimuPerYear_Init = 3
Const.NbAnneeSimulee_Init = 3
Const.NbBestResult_Init = 3

Const.VparcelleCulture_N_1_Init = np.array([1, 2, 4, 3, 0, 1])
assert len(Const.VparcelleCulture_N_1_Init) == Const.NbParcelle_Init


class DefaultInit:
    def __init__(self):
        self.Vparcelle_Init = Const.Vparcelle_Init
        self.NbParcelle_Init = Const.NbParcelle_Init

        self.VparcelleTaille_Init = Const.VparcelleTaille_Init
        self.NbParcelleTaille_Init = Const.NbParcelleTaille_Init

        self.VparcelleTypeSol_Init = Const.VparcelleTypeSol_Init
        self.NbParcelleTypeSol_Init = Const.NbParcelleTypeSol_Init

        self.Vculture_Init = Const.Vculture_Init
        self.NbCulture_Init = Const.NbCulture_Init
        self.VredementCulture_Init = Const.VredementCulture_Init
        self.VculturePrice_Init = Const.VculturePrice_Init
        self.VcultureProdPrice_Init = Const.VcultureProdPrice_Init
        self.VredementCulturePaille_Init = Const.VredementCulturePaille_Init
        self.VredementCultureEnsilage_Init = Const.VredementCultureEnsilage_Init
        self.VredementCultureLuzerne_Init = Const.VredementCultureLuzerne_Init
        self.VcultureIft_Init = Const.VcultureIft_Init

        self.Vtypesol_Init = Const.Vtypesol_Init
        self.NbTypeSol_Init = Const.NbTypeSol_Init
        self.VcultureSol_Init = Const.VcultureSol_Init

        self.VRotationN_1_Init = Const.VRotationN_1_Init

        self.QttPailleMin_Init = Const.QttPailleMin_Init
        self.QttEnsilageMin_Init = Const.QttEnsilageMin_Init
        self.QttLuzerneMin_Init = Const.QttLuzerneMin_Init

        self.NbSimuPerYear_Init = Const.NbSimuPerYear_Init
        self.NbAnneeSimulee_Init = Const.NbAnneeSimulee_Init

        self.NbBestResult_Init = Const.NbBestResult_Init

        self.VparcelleCulture_N_1_Init = Const.VparcelleCulture_N_1_Init
