"""Something."""


class Export_document_result(object):

    def __init__(self):
        self.document = None
        self.is_success = False
        self.message = None

    def setSucess(self, document, mess):
        self.is_success = True
        self.message = mess
        self.document = document

    def setFailure(self, document, err):
        self.is_success = False
        self.message = err
        self.document = document


class Export_result(object):
    def __init__(self, profile):
        self.profile = profile
        self.is_success = True
        self.message = None
        self.docResult = []

    def setFailure(self, message):
        self.is_success = False
        self.message = message

    def addResultDoc(self, edr):
        if not edr.is_success:
            self.is_success = False
            self.message = "At least document has fail."
        self.docResult.append(edr)
