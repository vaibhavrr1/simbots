from .Intent import IntentsHandler
from .Entity import EntitiesHandler
from objectpath import Tree
import datetime

class ContextManager():
    """

    Context handler class, This maintains context as a dict and also as a Object Path tree, to facilitate searching within the context
    also provides functions to search within the context object. Context manager also manages and handles subconversations .

    """

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
        """
        Deletes the old context and sets a new one .
        :param newContext: the new context object as json

        """
        self.context = newContext
        self.updateContextTree()

    def clearContext(self):
        """
        Clears context
        """
        context = {
            "entities": [],
            "intents": [],
            "dialogs": [],
            "messages": []
        }
        self.setNewContext(context)

    def updateDialog(self,message,type="input"):
        """
        Updates the context by
        1) Computing all entities present in the message
        2) Extracting all intents in the message
        3) Updating the current dialog number
        4) Updating messages in the context


        :param message: Message text
        :param type: message type : "input" or "output"

        """

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

    def findStuff(self,_filter=None,stuff="intents"):
        """
        Basic method to search a particular part of the context ie Intent, Entities, Message
        :param filter: dict of terms to search
        :param stuff: part of context that needs to be searched ie Intent, Entities, Message
        :return: matched values as list
        """
        matchedStuff=[]
        if _filter:
            # $.intss[@.foo is 1][@.bar is b]
            query=["$.{0}".format(stuff)]
            for key in _filter:
                if key != "confidence":
                    query.append("[@.{0} is {1}]".format(key,_filter[key]))
                else:
                    query.append("[@.{0} > {1}]".format(key,_filter[key]))

            query="".join(query)

            matchedStuff =list(self.contextTree.execute(query))
        return matchedStuff

    def findCurrentTopIntent(self):
        """
        Find the the top intent in the current message
        :return: topIntent: the Top intent ie intent with rank 1
        """
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
        """
        Find the entities detected in the current message
        :return: currentEntities : the entities detected in the current message as list
        """
        # Find current dialog number
        currentDialogNumber = self.context["dialogs"][-1]

        # Find current Entities
        currentEntities = list(self.findStuff({"dialogNumber": currentDialogNumber}, stuff="entities"))


        return currentEntities

    @staticmethod
    def findObjectInStuff(stuff,_filter):
        """
        Generalised method to search within any given dictionary using objectPath library
        :param stuff: the dictionary where the object is to be searched
        :param filter: the filter
        :return: list of matched objects
        """

        allStuff={
            "allStuff":stuff,

        }
        stuffTree=Tree(allStuff)
        query=["$.allStuff"]
        for key in _filter:
            query.append("[@.{0} is {1}]".format(key, _filter[key]))

        query = "".join(query)
        return list(stuffTree.execute(query))

    def updateContextTree(self):
        """
        Updates the contextTree with the current context  so that everything in the context is searchable,
        this becomes useful when saving custom variables in context .

        """
        self.contextTree = Tree(self.context)





