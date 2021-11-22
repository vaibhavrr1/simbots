from objectpath import Tree
import random
from .Context import ContextManager

class Bot():
    """
    Whenever a new bot is created it will inherit from the Bot class. Always overwrite the reason method with your own
    bot logic

    """

    def __init__(self, intentExamples, entityExamples, templates, confidenceLimit=0):
        """

        :param intentExamples: The Intents need to be in a json format as accepted by IntentsHandler
        :param entityExamples:
        :param templates:
        :param confidenceLimit:
        """

        contextManager = ContextManager(allIntentExamples=intentExamples, entitiesExtractorJson=entityExamples)
        self.contextManager = contextManager
        self.templatesTree = Tree(templates)
        self.templates = templates
        self.confidenceLimit = confidenceLimit

    def updateConversation(self, message):
        self.contextManager.updateDialog(message)

    def reason(self):

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
        return self.contextManager.context

    def getBotConfidence(self):
        currentDialogNumber = self.contextManager.context["dialogs"][-1]
        return [(elem["name"], elem["confidence"]) for elem in
                self.contextManager.findStuff(filter={"dialogNumber": currentDialogNumber}, stuff="intents")]

    def getBotOutput(self, message, outputTheme):
        # update the conversation
        self.updateConversation(message)

        # reason
        output = self.reason()

        # say
        messages = self.say(output, outputTheme)

        return "\n".join(messages)


