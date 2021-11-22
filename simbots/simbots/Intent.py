import json
from abc import ABC, abstractmethod
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn import metrics
import copy

class Intent(ABC):

    @abstractmethod
    def __init__(self, intentName="Irrelevant",allIntentExamples=None, entityHandler=None,testSize=0.25,vocab=None):

        self.intentName = intentName
        self.testSize = testSize

        if not allIntentExamples:
            allIntentExamples = {}

        self.entityHandler = entityHandler
        self.allIntentExamples = allIntentExamples
        if self.entityHandler:
            self.substituteAllEntitiesInAllTrainingExamples()

        self.classifier = None
        self.vocab=vocab

        self.trainedIntentArray = []
        self.trained = False
        self.createIntent()

    def substituteAllEntitiesInAllTrainingExamples(self):

        """

        Substitutes all the training examples with the entity classes

        :return:
        """

        allIntentExamplesSubstituted = {}
        allIntentExamplesCopy = copy.deepcopy(self.allIntentExamples)

        for key in allIntentExamplesCopy:
            dum = []
            for mes in allIntentExamplesCopy[key]:
                dum.append(self.entityHandler.substituteAllEntities(" {0} ".format(mes)))

            allIntentExamplesSubstituted[key] = dum

        self.allIntentExamples = allIntentExamplesSubstituted

    @abstractmethod
    def createIntent(self,clfName=None):
        pass

    @staticmethod
    @abstractmethod
    def train(X_train, y_train, params = None):
        pass


class MultinomialNBIntent(Intent):

    def __init__(self,intentName="Irrelevant",allIntentExamples=None,entityHandler = None,vocab=None):
        """

        :param allIntentExamples:
        :param entityHandler:
        """

        super().__init__(intentName=intentName,allIntentExamples=allIntentExamples,
                         entityHandler = entityHandler,testSize=0.25,vocab=vocab)


    def substituteAllEntitiesInAllTrainingExamples(self):
        """

        :return:
        """
        super().substituteAllEntitiesInAllTrainingExamples()


    def createVocab(self):

        ##
        ##
        ## this function creates the vocabulary for the BOW /
        ##
        ##
        ##
        ## Initialise the Count Vectoriser
        ##
        count_vect = CountVectorizer() # stop_words="english"
        ##
        ## Create the Count Vectoriser Object (This gives a bag of words representation)
        ##
        allIntentExamplesCopy = copy.deepcopy(self.allIntentExamples)

        allData=[intentExample for intentExamples in allIntentExamplesCopy.values() for intentExample in intentExamples]
        count_vect.fit_transform(allData)
        vocab=count_vect.vocabulary_
        count_vect.revVocabulary_ =  dict(zip(vocab.values(),vocab.keys()))
        self.vocab = count_vect

        return count_vect

    def createDataSetForIntent(self):

        ##
        ## if output is 1 means intent is present else not
        ##
        allIntentExamplesCopy = copy.deepcopy(self.allIntentExamples)

        intentSamples = allIntentExamplesCopy[self.intentName]
        #
        # pop the intent from json
        #
        allIntentExamplesCopy.pop(self.intentName, None)
        nonIntentSamples = [intentExample for intentExamples in allIntentExamplesCopy.values() for intentExample in
                            intentExamples]
        Y = [1 for i in range(len(intentSamples))] + [0 for i in range(len(nonIntentSamples))]
        intentSamples.extend(nonIntentSamples)
        X = copy.deepcopy(intentSamples)

        ##
        ## stratify split the dataset to maintain class balance
        ##

        X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=self.testSize, stratify=Y, random_state=2020)

        return X_train, X_test, X, y_train, y_test, Y

    @staticmethod
    def train(X_train, y_train, params = None):
        vectorizer = params["vectorizer"]
        X_trainCount = vectorizer.transform(X_train)
        clf = MultinomialNB()
        clf.fit(X_trainCount, y_train)
        return clf

    @staticmethod
    def predictClassifierOutput(clf, X, count_vect):
        X_count = count_vect.transform(X)
        predictions = clf.predict(X_count)
        probabilities = clf.predict_proba(X_count)
        return predictions, probabilities


    def getIntentProbability(self, userMessage):
        userMessage = [userMessage]
        predictions, probabilities = self.predictClassifierOutput(self.classifier["classifier"], userMessage,
                                                             self.classifier["data"]["countVect"])

        # print probabilities
        return {"name": self.classifier["name"], "confidence": probabilities[0][1]}

    def createIntent(self, clfName=None):
        if not clfName:
            clfName = self.intentName + "_multinomialNbClassifier"

        ##
        ## Create vocabulary
        ##

        if not self.vocab:
            cv = self.createVocab()
        else:
            cv= self.vocab

        X_train, X_test, X_all, y_train, y_test, y_all = self.createDataSetForIntent()

        clf = self.train(X_train, y_train, {"vectorizer" :cv})

        predictions, probabilities = self.predictClassifierOutput(clf, X_test, cv)

        expectedAccuracy = metrics.accuracy_score(y_test, predictions)

        ##
        ## Now train on the complete dataset
        ##
        clf = self.train(X_all, y_all, {"vectorizer" :cv})

        classifier = {
            "name": clfName,
            "classifier": clf,
            "expectedAccuracy": expectedAccuracy,
            "data": {
                "countVect": cv,
                "trainedOnX": X_train,
                "trainedOnY": y_train
            }
        }

        self.classifier = classifier
        return classifier



class IntentsHandler():

    def __init__(self,allIntentExamples=None, entityHandler=None):

        self.allIntentExamples = allIntentExamples
        self.intentSamplesAugment()
        self.entityHandler     = entityHandler
        self.trained    = False
        self.createAllTrainedIntents()


    def intentSamplesAugment(self):
        # Write a better function for this
        for i in range(4):
            for key in self.allIntentExamples:
                self.allIntentExamples[key].extend(self.allIntentExamples[key])
                if len(self.allIntentExamples[key]) < 20:
                    self.allIntentExamples[key].extend(self.allIntentExamples[key])


    def createAllTrainedIntents(self):

        allIntentExamplesCopy = copy.deepcopy(self.allIntentExamples)

        trainedIntentArray = []
        intentNames  = list(allIntentExamplesCopy.keys())
        intentNames.sort()
        #trainedIntentArray.append(MultinomialNBIntent(intentName=intentNames[0],allIntentExamples=self.allIntentExamples,entityHandler=self.entityHandler))
        #vocab = trainedIntentArray[0].vocab

        for intentName in intentNames:
            #
            # allIntentExamplesCopy = copy.deepcopy(self.allIntentExamples)
            # print intent
            #
            trainedIntentArray.append(
                MultinomialNBIntent(intentName=intentName,allIntentExamples=self.allIntentExamples,entityHandler=self.entityHandler,vocab=None)

            )
        self.trainedIntentArray =trainedIntentArray
        self.trained=True



    def getMessageIntents(self, message,dialogNumber=0):

        if self.entityHandler:
            message = self.entityHandler.substituteAllEntities(message)

        if self.trained:
            allIntents=sorted([trainedIntent.getIntentProbability(message) for trainedIntent in self.trainedIntentArray],
                      key=lambda x: x["confidence"], reverse=True)

            allIntentsDialogCounterUpdated=[]
            rank=1
            for elem in allIntents:
                elem["dialogNumber"]=dialogNumber
                elem["rank"]=rank
                allIntentsDialogCounterUpdated.append(elem)
                rank+=1

            return allIntentsDialogCounterUpdated
        else:
            return "error"



