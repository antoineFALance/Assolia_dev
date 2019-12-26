import sklearn.datasets as datasets
from sklearn.tree import DecisionTreeClassifier
import pandas as pd
from sklearn.externals.six import StringIO
from sklearn import tree


iris=datasets.load_iris()
df=pd.DataFrame(iris.data, columns=iris.feature_names)
y=iris.target

print(iris.data)
print(iris.feature_names)
print(y)


dtree=DecisionTreeClassifier()
dtree.fit(df,y)
tree.plot_tree(dtree)

