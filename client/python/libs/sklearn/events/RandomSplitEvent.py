#!/usr/bin/python
import numpy as np
import pandas as pd
import ModelDbSyncer
import sys
sys.path.append('./thrift/gen-py')
from modeldb import ModelDBService
import modeldb.ttypes as modeldb_types

class SyncRandomSplitEvent:
    def __init__(self, df, weights, seed, result, experimentRunId):
        self.df = df
        self.weights = weights
        self.seed = seed
        self.result = result
        self.experimentRunId = experimentRunId

    def makeEvent(self, syncer):
        self.syncableDataFrame = syncer.convertDftoThrift(self.df)

        allSyncableFrames = []
        for dataFrame in self.result:
            allSyncableFrames.append(syncer.convertDftoThrift(dataFrame))
        re = modeldb_types.RandomSplitEvent(self.syncableDataFrame, self.weights, self.seed, allSyncableFrames, self.experimentRunId)
        return re

    def associate(self, res, syncer):
         #generate identity for storing in dictionary
        dfImmOld = id(self.df)

        syncer.storeObject(dfImmOld,res.oldDataFrameId)
        for i in range(0, len(self.result)):
            syncer.storeObject(id(self.result[i]), res.splitIds[i])
        syncer.storeObject(self, res.splitEventId)

    def sync(self, syncer):
        re = self.makeEvent(syncer)

        #Invoking thrift client
        thriftClient = syncer.client
        res = thriftClient.storeRandomSplitEvent(re)
        self.associate(res, syncer)