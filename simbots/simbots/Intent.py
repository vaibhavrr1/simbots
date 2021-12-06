import json
from abc import ABC, abstractmethod
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn import metrics
import copy
from simbots.utils.exceptions import SchemaException

class Intent(ABC):
    """
    The abstract method for any intent.
    """

    @abstractmethod
    def __init__(self, intentName="Irrelevant",allIntentExamples=None, entityHandler=None,testSize=0.25,vocab=None):

        self.intentName = intentName
        self.testSize = testSize

        if not allIntentExamples:
            allIntentExamples = {}

        self.entityHandler = entityHandler
        self.allIntentExamples = allIntentExamples

        self.classifier = None
        self.vocab=vocab

        self.trainedIntentArray = []
        self.trained = False
        self.createIntent()



    @abstractmethod
    def createIntent(self,clfName=None):
        """

        Method to create intent will be overridden in the derived class

        :param clfName: Classifier Name
        :return: the inherited class should return a classifier

        """
        pass

    @staticmethod
    @abstractmethod
    def train(X_train, y_train, params = None):
        """

        :param X_train: Training examples
        :param y_train: Training labels
        :param params: Any additional parameters that may be needed can be defined here
        :return:

        """
        pass


class MultinomialNBIntent(Intent):
    """
    Uses Multinomial Naive bayes classifier for intent training.
    """

    def __init__(self,intentName="Irrelevant",allIntentExamples=None,entityHandler = None,vocab=None):
        """

        :param allIntentExamples:
        :param entityHandler:
        """

        super().__init__(intentName=intentName,allIntentExamples=allIntentExamples,
                         entityHandler = entityHandler,testSize=0.25,vocab=vocab)



    def createVocab(self):
        """
        This function creates the vocab for intent and updates the intent vocabulary
        :return:
        count_vect : This returns a fitted Countvectorizer object
        """

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
        """
        Creates the data set for the intent model
        :return:
        X_train: training sentences asn list
        X_test: testing sentences as list
        X : all sentences as list
        y_train: train set labels
        y_test: testset labels
        y : the complete  sample labels (including the training and the testing sets)

        """
        ##
        ## if output is 1 means intent is present else not
        ##
        allIntentExamplesCopy = copy.deepcopy(self.allIntentExamples)

        intentSamples = allIntentExamplesCopy[self.intentName]

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
        """
        Train the intent model

        :param X_train: Training sentences
        :param y_train: Training labels
        :param params: None
        :return: trained classifier
        """
        vectorizer = params["vectorizer"]
        X_trainCount = vectorizer.transform(X_train)
        clf = MultinomialNB()
        clf.fit(X_trainCount, y_train)
        return clf

    @staticmethod
    def predictClassifierOutput(clf, X, count_vect):
        """
        Make predictions on the trained intent
        :param clf: trained classifier
        :param X: The sample for prediction
        :param count_vect: count vectoriser for the classifier
        :return:

        predictions: predicted class
        probabilities: probablities for the predicted class
        """
        X_count = count_vect.transform(X)
        predictions = clf.predict(X_count)
        probabilities = clf.predict_proba(X_count)
        return predictions, probabilities


    def getIntentProbability(self, userMessage):
        """
        Get the intent probability
        :param userMessage: Text message from the user
        :return: {
        "name": classifier name
        "confidence": classifier confidence
        }
        """
        userMessage = [userMessage]
        predictions, probabilities = self.predictClassifierOutput(self.classifier["classifier"], userMessage,
                                                             self.classifier["data"]["countVect"])


        return {"name": self.classifier["name"], "confidence": probabilities[0][1]}

    def createIntent(self, clfName=None):
        """

        :param clfName: Classifier Name , if not provided , will default to intentName+'_multinomialNbClassifier'
        :return: classifier

        classifier = {
            "name": Classifier name,
            "classifier": Classifier Object,
            "expectedAccuracy": Training accuracy achieved by the intent,
            "data": {
                "countVect": count vectoriser ,
                "trainedOnX": Training samples,
                "trainedOnY": Training labels
            }



        """
        if not clfName:
            clfName = self.intentName  # + "_multinomialNbClassifier"

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
    """
    Class for creating and handling multiple intents
    """

    def __init__(self,allIntentExamples=None, entityHandler=None):

        """

        Intent Schema validation

        """

        if type(allIntentExamples)  != dict:
            raise SchemaException("Intent Samples","",
                                  "Intents should be a dict of the schema : \n "+
                                  "{\n 'IntentName1' : list of str  ,\n 'IntentName2' : list of str \n "+"}"

                                  )

        for intentName in allIntentExamples.keys():
            if "_" in intentName:
                raise SchemaException("Intent", intentName,"Intent Name should not contain '_'  .")

            intentExamples = allIntentExamples[intentName]

            if type(intentExamples) != list:
                raise SchemaException("Intent",intentName ,"Intent should be a list of type str , instead intent is {0} .".format(type(intentExamples)))

            for i,intentSample in enumerate(intentExamples):
                if type(intentSample) != str:
                    raise SchemaException("Intent",intentName,"Intent should be a list of type str ,instead intent sample no {0} ({1}) is {2} .".format(i,intentSample,type(intentSample)))

        intentNames = allIntentExamples.keys()
        if "Irrelevant" not in intentNames:
            raise SchemaException("Intent Samples","No intent with the name Irrelevant .","Every bot should have an intent with the name 'Irrelevant' , not found in detected intent names .")
        ##
        ## Initialise intent
        ##
        self.allIntentExamples = allIntentExamples
        self.entityHandler = entityHandler
        self.substituteAllEntitiesInAllTrainingExamples()
        self.intentSamplesAugment()

        self.trained    = False
        self.createAllTrainedIntents()


    def intentSamplesAugment(self):
        """

        Function to augment intent samples ,making sure each intent is at least 100 samples long


        """

        for key in self.allIntentExamples:
            while len(self.allIntentExamples[key]) < 100:
                self.allIntentExamples[key].extend(self.allIntentExamples[key])


    def substituteAllEntitiesInAllTrainingExamples(self):

        """

        For certain types of classifiers it is helpful to have entities substituted
        Whenever a new intent is trained , all the entitiy values in the message texts get replaced by the entity kind values.
        This is to help training the intents . Note that you can define certain entities to help increase the accuracy of intent


        """

        allIntentExamplesSubstituted = {}
        allIntentExamplesCopy = copy.deepcopy(self.allIntentExamples)

        for key in allIntentExamplesCopy:
            dum = []
            for mes in allIntentExamplesCopy[key]:
                dum.append(self.entityHandler.substituteAllEntities(" {0} ".format(mes)))

            allIntentExamplesSubstituted[key] = dum

        self.allIntentExamples = allIntentExamplesSubstituted

    def createAllTrainedIntents(self):
        """
        Creates trained intents and sets self.trained

        """

        allIntentExamplesCopy = copy.deepcopy(self.allIntentExamples)

        trainedIntentArray = []
        intentNames  = list(allIntentExamplesCopy.keys())
        intentNames.sort()
        #trainedIntentArray.append(MultinomialNBIntent(intentName=intentNames[0],allIntentExamples=self.allIntentExamples,entityHandler=self.entityHandler))
        #vocab = trainedIntentArray[0].vocab

        for intentName in intentNames:
            #
            # allIntentExamplesCopy = copy.deepcopy(self.allIntentExamples)
            #
            trainedIntentArray.append(
                MultinomialNBIntent(intentName=intentName,allIntentExamples=self.allIntentExamples,entityHandler=self.entityHandler,vocab=None)

            )
        self.trainedIntentArray =trainedIntentArray
        self.trained=True



    def getMessageIntents(self, message,dialogNumber=0):
        """
        Get message intents for a given dialog number
        :param message: Message Text
        :param dialogNumber:  The current dialog number
        :return:
        list of [{
        "name": classifier name
        "confidence": Classifier confidence
        "dialogNumber": Current dialog number
        "rank": Classifier rank
        }]
        """

        if self.entityHandler:
            # substitute message entities if they are available
            message = self.entityHandler.substituteAllEntities(message)

        if self.trained:
            allIntents = sorted([trainedIntent.getIntentProbability(message) for trainedIntent in self.trainedIntentArray],
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
            return "model not trained"



