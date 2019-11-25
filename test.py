"""Some test for the project."""

import unittest
import os

import riminder

from resume_exporter.export_worker import Export_worker
from resume_exporter.profile_entity import Profile_entity


class Helper(object):
    def __init__(self):
        self.api_url = ""
        self.api_key = ""
        # if you want to use a source in particular set it ti None otherwise
        # must be a list
        self.source_name = []

        self.api = riminder.Riminder(api_key=self.api_key, None, self.api_url)
        self.source_id = None
        self.profile_raw = None
        self.documents_raw = None

    def _get_source_id(self):
        resp = self.api.source.list()

        if self.source_name is None or len(self.source_name) == 0:
            self.source_id = resp['data'][0]['source_id']
            return resp['data'][0]['source_id']
        for source in resp['data']:
            if source['name'] in self.source_name:
                self.source_id = source['source_id']
                return source['source_id']
        raise ValueError('No source matching {}'.format(self.source_name))

    def _get_profile_raw(self):
        s_ids = []
        s_ids.append(str(self.source_id))
        resp = self.api.profile.list(source_ids=s_ids)
        for profile in resp['data']['profiles']:
            self.profile_raw = profile
            r2 = self.api.profile.document.list(source_id=self.source_id, profile_id=profile['profile_id'])
            if len(r2['data']) > 0:
                self.documents_raw = r2['data']
                return
        raise ValueError('No profile with document for source {}'.format(self.source_id))

    def setup(self):
        self._get_source_id()
        self._get_profile_raw()


class test_profile_entity(unittest.TestCase):

    def test_profile_entity_fill(self):
        self.helper = Helper()
        self.helper.setup()
        profile_id = self.helper.profile_raw['profile_id']
        source_name = self.helper.profile_raw['source']['name']
        source_id = self.helper.profile_raw['source']['source_id']
        p_entity = Profile_entity(profile_id=profile_id, source_id=source_id, source_name=source_name)
        self.assertEqual(p_entity.id, profile_id, "test_profile_entity_fill:profile_id:Expected {} got {}".format(profile_id, p_entity.id))
        self.assertEqual(p_entity.source_id, source_id, "test_profile_entity_fill:source_id:Expected {} got {}".format(source_id, p_entity.source_id))
        self.assertEqual(p_entity.source_name, source_name, "test_profile_entity_fill:source_name:Expected {} got {}".format(source_name, p_entity.source_name))
        self.assertEqual(p_entity.documents, [], "test_profile_entity_fill:documents:Expected {} got {}".format([], p_entity.documents))

    def test_profile_entity_document(self):
        self.helper = Helper()
        self.helper.setup()
        profile_id = self.helper.profile_raw['profile_id']
        source_name = self.helper.profile_raw['source']['name']
        source_id = self.helper.profile_raw['source']['source_id']
        p_entity = Profile_entity(profile_id=profile_id, source_id=source_id, source_name=source_name)
        p_entity.fill_documents_from_api(self.helper.api)
        self.assertNotEqual(len(p_entity.documents), 0, "test_profile_entity_document:document presence: There must be some documents")
        self.assertEqual(len(p_entity.documents), len(self.helper.documents_raw), "test_profile_entity_document:document number:Expected {} got {}".format(len(self.helper.documents_raw), len(p_entity.documents)))
        for raw_doc in self.helper.documents_raw:
            r = False
            for p_doc in p_entity.documents:
                if raw_doc['original_file_name'] == p_doc.file_name:
                    if raw_doc['url'] == p_doc.url:
                        r = True
                        break
            self.assertTrue(r, "test_profile_entity_document:document absence:Document {} (url: {}) is absent.".format(raw_doc['original_file_name'], raw_doc['url']))


class test_worker(unittest.TestCase):

    def init(self):
        self.helper = Helper()
        self.helper.setup()
        self.api = self.helper.api
        self.export_target = "./test/target"
        self.worker = Export_worker(0, self.api, self.export_target)
        profile_id = self.helper.profile_raw['profile_id']
        source_name = self.helper.profile_raw['source']['name']
        source_id = self.helper.profile_raw['source']['source_id']
        self.p_entity = Profile_entity(profile_id=profile_id, source_id=source_id, source_name=source_name)
        self.p_entity.fill_documents_from_api(self.api)

    def cb_test(self, id, result):
        for document in self.p_entity.documents:
            source_folder = "{}_{}".format(self.p_entity.source_name,
                self.p_entity.source_id)
            profile_folder = self.p_entity.id
            file_name = document.file_name
            p = os.path.join(self.export_target, source_folder, profile_folder, file_name)
            self.assertTrue(os.path.isfile(p), "test_worker:export:Exported document: {} should exist in {}.".format(document.file_name, p))
            self.assertGreater(os.path.getsize(p), 0, "test_worker:export:Exported document: {} should not be empty.".format(document.file_name))
            self.assertEqual(len(result.docResult), len(self.p_entity.documents), "test_worker:export:number of result: Expected {} got {}".format(len(self.p_entity.documents), len(result.docResult)))

    def test_export_file(self):
        self.init()
        self.worker.set_profile(self.p_entity, self.cb_test)
        self.worker.process_file()


if __name__ == '__main__':
    unittest.main()
