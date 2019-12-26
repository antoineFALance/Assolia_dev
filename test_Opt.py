import numpy as np
from ortools.linear_solver import pywraplp



nbParcelle=6
nbCulture = 5

MPCn1 = np.array([[0,0,1,0,0],
               [1,0,0,0,0],
               [0,1,0,0,0],
               [1,0,0,0,0],
               [0,0,1,0,0],
               [0,0,0,1,0]])


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

surface=np.array([10,10,10,20,20,20])
prixVenteCulture=np.array([350,200,150,150,400])
coutProdCulture=np.array([400,600,400,1200,300])

eta=np.array([4,8,7,13,3.4])
etaPaille=np.array([0,5.44,4.76,0,0])
etaEnsillage=np.array([0,0,0,18.525,0])

#1.Contruction matrice etap
etap = np.zeros((nbParcelle,nbCulture))
for i in range(nbCulture):
    for j in range(nbParcelle):
        etap[j][i]=eta[i]
print(etap)

#2.Construction de la matrice eta_ts

eta_ts =np.ones((nbParcelle,nbCulture))- 1/100*(np.transpose(np.matmul(R1,np.transpose(MPTS))))
print(eta_ts)

#3.Construction de la matrice eta_n1
eta_n1 = 1/100*np.matmul(MPCn1,R2)
print(eta_n1)
#4.Construction de la matrice etaG
etaG=np.zeros((nbParcelle,nbCulture))
Marge=np.zeros((nbParcelle,nbCulture))
for i in range(nbCulture):
    for j in range(nbParcelle):
        etaG[j][i]=etap[j][i]*eta_ts[j][i]*eta_n1[j][i]

print(etaG)

#5.Matrice Prix culture/parcelle
Pv = np.zeros((nbParcelle,nbCulture))
Ct= np.zeros((nbParcelle,nbCulture))
for i in range(nbCulture):
    for j in range(nbParcelle):
        Pv[j][i]=prixVenteCulture[i]
        Ct[j][i]=coutProdCulture[i]
print(Pv)
print(Ct)

#6.Matrice de marge
Mg= np.zeros((nbParcelle,nbCulture))
for i in range(nbCulture):
    for j in range(nbParcelle):
        Mg[j][i]=surface[j]*(etaG[j][i]*Pv[j][i]-Ct[j][i])
print(Mg)

weight =[]
for row in Mg:
    for element in row:
        weight.append(element)
print(weight)

#7. Creation du modèle
solver = pywraplp.Solver('simple_mip_program',
                             pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)

#8.  réation de la liste des variables
variables,nameVariable =[],[]
infinity = solver.infinity()

for i in range(nbCulture):
    for j in range(nbParcelle):
        nameVariable.append('x'+str(i+1)+str(j+1))
        variables.append(solver.IntVar(0, infinity,'x'+str(i+1)+str(j+1)))


#9. Ajout des contraintes
for var in variables:
    solver.Add(var <= 1)
    solver.Add(var >= 0)

#10.Fonction objectif
funObj=sum(x * y for x, y in zip(weight, variables))
solver.Maximize(funObj)


status = solver.Solve()

if status == pywraplp.Solver.OPTIMAL:
    print('Solution:')
    print('Objective value =', solver.Objective().Value())
    for var in variables:
        print(var.solution_value())

else:
    print('The problem does not have an optimal solution.')