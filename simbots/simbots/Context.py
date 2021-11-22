from .Intent import IntentsHandler
from .Entity import EntitiesHandler
from objectpath import Tree
import datetime

class ContextManager():

    def __init__(self,entitiesExtractorJson,allIntentExamples):

        entitiesHandler =  EntitiesHandler(entitiesExtractorJson)
        intentHandlers  = [IntentsHandler(allIntentExamples,entityHandler=entitiesHandler)]

        self.entitiesHandler = entitiesHandler
        self.intentHandlers  = intentHandlers
        self.context={
            "entities":[],
            "intents":[],
            "dialogs":[],
            "messages":[]
        }
        self.contextTree = Tree(self.context)

    def setNewContext(self,newContext):
        self.context = newContext
        self.contextTree =Tree(self.context)

    def clearContext(self):
        context = {
            "entities": [],
            "intents": [],
            "dialogs": [],
            "messages": []
        }
        self.setNewContext(context)



    def updateDialog(self,message,type="input"):

        if type =="input":
            # for input
            dialogNumber = len(self.context["dialogs"]) + 1
            extractedEntities = self.entitiesHandler.extractAllEntities(message,dialogNumber=dialogNumber)
            extractedIntents  = [ intent for ihandler in self.intentHandlers for intent in ihandler.getMessageIntents(message=message,dialogNumber=dialogNumber) ]

            self.context["entities"].extend(extractedEntities)
            self.context["intents"].extend(extractedIntents)
            self.context["dialogs"].append(dialogNumber)
            messageJson={
                "text":message,
                "entitiesSub":self.entitiesHandler.substituteAllEntities(message),
                "messageType":type,
                "dialogNumber":dialogNumber,
                "sendTime":  datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")

            }
        else:
            # for output message
            dialogNumber = len(self.context["dialogs"])
            messageJson ={
                "text":message,
                "entitiesSub":message,
                "messageType":type,
                "dialogNumber":dialogNumber,
                "sendTime": datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")

            }

        self.context["messages"].append(messageJson)
        # update the tree
        self.contextTree =Tree(self.context)

    def findStuff(self,filter=None,stuff="intents"):
        matchedStuff=[]
        if filter:
            # $.intss[@.foo is 1][@.bar is b]
            query=["$.{0}".format(stuff)]
            for key in filter:
                if key != "confidence":
                    query.append("[@.{0} is {1}]".format(key,filter[key]))
                else:
                    query.append("[@.{0} > {1}]".format(key,filter[key]))

            query="".join(query)

            matchedStuff =list(self.contextTree.execute(query))
        return matchedStuff

    def findCurrentTopIntent(self):
        # Find current dialog number
        currentDialogNumber = self.context["dialogs"][-1]

        # Find
        #if confidenceLimit:
        topIntent= list(self.findStuff({"dialogNumber": currentDialogNumber, "rank": 1}, stuff="intents"))

        #print "topfound",topIntent
        if len(topIntent)>0:
            topIntent=topIntent[-1]
        else:
            topIntent={}

        return topIntent

    def findCurrentEntities(self):
        # Find current dialog number
        currentDialogNumber = self.context["dialogs"][-1]

        # Find current Entities
        currentEntities = list(self.findStuff({"dialogNumber": currentDialogNumber}, stuff="entities"))


        return currentEntities

    @staticmethod
    def findObjectInStuff(stuff,filter):

        allStuff={
            "allStuff":stuff,

        }
        stuffTree=Tree(allStuff)
        query=["$.allStuff"]
        for key in filter:
            query.append("[@.{0} is {1}]".format(key, filter[key]))

        query = "".join(query)
        return list(stuffTree.execute(query))



