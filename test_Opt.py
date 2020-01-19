import numpy as np
import pandas as pd
pd.set_option('max_columns', 800)
from ortools.linear_solver import pywraplp
from tabulate import tabulate
import time
from skcriteria import Data, MIN, MAX
from skcriteria.madm import closeness, simple
from scipy.spatial.distance import euclidean as dist_euclid

start_time_2 = time.clock()
#Mode du solver
#choix à rentrer : 'unconstrained IDT', 'constrained IFT', 'constrained decreasing IFT'
#choix selection : 'MB', 'MCDA'

solverMode = 'unconstrained IFT'
kIft=0.0
resultSelectionMode = 'MB'
#

#Déclaration des constantes

Vculture=['Soja','Blé de force','Orge', 'Maïs','Tournesol']
Vparcelle=['Souleilla','Paguère','4 chemins','Champs long','Loujeas','Labourdte']
nbParcelle=len(Vparcelle)
nbCulture = len(Vculture)
iterCalcul=0
numPailleMin = 200
numEnsilageMin = 250
numSolutionYear=5
numYear=6

MCDAweight=[0.5,0.5]

eta=np.array([4,8,7,13,3.4])

ift=np.array([0.7,2.3,1.6,1.1,1.7])

surface=np.array([10,10,10,20,20,20])
#prixVenteCulture=np.array([350,200,150,150,400])
prixVenteCulture=np.array([350,200,150,150,375])
#prixVenteCulture=np.array([350,200,185,150,400])
coutProdCulture=np.array([400,600,400,1200,300])

# Construction de la matrice des IFT
iftMatrix = np.zeros((nbParcelle, nbCulture))
for i in range(nbParcelle):
    for j in range(nbCulture):
        iftMatrix[i][j] = ift[j]*surface[i]/sum(surface)

# print("ift ")
# print(iftMatrix)




# Coefficient pondération IFT
weightIFT = []
for row in iftMatrix:
    for coefficent in row:
        weightIFT.append(coefficent)


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



#Construction matrice Lambda paille
indexCulturePaille=[]
for culture in Vculture:
    if culture=='Blé de force' or culture =='Orge':
        indexCulturePaille.append(Vculture.index(culture))
lambdaPaille=np.zeros((nbCulture,nbCulture))
for index in indexCulturePaille:
    lambdaPaille[index][index]=1


#Construction matrice Lambda ensilage
indexCultureEnsilage=[]
for culture in Vculture:
    if culture=='Maïs':
        indexCultureEnsilage.append(Vculture.index(culture))
lambdaEnsilage=np.zeros((nbCulture,nbCulture))
for index in indexCultureEnsilage:
    lambdaEnsilage[index][index]=1




