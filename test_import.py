import Assolia_Solver as A_solver
import numpy as np
from tabulate import tabulate



#Déclaration des constantes

Vculture=['Soja','Blé de force','Orge', 'Maïs','Tournesol','Luzerne']
Vparcelle=['Souleilla','Paguère','4 chemins','Champs long','Loujeas','Labourdte']

nbParcelle=len(Vparcelle)
nbCulture = len(Vculture)
iterCalcul=0
numPailleMin = 145
numEnsilageMin = 280
numMinLuzerne= 0
yearRollLuzerne = 5
numSolutionYear=3
numYear=8
eta=np.array([4,8,7,13,3.4,8])
ift=np.array([0.7,2.3,1.6,1.1,1.7,0])
surface=np.array([10,10,10,20,20,20])

prixVenteCulture=np.array([350,200,150,150,375,0])
coutProdCulture=np.array([400,600,400,1200,300,0])

# Définition des cultures précédentes
# Année N-1
MPCn1 = np.array(
              [[1,0,0,0,0,0],
               [0,1,0,0,0,0],
               [0,0,0,0,1,0],
               [0,0,0,1,0,0],
               [1,0,0,0,0,0],
               [0,1,0,0,0,0]])

# Année N-2
MPCn2 = np.array(
              [[0,0,0,0,0,1],
               [0,0,0,0,0,1],
               [0,0,1,0,0,0],
               [0,1,0,0,0,0],
               [0,0,1,0,0,0],
               [0,0,0,1,0,0]])
# Année N-3
MPCn3 = np.array(
              [[1,0,0,0,0,0],
               [1,0,0,0,0,0],
               [0,1,0,0,0,0],
               [1,0,0,0,0,0],
               [0,1,0,0,0,0],
               [0,0,0,1,0,0]])
# Année N-4
MPCn4 = np.array(
              [[1,0,0,0,0,0],
               [1,0,0,0,0,0],
               [0,1,0,0,0,0],
               [1,0,0,0,0,0],
               [0,1,0,0,0,0],
               [0,0,0,1,0,0]])

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
               [15,10,25,5],
               [0,10,10,10]])

R2=np.array([[50,100,100,95,95,100],
             [100,30,70,100,100,100],
             [100,50,50,100,100,100],
             [100,80,80,80,80,100],
             [100,95,95,95,50,100],
             [100,120,120,100,100,100]])


#choix mode de solver
#'unconstrained IFT', 'constrained IFT', 'constrained decreasing IFT'

solver = A_solver.objectSolver(
solverMode = 'unconstrained IFT',
kIFT = 0.01,
cultureList = Vculture,
parcelleList = Vparcelle,
constraintPaille = numPailleMin,
constraintEnsilage = numEnsilageMin,
constraintLuzerne=numMinLuzerne,
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
R2 = R2,
yearRollLuzerne=yearRollLuzerne,
MPCN=[MPCn1,MPCn2,MPCn3,MPCn4])


print(solver.solve())

#Choix du mode de selection: 'MB' ou 'MCDA'
solver.resultSelection(selectionMode='MCDA',weightIFT=0.5,weightMB=0.5)
solver.assolement()


# print(solver.dfMBSolution)
# print(solver.dfIFTSolution)
# print("N° rows solution :"+str(solver.indexRowResult))
# print(solver.yearAssolementConfig)
# print(solver.yearMB)
# print(solver.yearQtePaille)
# print(solver.yearQteEnsilage)
# print(solver.yearQteLuzerne)

print(tabulate(solver.debugMb, headers='keys', tablefmt='psql'))
print('######')
print(tabulate(solver.debugIFT, headers='keys', tablefmt='psql'))
print('######')
print(tabulate(solver.debugConfig, headers='keys', tablefmt='psql'))
print("######")
print(tabulate(solver.debugPaille, headers='keys', tablefmt='psql'))
print("######")
print(tabulate(solver.debugEnsilage, headers='keys', tablefmt='psql'))
print("######")
print(tabulate(solver.debugLuzerne, headers='keys', tablefmt='psql'))





