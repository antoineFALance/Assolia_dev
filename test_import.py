import Assolia_Solver as A_solver
import numpy as np


#Déclaration des constantes

Vculture=['Soja','Blé de force','Orge', 'Maïs','Tournesol']
Vparcelle=['Souleilla','Paguère','4 chemins','Champs long','Loujeas','Labourdte']

nbParcelle=len(Vparcelle)
nbCulture = len(Vculture)
iterCalcul=0
numPailleMin = 200
numEnsilageMin = 250
numSolutionYear=3
numYear=6
eta=np.array([4,8,7,13,3.4])
ift=np.array([0.7,2.3,1.6,1.1,1.7])
surface=np.array([10,10,10,20,20,20])
prixVenteCulture=np.array([350,200,150,150,375])
coutProdCulture=np.array([400,600,400,1200,300])

MPCn1 = np.array([[0,1,0,0,0],
               [0,0,1,0,0],
               [0,0,0,0,1],
               [0,0,0,1,0],
               [1,0,0,0,0],
               [0,1,0,0,0]])

MPTS=np.array([[1, 0, 0, 0],
               [1, 0, 0, 0],
               [1, 0, 0, 0],
               [0, 0, 0, 1],
               [0, 0, 0, 1],
               [0, 0, 0, 1]])

R1=np.array([[50,15,30,5],
               [15,15,25,5],
               [15,15,25,5],
               [25,10,25,5],
               [15,10,25,5]])

R2=np.array([[50,100,100,95,95],
             [100,30,70,100,100],
             [100,50,50,100,100],
             [100,80,80,80,80],
             [100,95,95,95,95]])


#choix mode de solver
#'unconstrained IFT', 'constrained IFT', 'constrained decreasing IFT'


solver = A_solver.objectSolver(
solverMode = 'constrained IFT',
kIFT = 0,
cultureList = Vculture,
parcelleList = Vparcelle,
constraintPaille = numPailleMin,
constraintEnsilage = numEnsilageMin,
numSolutionYear = numSolutionYear,
numYear = numYear,
eta = eta,
ift = ift,
surface = surface,
prixVenteCulture = prixVenteCulture,
coutProdCulture = coutProdCulture,
MPTS = MPTS,
MPCn1=MPCn1,
R1 = R1,
R2 = R2)


solver.solve()
#Choix du mode de selection: 'MB' ou 'MCDA'
solver.resultSelection(selectionMode='MCDA',weightIFT=0.5,weightMB=0.5)
solver.assolement()

print(solver.dfMBSolution)
print(solver.dfIFTSolution)
print(solver.yearAssolementConfig)
print(solver.yearMB)
print(solver.yearQtePaille)
print(solver.yearQteEnsilage)
