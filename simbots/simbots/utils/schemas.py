
class Definitions():

    def __init__(self):
        pass

    @staticmethod
    def emptyContext():
        return  {
            "entities": [],
            "intents": [],
            "dialogs": [],
            "messages": [],
            "relations": []
        }

    @staticmethod
    def emptyRelation():
        return {}