"""Classes that contains export results."""

import json


class Export_document_result(object):
    """Contains export result for a document."""

    def __init__(self):
        """Init."""
        self.document = None
        self.is_success = False
        self.message = None

    def setSucess(self, document, mess):
        """Set the export to failed for the given document."""
        self.is_success = True
        self.message = mess
        self.document = document

    def setFailure(self, document, err):
        """Set the export to succes for the given document."""
        self.is_success = False
        self.message = err
        self.document = document


class Export_result(object):
    """Contains export result for a profile."""

    def __init__(self, profile):
        """Init."""
        self.profile = profile
        # if false, an error occurs for one document or on the profile itself
        # (for example cannot get documents url)
        self.is_success = True
        self.message = None
        # export result for documents
        self.docResult = []

    def setFailure(self, message):
        """Set profile status to failure."""
        self.is_success = False
        self.message = message

    def addResultDoc(self, edr):
        """Add a document result."""
        if not edr.is_success:
            self.is_success = False
            self.message = "At least document has fail."
        self.docResult.append(edr)

    def to_json(self):
        """Return a json representation of object."""
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
