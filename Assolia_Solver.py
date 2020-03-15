import numpy as np
import pandas as pd

pd.set_option('display.max_rows', 50000)
pd.set_option('display.max_columns', 50000)
from ortools.linear_solver import pywraplp



class objectSolver:
    def __init__(self,
                 solverMode='unconstrained IFT',
                 kIFT=0.0,
                 cultureList=[],
                 parcelleList=[],
                 constraintPaille=0,
                 constraintEnsilage=0,
                 constraintLuzerne=0,
                 numSolutionYear=0,
                 numYear=0,
                 eta=np.array([]),
                 ift=np.array([]),
                 surface=[],
                 prixVenteCulture=[],
                 coutProdCulture=[],
                 MPTS=np.array([]),
                 MPCn1=np.array([]),
                 R1=np.array([]),
                 MPCN=[],
                 R2=np.array([]),
                 yearRollLuzerne=4):



        self.solverMode = solverMode
        self.kIft = kIFT
        self.cultureList = cultureList
        #self.cultureList=self.updateCultureList(cultureList=cultureList,boundDict={'Luzerne':constraintLuzerne})
        self.parcelleList = parcelleList
        self.nbParcelle = len(self.parcelleList)
        self.nbCulture = len(self.cultureList)
        self.constraintPaille = constraintPaille
        self.constraintEnsilage = constraintEnsilage
        self.constraintLuzerne = constraintLuzerne
        self.numSolutionYear = numSolutionYear
        self.numYear = numYear
        self.surface = surface
        self.eta = eta
        self.ift = ift
        self.prixVenteCulture = prixVenteCulture
        self.coutProdCulture = coutProdCulture
        self.MPTS = MPTS
        self.R1 = R1
        self.R2 = R2,
        self.MPCn1 = MPCn1
        self.MPCN = MPCN
        self.iftMatrix = self.functionIFTmatrix(nbParcelle=self.nbParcelle, nbCulture=self.nbCulture,surface=self.surface, ift=self.ift)
        self.weightIFT = self.functionWeightIFT(iftMatrix=self.iftMatrix)
        self.lambdaPaille = self.functionLambdaPaille(Vculture=cultureList, nbCulture=self.nbCulture)
        self.lambdaEnsilage = self.functionLambdaEnsilage(Vculture=self.cultureList, nbCulture=self.nbCulture)
        self.lambdaLuzerne = self.functionLambdaLuzerne(Vculture=self.cultureList, nbCulture=self.nbCulture)
        self.dfMBSolution = pd.DataFrame()
        self.dfIFTSolution = pd.DataFrame()
        self.dfMCDA = pd.DataFrame()
        self.yearSolutionRepartition = []
        self.yearSolutionValue = []
        self.yearIftSolutionValue = []
        self.yearAssolementConfig = []
        self.yearQtePaille = []
        self.yearQteEnsilage = []
        self.yearQteLuzerne=[]
        self.yearMB = []
        self.yearIFT = []
        self.yearRollLuzerne=yearRollLuzerne
        #####
        self.debugConfig=pd.DataFrame()
        self.debugPaille=pd.DataFrame()
        self.debugEnsilage=pd.DataFrame()
        self.debugMb = pd.DataFrame()
        self.debugLuzerne=pd.DataFrame()

    def updateCultureList(self,cultureList,boundDict):
        culture=cultureList.copy()
        #map(lambda key: culture.remove(key) if boundDict[key]==0 else None ,cultureList)
        for key in boundDict:
            if boundDict[key]==0:
                culture.remove(key)
        return culture

    def updateVector(self,vector,boundDict,cultureList):
        map(lambda key: np.delete(vector,cultureList.index(key),axis=0) if boundDict[key] == 0 else None, boundDict)
        return vector

    def updateMatrix(self,matrix,boundDict,cultureList):
        map(lambda key: np.delete(matrix,cultureList.index(key),axis=1) if boundDict[key] == 0 else None, boundDict)
        return matrix


    def functionIFTmatrix(self, nbParcelle, nbCulture, surface, ift):
        tempiftMatrix = np.vstack([ift]*self.nbCulture)
        iftMatrix=1/sum(surface)*np.transpose(surface*np.transpose(tempiftMatrix))
        return iftMatrix

    # Coefficient pondération IFT
    def functionWeightIFT(self, iftMatrix):
        weightIFT = [element for row in iftMatrix for element in row]
        return weightIFT

    def functionLambdaPaille(self, Vculture, nbCulture):

        indexCulturePaille = [Vculture.index(culture) for culture in Vculture if culture == 'Blé de force' or culture == 'Orge']
        lambdaPaille = np.zeros((nbCulture, nbCulture))
        for index in indexCulturePaille:
            lambdaPaille[index][index] = 1

        return lambdaPaille

    # Construction matrice Lambda ensilage
    def functionLambdaEnsilage(self, Vculture, nbCulture):
        indexCultureEnsilage = [Vculture.index(culture) for culture in Vculture if culture == 'Maïs']
        lambdaEnsilage = np.zeros((nbCulture, nbCulture))
        for index in indexCultureEnsilage:
            lambdaEnsilage[index][index] = 1
        return lambdaEnsilage

    # Construction matrice Lambda Luzerne
    def functionLambdaLuzerne(self, Vculture, nbCulture):
        indexCultureLuzerne=[Vculture.index(culture) for culture in Vculture if culture=='Luzerne']
        lambdaLuzerne = np.zeros((nbCulture, nbCulture))
        for index in indexCultureLuzerne:
            lambdaLuzerne[index][index] = 1
        return lambdaLuzerne

    #Construction du vecteur d'historicité des configurations
    def functionHistSolution(self,indexSolution, indexYear):
        k = 0
        previousIndexList = []
        for backwardYear in range(indexYear, 0, -1):
            while True:
                if (indexSolution + k) % self.numSolutionYear == 0:
                    previousIndexList.append((indexSolution + k) / self.numSolutionYear)
                    indexSolution = (indexSolution + k) / self.numSolutionYear
                    k = 0
                    break
                k += 1
        return previousIndexList[::-1]

    def identifyPresenceCulture(self,repartition,cultureName):
        indexCulture = self.cultureList.index(cultureName)
        cultureParcelleMatch=[1 for rowParcelleIndex in range(repartition.shape[0]) if repartition[rowParcelleIndex][indexCulture]==1]

        return cultureParcelleMatch

    def transformEta(self,swapMatrix,eta,range_,cultureIndex):
        etaTransform = np.matmul(swapMatrix, eta)
        etaTransform = np.delete(etaTransform, range_, 0)
        etaTransform = np.delete(etaTransform, cultureIndex, 1)
        return etaTransform

    def swapMatrix(self,parcelleLuzIndex):
        swapList = []
        initCultureIndexList = list(range(self.nbCulture))
        for varLuz in parcelleLuzIndex:
              initCultureIndexList.remove(varLuz)
        swapedCultureIndexList = parcelleLuzIndex + initCultureIndexList


        row = [0] * self.nbCulture
        for rowIndex in range(self.nbParcelle):
            row[swapedCultureIndexList[rowIndex]] = 1
            swapList.append(row)
            row = [0] * self.nbCulture
        swapMatrix = np.array(swapList)
        swapMatrixInverse = np.linalg.inv(swapMatrix)

        return(swapMatrix,swapMatrixInverse)

    def mainConstraintMatrix(self,parcelleLuzIndex,weightDict):
        if len(parcelleLuzIndex) == 0:
            Mask = np.fromfunction(
                lambda i, j: np.logical_and(self.nbCulture * i <= j,j <= self.nbCulture * (i + 1) - 1),
                (self.nbParcelle, self.nbParcelle * self.nbCulture),
                dtype=int)
            constCulture = np.where(Mask == True, 1, 0)

        else:
            Mask = np.fromfunction(
                lambda i, j: np.logical_and((self.nbCulture - 1) * i <= j, j <= (self.nbCulture - 1) * (i + 1) - 1),
                                            (self.nbParcelle - len(parcelleLuzIndex),(self.nbParcelle - len(parcelleLuzIndex)) * (self.nbCulture - 1)),
                                             dtype=int)
            constCulture = np.where(Mask == True, 1, 0)


        constPaille = np.array(weightDict['Paille'])
        constEnsilage = np.array(weightDict['Ensilage'])
        constIFT = np.array(weightDict['IFT'])
        constLuzerne = np.array(weightDict['Luzerne'])

        if self.solverMode in ('constrained IFT', 'constrained decreasing IFT') and self.constraintLuzerne==0:
            constLuzerne=[1 if element>0 else 0 for element in constLuzerne]


        ##TEST
        if self.constraintLuzerne==0:
            constLuzerne = [1 if element > 0 else 0 for element in constLuzerne]


        if self.constraintPaille==0:
            constPaille= [1 if element > 0 else 0 for element in constPaille]


        if self.constraintEnsilage==0:
            constEnsilage= [1 if element > 0 else 0 for element in constEnsilage]

        #constaintsMask = [True if infoFlag > 0 else False for infoFlag in [self.constraintPaille, self.constraintEnsilage, self.constraintLuzerne]]
        constaintsMask = [True,True,True]

        #if len(parcelleLuzIndex) != 0 or self.constraintLuzerne == 0:
        if len(parcelleLuzIndex) != 0:
             constaintsMask[2] = False
        defautConstraintsList = [constPaille, constEnsilage, constLuzerne]
        tempArray = np.array(defautConstraintsList)
        tempArray = tempArray[constaintsMask]
        defautConstraintsList = tempArray.tolist()
        defautConstraintsList.insert(0, constCulture)

        if self.solverMode in ('constrained IFT', 'constrained decreasing IFT'):
            defautConstraintsList.append(constIFT)
        constMatrix = np.vstack(defautConstraintsList)

        return constMatrix

    def mainBoundaries(self,numConstraints,parcelleLuzIndex,indexNumSolution,iftRepartition):

        bound_Paille_sup, bound_Paille_inf = [], []
        bound_Ensilage_sup, bound_Ensilage_inf = [], []
        bound_Luzerne_sup, bound_Luzerne_inf = [], []
        boundMask=[]


        #Bound lié à la répartition culture/parcelle
        bound_culture_sup= [1] * (self.nbParcelle-len(parcelleLuzIndex))
        bound_culture_inf = [1] *(self.nbParcelle-len(parcelleLuzIndex))

        #Bound liés aux contraintes de Paille
        bound_Paille_inf.append(self.constraintPaille)
        bound_Paille_sup.append(100 * self.constraintPaille)

        # Bound liés aux contraintes d'Ensilage
        bound_Ensilage_inf.append(self.constraintEnsilage)
        bound_Ensilage_sup.append(100 * self.constraintEnsilage)

        # Bound liés aux contraintes de Luzerne
        bound_Luzerne_inf.append(self.constraintLuzerne)
        bound_Luzerne_sup.append(100 * self.constraintLuzerne)

        #boundMask = [True if infoFlag > 0 else False for infoFlag in [self.constraintPaille, self.constraintEnsilage, self.constraintLuzerne]]
        boundMask=[True,True,True]
        #if len(parcelleLuzIndex) != 0 or self.constraintLuzerne == 0:
        if len(parcelleLuzIndex) != 0 :
            boundMask[2] = False

        defautboundListSup = [bound_Paille_sup[0], bound_Ensilage_sup[0],  bound_Luzerne_sup[0]]
        defautboundListInf = [bound_Paille_inf[0], bound_Ensilage_inf[0],  bound_Luzerne_inf[0]]
        #Sup
        tempArraySup = np.array(defautboundListSup)
        tempArraySup = tempArraySup[boundMask]
        bound_sup = tempArraySup.tolist()

        #Inf
        tempArrayInf = np.array(defautboundListInf)
        tempArrayInf = tempArrayInf[boundMask]
        bound_inf = tempArrayInf.tolist()

        bound_sup=bound_culture_sup+bound_sup
        bound_inf=bound_culture_inf+bound_inf

        if self.solverMode in ('constrained IFT', 'constrained decreasing IFT'):
            bound_sup.append(
                sum(map(lambda IFTi, Si: IFTi * Si, iftRepartition, self.surface)) / sum(self.surface) * (
                        1 - self.kIft))
            bound_inf.append(0)

        return (bound_inf,bound_sup)

    #Fonction de résolution d'otimisation sous contraintes (MIP : Mixed Integer Programming)
    def MIPSolver(self,numvar,
                  numConstraints,
                  constMatrix,
                  weight,
                  bound_inf,
                  bound_sup,
                  parcelleLuzIndex,
                  swapMatrixInverse,
                  solutionRepartition,
                  solutionValue,
                  iftValue,
                  solutionConstraintList,
                  solutionBoundList
                  ):
        # OPTIMISATION

        # Create the mip solver with the CBC backend.
        solver = pywraplp.Solver('simple_mip_program', pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)
        infinity = solver.infinity()
        xvalues = [solver.IntVar(0, infinity, 'x[%i]' % j) for j in range(numvar)]
        x=dict(list(enumerate(xvalues)))

        for i in range(numConstraints):
            constraint = solver.RowConstraint(bound_inf[i], bound_sup[i], '')
            for j in range(numvar):
                constraint.SetCoefficient(x[j], (constMatrix[i][j]))

        objective = solver.Objective()

        #!!! Ne pas passer en map
        for j in range(numvar):
            objective.SetCoefficient(x[j], weight[j])
        objective.SetMaximization()

        status = solver.Solve()

        if status == pywraplp.Solver.OPTIMAL:
            solution=[x[j].solution_value() for j in range(numvar)]
            if numvar ==self.nbParcelle*self.nbCulture:
                repartition = np.vstack((np.array_split(solution, self.nbParcelle)))
            else :
                tempRepartition = np.vstack(np.array_split(solution, self.nbParcelle-len(parcelleLuzIndex)))
                tempRepartition = np.hstack((tempRepartition,np.zeros((tempRepartition.shape[0],1))))
                tempList=[0]*(self.nbCulture)
                tempList[self.cultureList.index('Luzerne')]=1
                for index in parcelleLuzIndex:
                     tempRepartition = np.vstack((np.array(tempList),tempRepartition))
                repartition = np.matmul(swapMatrixInverse,tempRepartition)

            solutionRepartition.append(repartition)
            marge_brute_optimale = solver.Objective().Value()
            solutionValue.append(marge_brute_optimale)
            iftValue.append(sum(np.matmul(repartition, self.ift) * self.surface) / sum(self.surface))

            # Préparation de la contrainte issue de la solution
            solutionConstraint, solutionBound = [], []
            solutionConstraint=[-1 if element ==0 else 1 if element ==1 else 0 for element in repartition.flatten().tolist()]
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


        return {
                'solutionRepartition':solutionRepartition,
                'solutionValue':solutionValue,
                'iftValue':iftValue,
                'solutionBound':solutionBound,
                'solutionConstraintList':solutionConstraintList,
                'solutionBoundList':solutionBoundList
                }


    def lambdaLocal(self,yearSolutionValue,yearIftSolutionValue):
        # A Optimiser
        listMatrix, colMatrix, iftTable = [], [], []

        for indexYear in range(self.numYear):

            Mask=np.fromfunction(lambda i,j:np.logical_and(i * (self.numSolutionYear) ** (self.numYear - (indexYear + 1)) <= j,j <= (i + 1) * self.numSolutionYear ** (self.numYear - (indexYear + 1)) - 1) ,
                                        (self.numSolutionYear ** (indexYear + 1), self.numSolutionYear ** self.numYear),
                                        dtype=int)
            LambdaLocal=np.where(Mask==True,1,0)

            listMatrix.append(LambdaLocal)
            colMatrix.append(np.matmul(yearSolutionValue[indexYear], listMatrix[indexYear]))
            iftTable.append(np.matmul(yearIftSolutionValue[indexYear], listMatrix[indexYear]))

        return {'colMatrix':colMatrix,'iftTable':iftTable}

    def printProgressBar(self,iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█', printEnd="\r"):
        """
        Call in a loop to create terminal progress bar
        @params:
            iteration   - Required  : current iteration (Int)
            total       - Required  : total iterations (Int)
            prefix      - Optional  : prefix string (Str)
            suffix      - Optional  : suffix string (Str)
            decimals    - Optional  : positive number of decimals in percent complete (Int)
            length      - Optional  : character length of bar (Int)
            fill        - Optional  : bar fill character (Str)
            printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
        """
        percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
        filledLength = int(length * iteration // total)
        bar = fill * filledLength + '-' * (length - filledLength)
        print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end='',flush=True)


        # Print New Line on Complete
        if iteration == total:
            print()

    def solve(self):
        #try:
        yearSolutionRepartition, yearSolutionValue, yearIftSolutionValue = [], [], []
        progressBarIter=0
        maxProgressBarIter=(1-self.numSolutionYear**(self.numYear+1))/(1-self.numSolutionYear)-1
        for indexYear in range(self.numYear):

            #print("ANNEE " + str(indexYear))
            solutionRepartition, solutionValue, iftValue = [], [], []
            indexNumSolution=0

            if indexYear == 0:
                initRepartition = [self.MPCn1]

            for cultureRepartition in initRepartition:
                solutionConstraintList, solutionBoundList = [], []

                if sum(cultureRepartition.flatten().tolist())!=0 :

                    for indexSolution in range(self.numSolutionYear):

                        #0. Identification des parcelles -> Luzerne
                        parcelleLuzIndex=[]
                        nullLuzParcelleFlag = []

                        if indexNumSolution == 0 and indexYear <= (self.yearRollLuzerne-2):
                            try:
                                varLuz=cultureRepartition[:,self.cultureList.index('Luzerne')]
                                if sum(varLuz)>0:
                                    parcelleLuzIndex=[varIndex for varIndex in range(len(varLuz)) if varLuz[varIndex]==1]
                            except:
                                pass

                        # A modifier pour prise en compte de MPCN2
                        elif indexYear>(self.yearRollLuzerne-2) and indexNumSolution==0:
                            previousRepartitionList,luzerneParcelleList,luzHistList,luzParcelleList,luzParcelGlobalList=[],[],[],[],[]
                            previousYearSolutionRepartition=yearSolutionRepartition


                            histCulture=self.functionHistSolution(indexSolution=indexNumSolution,indexYear=indexYear)
                            for index in range(len(histCulture)):
                                previousRepartitionList.append(previousYearSolutionRepartition[index][int(histCulture[index])])
                            #insertion de la répartition N-1
                            previousRepartitionList.insert(0,self.MPCn1)
                            previousRepartitionList=previousRepartitionList[-self.yearRollLuzerne:]# ne garde que les N dernieres repartition

                            #Presence Luzerne
                            for repartition in previousRepartitionList:
                                tempArray = repartition[:,self.cultureList.index('Luzerne')]
                                luzHistList.append(np.reshape(tempArray,(tempArray.size,1)))

                            luzHistArray = np.hstack(luzHistList)

                            parcelleLuzIndex=[indexParcelle for indexParcelle in range(self.nbParcelle) if (luzHistArray[indexParcelle][self.yearRollLuzerne-1]==1 and int(sum(luzHistArray[indexParcelle])<self.yearRollLuzerne))]
                            nullLuzParcelleFlag=[indexParcelle for indexParcelle in range(self.nbParcelle) if (luzHistArray[indexParcelle][self.yearRollLuzerne-1]==1 and sum(luzHistArray[indexParcelle])==self.yearRollLuzerne) or (luzHistArray[indexParcelle][self.yearRollLuzerne-1]==0 and 1<=sum(luzHistArray[indexParcelle])<=self.yearRollLuzerne-1)]

                        else:
                            table=solutionRepartition[indexNumSolution-1]
                            if sum(table.flatten().tolist())==0:
                                # init solution is a non convergent solution
                                solutionConstraint, solutionBound = [], []
                                solution = [0] * self.nbCulture * self.nbParcelle
                                repartition = np.zeros((self.nbParcelle, self.nbCulture))
                                solutionRepartition.append(repartition)
                                solutionValue.append(0)
                                iftValue.append(0)

                                solutionConstraint=[0]*(len(solution))
                                solutionBound.append(0)
                                solutionConstraintList.append(solutionConstraint)
                                solutionBoundList.append(solutionBound)
                                indexNumSolution += 1
                                progressBarIter+=1
                                self.printProgressBar(total=maxProgressBarIter, iteration=progressBarIter,
                                                      prefix='Progress:', suffix='Complete', length=50)
                                continue
                            else:
                                varLuz = table[:, self.cultureList.index('Luzerne')]
                                if sum(varLuz) > 0:
                                    parcelleLuzIndex=[varIndex for varIndex in range(len(varLuz)) if varLuz[varIndex] == 1]

                        #0.1-Modification de la matrice de culture initiale
                        #a.Matrice SWAP
                        try:
                            swapMatrix = self.swapMatrix(parcelleLuzIndex=parcelleLuzIndex)[0]
                            swapMatrixInverse = self.swapMatrix(parcelleLuzIndex=parcelleLuzIndex)[1]
                        except:
                            pass

                        # 1.Contruction matrice etap
                        etap = np.vstack([self.eta]*self.nbParcelle)

                        # 2.Construction de la matrice eta_ts
                        eta_ts = np.ones((self.nbParcelle, self.nbCulture)) - 1 / 100 * (np.transpose(np.matmul(self.R1, np.transpose(self.MPTS))))

                        # 3.Construction de la matrice eta_n1
                        eta_n1 = 1 / 100 * np.matmul(cultureRepartition, self.R2)[0]

                        # 4.Construction de la matrice etaG
                        etaG = etap * eta_ts * eta_n1

                        # Construction de la matrice/liste des eta Paille
                        surface = self.surface
                        weightIFTMatrix=self.iftMatrix

                        etaPaille= 0.8 * (np.transpose(surface*np.transpose(etaG)))
                        etaEnsilage = 1.5 * (np.transpose(surface*np.transpose(etaG)))
                        etaLuzerne = 1.0 * (np.transpose(surface*np.transpose(etaG)))

                        for i in range(len(etaPaille)):
                            if i not in [self.cultureList.index('Blé de force'), self.cultureList.index('Orge')]:
                                etaPaille[:, i] = 0
                        for i in range(len(etaEnsilage)):
                            if i not in[self.cultureList.index('Maïs')]:
                                etaEnsilage[:,i]=0
                        for i in range(len(etaLuzerne)):
                            if i not in[self.cultureList.index('Luzerne')]:
                                etaLuzerne[:,i]=0

                        if len(parcelleLuzIndex)>0:

                            etaPaille=self.transformEta(swapMatrix=swapMatrix,eta=etaPaille,range_=range(len(parcelleLuzIndex)),cultureIndex=self.cultureList.index('Luzerne'))
                            etaEnsilage = self.transformEta(swapMatrix=swapMatrix, eta=etaEnsilage,range_=range(len(parcelleLuzIndex)),cultureIndex=self.cultureList.index('Luzerne'))
                            etaLuzerne = self.transformEta(swapMatrix=swapMatrix, eta=etaLuzerne,range_=range(len(parcelleLuzIndex)),cultureIndex=self.cultureList.index('Luzerne'))
                            weightIFTMatrix = self.transformEta(swapMatrix=swapMatrix, eta= weightIFTMatrix,range_=range(len(parcelleLuzIndex)),cultureIndex=self.cultureList.index('Luzerne'))

                        weightPaille=[element for row in etaPaille for element in row]
                        weightEnsilage = [element for row in etaEnsilage for element in row]
                        weightLuzerne = [element for row in etaLuzerne for element in row]
                        weightIFT = [element for row in weightIFTMatrix for element in row]

                        # 5.Matrice Prix culture/parcelle
                        Pv = np.vstack([self.prixVenteCulture] * self.nbParcelle)
                        Ct = np.vstack([self.coutProdCulture] * self.nbParcelle)


                        # 6.Matrice de marge

                        Mg = np.transpose(surface*np.transpose(eta_n1*(etap*eta_ts*Pv-Ct)))


                        if len(parcelleLuzIndex) != 0:
                            Mg = self.transformEta(swapMatrix=swapMatrix, eta=Mg,range_=range(len(parcelleLuzIndex)), cultureIndex=self.cultureList.index('Luzerne'))

                        # Coefficient pondération calcul Marge Brute
                        weight = [element for row in Mg for element in row]

                        # 7.Matrice des contraintes
                        weightDict={'Paille':weightPaille,'Ensilage':weightEnsilage,'Luzerne':weightLuzerne,'IFT':weightIFT}
                        constMatrix=self.mainConstraintMatrix(parcelleLuzIndex=parcelleLuzIndex,weightDict=weightDict)
                        iftRepartition = np.matmul(cultureRepartition, self.ift)

                        if len(nullLuzParcelleFlag)!=0 and constMatrix.shape[1]==self.nbParcelle*self.nbCulture:
                            for indexParcelle in nullLuzParcelleFlag:
                                tempConstraint=[0]*constMatrix.shape[1]
                                tempConstraint[self.nbCulture*(indexParcelle+1)-1]=1
                                constMatrix = np.vstack((constMatrix,np.array(tempConstraint)))

                        if indexSolution >= 1:

                            for prvsol in solutionConstraintList:
                                if sum(prvsol)!=0 and len(parcelleLuzIndex)!=0 :

                                    #previousSol = np.matmul(swapMatrix, np.vstack((np.array_split(np.array(prvsol), self.nbParcelle))))
                                    previousSol = np.matmul(swapMatrix, np.vstack((np.array_split(np.array(prvsol), self.nbParcelle))))
                                    previousSol=  previousSol[len(parcelleLuzIndex):,0:self.nbCulture-1]
                                    constMatrix = np.vstack((constMatrix, np.array(previousSol.flatten())))
                                else:
                                    constMatrix = np.vstack((constMatrix, np.array(prvsol)))


                        numvar = constMatrix.shape[1]
                        numConstraints = constMatrix.shape[0]

                        #8. Défintion des boundaries
                        bound_sup=self.mainBoundaries(numConstraints=numConstraints,parcelleLuzIndex=parcelleLuzIndex,indexNumSolution=indexNumSolution,iftRepartition=iftRepartition)[1]
                        bound_inf = self.mainBoundaries(numConstraints=numConstraints,parcelleLuzIndex=parcelleLuzIndex,indexNumSolution=indexNumSolution,iftRepartition=iftRepartition)[0]

                        if len(nullLuzParcelleFlag) != 0 and constMatrix.shape[1] == self.nbParcelle * self.nbCulture:
                            for bound in nullLuzParcelleFlag:
                                bound_sup.append(0)
                                bound_inf.append(0)

                        if indexSolution >= 1:
                            for indexSolBound in range(len(solutionBoundList)):
                                if sum(solutionConstraintList[indexSolution - 1])!=0:
                                    if len(parcelleLuzIndex)!=0:
                                        solBnd =  np.matmul(swapMatrix, np.array_split(np.array(solutionConstraintList[indexSolution - 1]), self.nbParcelle))
                                        solBnd =  solBnd[len(parcelleLuzIndex):,0:self.nbCulture-1]
                                        solBnd=solBnd.flatten()
                                        solBnd = solBnd.tolist()
                                    else:
                                        solBnd=np.array(solutionConstraintList[indexSolution - 1])
                                        solBnd = solBnd.flatten()
                                        solBnd = solBnd.tolist()

                                    bound_sup.append(-(1 - solBnd.count(1)))
                                    bound_inf.append(0)

                        optimisationResult=self.MIPSolver(numConstraints=numConstraints,
                                                          numvar=numvar,
                                                          constMatrix=constMatrix,
                                                          weight=weight,
                                                          bound_inf=bound_inf,
                                                          bound_sup=bound_sup,
                                                          parcelleLuzIndex=parcelleLuzIndex,
                                                          swapMatrixInverse=swapMatrixInverse,
                                                          solutionRepartition=solutionRepartition,
                                                          solutionValue=solutionValue,
                                                          iftValue=iftValue,
                                                          solutionConstraintList=solutionConstraintList,
                                                          solutionBoundList=solutionBoundList)

                        solutionRepartition=optimisationResult['solutionRepartition']
                        solutionValue=optimisationResult['solutionValue']
                        iftValue=optimisationResult['iftValue']
                        solutionBound=optimisationResult['solutionBound']
                        solutionConstraintList=optimisationResult['solutionConstraintList']
                        solutionBoundList=optimisationResult['solutionBoundList']





                        indexNumSolution+=1
                        progressBarIter += 1
                        self.printProgressBar(total=maxProgressBarIter, iteration=progressBarIter,
                                              prefix='Progress:', suffix='Complete', length=50)



                else:
                    #init solution is a non convergent solution
                    solutionConstraint, solutionBound = [], []
                    solution = [0] * self.nbCulture * self.nbParcelle
                    for indexSolution in range(self.numSolutionYear):
                        repartition = np.zeros((self.nbParcelle, self.nbCulture))
                        solutionRepartition.append(repartition)
                        solutionValue.append(0)
                        iftValue.append(0)
                        for element in solution:
                            solutionConstraint.append(0)
                        solutionBound.append(0)
                        solutionConstraintList.append(solutionConstraint)
                        solutionBoundList.append(solutionBound)
                        indexNumSolution += 1
                        progressBarIter += 1
                        self.printProgressBar(total=maxProgressBarIter, iteration=progressBarIter,
                                              prefix='Progress:', suffix='Complete', length=50)



            initRepartition = solutionRepartition
            yearSolutionRepartition.append(solutionRepartition)
            yearSolutionValue.append(solutionValue)
            yearIftSolutionValue.append(iftValue)
            progressBarIter+=1

        if len(yearSolutionRepartition[0])==1:
            del yearSolutionRepartition[0]
        self.yearSolutionRepartition = yearSolutionRepartition
        self.yearSolutionValue = yearSolutionValue
        self.yearIftSolutionValue = yearIftSolutionValue

        # Création de la matrice des résultats
        colMatrix = self.lambdaLocal(yearSolutionValue=yearSolutionValue,yearIftSolutionValue=yearIftSolutionValue)['colMatrix']
        iftTable = self.lambdaLocal(yearSolutionValue=yearSolutionValue,yearIftSolutionValue=yearIftSolutionValue)['iftTable']

        matrixResult = np.transpose(colMatrix)
        matrixIFT = np.transpose(iftTable)

        dfResult = pd.DataFrame(matrixResult)
        dfIFT = pd.DataFrame(matrixIFT)
        dfResult['mean'] = dfResult.mean(axis=1)
        dfIFT['mean'] = dfIFT.mean(axis=1)

        self.dfMBSolution = dfResult.copy(deep=True)
        self.dfIFTSolution = dfIFT.copy(deep=True)
        return True

        # except Exception as Er:
        #      print(Er)
        #      return False

    def resultSelection(self, selectionMode='MB', weightMB=0.5, weightIFT=0.5):

        #try:
        dfMBSolutionNonNull=self.dfMBSolution[~(self.dfMBSolution == 0).any(axis=1)]
        dfIFTSolutionNonNull = self.dfIFTSolution[~(self.dfIFTSolution == 0).any(axis=1)]

        dfMCDA = pd.DataFrame()

        if dfMBSolutionNonNull.empty and dfIFTSolutionNonNull.empty:
            dfMCDA['MB'] = self.dfMBSolution['mean']
            dfMCDA['IFT'] = self.dfIFTSolution['mean']
        else:
            dfMCDA['MB'] = self.dfMBSolution[~(self.dfMBSolution == 0).any(axis=1)]['mean']
            dfMCDA['IFT'] = self.dfIFTSolution[~(self.dfIFTSolution == 0).any(axis=1)]['mean']

        dfMCDA['MB2'] = dfMCDA.apply(lambda row: row.MB ** 2, axis=1)
        dfMCDA['IFT2'] = dfMCDA.apply(lambda row: row.IFT ** 2, axis=1)

        dfMCDA['MB2Sum'] = dfMCDA.apply(lambda row: dfMCDA['MB2'].sum(), axis=1)
        dfMCDA['IFT2Sum'] = dfMCDA.apply(lambda row: dfMCDA['IFT2'].sum(), axis=1)

        dfMCDA['MB_Norm'] = dfMCDA.apply(lambda row: row.MB2 / row.MB2Sum, axis=1)
        dfMCDA['IFT_Norm'] = dfMCDA.apply(lambda row: row.IFT2 / row.IFT2Sum, axis=1)

        if selectionMode == 'MB':
            dfMCDA['MBNormWeighted'] = dfMCDA.apply(lambda row: row.MB_Norm * 1, axis=1)
            dfMCDA['IFTNormWeighted'] = dfMCDA.apply(lambda row: row.IFT_Norm * 0, axis=1)
        elif selectionMode == 'MCDA':
            dfMCDA['MBNormWeighted'] = dfMCDA.apply(lambda row: row.MB_Norm * weightMB, axis=1)
            dfMCDA['IFTNormWeighted'] = dfMCDA.apply(lambda row: row.IFT_Norm * weightIFT, axis=1)

        dfMCDA['MB_ideal'] = dfMCDA.apply(lambda row: dfMCDA['MBNormWeighted'].max(), axis=1)
        dfMCDA['MB_anti_ideal'] = dfMCDA.apply(lambda row: dfMCDA['MBNormWeighted'].min(), axis=1)

        dfMCDA['IFT_ideal'] = dfMCDA.apply(lambda row: dfMCDA['IFTNormWeighted'].min(), axis=1)
        dfMCDA['IFT_anti_ideal'] = dfMCDA.apply(lambda row: dfMCDA['IFTNormWeighted'].max(), axis=1)

        dfMCDA['IFT_ideal'] = dfMCDA.apply(lambda row: dfMCDA['IFTNormWeighted'].min(), axis=1)
        dfMCDA['IFT_anti_ideal'] = dfMCDA.apply(lambda row: dfMCDA['IFTNormWeighted'].max(), axis=1)

        dfMCDA['ideal_dist'] = dfMCDA.apply(
            lambda row: ((row.MBNormWeighted - row.MB_ideal) ** 2 + (
            row.IFTNormWeighted - row.IFT_ideal) ** 2) ** 0.5,
            axis=1)

        dfMCDA['anti_ideal_dist'] = dfMCDA.apply(lambda row: ((row.MBNormWeighted - row.MB_anti_ideal) ** 2 + (row.IFTNormWeighted - row.IFT_anti_ideal) ** 2) ** 0.5, axis=1)
        dfMCDA['ranking'] = dfMCDA.apply(lambda row: row.anti_ideal_dist / (row.anti_ideal_dist + row.ideal_dist),axis=1)

        dfMCDA['index_col'] = dfMCDA.index
        dfMCDA = dfMCDA.sort_values(['ranking'], ascending=[False])
        dfMCDA =dfMCDA.head(1)
        self.dfMCDA = dfMCDA.copy(deep=True)
        self.indexRowResult = dfMCDA['index_col'].tolist()[0]

        return dfMCDA
        # except Exception as Er:
        #      print(Er)
        #      return False

    def assolement(self):
        #try:
        resultList = self.dfMBSolution[self.dfMBSolution.index == self.indexRowResult].values.tolist()[0]
        IFTresultList = self.dfIFTSolution[self.dfIFTSolution.index == self.indexRowResult].values.tolist()[0]
        configResultList, qtePaille, qteEnsillage,qteLuzerne = [], [], [], []
        for indexYear in range(self.numYear):


            configResultList.append(self.yearSolutionRepartition[indexYear][(self.indexRowResult // (self.numSolutionYear ** (self.numYear - (indexYear + 1))))])
            if indexYear < 1:
                MPCn1 = self.MPCn1
            else:
                MPCn1 = configResultList[indexYear - 1]

            v = sum(map(lambda i: np.matmul(np.matmul(configResultList[indexYear][i], self.R1), np.transpose(self.MPTS[i])) * np.identity(self.nbParcelle)[i], range(len(configResultList[indexYear]))))
            eta2 = (np.ones(self.nbParcelle) - v / 100)

            u = sum(map(lambda i: np.matmul(np.matmul(self.R2, configResultList[indexYear][i]), MPCn1[i]) * np.identity(self.nbParcelle)[i], range(self.nbParcelle)))
            eta3 = (u / 100)

            etaPaille = np.matmul(np.matmul(configResultList[indexYear], self.lambdaPaille), self.eta)
            etaEnsillage = np.matmul(np.matmul(configResultList[indexYear], self.lambdaEnsilage), self.eta)
            etaLuzerne = np.matmul(np.matmul(configResultList[indexYear], self.lambdaLuzerne), self.eta)

            qtePaille.append(sum(0.8*(np.transpose(self.surface*np.transpose(etaPaille * eta2 * eta3)))))
            qteEnsillage.append(sum(1.5 * (np.transpose(self.surface*np.transpose(etaEnsillage * eta2 * eta3)))))
            qteLuzerne.append(sum(1.0 * (np.transpose(self.surface*np.transpose(etaLuzerne * eta2 * eta3)))))

        culture, cultureConfig = [], []
        dfConfig = pd.DataFrame()
        dfPaille = pd.DataFrame()
        dfEnsilage = pd.DataFrame()
        dfLuzerne = pd.DataFrame()
        dfMb = pd.DataFrame()
        dfIFT = pd.DataFrame()
        dfConfig["Parcelle"] = self.parcelleList
        dfPaille["-"] = ['Qte paille']
        dfEnsilage["-"] = ["Qte Ensilage"]
        dfLuzerne["-"] = ["Qte Luzerne"]
        dfMb["-"] = ["Marge Brute"]
        dfIFT["-"] = ["IFT"]
        year = 0
        for config in configResultList:
            culture = []
            for row in config:
                try:
                    culture.append(self.cultureList[(row.tolist()).index(1)])
                except:
                    culture.append("-")

            dfConfig["Culture Année " + str(year)] = culture
            dfPaille["Année " + str(year)] = qtePaille[year]
            dfEnsilage["Année " + str(year)] = qteEnsillage[year]
            dfLuzerne["Année " + str(year)] = qteLuzerne[year]
            dfMb["Année " + str(year)] = resultList[year]
            dfIFT["Année " + str(year)] = IFTresultList[year]
            cultureConfig.append(culture)
            year = year + 1

        self.yearAssolementConfig = configResultList
        self.yearQtePaille = qtePaille
        self.yearQteEnsilage = qteEnsillage
        self.yearQteLuzerne = qteLuzerne
        self.yearMB = resultList
        self.yearIFT = IFTresultList
        #####
        self.debugConfig=dfConfig
        self.debugPaille = dfPaille
        self.debugEnsilage = dfEnsilage
        self.debugLuzerne = dfLuzerne
        self.debugMb = dfMb
        self.debugIFT=dfIFT

        return True
        # except Exception as Er:
        #     print(Er)
        #     return False



