import numpy as np
import pandas as pd
pd.set_option('max_columns', 800)
from ortools.linear_solver import pywraplp
from tabulate import tabulate
import time
from skcriteria import Data, MIN, MAX
from skcriteria.madm import closeness, simple
from scipy.spatial.distance import euclidean as dist_euclid

class Solver:
    def __init__(self):
        self.solverMode='unconstrained IFT'
        self.selectionMode='Max MB'
        self.kIFT = 0
        self.cultureList=[]
        self.parcelleList=[]
        self.nbParcelle = 0
        self.NbCulture = 0
        self.constraintPaille=0
        self.constraintEnsilage=0
        self.numSolutionYear = 5
        self.numYear = 6
        self.MCDAweight = [1, 1]
        self.eta = np.array([])
        self.ift = np.array([])
        self.surface = np.array([])
        self.prixVenteCulture = np.array([])
        self.coutProdCulture = np.array([])
        self.MPTS = np.array([])
        self.R1 = np.array([])
        self.R2 = np.array([])

    def IFTmatrix(self,nbParcelle,nbCulture,surface,ift):
        iftMatrix = np.zeros((nbParcelle, nbCulture))
        for i in range(nbParcelle):
            for j in range(nbCulture):
                iftMatrix[i][j] = ift[j] * surface[i] / sum(surface)

        return iftMatrix

    # Coefficient pondération IFT
    def weightIFT(self,iftMatrix):
        weightIFT = []
        for row in iftMatrix:
            for coefficent in row:
                weightIFT.append(coefficent)
        return weightIFT


    def lambdaPaille(self,Vculture,nbCulture):
        # Construction matrice Lambda paille
        indexCulturePaille = []
        for culture in Vculture:
            if culture == 'Blé de force' or culture == 'Orge':
                indexCulturePaille.append(Vculture.index(culture))
        lambdaPaille = np.zeros((nbCulture, nbCulture))
        for index in indexCulturePaille:
            lambdaPaille[index][index] = 1

        return lambdaPaille

    # Construction matrice Lambda ensilage
    def lambdaEnsilage(self,Vculture,nbCulture):
        indexCultureEnsilage = []
        for culture in Vculture:
            if culture == 'Maïs':
                indexCultureEnsilage.append(Vculture.index(culture))
        lambdaEnsilage = np.zeros((nbCulture, nbCulture))
        for index in indexCultureEnsilage:
            lambdaEnsilage[index][index] = 1


    def optimization(self,numYear,MPCn1,nbParcelle,nbCulture,eta,R1,R2,MPTS,surface,prixVenteCulture,coutProdCulture,ift,numSolutionYear,weightIFT,numPailleMin,numEnsilageMin,kIft):
        yearSolutionRepartition, yearSolutionValue, yearIftSolutionValue = [], [], []
        for indexYear in range(numYear):
            print("ANNEE " + str(indexYear))
            solutionRepartition, solutionValue, iftValue = [], [], []

            if indexYear == 0:
                initRepartition = [MPCn1]

            for cultureRepartition in initRepartition:

                # 1.Contruction matrice etap
                etap = np.zeros((nbParcelle, nbCulture))
                for i in range(nbCulture):
                    for j in range(nbParcelle):
                        etap[j][i] = eta[i]
                # print(etap)

                # 2.Construction de la matrice eta_ts

                eta_ts = np.ones((nbParcelle, nbCulture)) - 1 / 100 * (np.transpose(np.matmul(R1, np.transpose(MPTS))))
                # print(eta_ts)

                # 3.Construction de la matrice eta_n1
                eta_n1 = 1 / 100 * np.matmul(cultureRepartition, R2)
                # print("n1")
                # print(eta_n1)

                # 4.Construction de la matrice etaG
                etaG = np.zeros((nbParcelle, nbCulture))
                Marge = np.zeros((nbParcelle, nbCulture))
                for i in range(nbCulture):
                    for j in range(nbParcelle):
                        etaG[j][i] = etap[j][i] * eta_ts[j][i] * eta_n1[j][i]

                # Construction de la matrice/liste des eta Paille
                etaPaille, etaEnsilage = np.zeros((nbParcelle, nbCulture)), np.zeros((nbParcelle, nbCulture))
                weightPaille, weightEnsilage = [], []
                for i in range(nbParcelle):
                    for j in range(nbCulture):
                        if j in (1, 2):
                            etaPaille[i][j] = 0.8 * etaG[i][j] * surface[i]
                        elif j == 3:
                            etaEnsilage[i][j] = 1.5 * etaG[i][j] * surface[i]

                for row in etaPaille:
                    for element in row:
                        weightPaille.append(element)

                for row in etaEnsilage:
                    for element in row:
                        weightEnsilage.append(element)

                # print(weightEnsilage)
                # print(weightPaille)


                # 5.Matrice Prix culture/parcelle
                Pv = np.zeros((nbParcelle, nbCulture))
                Ct = np.zeros((nbParcelle, nbCulture))
                for i in range(nbCulture):
                    for j in range(nbParcelle):
                        Pv[j][i] = prixVenteCulture[i]
                        Ct[j][i] = coutProdCulture[i]
                # print(Pv)
                # print(Ct)

                # 6.Matrice de marge
                Mg = np.zeros((nbParcelle, nbCulture))
                for i in range(nbCulture):
                    for j in range(nbParcelle):
                        # Mg[j][i]=surface[j]*(etaG[j][i]*Pv[j][i]-Ct[j][i])
                        Mg[j][i] = surface[j] * eta_n1[j][i] * (etap[j][i] * eta_ts[j][i] * Pv[j][i] - Ct[j][i])
                # print(Mg)

                # Coefficient pondération calcul Marge Brute
                weight = []
                for row in Mg:
                    for element in row:
                        weight.append(element)

                # 7.Matrice des contraintes

                constMatrix1 = np.zeros((nbParcelle, nbParcelle * nbCulture))
                for i in range(nbParcelle):
                    for j in range(nbParcelle * nbCulture):
                        if nbCulture * i <= j <= nbCulture * (i + 1) - 1:
                            constMatrix1[i][j] = 1

                iftRepartition = np.matmul(cultureRepartition, ift)

                constMatrix2 = np.array(weightPaille)
                constMatrix3 = np.array(weightEnsilage)
                constMatrix = np.vstack((constMatrix1, constMatrix2, constMatrix3, np.array(weightIFT)))

                solutionConstraintList, solutionBoundList = [], []
                for indexSolution in range(numSolutionYear):

                    if indexSolution >= 1:
                        constMatrix = np.vstack((constMatrix, np.array(solutionConstraintList[indexSolution - 1])))

                    #
                    # print("MATRICE CONTRAINTES")
                    # print(constMatrix)
                    numvar = nbCulture * nbParcelle
                    numConstraints = len(constMatrix)
                    # print("NUMCONSTRAINTS")
                    # print(numConstraints)

                    # 8.Matrice des boundaries
                    # bound=[1]*(numConstraints-(2+len(solutionBoundList)))
                    # bound=[1]*nbParcelle
                    # bound.append(numPailleMin)
                    # bound.append(numEnsilageMin)
                    # bound.append(sum(map(lambda IFTi,Si : IFTi*Si,iftRepartition,surface))/sum(surface)*(1-kIft))
                    # if indexSolution>=1:
                    #     for indexBound in range(len(solutionBoundList)):
                    #         bound.append(solutionBoundList[indexBound][0])
                    # # print("bound")
                    # # print(bound)
                    bound_sup, bound_inf = [], []
                    for indexBound in range(numConstraints):
                        if indexBound <= 5:
                            bound_sup.append(1)
                            bound_inf.append(1)
                        elif indexBound == 6:
                            bound_inf.append(numPailleMin)
                            bound_sup.append(100 * numPailleMin)
                        elif indexBound == 7:
                            bound_inf.append(numEnsilageMin)
                            bound_sup.append(100 * numEnsilageMin)
                        else:
                            bound_sup.append(
                                sum(map(lambda IFTi, Si: IFTi * Si, iftRepartition, surface)) / sum(surface) * (
                                1 - kIft))
                            bound_inf.append(0)
                            if indexSolution >= 1:
                                for indexSolBound in range(len(solutionBoundList)):
                                    bound_sup.append(solutionBoundList[indexSolBound][0])
                                    bound_inf.append(0)
                                    # print("bound")
                                    # print(bound_sup)
                                    # print(bound_inf)

                    # OPTIMISATION

                    # Create the mip solver with the CBC backend.
                    solver = pywraplp.Solver('simple_mip_program', pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)
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
                    # print('Number of constraints =', solver.NumConstraints())


                    objective = solver.Objective()
                    for j in range(numvar):
                        objective.SetCoefficient(x[j], weight[j])
                    objective.SetMaximization()

                    status = solver.Solve()
                    solution = []
                    if status == pywraplp.Solver.OPTIMAL:
                        # print('Objective value =', solver.Objective().Value())
                        for j in range(numvar):
                            # print(x[j].name(), ' = ', x[j].solution_value())
                            solution.append(x[j].solution_value())

                        # print('Problem solved in %f milliseconds' % solver.wall_time())
                        # print("SOLUTION N° "+str(indexSolution)+" ANNEE "+str(indexYear))
                        # print("REPARTITION")

                        repartition = np.vstack((np.array_split(solution, nbParcelle)))

                        solutionRepartition.append(repartition)
                        # print(repartition)
                        # print("SOLUTION")
                        marge_brute_optimale = solver.Objective().Value()
                        solutionValue.append(marge_brute_optimale)
                        iftValue.append(sum(np.matmul(repartition, ift) * surface) / sum(surface))
                        # print(solver.Objective().Value())
                        # print('IFT')
                        # print(iftValue)
                        # print("QTE PAILLE")
                        # print(etaPaille)
                        # print(np.matmul(np.transpose(repartition[:,1]),etaPaille))
                        # Préparation de la contrainte issue de la solution
                        solutionConstraint, solutionBound = [], []
                        for element in solution:
                            if element == 0:
                                solutionConstraint.append(-1)
                            elif element == 1:
                                solutionConstraint.append(1)

                        solutionBound.append(-(1 - solution.count(1)))
                        solutionConstraintList.append(solutionConstraint)

                        solutionBoundList.append(solutionBound)


                    else:
                        # print('The problem does not have an optimal solution.')
                        solutionConstraint, solutionBound = [], []
                        solution = [0] * nbCulture * nbParcelle

                        repartition = np.zeros((nbParcelle, nbCulture))
                        solutionRepartition.append(repartition)
                        solutionValue.append(0)
                        iftValue.append(0)
                        for element in solution:
                            solutionConstraint.append(0)
                        solutionBound.append(0)
                        solutionConstraintList.append(solutionConstraint)
                        solutionBoundList.append(solutionBound)

            initRepartition = solutionRepartition
            yearSolutionRepartition.append(solutionRepartition)
            yearSolutionValue.append(solutionValue)
            yearIftSolutionValue.append(iftValue)

        # print(yearSolutionRepartition)

        # Création de la matrice des résultats
        listMatrix, colMatrix, iftTable = [], [], []

        for indexYear in range(numYear):
            LambdaLocal = np.zeros((numSolutionYear ** (indexYear + 1), numSolutionYear ** numYear))
            for i in range((numSolutionYear) ** (indexYear + 1)):
                for j in range(numSolutionYear ** numYear):
                    if i * (numSolutionYear) ** (numYear - (indexYear + 1)) <= j <= (i + 1) * numSolutionYear ** (
                        numYear - (indexYear + 1)) - 1:
                        LambdaLocal[i][j] = 1

            listMatrix.append(LambdaLocal)
            colMatrix.append(np.matmul(yearSolutionValue[indexYear], listMatrix[indexYear]))
            iftTable.append(np.matmul(yearIftSolutionValue[indexYear], listMatrix[indexYear]))

        matrixResult = np.transpose(colMatrix)
        matrixIFT = np.transpose(iftTable)

        dfResult = pd.DataFrame(matrixResult)
        dfIFT = pd.DataFrame(matrixIFT)
        dfResult['mean'] = dfResult.mean(axis=1)
        dfIFT['mean'] = dfIFT.mean(axis=1)

        print(tabulate(dfResult, headers='keys', tablefmt='psql'))
        print(tabulate(dfIFT, headers='keys', tablefmt='psql'))
        dfMCDA = pd.DataFrame()
        dfMCDA['MB'] = dfResult['mean']
        dfMCDA['IFT'] = dfIFT['mean']

        dfMCDA['MB2'] = dfMCDA.apply(lambda row: row.MB ** 2, axis=1)
        dfMCDA['IFT2'] = dfMCDA.apply(lambda row: row.IFT ** 2, axis=1)

        dfMCDA['MB2Sum'] = dfMCDA.apply(lambda row: dfMCDA['MB2'].sum(), axis=1)
        dfMCDA['IFT2Sum'] = dfMCDA.apply(lambda row: dfMCDA['IFT2'].sum(), axis=1)

        dfMCDA['MB_Norm'] = dfMCDA.apply(lambda row: row.MB2 / row.MB2Sum, axis=1)
        dfMCDA['IFT_Norm'] = dfMCDA.apply(lambda row: row.IFT2 / row.IFT2Sum, axis=1)

        dfMCDA['MBNormWeighted'] = dfMCDA.apply(lambda row: row.MB_Norm * MCDAweight[0], axis=1)
        dfMCDA['IFTNormWeighted'] = dfMCDA.apply(lambda row: row.IFT_Norm * MCDAweight[1], axis=1)

        dfMCDA['MB_ideal'] = dfMCDA.apply(lambda row: dfMCDA['MBNormWeighted'].max(), axis=1)
        dfMCDA['MB_anti_ideal'] = dfMCDA.apply(lambda row: dfMCDA['MBNormWeighted'].min(), axis=1)

        dfMCDA['IFT_ideal'] = dfMCDA.apply(lambda row: dfMCDA['IFTNormWeighted'].min(), axis=1)
        dfMCDA['IFT_anti_ideal'] = dfMCDA.apply(lambda row: dfMCDA['IFTNormWeighted'].max(), axis=1)

        dfMCDA['IFT_ideal'] = dfMCDA.apply(lambda row: dfMCDA['IFTNormWeighted'].min(), axis=1)
        dfMCDA['IFT_anti_ideal'] = dfMCDA.apply(lambda row: dfMCDA['IFTNormWeighted'].max(), axis=1)

        dfMCDA['ideal_dist'] = dfMCDA.apply(
            lambda row: ((row.MBNormWeighted - row.MB_ideal) ** 2 + (row.IFTNormWeighted - row.IFT_ideal) ** 2) ** 0.5,
            axis=1)

        dfMCDA['anti_ideal_dist'] = dfMCDA.apply(lambda row: ((row.MBNormWeighted - row.MB_anti_ideal) ** 2 + (
        row.IFTNormWeighted - row.IFT_anti_ideal) ** 2) ** 0.5, axis=1)

        dfMCDA['ranking'] = dfMCDA.apply(lambda row: row.anti_ideal_dist / (row.anti_ideal_dist + row.ideal_dist),
                                         axis=1)

        dfMCDA['index_col'] = dfMCDA.index
        dfMCDA = dfMCDA.sort_values(['ranking'], ascending=[False])
        dfMCDA = dfMCDA.head(5)

        print(dfMCDA)
        return dfMCDA

