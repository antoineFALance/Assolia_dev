import numpy as np
import pandas as pd
from ortools.linear_solver import pywraplp
from tabulate import tabulate
import time
start_time_2 = time.clock()

Vculture=['Soja','Blé de force','Orge', 'Maïs','Tournesol']
nbParcelle=6
nbCulture = 5

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

surface=np.array([10,10,10,20,20,20])
prixVenteCulture=np.array([350,200,150,150,400])
coutProdCulture=np.array([400,600,400,1200,300])

numPailleMin = 200
numEnsilageMin = 250
numSolutionYear=3
numYear=3

eta=np.array([4,8,7,13,3.4])

yearSolutionRepartition,yearSolutionValue=[],[]
for indexYear in range(numYear):
    solutionRepartition,solutionValue=[],[]

    if indexYear==0:
        initRepartition=[MPCn1]


    for cultureRepartition in initRepartition:

        #1.Contruction matrice etap
        etap = np.zeros((nbParcelle,nbCulture))
        for i in range(nbCulture):
            for j in range(nbParcelle):
                etap[j][i]=eta[i]
        # print(etap)

        #2.Construction de la matrice eta_ts

        eta_ts =np.ones((nbParcelle,nbCulture))- 1/100*(np.transpose(np.matmul(R1,np.transpose(MPTS))))
        # print(eta_ts)

        #3.Construction de la matrice eta_n1
        eta_n1 = 1/100*np.matmul(cultureRepartition,R2)
        # print("n1")
        # print(eta_n1)

        #4.Construction de la matrice etaG
        etaG=np.zeros((nbParcelle,nbCulture))
        Marge=np.zeros((nbParcelle,nbCulture))
        for i in range(nbCulture):
            for j in range(nbParcelle):
                etaG[j][i]=etap[j][i]*eta_ts[j][i]*eta_n1[j][i]
        # print("eta")
        # print(etaG)

        #Construction de la matrice/liste des eta Paille
        etaPaille,etaEnsilage=np.zeros((nbParcelle,nbCulture)),np.zeros((nbParcelle,nbCulture))
        weightPaille,weightEnsilage=[],[]
        for i in range(nbParcelle):
            for j in range(nbCulture):
                if j in (1,2):
                    etaPaille[i][j]=0.8*etaG[i][j]*surface[i]
                elif j==3:
                    etaEnsilage[i][j]=1.5*etaG[i][j]*surface[i]

        for row in etaPaille:
            for element in row:
                weightPaille.append(element)

        for row in etaEnsilage:
            for element in row:
                weightEnsilage.append(element)

        # print(weightEnsilage)
        # print(weightPaille)


        #5.Matrice Prix culture/parcelle
        Pv = np.zeros((nbParcelle,nbCulture))
        Ct= np.zeros((nbParcelle,nbCulture))
        for i in range(nbCulture):
            for j in range(nbParcelle):
                Pv[j][i]=prixVenteCulture[i]
                Ct[j][i]=coutProdCulture[i]
        # print(Pv)
        # print(Ct)

        #6.Matrice de marge
        Mg= np.zeros((nbParcelle,nbCulture))
        for i in range(nbCulture):
            for j in range(nbParcelle):
                #Mg[j][i]=surface[j]*(etaG[j][i]*Pv[j][i]-Ct[j][i])
                Mg[j][i]=surface[j]*eta_n1[j][i]*(etap[j][i]*eta_ts[j][i]*Pv[j][i]-Ct[j][i])
        # print(Mg)

        weight =[]
        for row in Mg:
            for element in row:
                weight.append(element)
        # print(weight)

        #7.Matrice des contraintes
        constMatrix1 = np.array([
                [1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1]])
        constMatrix2 = np.array(weightPaille)
        constMatrix3 = np.array(weightEnsilage)
        constMatrix = np.vstack((constMatrix1, constMatrix2, constMatrix3))



        solutionConstraintList,solutionBoundList=[],[]
        for indexSolution in range(numSolutionYear):


            if indexSolution>=1:

                constMatrix = np.vstack((constMatrix, np.array(solutionConstraintList[indexSolution-1])))
            #
            # print("MATRICE CONTRAINTES")
            # print(constMatrix)
            numvar=30
            numConstraints=len(constMatrix)

            #8.Matrice des boundaries
            bound=[1]*(numConstraints-(2+len(solutionBoundList)))
            bound.append(numPailleMin)
            bound.append(numEnsilageMin)
            if indexSolution>=1:
                for indexBound in range(len(solutionBoundList)):
                    bound.append(solutionBoundList[indexBound][0])
            # print("bound")
            # print(bound)


            #OPTIMISATION

            # Create the mip solver with the CBC backend.
            solver = pywraplp.Solver('simple_mip_program',pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)
            infinity = solver.infinity()
            x = {}
            for j in range(numvar):
                x[j] = solver.IntVar(0, infinity, 'x[%i]' % j)
                # print('Number of variables =', solver.NumVariables())

            for i in range(numConstraints):
                if i<6:
                    constraint = solver.RowConstraint(0, bound[i], '')
                elif i==6 or i==7:
                    constraint = solver.RowConstraint(bound[i], 100 * bound[i], '')
                else:
                    constraint = solver.RowConstraint(0,bound[i], '')

                for j in range(numvar):
                    constraint.SetCoefficient(x[j], int(constMatrix[i][j]))
            print('Number of constraints =', solver.NumConstraints())


            objective = solver.Objective()
            for j in range(numvar):
                objective.SetCoefficient(x[j], weight[j])
            objective.SetMaximization()


            status = solver.Solve()
            solution=[]
            if status == pywraplp.Solver.OPTIMAL:
                print('Objective value =', solver.Objective().Value())
                for j in range(numvar):
                    #print(x[j].name(), ' = ', x[j].solution_value())
                    solution.append(x[j].solution_value())


                print('Problem solved in %f milliseconds' % solver.wall_time())


            else:
                print('The problem does not have an optimal solution.')


            print("SOLUTION N° "+str(indexSolution)+" ANNEE "+str(indexYear))
            print("REPARTITION")

            repartition=np.vstack((np.array_split(solution,nbParcelle)))
            solutionRepartition.append(repartition)
            print(repartition)
            print("SOLUTION")
            marge_brute_optimale=solver.Objective().Value()
            solutionValue.append(marge_brute_optimale)
            print(solver.Objective().Value())
            # print("QTE PAILLE")
            # print(etaPaille)
            # print(np.matmul(np.transpose(repartition[:,1]),etaPaille))
            #Préparation de la contrainte issue de la solution
            solutionConstraint,solutionBound=[],[]
            for element in solution:
                if element ==0:
                    solutionConstraint.append(-1)
                elif element ==1:
                    solutionConstraint.append(1)
            solutionBound.append(-(1-solution.count(1)))
            solutionConstraintList.append(solutionConstraint)
            solutionBoundList.append(solutionBound)
            # print(solutionConstraintList)
            # print(solution)
            # print(solutionBoundList)

    initRepartition=solutionRepartition
    yearSolutionRepartition.append(solutionRepartition)
    yearSolutionValue.append(solutionValue)
