from BouiBouiTools import Const
import numpy as np

# Initialisation of variables to be used in case that there is no file to open.
Const.Vparcelle_Init = ['souleilla', 'paguère', '4 chemins', 'champ long', 'lougeas', 'labourdette']
Const.NbParcelle_Init = len(Const.Vparcelle_Init)

Const.VparcelleTaille_Init = np.array([10, 10, 10, 20, 20, 20])
Const.NbParcelleTaille_Init = len(Const.VparcelleTaille_Init)
assert Const.NbParcelleTaille_Init == Const.NbParcelle_Init

Const.VparcelleTypeSol_Init = np.array([0, 0, 0, 3, 3, 3])
Const.NbParcelleTypeSol_Init = len(Const.VparcelleTypeSol_Init)
assert Const.NbParcelleTypeSol_Init == Const.NbParcelle_Init

Const.Vculture_Init = ['Soja', 'Blé de force', 'Orge', 'Maïs', 'Tournesol']
Const.NbCulture_Init = len(Const.Vculture_Init)

Const.Vtypesol_Init = ['Coteaux', 'plaines argilo-calcaires', 'plaines boulbènes', 'plaines irrigués']
Const.NbTypeSol_Init = len(Const.Vtypesol_Init)

Const.NbSimuPerYear_Init = 5

Const.NbAnneeSimulee_Init = 3
Const.PailleMin_Init = 200
Const.EnsilageMin_Init = 250

Const.VInputN_1_Init = np.array([0, 1, 2, 3, 4, 5])
assert len(Const.VInputN_1_Init) == Const.NbParcelle_Init

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

        self.Vtypesol_Init = Const.Vtypesol_Init
        self.NbTypeSol_Init = Const.NbTypeSol_Init

        self.NbSimuPerYear_Init = Const.NbSimuPerYear_Init

        self.NbAnneeSimulee_Init = Const.NbAnneeSimulee_Init
        self.PailleMin_Init = Const.PailleMin_Init
        self.EnsilageMin_Init = Const.EnsilageMin_Init

        self.VInputN_1_Init = Const.VInputN_1_Init