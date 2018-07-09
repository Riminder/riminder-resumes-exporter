"""Upload worker file."""

import threading
import urllib
import os

from resume_exporter import export_result


class Export_worker(threading.Thread):
    """Worker for that manage upload."""

    def __init__(self, worker_id, api, export_target):
        """Init."""
        threading.Thread.__init__(self)
        self.profile_to_process = None
        self.callback = None
        self.api = api
        self.worker_id = worker_id
        self.export_target = export_target

    def set_profile(self, profile, cb):
        """Add a file for next upload."""
        self.profile_to_process = profile
        self.callback = cb

    def process_file(self):
        """Upload file and notify supervisor."""
        res = self._export_profile()
        self.profile_to_process = None
        self.callback(self.worker_id, res)

    def run(self):
        """Upload file until no new file is placed by callback."""
        while self.profile_to_process is not None:
            self.process_file()

    def _generate_export_path(self, document):
        # $taget_path/$source_name_$source_id/$profile_id/document_file_name
        source_folder = "{}_{}".format(self.profile_to_process.source_name,
            self.profile_to_process.source_id)
        profile_folder = self.profile_to_process.id
        file_name = document.file_name
        return os.path.join(self.export_target, source_folder, profile_folder, file_name)

    def _export_document(self, document):
        edr = export_result.Export_document_result()
        try:
            os.makedirs(os.path.dirname(document.export_path), exist_ok=True)
            urllib.request.urlretrieve(document.url, document.export_path)
        except BaseException as e:
            edr.setFailure(document, "Cannot download document: {}".format(str(e)))
            print(edr.message)
            return edr
        edr.setSucess(document, "Export sucessful!")
        return edr

    def _export_profile(self):
        res = export_result.Export_result(self.profile_to_process)
        err = self.profile_to_process.fill_documents_from_api(self.api)
        if err is not None:
            res.setFailure(err)
            return res
        for doc in self.profile_to_process.documents:
            doc.export_path = self._generate_export_path(doc)
            res.addResultDoc(self._export_document(doc))
        return res
