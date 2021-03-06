#from examples import entities as entitiesExtractorJson
import re
import json
from .utils.exceptions import SchemaException

class EntitiesHandler():
    """
    This class is responsible for handling entities within the bot
    The init method for the EntitiesHandler Class
        :param entitiesExtractorJson: this is a json which specifies the type of entities and their definitions . Note currently no schema checks have been implemented .

        **Sample Json accepted**

        .. code-block:: json

            {
                    "GreetingsHelper":{
                        "wsup" : [{
                                    "tag":"case-insensitive",
                                    "pattern":"\s[w]*[a]*[s]+[u]+[p]+\s",
                                    "type":"regex"
                        }
                                ],
                        "hi":[
                            {
                                "tag":"case-insensitive",
                                "pattern":"\s[h]+[i]+\s",
                                "type":"regex"


                            }

                        ],
                        "hello":[
                            {
                                "tag":"case-insensitive",
                                "pattern":"\s[h]+[e]+[l]+[o]+\s",
                                "type":"regex"


                            },
                            {
                               "tag":"case-insensitive",
                               "extractor":helloExtractorFunc ->
                               "type":"function"

                            }

                        ]


                    },

                    "LaughterHelper":{

                        "haha" : [{
                                    "tag":"case-insensitive",
                                    "pattern":"\s(h+(a|e)+)+(h+)?\s",
                                    "type":"regex"


                        }
                                ],
                        "happysmily":[
                            {
                                "tag":"case-insensitive",
                                "pattern":"\s\:\)\s",
                                "type":"regex"


                            }

                        ],

                    },
                    "CoolHelper":{
                        "cool":[
                            {
                                "tag":"case-insensitive",
                                "pattern":"\sc+oo+l+\s",
                                "type":"regex"

                            }


                        ]


                    },
                    "ByeHelper":{
                        "bye":[
                            {
                                "tag":"case-insensitive",
                                "pattern":"\s(goo+d)?b+y+e+\s",
                                "type":"regex"

                            }
                        ]

                    }

                }

        **kind** : Here GreetingsHelper,LaughterHelper,CoolHelper,ByeHelper are entity kinds.
        also "wsup","hi","hello" are entity values assosciated with the entity kind GreetingsHelper

        **type**: Only two types are supported -> regex and function.

        **pattern** : the pattern of the regex, only used if type is regex,

        **extractor**: A function that extracts the given entity from the message text should be present if type is function,

        Note that any function used should take in two arguments messageText and dialogNumber and should
        return A list of dicts of the format

        .. code-block:: json

            [{
                        "value":the value of the entity , for more details look at the sample json.,
                        "exactValue":the exact value that occurs within the message text.,
                        "kind":the kind of the entity eg  food in case of pizza.,
                        "dialogNumber":the dialog number of the current message -> same as the input param.,
                        "foundAt":[start location , end location],

            }]


        **substituter**: A custom substitution function to substitute entity by another value, This function takes in the message text and should
        return the substituted message text this should always be present if type is "function". should return substituted message text.


    """

    def __init__(self,entitiesExtractorJson=None):
        if not entitiesExtractorJson:
            entitiesExtractorJson={}
        else:
            # validate entity schema here
            if type(entitiesExtractorJson) != dict:
                # check if entity is dict
                raise SchemaException("Entities", "Entity samples",
                                      "Entities should be specified as a dict instead got  {0} .".format(type(entitiesExtractorJson)))

            for entityName in entitiesExtractorJson.keys():
                entityContent = entitiesExtractorJson[entityName]
                if type(entityContent) != dict:
                    raise SchemaException("Entity", entityName,
                                          "Entities should be specified as a dict instead got  {0} .".format(
                                              type(entityContent)))
                for entitySynonym in entityContent.keys():
                    synonymContent = entityContent[entitySynonym]
                    if type(synonymContent) != list:
                       raise SchemaException("Entity","{0} - {1}".format(entityName,entitySynonym),"Should be a list of dicts instead got {0} of {1}".format(synonymContent,type(synonymContent))

                                             )
                    for i,synonymDefinition in enumerate(synonymContent):
                        if type(synonymDefinition) != dict:
                            raise SchemaException("Entity","{0} - {1}- index {2}".format(entityName,entitySynonym,i),"Should be a dict got {0} of {1}".format(synonymDefinition,type(synonymDefinition))

                                             )
                        for key in synonymDefinition.keys():
                            if key == 'tag':
                                value = synonymDefinition[key]
                                if value not in ["case-insensitive","case-sensitive"]:
                                    raise SchemaException("Entity","{0} - {1}- index {2}".format(entityName,entitySynonym,i),"allowed 'tag' values in ['case-insensitive','case-sensitive'] got {0}".format(value))
                            if key == "type":
                                value = synonymDefinition[key]
                                if value not in ["regex", "function"]:
                                    raise SchemaException("Entity",
                                                          "{0} - {1}- index {2}".format(entityName, entitySynonym,
                                                                                         i),
                                                          "allowed 'type' values in ['regex', 'function'] got {0}".format(
                                                              value))
                            if key == "pattern":
                                value = synonymDefinition[key]
                                if type(value) != str:
                                    raise SchemaException("Entity",
                                                          "{0} - {1}- index {2}".format(entityName, entitySynonym,
                                                                                         i),
                                                          "pattern should be a regex got {0}".format(
                                                              type(value)))
                            if key =="extractor":
                                # work more on this
                                value = synonymDefinition[key]
                                if not callable(value):
                                    raise SchemaException("Entity",
                                                          "{0} - {1}- index {2}".format(entityName, entitySynonym,
                                                                                         i),
                                                          "extractor should be a function got {0}".format(
                                                              type(value)))
                                # write extractor text here

                            if "tag" not in synonymDefinition.keys():
                                raise SchemaException("Entity",
                                                      "{0} - {1}- index {2}".format(entityName, entitySynonym, i),
                                                      "should have  a key called 'tag' ")
                            if "type" not in synonymDefinition.keys():
                                raise SchemaException("Entity",
                                                      "{0} - {1}- index {2}".format(entityName, entitySynonym, i),
                                                      "should have  a key called 'type' ")

                            if ("tag" =='regex') and "pattern" not in synonymDefinition.keys():
                                raise SchemaException("Entity",
                                                      "{0} - {1}- index {2}".format(entityName, entitySynonym, i),
                                                      "if  'tag' =='regex' you must add a key called 'pattern' with a regex value  ")

                            if ("tag" =='function') and "extractor" not in synonymDefinition.keys():
                                raise SchemaException("Entity",
                                                      "{0} - {1}- index {2}".format(entityName, entitySynonym, i),
                                                      "if  'tag' =='function' you must add a key called 'extractor' with a function that extracts the entities and a key called 'substituter' which is a function that substitues the message entities for more details refer documentation -> EntitiesHandler")

                            if ("tag" =='function') and "substituter" not in synonymDefinition.keys():
                                raise SchemaException("Entity",
                                                      "{0} - {1}- index {2}".format(entityName, entitySynonym, i),
                                                      "if  'tag' =='function' you must add a key called 'extractor' with a function that extracts the entities and a key called 'substituter' which is a function that substitues the message entities for more details refer documentation -> EntitiesHandler")





        self.entitiesExtractorJson=entitiesExtractorJson


    def extractEntitySynonym(self,message,pattern,value,kind,tag,dialogNumber):
        """
            This function extracts the entities and synonyms from the text message and returns a json. Currently it does not extract any synonyms
                :param message: The text message str eg "I want to buy a pizza"
                :param pattern:
                :param value:
                :param kind:
                :param tag: can be "case-insensitive" if we want the extractor to ignore the casing (uppercase or lowercase) of the entity text
                :param dialogNumber: the dialog number of the message string.
                :return: A list of dicts of the format

                .. code-block:: json

                    [{
                                "value":the value of the entity , for more details look at the sample json.,
                                "exactValue":the exact value that occurs within the message text.,
                                "kind":the kind of the entity eg : food in case of pizza.,
                                "dialogNumber":the dialog number of the current message -> same as the input param.,
                                "foundAt":[start location , end location],

                    }]
        """


        entitiesFound=[]
        if "case-insensitive" in tag:
            iter=re.finditer(pattern=pattern,string= message,flags=re.I)
        else:
            iter = re.finditer(pattern=pattern, string=message)

        for entityDetected in iter:

            exactValue=message[entityDetected.start() : entityDetected.end()]
            entitiesFound.append(
                {
                    "value":value,
                    "exactValue":exactValue.strip(),
                    "kind":kind,
                    "dialogNumber":dialogNumber,
                    "foundAt":[entityDetected.start() , entityDetected.end()],
                    #"logic":synonymSpecs

                }
            )
        return entitiesFound


    def extractAllEntities(self,message,dialogNumber=0):
        """
        This function extracts all entities from the message .
            :param message: The message text
            :param dialogNumber:  the current dialog number
            :return: A list of dicts of the format

            .. code-block:: json

                [{
                            "value":the value of the entity , for more details look at the sample json.,
                            "exactValue":the exact value that occurs within the message text.,
                            "kind":the kind of the entity eg : food in case of pizza.,
                            "dialogNumber":the dialog number of the current message -> same as the input param.,
                            "foundAt":[start location , end location],

                }]
        """
        #message = " {0} ".format(message)
        allEntities=[]
        for entityKind in  self.entitiesExtractorJson.keys():
            for entityValue in self.entitiesExtractorJson[entityKind].keys():
                for synonymSpecs in self.entitiesExtractorJson[entityKind][entityValue]:
                    if synonymSpecs["type"] == "regex":
                        tag=synonymSpecs["tag"]
                        synonymPattern=synonymSpecs["pattern"]
                        entFound =  self.extractEntitySynonym(message,synonymPattern,entityValue,entityKind,tag,dialogNumber)
                    elif synonymSpecs["type"] == "function":
                        entFound = synonymSpecs["extractor"](message,dialogNumber)
                    else:
                        entFound =[]

                    allEntities.extend(entFound)


        return allEntities



    def substituteEntityKind(self,message,pattern,by,tag):
        """
        This function substitutes an entity value for its kind in the message text and returns the substituted message text .
        Note this function is currently unstable and a better version needs to be written to substitute entities effectively .
            :param message: The message text
            :param pattern: the entity pattern
            :param by:  the value to be substituted by eg if we need to substitute the word "equivalent" by "alike" then by ="alike"
            or if pizza then it will be kind
            :param tag:"case-insensitive" or not
            :return: the substituted message text
        """

        #message = " {0} ".format(message)
        if "case-insensitive" in tag:
            flags=re.I
        else:
            flags=None

        messageVar = re.sub( pattern , by, message,flags=flags)

        return messageVar

    def substituteAllEntities(self,message):
        """
        This function substitutes all entity values with entity kinds
            :param message:The message text
            :return: substituted message text
        """
        #message =" {0} ".format(message)
        for entityKind in  self.entitiesExtractorJson.keys():
            for entityValue in self.entitiesExtractorJson[entityKind].keys():
                for synonymSpecs in self.entitiesExtractorJson[entityKind][entityValue]:
                    if synonymSpecs["type"] == "regex":
                        tag=synonymSpecs["tag"]
                        synonymPattern=synonymSpecs["pattern"]
                        message = self.substituteEntityKind(message, synonymPattern, " --!{0} ".format(entityKind), tag)
                    elif synonymSpecs["type"] == "function":
                        message = synonymSpecs["substituter"](message)


        return message


