yearSolutionRepartition,yearSolutionValue,yearIftSolutionValue=[],[],[]
for indexYear in range(numYear):
    print("ANNEE "+str(indexYear))
    solutionRepartition,solutionValue,iftValue=[],[],[]

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

        #Coefficient pondération calcul Marge Brute
        weight =[]
        for row in Mg:
            for element in row:
                weight.append(element)

        #7.Matrice des contraintes

        constMatrix1=np.zeros((nbParcelle,nbParcelle*nbCulture))
        for i in range(nbParcelle):
            for j in range(nbParcelle*nbCulture):
                if nbCulture*i<=j<=nbCulture*(i+1)-1:
                    constMatrix1[i][j]=1

        iftRepartition = np.matmul(cultureRepartition,ift)

        constMatrix2 = np.array(weightPaille)
        constMatrix3 = np.array(weightEnsilage)
        constMatrix = np.vstack((constMatrix1, constMatrix2, constMatrix3,np.array(weightIFT)))



        solutionConstraintList,solutionBoundList=[],[]
        for indexSolution in range(numSolutionYear):


            if indexSolution>=1:

                constMatrix = np.vstack((constMatrix, np.array(solutionConstraintList[indexSolution-1])))


            #
            # print("MATRICE CONTRAINTES")
            # print(constMatrix)
            numvar=nbCulture*nbParcelle
            numConstraints=len(constMatrix)
            # print("NUMCONSTRAINTS")
            # print(numConstraints)

            #8.Matrice des boundaries
            #bound=[1]*(numConstraints-(2+len(solutionBoundList)))
            # bound=[1]*nbParcelle
            # bound.append(numPailleMin)
            # bound.append(numEnsilageMin)
            # bound.append(sum(map(lambda IFTi,Si : IFTi*Si,iftRepartition,surface))/sum(surface)*(1-kIft))
            # if indexSolution>=1:
            #     for indexBound in range(len(solutionBoundList)):
            #         bound.append(solutionBoundList[indexBound][0])
            # # print("bound")
            # # print(bound)
            bound_sup,bound_inf=[],[]
            for indexBound in range(numConstraints):
                if indexBound<=5:
                    bound_sup.append(1)
                    bound_inf.append(1)
                elif indexBound==6:
                    bound_inf.append(numPailleMin)
                    bound_sup.append(100*numPailleMin)
                elif indexBound==7:
                    bound_inf.append(numEnsilageMin)
                    bound_sup.append(100*numEnsilageMin)
                else:
                    bound_sup.append(sum(map(lambda IFTi,Si : IFTi*Si,iftRepartition,surface))/sum(surface)*(1-kIft))
                    bound_inf.append(0)
                    if indexSolution>=1:
                        for indexSolBound in range(len(solutionBoundList)):
                            bound_sup.append(solutionBoundList[indexSolBound][0])
                            bound_inf.append(0)
                    # print("bound")
                    # print(bound_sup)
                    # print(bound_inf)

            #OPTIMISATION

            # Create the mip solver with the CBC backend.
            solver = pywraplp.Solver('simple_mip_program',pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)
            infinity = solver.infinity()
            x = {}
            for j in range(numvar):
                x[j] = solver.IntVar(0, infinity, 'x[%i]' % j)
                # print('Number of variables =', solver.NumVariables())

            for i in range(numConstraints):
                # if i not in (6,7):
                #     constraint = solver.RowConstraint(bound_inf[i], bound_sup[i], '')
                # else :
                #     constraint = solver.RowConstraint(bound_inf[i], bound_sup[i], '')
                constraint = solver.RowConstraint(bound_inf[i], bound_sup[i], '')



                for j in range(numvar):
                    constraint.SetCoefficient(x[j], (constMatrix[i][j]))
            #print('Number of constraints =', solver.NumConstraints())


            objective = solver.Objective()
            for j in range(numvar):
                objective.SetCoefficient(x[j], weight[j])
            objective.SetMaximization()


            status = solver.Solve()
            solution=[]
            if status == pywraplp.Solver.OPTIMAL:
                #print('Objective value =', solver.Objective().Value())
                for j in range(numvar):
                    #print(x[j].name(), ' = ', x[j].solution_value())
                    solution.append(x[j].solution_value())


                # print('Problem solved in %f milliseconds' % solver.wall_time())
                # print("SOLUTION N° "+str(indexSolution)+" ANNEE "+str(indexYear))
                # print("REPARTITION")

                repartition=np.vstack((np.array_split(solution,nbParcelle)))

                solutionRepartition.append(repartition)
                # print(repartition)
                # print("SOLUTION")
                marge_brute_optimale=solver.Objective().Value()
                solutionValue.append(marge_brute_optimale)
                iftValue.append(sum(np.matmul(repartition,ift)*surface)/sum(surface))
                # print(solver.Objective().Value())
                # print('IFT')
                # print(iftValue)
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


            else:
                # print('The problem does not have an optimal solution.')
                solutionConstraint, solutionBound = [], []
                solution=[0]*nbCulture*nbParcelle

                repartition=np.zeros((nbParcelle,nbCulture))
                solutionRepartition.append(repartition)
                solutionValue.append(0)
                iftValue.append(0)
                for element in solution:
                    solutionConstraint.append(0)
                solutionBound.append(0)
                solutionConstraintList.append(solutionConstraint)
                solutionBoundList.append(solutionBound)

    initRepartition=solutionRepartition
    yearSolutionRepartition.append(solutionRepartition)
    yearSolutionValue.append(solutionValue)
    yearIftSolutionValue.append(iftValue)

