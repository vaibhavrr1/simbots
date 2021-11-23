
class IntentSamples():
    """
    Contains samples for frequently used intents, which can be used to train intents .Each method returns a list of samples

    """
    def __init__(self):
        pass

    @staticmethod
    def greetingSamples():
        """
        :return: list of samples like  'Hello !', 'Hi , How are you ?',
        """
        return [
        'Hello !',
        'Hi , How are you ?',
        'Hey !! ',
        'Namaste ',
        'Good day',
        'Good evening',
        'Good morning',
        'Good to see you',
        'Greetings',
        'Have you been well?',
        'Hello Agent',
        'Hello',
        'Hey how are you doing',
        'Hey there all',
        'Hey there',
        'Hey twin',
        'Hey you',
        'Hi advisor',
        'Hi there',
        'How are things going?',
        'How are you today?',
        'How have you been?',
        'How is it going?',
        'How r u?',
        'Looking good eve',
        "What's new?",
        "What's up?",
        'You there',
        'Namaste',
        'satsriyakaal',
        'helo',
        'hiiiiiii',
        ' sup ',
        ' wassup bruh ',
        ' sup bro ',
        ' ssssup mate whats up',
            "hi",
            "hey"
    ]
    @staticmethod
    def botNameSamples():
        """
        :return:  list of samples like  'Who is this?', 'Hi' ,'Who are you',
        """
        return [
        'Who is this?',
        'Who are you',
        'Who are you ?',
        'What is your Name ?',
        'What is your name ',
        'what should i call you ?',
        'What should i call you',
        'How to address you ?',
        'how  to address you by name',
        'what is your name ',
        'call you',
        'your name',
        'call you ?',
        'your name ?',
        'whom are you',
        'whom are you referred as',
    ]

    @staticmethod
    def relativeSamples():
        """

        :return:  list of samples like  'Do you have any relatives ' , "do you have any siblings ?"
        """
        return [
        'Do you have any relatives ',
        'Do you have a sibling ',
        'Any brother or sister',
        'Do you have a father',
        'Do you happen to have a grandparent ?',
        'Any grandparents or parents ',
        'do you have Any wife ?',
        'Are you married ?',
    ]

    @staticmethod
    def ageSamples():
        """
        :return:  list of samples like  'what is your age' , "how old are you ?"

        """
        return [
            'What is your age',
            'your age ?',
            'how old are you ?'
            'when were you born',
            'your year of birth',
            'year of birth',
            'when were you born again',
            'born ?',
            'born again ?',
            "how long have you lived ?"

        ]

    @staticmethod
    def birthPlaceSamples():
        """

        :return:  list of samples like  'where were you born ' , "where are you from ?"
        """
        return [
        'where were you born ?',
        'where are you from',
        'where in the world are you from ?',
        'where do you belong to',
        'you are from ',
        'are you from ',
        'you belong to ',
        'place of birth',
        'and you are from ?',
        'and your birthplace is from ?and you are from ?',
        'birthplace',
        'place of birth',
        'location of birth',
        'place of residence',
        'location',
        'your address',
        'where do you reside ?',
        'place of residence ?',
    ]

    @staticmethod
    def abilitiesSamples():
        """

        :return:  list of samples like  'what can you do ? ' , "what are your capabilities ?"
        """
        return [
        'What can you do ?',
        'What are your abilities ',
        'your abilities',
        'your capabilities',
        'what are your capabilities',
        'ability',
        'your ability',
        'capability',
        'your capability',
        'your abilities',
        'your powers',
        'what are your superpowers',
        'superpowers',
        'you are capable of ',
        'what are you capable of',
        'what can you do ?',
        'what can you do ?',
        'Can you jump ?',
        'can you shit ?',
        'could you do this ?',
        'could you please do this ?',
    ]
    @staticmethod
    def reallySamples():
        """

        :return:  list of samples like  'is that so ? ' , "really ?"
        """
        return [
            'really',
            'is that so ?',
            'is that what you believe',
            'are you sure',
            'is that what you belief',
            'you positive about that',
            'are you positively sure',
            'is that what you think',
            'are you positive about that ?',
            'you positive',
            'are you really sure',
            'really bro ?',
            "ya sure ?"
        ]

    @staticmethod
    def laughterSamples():
        """

        :return:  list of samples like  'hahaha' , "thats very funny"
        """
        return [
        'i think thats funny ',
        'thats very funny ,hahaha',
        'i think that hahahaha',
        'thats very funny',
        'laughter',
        ':)',
        'thats really funny ',
        'I think thats hilarious',
        'thats so funny !',
        'that really made me laugh !',
        "you are so funny :)"
    ]


    @staticmethod
    def coolSamples():
        """

        :return:  list of samples like  "thats cool !","cool"
        """
        return [
        'thats cool',
        'cool',
        'that is really cool',
        'very cool',
        'totally cool !',
        'Awesome !',
        'Very cool',
        'Pretty cool',
        'surely very cool',
        'nice',
        'neat',
        'thats neat',
        'thats pretty neat',
        'thats nice',
    ]

    @staticmethod
    def praiseSamples():
        """

        :return:  list of samples like  'you are awesome ' , "thats incredible !"
        """
        return [
        'I think that you are absolutely amazing  !',
        'I really think you are amazing',
        'You are absolutely fantastic',
        'Thats Incredible',
        'How Extraordinary !',
        'Far Out ! ',
        'Great ! ',
        'Outstanding',
        'Performance',
        'Marvelous',
        'I Cant Get Over It !',
        'Wonderful ! ',
        'Amazing Effort !',
        'Unbelievable Work',
        'You Should Be Proud',
        'Phenomenal ! ',
        'Youve Got It',
        'Superb ! ',
        'Youre Special',
        'Excellent ! ',
        'Cool ! ',
        'Your Project Is First Rate !',
        'Way to Go ! ',
        'Youve Outdone',
        'Yourself',
        'Thumbs Up',
        'What A Great',
        'Listener',
        'Your Help Counts ! ',
        'You Came Through ! ',
        'Terrific',
        'You Tried Hard',
        'Youre OK',
        'Fabulous',
        'You Made It',
        'Happen',
        'Youre a Real',
        'Trooper',
        'It Couldnt Be',
        'Better',
        'The Time You Put in Shows',
        'Bravo ! ',
        'Youre Unique',
        'Exceptional',
        'Fantastic Work',
        'Breathtaking ! ',
        'Youre a Great',
        'Example For Others',
        'Keep Up the Good',
        'Work',
        'Awesome  !',
        'I Knew You Had It In You',
        'Youve Made',
        'Progress',
        'Your Work Is Out of Sight',
        'What an Imagination  ! ',
        'Its Everything I Hoped For',
        'Stupendous',
        'Youre Sensational',
        'Very Good !',
    ]

    @staticmethod
    def trueSamples():
        """

        :return:  list of samples like  'thats true' , "thats evident"
        """
        return [
        'Thats True',
        'thats self evident',
        'thats evident',
        'thats truly evident',
        'true that',
        'true as it comes',
        'thats completely true',
        'true as it comes',
        'thats correct',
        'absolutely correct',
    ]

    @staticmethod
    def falseSamples():
        """

        :return:  list of samples like  'thats false ' , "you are wrong "
        """
        return [
        'thats false',
        'you are wrong',
        'completely wrong',
        'absolutely and utterly wrong',
        'I dont believe that',
        'i think thats not correct ',
        'thats absolutely not correct',
    ]

    @staticmethod
    def byeSamples():
        """

        :return:  list of samples like  'bye ' , "goodbye"
        """
        return [
        'good bye',
        'bye bye',
        'buh bye',
        'see you later',
        'byee',
        'se ya later aligator',
        'I gotta go',
        'I have someplace else i need to be',
        'I Need to be someplace else',
        'We can talk later',
        'Will chat later',
        'We can chat later',
        'Will be chatting later',
        'goodbye',
    ]

    @staticmethod
    def confirmSamples():
        """

        :return:  list of samples like  'confirm that' , "yes","do that please"
        """
        return [
            'Yes ',
            'Okay',
            'Please do that',
            'Okay go ahead',
            'You do that',
            'Wrap it up',
            'I confirm',
            'Please do',
            'Sure go ahead',
            'Sure',
            'ok',
            'ok',
            'yep',
            'yep yep do that ',
        ]

    @staticmethod
    def thanksSamples():
        """
        :return:  list of samples like  "Thanks"," Thank you"
        """
        return ['Thank you', 'Thanks', 'Thank you so very much !'," my thanks !"]
    @staticmethod
    def discardSamples():
        """

        :return:  list of samples like  'No","cancel that "
        """

        return [
            'No',
            'No , i dont wanna do that',
            'Nope change that',
            ' negative ',
            'No no',
            'I said no',
            'Never',
            'Cancel that',
            'Build a new one',
        ]

    @staticmethod
    def jokeSamples():
        """

        :return:  list of samples like  "can you tell me a joke","tell a joke"
        """
        return [
        'Can you tell a joke ?',
        'Tell a joke !',
        'Tell me another joke !',
        'I want to smile ',
        'can you make me smile',
        'could you tell me a joke ?',
        'make me laugh',
        'I want some laughter',
        'make some laughter',
        'give me some jokes ',
    ]

