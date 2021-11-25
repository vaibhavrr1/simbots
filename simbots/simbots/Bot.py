from objectpath import Tree
import json
import random
from .Context import ContextManager
from .utils.exceptions import SchemaException,IndexingError
class Bot():
    """
    Whenever a new bot is created it will inherit from the Bot class.

    """

    def __init__(self, intentExamples, entityExamples, templates, confidenceLimit=0,testCases=None):
        """

        :param intentExamples: The Intents need to be in a json format as accepted by IntentsHandler
        :param entityExamples: The Entities need to be in a json format as accepted by entities handler
        :param templates:  Bot output message templates
        :param confidenceLimit: Confidence limit for any intent to be accepted to generate a response
        """

        contextManager = ContextManager(allIntentExamples=intentExamples, entitiesExtractorJson=entityExamples)
        self.contextManager = contextManager
        ## Exception handling for bot messages

        if type(templates) != dict:
            # check if entity is dict
            raise SchemaException("Templates", "Template samples","Templates should be specified as a dict instead got  {0} .".format(type(templates)))
        for themeName in templates.keys():
            themeContent = templates[themeName]
            if type(themeContent) != dict:
                raise SchemaException("Templates", themeName,"Templates should be specified as a dict instead got  {0} for theme {1}.".format(type(themeContent),themeName))
            for outputName in themeContent.keys():
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
        if not testCases:
            self.testCases  =[]

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
        :return:
        """

        botSpeech = []

        for component in output:
            componentTag = component["tag"]
            query = "$.{0}.{1}".format(outputTheme, componentTag)
            queryResults = self.templatesTree.execute(query)
            message = random.choice(queryResults)
            data = component["data"]
            if data:
                message = message.format(data)


            botSpeech.append(message)



        return botSpeech

    def getBotContext(self):
        """
        Returns bot context
        :return: context as json
        """
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
                self.contextManager.findStuff(filter={"dialogNumber": currentDialogNumber}, stuff="intents")]


    def getBotOutput(self, message, outputTheme):
        # update the conversation with Inputs
        self.updateConversationInputs(message)

        # reason
        output = self.reason()

        # say
        messages = self.say(output, outputTheme)

        # update the conversation with Outputs
        for message in messages:
            self.updateConversationOutputs(message)



        return "\n".join(messages)

    def run(self,theme="basic",mode='dev'):
        """

        :param theme: The theme name from bot responses
        :param mode: The mode in which bot is to run , currently only 'dev' mode is supported

        """
        if mode =='dev':
            print('Type @@ to exit bot ,@i to get intents , @c to get context ,@e to get entities')
            while True:
                inputMessage = input('User : ')
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

                else:
                    inputMessage = ' {0} '.format(inputMessage)
                    output = self.getBotOutput(inputMessage, theme)
                    print('{0}Bot : {1}'.format(theme, output))
        else:
            return "only dev mode is supported to run bot as of now . To get bot response use bot.getBotOutput(userMessage,theme)"

    def addConversationAsTestCase(self,caseName,dialogStart,dialogEnd):
        """
        This function can be used to add a sample conversation in the dev mode as a test case

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

        self.testCases.append([{ caseName : [(inp,outp) for inp,outp in zip(inputs,outputs)] }])




