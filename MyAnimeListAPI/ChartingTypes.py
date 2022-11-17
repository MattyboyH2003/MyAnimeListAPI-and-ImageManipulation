import matplotlib.pyplot as plt
from pandas import DataFrame
from copy import deepcopy

class ChartErrors(Exception): pass

class StackedBarChart:
    def __init__(self, xLabel, yLabel, layers, **kwargs):
        # Axis Labels
        self.xLabel = xLabel
        self.yLabel = yLabel

        # Number of layers (stacked)
        self.numberOfLayers = len(layers)
        self.layers = layers

        # Data for the bars
        self.columns = []
        self.columnLabels = []

        if "colours" in list(kwargs.keys()):
            if isinstance(kwargs["colours"], dict):
                self.coloursDict = kwargs["colours"]
            else:
                raise ChartErrors("Please provide data of type Dict for the chart colours")
        else:
            self.coloursDict = None
        
        if "title" in list(kwargs.keys()):
            self.title = str(kwargs["title"])
        else:
            self.title = "Stacked Bar Chart"

    ####################
    # Public Functions #
    ####################

    def AddColumn(self, label, data = None):
        if data == None:
            data = [0 for _ in range(self.numberOfLayers)]
        if len(data) != self.numberOfLayers:
            raise ChartErrors("Unable to add column due to invalid data")
        for item in data:
            if not isinstance(item, int):
                raise ChartErrors("Please make sure all data points are of type int")
        if label in self.columnLabels:
            raise ChartErrors(f"Column with the label '{label}' already exists")

        self.columns.append(data)
        self.columnLabels.append(label)

    def AddLayer(self, layerName : str, defaultValue = 0, colour = "#000000"):
        self.numberOfLayers += 1
        self.layers.append(layerName)
        
        self.coloursDict[layerName] = colour

        for column in self.columns:
            column.append(defaultValue)

    def ModifyColumn(self, columnName, data):
        if columnName in self.columnLabels:
            if len(data) != self.numberOfLayers:
                raise ChartErrors("Unable to modify column due to invalid data")
            else:
                for point in data:
                    if not isinstance(point, int):
                        raise ChartErrors("Please make sure all data points are of type int")
                self.columns[self.columnLabels.index(columnName)] = data
        else:
            raise ChartErrors(f"Column '{columnName} is not in this table, please use 'AddColumn' to add as a new one")
    
    def GetColumn(self, columnName):
        if columnName in self.columnLabels:
            return self.columns[self.columnLabels.index(columnName)]
        else:
            raise ChartErrors(f"Column '{columnName} is not in this table, please use 'AddColumn' to add as a new one")

    def GetColumnLabels(self):
        return self.columnLabels

    def GetLayers(self):
        return deepcopy(self.layers)

    def SetColours(self, colours : dict):
        self.coloursDict = colours

    def Draw(self, order = None):
        validOrder = [
            "total",
            "alphabetical"
        ]
        if isinstance(order, list):
            columnOrder = self.OrderColumns(order)
        elif order != None:
            raise ChartErrors("Order needs to be a list")
        else:
            columnOrder = self.columnLabels
        
        dataframeList = []

        for i in range(0, len(columnOrder)):
            dfColumn = [columnOrder[i]]
            dfColumn.extend(self.columns[self.columnLabels.index(columnOrder[i])])
            dataframeList.append(dfColumn)

        print(dataframeList)
        
        dfColumns = [self.xLabel]
        dfColumns.extend(self.layers)
        dataframe = DataFrame(dataframeList, columns = dfColumns)

        colours = [self.coloursDict.get(x, "#000000") for x in self.layers]

        dataframe.plot(
            x = self.xLabel,
            ylabel = self.yLabel,
            kind = "bar", 
            stacked = True, 
            title = self.title,
            color = colours
        )

        plt.show()

    def OrderColumns(self, sortKeys = ["total"]):
        print("Ordering Data")
        
        columnsDict = {}
        for i in range(0, len(self.columnLabels)):
            columnsDict[self.columnLabels[i]] = self.columns[i]
        
        print(f"Starting Columns: {len(self.columns)}")
        
        return self._orderData(columnsDict, deepcopy(self.columnLabels), sortKeys)

    #####################
    # Private Functions #
    #####################

    def _orderData(self, columnsDict : dict, orderedColumnLables : list, sortKeys : list):
        print("Starting Sort")
        print(f"First Key: {sortKeys[0]}")
        print(f"Remaining Keys: {sortKeys[1:]}")
        
        lablesTree = self._orderDataRecc(columnsDict, orderedColumnLables, sortKeys[0], sortKeys[1:])

        print(lablesTree)

        unfoldedTree = self._ReadTree(lablesTree)

        print(unfoldedTree)

        return unfoldedTree

    def _orderDataRecc(self, columnsDict : dict, orderedColumnLables : list, currentKey : str, remainingKeys: list):
        print(f"Starting With: {orderedColumnLables}")
        
        keyFunc = {
            "total" : self._totalSplit,
            "alphabetical" : self._alphabeticalSplit,
        }

        if len(remainingKeys) > 1:
            nextKey = remainingKeys[0]
            remainingKeys = remainingKeys[1:]
        elif len(remainingKeys) == 1:
            nextKey = remainingKeys[0]
            remainingKeys = []
        else:
            nextKey = None 

        # Split into ordered sublists
        
        print(f"splitting based on '{currentKey}'")
        if currentKey in list(keyFunc.keys()):
            splitLables = keyFunc[currentKey](columnsDict, orderedColumnLables)
        elif currentKey in self.layers:
            splitLables = self._layerCountSplit(columnsDict, orderedColumnLables, currentKey)
        else:
            raise ChartErrors(f"Invalid sort key given: {currentKey}")
        
        print(f"result: {splitLables}")
        print(F"next key: {nextKey}, remaining keys: {remainingKeys}\n")

        if nextKey != None: 
            for index, sublist in enumerate(splitLables):
                if len(sublist) > 1:
                    splitLables[index] = self._orderDataRecc(columnsDict, sublist, nextKey, remainingKeys)

        return splitLables

    def _layerCountSplit(self, columnsDict : dict, orderedLables : list, sortLayer : str) -> list:
        tempDict = {}

        for label in orderedLables:
            if str(columnsDict[label][self.layers.index(sortLayer)]) not in list(tempDict.keys()):
                tempDict[str(columnsDict[label][self.layers.index(sortLayer)])] = [label]
            else:
                tempDict[str(columnsDict[label][self.layers.index(sortLayer)])].append(label)
        
        orderedKeys = sorted(list(tempDict.keys()), key = lambda a:int(a), reverse=True)

        return [tempDict[key] for key in orderedKeys]

    @staticmethod
    def _totalSplit(columnsDict : dict, orderedLables : list) -> list:
        tempDict = {}

        for label in orderedLables:
            key = str(sum(columnsDict[label]))
            if key not in list(tempDict.keys()):
                tempDict[key] = [label]
            else:
                tempDict[key].append(label)

        orderedKeys = sorted(list(tempDict.keys()), key = lambda a:int(a), reverse=True)

        return [tempDict[key] for key in orderedKeys]

    @staticmethod
    def _alphabeticalSplit(columnsDict : dict, orderedLables : list) -> list:
        tempDict = {}

        for label in orderedLables:
            if label not in list(tempDict.keys()):
                tempDict[label] = [label]
            else:
                tempDict[label].append(label)
        
        orderedKeys = sorted(list(tempDict))

        return [tempDict[key] for key in orderedKeys]

    def _ReadTree(self, tree) -> list:
        valuesRead = []
        for item in tree:
            if isinstance(item, list):
                valuesRead.extend(self._ReadTree(item))
            else:
                valuesRead.append(item)
        return valuesRead

