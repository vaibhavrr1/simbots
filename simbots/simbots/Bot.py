from objectpath import Tree
import random
from .Context import ContextManager

class Bot():
    """
    Whenever a new bot is created it will inherit from the Bot class.

    """

    def __init__(self, intentExamples, entityExamples, templates, confidenceLimit=0):
        """

        :param intentExamples: The Intents need to be in a json format as accepted by IntentsHandler
        :param entityExamples: The Entities need to be in a json format as accepted by entities handler
        :param templates:  Bot output message templates
        :param confidenceLimit: Confidence limit for any intent to be accepted to generate a response
        """

        contextManager = ContextManager(allIntentExamples=intentExamples, entitiesExtractorJson=entityExamples)
        self.contextManager = contextManager
        self.templatesTree = Tree(templates)
        self.templates = templates
        self.confidenceLimit = confidenceLimit

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
        currentDialogNumber = self.contextManager.context["dialogs"][-1]
        return [(elem["name"], elem["confidence"]) for elem in
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


