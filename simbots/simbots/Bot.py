from objectpath import Tree
import random
from .Context import ContextManager
from .utils.exceptions import SchemaException,IndexingError
import os
import uuid
import json
import datetime
import pickle as p
import copy
import uuid

class Bot():

    """

    Whenever a new bot is created it will inherit from the Bot class.

    """

    def __init__(self, intentExamples, entityExamples, templates, confidenceLimit=0,testCases=None,subConversations=None):
        """

        :param intentExamples: The Intents need to be in a json format as accepted by IntentsHandler
        :param entityExamples: The Entities need to be in a json format as accepted by entities handler
        :param templates:  Bot output message templates
        :param confidenceLimit: Confidence limit for any intent to be accepted to generate a response
        :param subConversations: a list of SubConversationObjects which may be used to execute reason
        """

        self.intentExamples = intentExamples
        self.entityExamples = entityExamples
        self.contextManager = None
        self.updateIntentsAndEntitiesInContextManager()
        ## Exception handling for bot messages

        if type(templates) != dict:
            # check if entity is dict
            raise SchemaException("Templates", "Template samples","Templates should be specified as a dict instead got  {0} .".format(type(templates)))
        for themeName in templates.keys():
            themeContent = templates[themeName]
            if type(themeContent) != dict:
                raise SchemaException("Templates", themeName,"Templates should be specified as a dict instead got  {0} for theme {1}.".format(type(themeContent),themeName))
            for outputName in themeContent.keys():
                if "_" in outputName:
                    raise SchemaException("Templates",themeName+" : "+outputName," {0} should not contain '_' .".format(outputName))

                outputContent = themeContent[outputName]
                if type(outputContent) != dict:
                    raise SchemaException("Templates", themeName+" : "+outputName,
                                          "Expected format to be a dict instead got  {0} .".format(
                                              type(outputContent)))
                if "basic" not in outputContent.keys():
                    raise SchemaException("Templates", themeName + " : " + outputName,"Should have a 'basic' response defined i.e. key called 'basic' .")

                for key in outputContent.keys():
                    opContent = outputContent[key]
                    if type(opContent) != list:
                        raise SchemaException("Templates", themeName + " : " + outputName+ " : "+ key,
                                              "Expected type to be a list instead got {0}".format(type(opContent)))
                    for i,response in enumerate(opContent):
                        if type(response) !=str:
                            raise SchemaException("Templates", themeName + " : " + outputName + " : " + key + " index :" +str(i),
                                                  "Expected type to be a string instead got {0}".format(type(response)))

        self.templatesTree = Tree(templates)
        self.templates = templates
        self.confidenceLimit = confidenceLimit

        # Subconversation Management

        if subConversations is not None:
            self.subConversations = subConversations
        else:
            self.subConversations = []


        # Test Case Management

        self.testCases = testCases
        if not self.testCases :
            self.testCases  = dict()
        else:
            if type(self.testCases) != dict:
                raise SchemaException("Test Cases", "","Expected type to be a dict instead got {0}".format(type(self.testCases)))
            else:
                for testCaseName in self.testCases.keys():
                    testCaseContent = self.testCases[testCaseName]
                    if "conversation" not in testCaseContent.keys():
                        raise SchemaException("TestCases", testCaseName + " : " , "Each test case must have a 'conversation'" )
                    if "description" not in testCaseContent.keys():
                        raise SchemaException("TestCases", testCaseName + " : " , "Each test case must have a 'description'"  )
                    if type(testCaseContent["description"]) != str:
                        raise SchemaException("TestCases", testCaseName + " : " , "'description' must be of type string instead got {0}".format(type(testCaseContent["description"]))  )
                    if type(testCaseContent["conversation"]) != list:
                        raise SchemaException("TestCases", testCaseName + " : " , "'conversation' should be a list of lists [[str,str],[str,str]..] instead found {0}".format(type(testCaseContent["conversation"]) ) )
                    else:
                        for i,dialog in enumerate(testCaseContent["conversation"]) :
                            if type(dialog) !=list:
                                raise SchemaException("TestCases", testCaseName + " : dialog number {0}".format(i),
                                                      "'conversation' should be a list of lists [[str,str],[str,str]..] instead found {0}".format(
                                                          type(dialog)))
                            if len(dialog) != 2:
                                raise SchemaException("TestCases", testCaseName + " : dialog number {0}".format(i),
                                                      "'conversation' should be a list of lists [[str,str],[str,str]..] each dialog should be of length 2 as multiple outputs currently not supported in test cases instead found {0}".format(dialog))
                            for conv in dialog:
                                if type(conv) != str:
                                    raise SchemaException("TestCases", testCaseName + " : dialog number {0} ".format(i),
                                                    "'conversation' should be a list of lists [[str,str],[str,str]..] instead found {0}".format(
                                                        type(conv)))


    def updateIntentsAndEntitiesInContextManager(self):
        """

        Use this function when you need to retrain the bot with newly added intent and entity examples


        """
        oldContext = None
        if self.contextManager is not None:
            oldContext = self.contextManager.context

        self.contextManager = ContextManager(allIntentExamples=self.intentExamples, entitiesExtractorJson=self.entityExamples)

        if oldContext is not None:
            # if old context was present then update it
            self.contextManager.setNewContext(oldContext)

    def updateConversationInputs(self, message):
        """
        Update the conversation by updating the context with the input message
        :param message:
        :return:
        """
        self.contextManager.updateDialog(message)

    def updateConversationOutputs(self,message):
        """
        Update the conversation by updating the context with the output message
        :param message:
        :return:
        """
        self.contextManager.updateDialog(message,"output")

    def reason(self):
        """
        Bot reasoning is done here , use bot intents and entities to create message logic here

        :return:
        Should return a list of
        {
        "tag": Used to identify output message from the template
        "data": To be used to fill the missing attributes in message to generate the complete message
        }

        """

        ## find current dialogNumber

        currentDialogNumber = self.contextManager.context["dialogs"][-1]

        currentTopIntent = self.contextManager.findCurrentTopIntent()

        currentEntities = self.contextManager.findCurrentEntities()

        output = []

        if (currentTopIntent["confidence"] < self.confidenceLimit) or (currentTopIntent["name"] == "Irrelevant"):
            currentTopIntent = {}

        if currentTopIntent:
            ##
            ## Rule For All
            ##
            # if currentTopIntent["name"]=="Greetings":
            ##
            ## Person is greeting
            ##
            name = currentTopIntent["name"].split("_")[0]
            reply = {
                "tag": "{0}.basic".format(name),
                "data": None,
                # "message":""

            }
            output.append(reply)

        else:
            ##
            ##
            ## Rule for irrelevant
            ##
            ##
            irrelevant = {
                "tag": "Irrelevant.basic",
                "data": None

            }
            output.append(irrelevant)

        return output

    def say(self, output, outputTheme):
        """
        Generate bot output message by adding message to the output components
        :param output:
        :param outputTheme:
        :return: message as string
        """

        botSpeech = []

        for component in output:
            componentTag = component["tag"]
            query = "$.{0}.{1}".format(outputTheme, componentTag)
            queryResults = self.templatesTree.execute(query)
            message = random.choice(queryResults)
            data = component["data"]

            if data:
                if type(data) not in [list,tuple]:
                    data=[data]

                message = message.format(*data)
            botSpeech.append(message)

        return botSpeech

    def getBotContext(self):
        """
        Returns bot context
        :return: context as json
        """
        try:
            currentDialogNumber = self.contextManager.context["dialogs"][-1]
        except Exception as e:
            raise IndexingError(
                "The context stack is currently empty as there have been no conversations so cant access context")


        return self.contextManager.context

    def getBotConfidence(self):
        """
        Returns the bot confidence as list of tuples
        :return: [(intentName,intentConfidence) ..]
        """
        try:
            currentDialogNumber = self.contextManager.context["dialogs"][-1]
        except Exception as e:
            raise IndexingError(
                "The context stack is currently empty as there have been no conversations so cant access Intents")

        return [(elem["name"], elem["confidence"],elem["dialogNumber"]) for elem in
                self.contextManager.findStuff(_filter={"dialogNumber": currentDialogNumber}, stuff="intents")]


    def getBotOutput(self, message, outputTheme):
        """
        Get's bot output for a given message and output theme

        :param message: input message as string
        :param outputTheme: theme from botTemplates
        :return: message as string
        """
        # update the conversation with Inputs
        self.updateConversationInputs(message)

        # load previous subconversation status
        self.updateSubConversationStatus()

        # reason
        output = self.reason()

        # say
        messages = self.say(output, outputTheme)

        # update the conversation with Outputs
        for message in messages:
            self.updateConversationOutputs(message)

        # save the subconversation status to contextManager
        self.saveSubConversationStatus()

        return "\n".join(messages)

    def run(self,theme="basic",mode='dev',loadPath ="",conversationId="",message="",conversationSavePath=""):
        """
        Bot can run in two modes

        dev : cli to debug, train intents, evaluate test cases and more
        singleMessageResponse : to be used when deploying in production , gives output for a single message only
        loads in conversations from conversationSavePath and trained bot from loadpath

        :param theme: The theme name from bot responses
        :param mode: dev and singleMessageResponse
        :param loadPath: Loads trained intents ,entities and relations from .p file ie. file exported from saveBotMethod (only used in singleMessageResponse mode)
        :param conversationId: conversationId of the conversation to continue (only used in singleMessageResponse mode)
        :param message:  (only used in singleMessageResponse mode)
        :param conversationSavePath: looks for context at this path (only used in singleMessageResponse mode)
        :return: conversationId,outputMessage (only used in singleMessageResponse mode)
        no returns in dev mode
        """


        if mode =='dev':
            currentDialogNumber =1
            botFunctions = ['@@ to exit bot' ,'@i to get intents' , '@c to get context ','@e to get entities' ,'@t to add a test case', '@etc to evaluate a test case' , '@eatc to evaluate all test cases',"@ti to add intent"]
            print("Type in" ,"\n".join(botFunctions).strip())
            while True:
                inputMessage = input('<{0}> User : '.format(currentDialogNumber))
                if inputMessage == '@@':
                    break
                elif inputMessage == '@i':
                    print('Bot Intents: ')
                    print(json.dumps(self.getBotConfidence(), indent=2))
                elif inputMessage == '@c':
                    print('Bot Context: ')
                    print(json.dumps(self.getBotContext(), indent=2))
                elif inputMessage == '@e':
                    print('Bot Entities')
                    try:
                        currentDialogNumber = self.contextManager.context["dialogs"][-1]
                    except Exception as e:
                        raise IndexingError("The context stack is currently empty as there have been no conversations so cant access entities")
                    entities = list(self.contextManager.findStuff({"dialogNumber": currentDialogNumber}, stuff="entities"))
                    print(json.dumps(entities,indent=2))
                elif inputMessage =='@t':
                    print("Please Enter the starting dialog Number")
                    try:
                        currentDialogNumber = self.contextManager.context["dialogs"][-1]
                    except Exception as e:
                        raise IndexingError(
                            "The context stack is currently empty as there have been no conversations ")

                    startIndex = input("startIndex :")
                    try:
                        startIndex = int(startIndex)
                    except:
                        raise Exception("Starting index must be an integer")

                    if startIndex > currentDialogNumber:
                        raise Exception("Starting index must be less than the current dialog number {0}".format(currentDialogNumber))

                    endIndex = input("endIndex :")
                    try:
                        endIndex = int(endIndex)
                    except:
                        raise Exception("Ending index must be an integer")

                    if endIndex > currentDialogNumber:
                        raise Exception("Ending index must be less than equal to  the current dialog number {0}".format(
                            currentDialogNumber))

                    caseName        = input("Please enter the case name :  ")
                    caseDescription = input("Please enter the case description :  ")
                    self.addConversationAsTestCase(caseName,caseDescription,startIndex,endIndex)
                    print("test case added")
                    print(json.dumps(self.testCases[caseName],indent=2))
                elif inputMessage == '@etc':
                    print("Test Cases available are :")
                    self.listAllTestCases()
                    testCaseName = input("enter the test case name : ")
                    print(json.dumps(self.evaluateTestCase(testCaseName,theme),indent=2))

                elif inputMessage == '@eatc':
                    for testCaseName in self.testCases.keys():
                        print("Evaluating : ",testCaseName)
                        print(json.dumps(self.evaluateTestCase(testCaseName, theme), indent=2))

                elif inputMessage =='@ti':
                    print("Intents available are : {0}".format("\n".join(self.intentExamples.keys())))
                    intentName = input("Enter intent name to update : ")
                    dialogNumber = int(input("Enter the dialog number of the message to add to this intent :"))
                    messageExample = [el for el in self.contextManager.findStuff(_filter ={"dialogNumber":dialogNumber},stuff="messages") if el["messageType"] =='input']
                    if messageExample:
                        messageExample = messageExample[0]
                        messageText = messageExample["text"]
                        self.intentExamples[intentName].append(messageText)
                        print(intentName,"\n")
                        print(json.dumps(self.intentExamples[intentName],indent=2))
                        self.updateIntentsAndEntitiesInContextManager() # to make sure that the new examples are added and intents/entities trained
                    else:
                        print("sorry this intent was not found")

                else:
                    inputMessage = ' {0} '.format(inputMessage)
                    output = self.getBotOutput(inputMessage, theme)
                    currentDialogNumber = self.contextManager.context["dialogs"][-1]
                    print('<{2}> {0}Bot : {1}'.format(theme, output,currentDialogNumber))
                try:
                    currentDialogNumber = self.contextManager.context["dialogs"][-1] +1
                except:
                    raise IndexingError("The Context Stack is Empty, cant access Current Dialog number")

        elif mode =='singleMessageResponse':
            self.loadBot(loadPath)
            message = "  {0}  ".format(message.replace('"', ""))
            if len(conversationId) == 0:
                conversationId = str(uuid.uuid4())
                oldContext = {
                    "intents": [],
                    "dialogs": [],
                    "entities": [],
                    "messages": []
                }
            else:
                pathToOldContext = os.path.join(conversationSavePath, "{0}.json".format(conversationId))
                oldContext = json.load(open(pathToOldContext, 'r'))

            self.contextManager.setNewContext(oldContext)
            outputMessage = self.getBotOutput(message, outputTheme=theme)

            savePath = os.path.join(conversationSavePath, "{0}.json".format(conversationId))
            self.saveConversation(savePath, uid=conversationId)


            return conversationId,outputMessage

    ###
    ### Test Case manipulation Functions
    ###
    def addConversationAsTestCase(self,caseName,caseDescription,dialogStart,dialogEnd):
        """
        This function can be used to add a sample conversation in the dev mode as a test case

        :param caseName: The case name
        :param caseDescription: Case Description (string)
        :param dialogStart: The test case will start from this dialog number
        :param dialogEnd: The test case will end at this dialog number (the current dialog is included)

        """
        # Getting all input Output Messages in the given range
        ## work on this

        query = "$.messages[@.dialogNumber>= {0} and @.dialogNumber <={1}]".format(dialogStart,dialogEnd)
        foundMessages = list(self.contextManager.contextTree.execute(query))
        rge = dialogEnd- dialogStart+1
        inputs = ["" for i in range(rge)]
        outputs = ["" for i in range(rge)]
        for el in foundMessages:
            idx = el["dialogNumber"] - 1
            if el["messageType"] == "input":
                inputs[idx] = el["text"]
            else:
                outputs[idx] = el["text"]

        if caseName in self.testCases.keys():
            raise Exception("Test case already exists !")

        else:

            self.testCases[caseName] = {
                                                 "conversation" : [(inp,outp) for inp,outp in zip(inputs,outputs)],
                                                 "description" : caseDescription
                                        }

    def listTestCase(self,caseName):
        """
        print test case with the given case name
        :param caseName: Case Name as string

        """
        print(caseName,json.dumps(self.testCases[caseName],indent=2))

    def listAllTestCases(self):
        """
        print all test cases
        """
        for caseName in self.testCases.keys():
            self.listTestCase(caseName)

    def evaluateTestCase(self,caseName,outputTheme):
        """
        evaluate a particular testCase
        :param caseName:
        :param outputTheme: The bot template theme to use for getting the output message
        :return:
        .. code:: json

        { "caseName" : "test case name as string" ,
         "failedCases" : "failedCases as int",
         "result" : "testResults"
        }

        """
        try:
            testCase = self.testCases[caseName]["conversation"]
        except:
            raise Exception("Test case not present !")

        testResults = []

        # Keep the bot context

        botContext = self.contextManager.context
        self.contextManager.clearContext()
        failedCases = 0
        for i,dialogSet in enumerate(testCase):
            inp = dialogSet[0]
            expOutput = dialogSet[1]
            actualOutput = self.getBotOutput(' {0} '.format(inp.strip()),outputTheme)
            testResults.append({"input":inp,"expectedOutput":expOutput,"actualOutput":actualOutput,"testCasePassed":expOutput ==actualOutput})
            if expOutput !=actualOutput:
                failedCases+=1

        # Set the old context again

        self.contextManager.clearContext()
        self.contextManager.setNewContext(botContext)
        return { "caseName" : caseName,
                 "failedCases" : failedCases,
                 "result" : testResults
        }

    def evaluateAllTestCases(self,theme):
        return [ self.evaluateTestCase(caseName,outputTheme=theme) for caseName in self.testCases.keys()]

    ##
    ## Save Functions
    ##
    def saveConversation(self,savePath=None,uid=None):

        """

        Export the current conversation (context stack ) to a json file which can be loaded in later to 
        continue the conversation
        :param savePath: Path to save the conversation
        :param uid: Unique Conversation Id (str) , if not supplied will be randomly generated


        """

        if "conversationId" in  self.contextManager.context.keys():
            uid = self.contextManager.context["conversationId"]


        if uid is None:
            uid = str(uuid.uuid4())

        if savePath is None:
            savePath = os.path.join(os.getcwd(),uid)+ ".json"

        data = self.contextManager.context
        # add a conversation id
        data["conversationId"] = uid
        data["savedOn"] = datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
        with open(savePath, 'w') as f:
            json.dump(data, f)

    def loadConversation(self,loadPath):

        """

        Will load existing conversation from json file
        :param loadPath: Path to json file

        """

        if loadPath is None:
            raise Exception("Need a conversation path to continue conversation")

        """
        sampleSchema = {
            "entities": [
                {
                    "value": "hello",
                    "exactValue": "hello",
                    "kind": "GreetingsHelper",
                    "dialogNumber": 1,
                    "foundAt": [
                        0,
                        7
                    ]
                }
            ],
            "intents": [
                {
                    "name": "Greetings_multinomialNbClassifier",
                    "confidence": 0.9785951855997805,
                    "dialogNumber": 1,
                    "rank": 1
                },
                {
                    "name": "Discard_multinomialNbClassifier",
                    "confidence": 0.015567841820508193,
                    "dialogNumber": 1,
                    "rank": 2
                },
                {
                    "name": "TrueT_multinomialNbClassifier",
                    "confidence": 0.01445546862595722,
                    "dialogNumber": 1,
                    "rank": 3
                },
                {
                    "name": "Confirm_multinomialNbClassifier",
                    "confidence": 0.014448303837935042,
                    "dialogNumber": 1,
                    "rank": 4
                },
                {
                    "name": "Cool_multinomialNbClassifier",
                    "confidence": 0.014448303837935042,
                    "dialogNumber": 1,
                    "rank": 5
                },
                {
                    "name": "Praise_multinomialNbClassifier",
                    "confidence": 0.013845046453123561,
                    "dialogNumber": 1,
                    "rank": 6
                },
                {
                    "name": "Thanks_multinomialNbClassifier",
                    "confidence": 0.013770075280207107,
                    "dialogNumber": 1,
                    "rank": 7
                },
                {
                    "name": "Abilities_multinomialNbClassifier",
                    "confidence": 0.013701582658465347,
                    "dialogNumber": 1,
                    "rank": 8
                },
                {
                    "name": "Laughter_multinomialNbClassifier",
                    "confidence": 0.013628431503934236,
                    "dialogNumber": 1,
                    "rank": 9
                },
                {
                    "name": "Joke_multinomialNbClassifier",
                    "confidence": 0.011813837920381681,
                    "dialogNumber": 1,
                    "rank": 10
                },
                {
                    "name": "Bye_multinomialNbClassifier",
                    "confidence": 0.011493728976210753,
                    "dialogNumber": 1,
                    "rank": 11
                },
                {
                    "name": "BirthPlace_multinomialNbClassifier",
                    "confidence": 0.011393391629187717,
                    "dialogNumber": 1,
                    "rank": 12
                },
                {
                    "name": "FalseT_multinomialNbClassifier",
                    "confidence": 0.011336732508689811,
                    "dialogNumber": 1,
                    "rank": 13
                },
                {
                    "name": "BotName_multinomialNbClassifier",
                    "confidence": 0.011305148152011418,
                    "dialogNumber": 1,
                    "rank": 14
                },
                {
                    "name": "Age_multinomialNbClassifier",
                    "confidence": 0.011028462608017221,
                    "dialogNumber": 1,
                    "rank": 15
                },
                {
                    "name": "Really_multinomialNbClassifier",
                    "confidence": 0.010358881454672588,
                    "dialogNumber": 1,
                    "rank": 16
                },
                {
                    "name": "Relatives_multinomialNbClassifier",
                    "confidence": 0.009544602509691033,
                    "dialogNumber": 1,
                    "rank": 17
                },
                {
                    "name": "Irrelevant_multinomialNbClassifier",
                    "confidence": 0.007362855137962881,
                    "dialogNumber": 1,
                    "rank": 18
                }
            ],
            "dialogs": [
                1
            ],
            "messages": [
                {
                    "text": " hello ",
                    "entitiesSub": " --!GreetingsHelper ",
                    "messageType": "input",
                    "dialogNumber": 1,
                    "sendTime": "03/12/2021, 10:02:41"
                },
                {
                    "text": "Hello",
                    "entitiesSub": "Hello",
                    "messageType": "output",
                    "dialogNumber": 1,
                    "sendTime": "03/12/2021, 10:02:41"
                }
            ],
            "conversationId": "a123-arfgt-345t-5677"
        }

        print(
            "Ensure that schema follows valid format otherwise it may introduce errors later . It must contain 'entities','intents','dialogs','messages','conversationId' , extra stuff is allowed ")
        print("Sample Schema \n\n", json.dumps(sampleSchema))
        """
        ##
        ## Add schema validation for context
        ##
        with open(loadPath, 'r') as f:
            context = json.load(f)

        self.contextManager.setNewContext(context)

    def saveBot(self,savePath):
        """

        Saves the trained bot to a pickle file , note that the context stack is not saved
        :param savePath: path to a pickle file for saving the bot contents

        """
        contextManager = copy.deepcopy(self.contextManager)
        templates = self.templates
        confidenceLimit = self.confidenceLimit

        contextManager.context = {
            "entities": [],
            "intents": [],
            "dialogs": [],
            "messages": []
        }
        contextManager.contextTree = None # Tree(contextManager.context)

        testCases = self.testCases

        data = {
            "contextManager": contextManager,
            "templates": templates,
            "confidenceLimit": confidenceLimit,
            "testCases":testCases,
            "intentExamples" :self.intentExamples,
            "entityExamples": self.entityExamples,
            "savedOn" : datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")

        }

        p.dump(data, open(savePath, "wb"))

    def loadBot(self,loadPath):
        """

        Loads trained bot from the path specified, note that context stack (conversation) is not loaded
        :param loadPath: path to a pickle file for loading the bot

        """
        data = p.load(open(loadPath, "rb"))
        self.contextManager = data["contextManager"]
        self.contextManager.contextTree = Tree(self.contextManager.context)
        self.templates = data["templates"]
        self.confidenceLimit = data["confidenceLimit"]
        self.templatesTree = Tree(data["templates"])
        self.testCases   = data["testCases"]
        self.intentExamples = data["intentExamples"]
        self.entityExamples = data["entityExamples"]

    ##
    ## SubConversation Functions
    ##

    def findCurrentlyHappeningSubconversation(self):

        """

        First checks if any subConversation is happening or not : returns first found , then checks if the enterOn condition
        of any subConversation is completed or not , returns first found
        :return: [index of the subconversation,subconversationId of the subconversation which matches the above criteria

        """

        # check if any sub conversation is already happening
        for i, subConv in enumerate(self.subConversations):
            if subConv.isHappening:
                return [i, subConv.subConversationId]

        # check if any sub conversation should now happen
        contextManagerCopy = copy.deepcopy(self.contextManager)
        for i, subConv in enumerate(self.subConversations):
            if subConv.enterOn(contextManagerCopy):
                return [i, subConv.subConversationId]

        return [None, None]

    def executeCurrentSubConversation(self, outputs=None):
        """
        Find which conversation has isHappenning set to true  and executes first found in subconversations
        :param outputs: outputs that were previously computed
        :return: outputs modified (contains outputs of the executed subConversation (as list))
        """
        if outputs is None:
            outputs = []

        convIndex, convId = self.findCurrentlyHappeningSubconversation()

        if convIndex is not None:
            # Overwrite the existing context manager
            self.contextManager, outputs =  self.subConversations[convIndex].execute(self.contextManager, outputs)


        return outputs

    def saveSubConversationStatus(self):
        """

        Save SubConversationStatus (isHappenning True or False) as a dict in the context manager

        """
        subConversationStatus = {}

        for subConversation in self.subConversations:
            subConversationStatus[subConversation.subConversationId] =  subConversation.isHappening

        self.contextManager.context["subConversationStatus"] = subConversationStatus
        self.contextManager.updateContextTree()

    def updateSubConversationStatus(self):
        if "subConversationStatus" in self.contextManager.context.keys():
            for i in range(len(self.subConversations)):
                self.subConversations[i].isHappening = self.contextManager.context["subConversationStatus"][self.subConversations[i].subConversationId]


