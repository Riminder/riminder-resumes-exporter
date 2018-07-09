"""Something."""

import json


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

    def to_json(self):
        data = {
            "no_error": self.is_success,
            "message": self.message,
            "profile_id": self.profile.id,
            "source": {
                "id": self.profile.source_id,
                "name": self.profile.source_name
            },
            "documents": []
        }
        for doc_res in self.docResult:
            doc_data = {
                "name": doc_res.document.file_name,
                "url": doc_res.document.url,
                "path": doc_res.document.export_path,
                "success": doc_res.is_success,
                "message": doc_res.message
            }
            data['documents'].append(doc_data)
        return json.dumps(data)
