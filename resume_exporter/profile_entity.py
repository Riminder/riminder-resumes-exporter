"""Class that contain useful profile datas."""

import riminder

from resume_exporter import api_utils


class ProfileDocument(object):
    """Contains data for a profile document."""

    def __init__(self, name, url=None, data=None):
        """Init."""
        self.file_name = name
        self.url = url
        self.data = data
        self.export_path = None


class Profile_entity(object):
    """Contains profile datas."""

    def __init__(self, profile_id, source_id, source_name):
        """Init."""
        self.id = profile_id
        self.source_id = source_id
        self.source_name = source_name
        self.documents = []

    def fill_documents_from_api(self, api: riminder.Riminder):
        """Get document files data from api."""
        # It gets the name and the url.
        resp, err = api_utils.exec_api_call(lambda: api.profile.document.list(source_id=self.source_id, profile_id=self.id))
        if err is not None:
            err = "Cannot get document: {}".format(err)
            return err
        for doc in resp:
            d = ProfileDocument(self.id + "_" + doc['type'] + "." + doc['extension'], url=doc['url'])
            self.documents.append(d)
        # Also for parsing json
        resp, err = api_utils.exec_api_call(lambda: api.profile.parsing.get(source_id=self.source_id, profile_id=self.id))
        if err is not None:
            err = "Cannot get parsing data: {}".format(err)
            return err
        d = ProfileDocument(self.id + '.json', data=resp)
        self.documents.append(d)
        return None