class SubConversation():
    """
    Subconversations can be used to divide bot logic into multiple small parts

    """

    def __init__(self, name=str(uuid.uuid4()), subConversationId=str(uuid.uuid4()), enter=None, exit=None,
                 onEnterLogic=None, onExitLogic=None):

        self.name = name

        self.isHappening = False

        self.subConversationId = subConversationId

        if enter is not None:

            self.enter = enter

        else:

            self.enter = lambda x: False

        if exit is not None:

            self.exit = exit

        else:

            self.exit = lambda x: False

        if onEnterLogic is not None:

            self.onEnterLogic = onEnterLogic

        else:

            self.onEnterLogic = lambda x, y: (False, x, y)

        if onExitLogic is not None:

            self.onExitLogic = onExitLogic

        else:

            self.onExitLogic = lambda x, y: (x, y)

    def enterOn(self, contextManager):
        """
        Enter this SubConversation when condition is fulfilled
        :param contextManager: contextManager object , use this to construct a bool
        :return: bool that indicates if to enter this SubConversation or not

        """

        self.isHappening = self.enter(contextManager)

        return self.isHappening

    def exitOn(self, contextManager):
        """
        Make a hard exit from this Subconversation when given condition is satisfied

        :param contextManager:  contextManager object , use this to construct a bool
        :return: bool that indicates if to make a hard exit or not

        """

        self.isHappening = self.exit(contextManager)

        return self.isHappening

    def execute(self, contextManager, outputs):
        """
        Checks the enterOn and exitOn condition and executes the
        :param contextManager:
        :param outputs: creates outputs of the SubConversation using contextManager
        :return: modified contextManager , outputs

        """

        if self.exitOn(contextManager):
            # hard exit the bot if exit on condition is fulfilled
            self.isHappening = False

            contextManger, outputs = self.onExitLogic(contextManager, outputs)

            return contextManager, outputs
        else:

            remainInSubConversation, contextManager, outputs = self.onEnterLogic(contextManager, outputs)

            self.isHappening = remainInSubConversation

            return contextManager, outputs
