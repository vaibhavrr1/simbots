class SchemaException(Exception):
    """
    Exception raised for errors in schema.

    """

    def __init__(self, type=None,name=None, message=None):

        self.message = "\n\n Error encountered in {0} : {1} \n Detail : {2}".format(type,name,message)
        super().__init__(self.message)




