import numpy as np
import pandas as pd
from ortools.linear_solver import pywraplp


class objectSolver:
    def __init__(self,solverMode='unconstrained IFT',kIFT=0.0,cultureList=[],parcelleList=[],constraintPaille=0,constraintEnsilage=0,numSolutionYear=0,numYear=0,eta=np.array([]),ift=np.array([]),surface=[],prixVenteCulture=[],coutProdCulture=[],MPTS=np.array([]),MPCn1 = np.array([]),R1=np.array([]),R2=np.array([])):

        self.solverMode=solverMode
        self.kIft = kIFT
        self.cultureList=cultureList
        self.parcelleList=parcelleList
        self.nbParcelle = len(parcelleList)
        self.nbCulture = len(cultureList)
        self.constraintPaille=constraintPaille
        self.constraintEnsilage=constraintEnsilage
        self.numSolutionYear = numSolutionYear
        self.numYear = numYear
        self.eta = eta
        self.ift = ift
        self.surface = surface
        self.prixVenteCulture = prixVenteCulture
        self.coutProdCulture = coutProdCulture
        self.MPTS = MPTS
        self.R1 = R1
        self.R2 = R2,
        self.MPCn1=MPCn1
        self.iftMatrix=self.functionIFTmatrix(nbParcelle=self.nbParcelle,nbCulture=self.nbCulture,surface=self.surface,ift=self.ift)
        self.weightIFT=self.functionWeightIFT(iftMatrix=self.iftMatrix)
        self.lambdaPaille = self.functionLambdaPaille(Vculture=cultureList,nbCulture=self.nbCulture)
        self.lambdaEnsilage = self.functionLambdaEnsilage(Vculture=self.cultureList,nbCulture=self.nbCulture)
        self.dfMBSolution=pd.DataFrame()
        self.dfIFTSolution=pd.DataFrame()
        self.dfMCDA=pd.DataFrame()
        self.yearSolutionRepartition=[]
        self.yearSolutionValue=[]
        self.yearIftSolutionValue=[]
        self.yearAssolementConfig=[]
        self.yearQtePaille=[]
        self.yearQteEnsilage = []
        self.yearMB = []
        self.yearIFT = []

    def functionIFTmatrix(self,nbParcelle,nbCulture,surface,ift):
        iftMatrix = np.zeros((nbParcelle, nbCulture))
        for i in range(nbParcelle):
            for j in range(nbCulture):
                iftMatrix[i][j] = ift[j] * surface[i] / sum(surface)
        return iftMatrix

    # Coefficient pondération IFT
    def functionWeightIFT(self,iftMatrix):
        weightIFT = []
        for row in iftMatrix:
            for coefficent in row:
                weightIFT.append(coefficent)
        return weightIFT

    def functionLambdaPaille(self,Vculture,nbCulture):
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
    def functionLambdaEnsilage(self,Vculture,nbCulture):
        indexCultureEnsilage = []
        for culture in Vculture:
            if culture == 'Maïs':
                indexCultureEnsilage.append(Vculture.index(culture))
        lambdaEnsilage = np.zeros((nbCulture, nbCulture))
        for index in indexCultureEnsilage:
            lambdaEnsilage[index][index] = 1
        return lambdaEnsilage

    def solve(self):
        try:

            yearSolutionRepartition, yearSolutionValue, yearIftSolutionValue = [], [], []
            for indexYear in range(self.numYear):
                print("ANNEE " + str(indexYear))
                solutionRepartition, solutionValue, iftValue = [], [], []

                if indexYear == 0:
                    initRepartition = [self.MPCn1]

                for cultureRepartition in initRepartition:

                    # 1.Contruction matrice etap
                    etap = np.zeros((self.nbParcelle, self.nbCulture))
                    for i in range(self.nbCulture):
                        for j in range(self.nbParcelle):
                            etap[j][i] = self.eta[i]
                    # print(etap)

                    # 2.Construction de la matrice eta_ts

                    eta_ts = np.ones((self.nbParcelle, self.nbCulture)) - 1 / 100 * (np.transpose(np.matmul(self.R1, np.transpose(self.MPTS))))
                    # print(eta_ts)

                    # 3.Construction de la matrice eta_n1

                    eta_n1 = 1 / 100 * np.matmul(cultureRepartition, self.R2)[0]
                    # print("n1")
                    # print(eta_n1)

                    # 4.Construction de la matrice etaG
                    etaG = np.zeros((self.nbParcelle, self.nbCulture))
                    Marge = np.zeros((self.nbParcelle, self.nbCulture))

                    for i in range(self.nbCulture):
                        for j in range(self.nbParcelle):
                            etaG[j][i] = etap[j][i] * eta_ts[j][i] * eta_n1[j][i]

                    # Construction de la matrice/liste des eta Paille
                    etaPaille, etaEnsilage = np.zeros((self.nbParcelle, self.nbCulture)), np.zeros((self.nbParcelle, self.nbCulture))
                    weightPaille, weightEnsilage = [], []
                    for i in range(self.nbParcelle):
                        for j in range(self.nbCulture):
                            if j in (1, 2):
                                etaPaille[i][j] = 0.8 * etaG[i][j] * self.surface[i]
                            elif j == 3:
                                etaEnsilage[i][j] = 1.5 * etaG[i][j] * self.surface[i]

                    for row in etaPaille:
                        for element in row:
                            weightPaille.append(element)

                    for row in etaEnsilage:
                        for element in row:
                            weightEnsilage.append(element)

                    # print(weightEnsilage)
                    # print(weightPaille)


                    # 5.Matrice Prix culture/parcelle
                    Pv = np.zeros((self.nbParcelle, self.nbCulture))
                    Ct = np.zeros((self.nbParcelle, self.nbCulture))
                    for i in range(self.nbCulture):
                        for j in range(self.nbParcelle):
                            Pv[j][i] = self.prixVenteCulture[i]
                            Ct[j][i] = self.coutProdCulture[i]
                    # print(Pv)
                    # print(Ct)

                    # 6.Matrice de marge
                    Mg = np.zeros((self.nbParcelle, self.nbCulture))
                    for i in range(self.nbCulture):
                        for j in range(self.nbParcelle):
                            # Mg[j][i]=surface[j]*(etaG[j][i]*Pv[j][i]-Ct[j][i])
                            Mg[j][i] = self.surface[j] * eta_n1[j][i] * (etap[j][i] * eta_ts[j][i] * Pv[j][i] - Ct[j][i])
                    # print(Mg)

                    # Coefficient pondération calcul Marge Brute
                    weight = []
                    for row in Mg:
                        for element in row:
                            weight.append(element)

                    # 7.Matrice des contraintes

                    constMatrix1 = np.zeros((self.nbParcelle, self.nbParcelle * self.nbCulture))
                    for i in range(self.nbParcelle):
                        for j in range(self.nbParcelle * self.nbCulture):
                            if self.nbCulture * i <= j <= self.nbCulture * (i + 1) - 1:
                                constMatrix1[i][j] = 1

                    iftRepartition = np.matmul(cultureRepartition, self.ift)

                    constMatrix2 = np.array(weightPaille)
                    constMatrix3 = np.array(weightEnsilage)

                    #'unconstrained IFT', 'constrained IFT', 'constrained decreasing IFT'
                    if self.solverMode in ('constrained IFT','constrained decreasing IFT'):
                        constMatrix = np.vstack((constMatrix1, constMatrix2, constMatrix3, np.array(self.weightIFT)))
                    else:
                        constMatrix = np.vstack((constMatrix1, constMatrix2, constMatrix3))

                    solutionConstraintList, solutionBoundList = [], []
                    for indexSolution in range(self.numSolutionYear):

                        if indexSolution >= 1:
                            constMatrix = np.vstack((constMatrix, np.array(solutionConstraintList[indexSolution - 1])))


                        numvar = self.nbCulture * self.nbParcelle
                        numConstraints = len(constMatrix)


                        bound_sup, bound_inf = [], []
                        for indexBound in range(numConstraints):
                            if indexBound <= 5:
                                bound_sup.append(1)
                                bound_inf.append(1)
                            elif indexBound == 6:
                                bound_inf.append(self.constraintPaille)
                                bound_sup.append(100 * self.constraintPaille)
                            elif indexBound == 7:
                                bound_inf.append(self.constraintEnsilage)
                                bound_sup.append(100 * self.constraintEnsilage)
                            else:
                                if self.solverMode in ('constrained IFT', 'constrained decreasing IFT'):
                                    bound_sup.append(sum(map(lambda IFTi, Si: IFTi * Si, iftRepartition, self.surface)) / sum(self.surface) * (1 - self.kIft))
                                    bound_inf.append(0)
                                if indexSolution >= 1:
                                    for indexSolBound in range(len(solutionBoundList)):
                                        bound_sup.append(solutionBoundList[indexSolBound][0])
                                        bound_inf.append(0)


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

                            repartition = np.vstack((np.array_split(solution, self.nbParcelle)))

                            solutionRepartition.append(repartition)
                            # print(repartition)
                            # print("SOLUTION")
                            marge_brute_optimale = solver.Objective().Value()
                            solutionValue.append(marge_brute_optimale)
                            iftValue.append(sum(np.matmul(repartition, self.ift) * self.surface) / sum(self.surface))
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
                            solution = [0] * self.nbCulture * self.nbParcelle

                            repartition = np.zeros((self.nbParcelle, self.nbCulture))
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



            self.yearSolutionRepartition=yearSolutionRepartition
            self.yearSolutionValue=yearSolutionValue
            self.yearIftSolutionValue=yearIftSolutionValue

            # print(yearSolutionRepartition)

            # Création de la matrice des résultats
            listMatrix, colMatrix, iftTable = [], [], []

            for indexYear in range(self.numYear):
                LambdaLocal = np.zeros((self.numSolutionYear ** (indexYear + 1), self.numSolutionYear ** self.numYear))
                for i in range((self.numSolutionYear) ** (indexYear + 1)):
                    for j in range(self.numSolutionYear ** self.numYear):
                        if i * (self.numSolutionYear) ** (self.numYear - (indexYear + 1)) <= j <= (i + 1) * self.numSolutionYear ** (
                            self.numYear - (indexYear + 1)) - 1:
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


            self.dfMBSolution=dfResult.copy(deep=True)
            self.dfIFTSolution=dfIFT.copy(deep=True)
            return True

        except:
            return False

    def resultSelection(self,selectionMode='MB',weightMB=0.5,weightIFT=0.5):

        try:
            dfMCDA = pd.DataFrame()
            dfMCDA['MB'] = self.dfMBSolution['mean']
            dfMCDA['IFT'] = self.dfIFTSolution['mean']

            dfMCDA['MB2'] = dfMCDA.apply(lambda row: row.MB ** 2, axis=1)
            dfMCDA['IFT2'] = dfMCDA.apply(lambda row: row.IFT ** 2, axis=1)

            dfMCDA['MB2Sum'] = dfMCDA.apply(lambda row: dfMCDA['MB2'].sum(), axis=1)
            dfMCDA['IFT2Sum'] = dfMCDA.apply(lambda row: dfMCDA['IFT2'].sum(), axis=1)

            dfMCDA['MB_Norm'] = dfMCDA.apply(lambda row: row.MB2 / row.MB2Sum, axis=1)
            dfMCDA['IFT_Norm'] = dfMCDA.apply(lambda row: row.IFT2 / row.IFT2Sum, axis=1)

            if selectionMode=='MB':
                dfMCDA['MBNormWeighted'] = dfMCDA.apply(lambda row: row.MB_Norm * 1, axis=1)
                dfMCDA['IFTNormWeighted'] = dfMCDA.apply(lambda row: row.IFT_Norm * 0, axis=1)
            elif selectionMode=='MCDA':
                dfMCDA['MBNormWeighted'] = dfMCDA.apply(lambda row: row.MB_Norm * weightMB, axis=1)
                dfMCDA['IFTNormWeighted'] = dfMCDA.apply(lambda row: row.IFT_Norm *weightIFT, axis=1)

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
            dfMCDA = dfMCDA.head(1)
            self.dfMCDA=dfMCDA.copy(deep=True)
            self.indexRowResult=self.dfMCDA['index_col'].tolist()[0]

            return dfMCDA
        except:
            return False

    def assolement(self):
        try:
            resultList=self.dfMBSolution[self.dfMBSolution.index==self.indexRowResult].values.tolist()[0]
            IFTresultList=self.dfIFTSolution[self.dfIFTSolution.index==self.indexRowResult].values.tolist()[0]
            configResultList,qtePaille,qteEnsillage=[],[],[]
            for indexYear in range(self.numYear):
                configResultList.append(self.yearSolutionRepartition[indexYear][(self.indexRowResult//(self.numSolutionYear**(self.numYear-(indexYear+1))))])
                if indexYear<1:
                    MPCn1 = self.MPCn1
                else:
                    MPCn1=configResultList[indexYear-1]
                #eta1 = np.matmul(configResultList[indexYear], self.eta)
                v = np.zeros(6)
                for i in range(len(configResultList[indexYear])):
                    v = v + np.matmul(np.matmul(configResultList[indexYear][i], self.R1), np.transpose(self.MPTS[i])) * np.identity(6)[i]
                eta2 = (np.ones(6) - v / 100)
                u = np.zeros(6)
                for i in range(6):
                    u = u + np.matmul(np.matmul(self.R2, configResultList[indexYear][i]), MPCn1[i]) * np.identity(6)[i]
                eta3 = (u / 100)
                etaPaille = np.matmul(np.matmul(configResultList[indexYear], self.lambdaPaille), self.eta)
                etaEnsillage = np.matmul(np.matmul(configResultList[indexYear], self.lambdaEnsilage), self.eta)
                qtePaille.append(sum(0.8 * self.surface * etaPaille * eta2 * eta3))
                qteEnsillage.append(sum(1.5 * self.surface * etaEnsillage * eta2 * eta3))
            self.yearAssolementConfig=configResultList
            self.yearQtePaille=qtePaille
            self.yearQteEnsilage=qteEnsillage
            self.yearMB=resultList
            self.yearIFT=IFTresultList
            return True
        except:
            return False



