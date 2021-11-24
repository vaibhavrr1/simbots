class EntitySamples():
    """
    Contains samples for frequently used entities

    """

    @staticmethod
    def greetingsHelper():
        """
        :return:

        {'wsup': [{'tag': 'case-insensitive',
                   'pattern': "\s[w]*[a]*[s]+[u]+[p]+\s",
                   'type': 'regex'}],
         'hi': [{'tag': 'case-insensitive',
                 'pattern': "\s[h]+[i]+\s", 'type': 'regex'}],
         'hello': [{'tag': 'case-insensitive',
                    'pattern': "\s[h]+[e]+[l]+[o]+\s",
                    'type': 'regex'}]}



        """
        return {'wsup': [{'tag': 'case-insensitive',
                   'pattern': "\s[w]*[a]*[s]+[u]+[p]+\s",
                   'type': 'regex'}],
         'hi': [{'tag': 'case-insensitive',
                 'pattern': "\s[h]+[i]+\s", 'type': 'regex'}],
         'hello': [{'tag': 'case-insensitive',
                    'pattern': "\s[h]+[e]+[l]+[o]+\s",
                    'type': 'regex'}]}

    @staticmethod
    def laughterHelper():
        """
        :return:

        {'haha': [{'tag': 'case-insensitive','pattern': "\s(h+(a|e)+)+(h+)?\s",'type': 'regex'}],'happysmily': [{'tag': 'case-insensitive','pattern': "\s\:\)\s", 'type': 'regex'}]}
        """

        return {'haha': [{'tag': 'case-insensitive',
                                 'pattern': "\s(h+(a|e)+)+(h+)?\s",
                                 'type': 'regex'}],
                       'happysmily': [{'tag': 'case-insensitive',
                                       'pattern': "\s\:\)\s", 'type': 'regex'}]}

    @staticmethod
    def coolHelper():
        """
        :return:

        {'cool': [{'tag': 'case-insensitive','pattern': "\sc+oo+l+\s", 'type': 'regex'}]}

        """
        return {'cool': [{'tag': 'case-insensitive','pattern': "\sc+oo+l+\s", 'type': 'regex'}]}

    @staticmethod
    def byeHelper():
        """
        :return:
        {'bye': [{'tag': 'case-insensitive','pattern': "\s(goo+d)?b+y+e+\s", 'type': 'regex'}]}

        """
        return {'bye': [{'tag': 'case-insensitive','pattern': "\s(goo+d)?(b+u+)?b+y+e+\s", 'type': 'regex'}]}