#print(yearSolutionRepartition)

#Création de la matrice des résultats
listMatrix,colMatrix,iftTable=[],[],[]

for indexYear in range(numYear):
    LambdaLocal=np.zeros((numSolutionYear**(indexYear+1),numSolutionYear**numYear))
    for i in range((numSolutionYear)**(indexYear+1)):
        for j in range(numSolutionYear**numYear):
            if i*(numSolutionYear)**(numYear-(indexYear+1))<=j<=(i+1)*numSolutionYear**(numYear-(indexYear+1))-1:
                LambdaLocal[i][j]=1

    listMatrix.append(LambdaLocal)
    colMatrix.append(np.matmul(yearSolutionValue[indexYear],listMatrix[indexYear]))
    iftTable.append(np.matmul(yearIftSolutionValue[indexYear],listMatrix[indexYear]))

matrixResult=np.transpose(colMatrix)
matrixIFT=np.transpose(iftTable)
columnLabel=[]
dfResult=pd.DataFrame(matrixResult)
dfIFT=pd.DataFrame(matrixIFT)
dfResult['mean'] = dfResult.mean(axis=1)
dfIFT['mean'] = dfIFT.mean(axis=1)

print(tabulate(dfResult,headers='keys',tablefmt='psql'))
print(tabulate(dfIFT,headers='keys',tablefmt='psql'))
dfMCDA=pd.DataFrame()
dfMCDA['MB']=dfResult['mean']
dfMCDA['IFT']=dfIFT['mean']



dfMCDA['MB2']=dfMCDA.apply(lambda row :row.MB**2,axis=1)
dfMCDA['IFT2']=dfMCDA.apply(lambda row:row.IFT**2,axis=1)

dfMCDA['MB2Sum']=dfMCDA.apply(lambda row : dfMCDA['MB2'].sum(),axis=1)
dfMCDA['IFT2Sum']=dfMCDA.apply(lambda row : dfMCDA['IFT2'].sum(),axis=1)

dfMCDA['MB_Norm']=dfMCDA.apply(lambda row :row.MB2/row.MB2Sum,axis=1)
dfMCDA['IFT_Norm']=dfMCDA.apply(lambda row :row.IFT2/row.IFT2Sum,axis=1)

dfMCDA['MBNormWeighted']=dfMCDA.apply(lambda row :row.MB_Norm*MCDAweight[0],axis=1)
dfMCDA['IFTNormWeighted']=dfMCDA.apply(lambda row:row.IFT_Norm*MCDAweight[1],axis=1)

dfMCDA['MB_ideal'] = dfMCDA.apply(lambda row: dfMCDA['MBNormWeighted'].max(), axis=1)
dfMCDA['MB_anti_ideal'] = dfMCDA.apply(lambda row: dfMCDA['MBNormWeighted'].min(), axis=1)

dfMCDA['IFT_ideal'] = dfMCDA.apply(lambda row: dfMCDA['IFTNormWeighted'].min(), axis=1)
dfMCDA['IFT_anti_ideal'] = dfMCDA.apply(lambda row: dfMCDA['IFTNormWeighted'].max(), axis=1)

dfMCDA['IFT_ideal'] = dfMCDA.apply(lambda row: dfMCDA['IFTNormWeighted'].min(), axis=1)
dfMCDA['IFT_anti_ideal'] = dfMCDA.apply(lambda row: dfMCDA['IFTNormWeighted'].max(), axis=1)

dfMCDA['ideal_dist']=dfMCDA.apply(lambda row:((row.MBNormWeighted-row.MB_ideal)**2+(row.IFTNormWeighted-row.IFT_ideal)**2)**0.5,axis=1)

dfMCDA['anti_ideal_dist']=dfMCDA.apply(lambda row:((row.MBNormWeighted-row.MB_anti_ideal)**2+(row.IFTNormWeighted-row.IFT_anti_ideal)**2)**0.5,axis=1)