print("DEBUG")
#
print(yearSolutionValue)
#print(yearSolutionRepartition)

#Création de la matrice des résultats
listMatrix,colMatrix=[],[]

for indexYear in range(numYear):
    LambdaLocal=np.zeros((numSolutionYear**(indexYear+1),numSolutionYear**numYear))
    for i in range((numSolutionYear)**(indexYear+1)):
        for j in range(numSolutionYear**numYear):
            if i*(numSolutionYear)**(numYear-(indexYear+1))<=j<=(i+1)*numSolutionYear**(numYear-(indexYear+1))-1:
                LambdaLocal[i][j]=1

    listMatrix.append(LambdaLocal)
    colMatrix.append(np.matmul(yearSolutionValue[indexYear],listMatrix[indexYear]))

matrixResult=np.transpose(colMatrix)
columnLabel=[]
dfResult=pd.DataFrame(matrixResult)
dfResult['mean'] = dfResult.mean(axis=1)

print(tabulate(dfResult,headers='keys',tablefmt='psql'))
maxMean=dfResult[dfResult['mean']==dfResult['mean'].max()]
resultList=maxMean.values.tolist()[0]
print("RESULT")
print(resultList)
print("row index")
print(dfResult.index.get_loc(maxMean.iloc[0].name))
rowSolutionIndex=dfResult.index.get_loc(maxMean.iloc[0].name)
configResultList=[]

for indexYear in range(numYear):
    configResultList.append(yearSolutionRepartition[indexYear][(rowSolutionIndex//(numSolutionYear**(numYear-(indexYear+1))))])

print(configResultList)
print(time.clock() - start_time_2)