dfMCDA['ranking'] = dfMCDA.apply(lambda row: row.anti_ideal_dist/(row.anti_ideal_dist+row.ideal_dist), axis=1)

dfMCDA['index_col'] = dfMCDA.index
dfMCDA=dfMCDA.sort_values(['ranking'], ascending=[False])
dfMCDA=dfMCDA.head(5)

print(dfMCDA)
print(time.clock()-start_time_2 )


# maxMean=dfResult[dfResult['mean']==dfResult['mean'].max()]
# resultList=maxMean.values.tolist()[0]
#
# # print("RESULT")
# # print(resultList)
# print("row index")
# print(dfResult.index.get_loc(maxMean.iloc[0].name))
# IFTresultList=dfIFT.iloc[[dfResult.index.get_loc(maxMean.iloc[0].name)]]
#
# rowSolutionIndex=dfResult.index.get_loc(maxMean.iloc[0].name)
# configResultList,qtePaille,qteEnsillage=[],[],[]
#
# for indexYear in range(numYear):
#     configResultList.append(yearSolutionRepartition[indexYear][(rowSolutionIndex//(numSolutionYear**(numYear-(indexYear+1))))])
#
#     if indexYear>0:
#         MPCn1=configResultList[indexYear-1]
#
#     eta1 = np.matmul(configResultList[indexYear], eta)
#
#     v = np.zeros(6)
#
#     for i in range(len(configResultList[indexYear])):
#         v = v + np.matmul(np.matmul(configResultList[indexYear][i], R1), np.transpose(MPTS[i])) * np.identity(6)[i]
#
#     eta2 = (np.ones(6) - v / 100)
#
#     u = np.zeros(6)
#     for i in range(6):
#         u = u + np.matmul(np.matmul(R2, configResultList[indexYear][i]), MPCn1[i]) * np.identity(6)[i]
#
#     eta3 = (u / 100)
#     etaPaille = np.matmul(np.matmul(configResultList[indexYear], lambdaPaille), eta)
#     etaEnsillage = np.matmul(np.matmul(configResultList[indexYear], lambdaEnsilage), eta)
#     qtePaille.append(sum(0.8 * surface * etaPaille * eta2 * eta3))
#     qteEnsillage.append(sum(1.5 * surface * etaEnsillage * eta2 * eta3))
#
#
# culture,cultureConfig=[],[]
# dfConfig=pd.DataFrame()
# dfPaille=pd.DataFrame()
# dfEnsilage=pd.DataFrame()
# dfMb=pd.DataFrame()
# dfIFTresult=pd.DataFrame()
# dfConfig["Parcelle"]=Vparcelle
# dfPaille["-"]=['Qte paille']
# dfEnsilage["-"]=["Qte Ensilage"]
# dfMb["-"]=["Marge Brute"]
# dfIFTresult["-"]=["IFT"]
#
# year=0
# for config in configResultList:
#     culture=[]
#
#     for row in config:
#         try:
#             culture.append(Vculture[list(row).index(1)])
#         except:
#             culture.append('-')
#
#     dfConfig["Culture Année "+str(year)]=culture
#     dfPaille["Année "+str(year)]=qtePaille[year]
#     dfEnsilage["Année " + str(year)] = qteEnsillage[year]
#     dfMb["Année " + str(year)]=resultList[year]
#     dfIFTresult["Année "+str(year)]=IFTresultList.values.tolist()[0][year]
#     cultureConfig.append(culture)
#     year=year+1
#
#
# print(tabulate(dfMb,headers='keys',tablefmt='psql'))
# print('######')
# print(tabulate(dfIFTresult,headers='keys',tablefmt='psql'))
# print("######")
# print(tabulate(dfConfig,headers='keys',tablefmt='psql'))
# print("######")
# print(tabulate(dfPaille,headers='keys',tablefmt='psql'))
# print("######")
# print(tabulate(dfEnsilage,headers='keys',tablefmt='psql'))



