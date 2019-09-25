"""Upload worker file."""
import json
import threading
import urllib
import os
import pandas as pd

from resume_exporter import calculate_ner_score

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
        source_folder = "{}_{}".format(self.profile_to_process.source_name, self.profile_to_process.source_id)
        profile_folder = self.profile_to_process.id
        file_name = document.file_name
        return os.path.join(self.export_target, source_folder, profile_folder, file_name)

    def _generate_export_jsons_path(self, document):
        # $taget_path/$source_name_$source_id_jsons/
        source_folder = "{}_{}_jsons".format(self.profile_to_process.source_name, self.profile_to_process.source_id)
        profile_folder = self.profile_to_process.id
        file_name = document.file_name
        return os.path.join(self.export_target, source_folder, file_name)

    def _export_document(self, document):
        edr = export_result.Export_document_result()
        try:
            if document.url is not None:
                os.makedirs(os.path.dirname(document.export_path), exist_ok=True)
                os.makedirs(os.path.dirname(document.export_jsons_path), exist_ok=True)
                urllib.request.urlretrieve(document.url, document.export_path)
            else:
                with open(document.export_path, "w") as wf:
                    json.dump(document.data, wf)
                with open(document.export_jsons_path, "w") as wf:
                    json.dump(document.data, wf)
                    print('doc urlss', document.data)
        except BaseException as e:
            edr.setFailure(document, "Cannot download document or dump json file: {}".format(str(e)))
            print(edr.message)
            return edr
        edr.setSucess(document, "Export sucessful!")
        return edr

    def generate_stat(self, document):
        source_folder = "{}_{}_jsons".format(self.profile_to_process.source_name, self.profile_to_process.source_id)
        profile_folder = self.profile_to_process.id
        file_name = document.file_name

        data_dir = os.path.join(self.export_target, source_folder)

        ner_scores = {
            "infos_score": [],
            "person_score": [],
            "email_score": [],
            "phone_score": [],
            "address_score": [],
            "exp_score": [],
            "exp_title_score": [],
            "exp_desc_score": [],
            "exp_company_score": [],
            "exp_start_date_score": [],
            "exp_end_date_score": [],
            "edu_score": [],
            "edu_title_score": [],
            "edu_desc_score": [],
            "edu_school_score": [],
            "edu_start_date_score": [],
            "edu_end_date_score": []
        }

        ner_scores_key = list(ner_scores.keys())

        ner_scores["file_path"] = []
        ner_scores["has_summary"] = []
        ner_scores["skills_count"] = []
        ner_scores["experiences_count"] = []
        ner_scores["educations_count"] = []

        for data_path in os.listdir(data_dir):
            data = json.load(open(os.path.join(data_dir, data_path), 'r'))
            print(os.path.join(data_dir, data_path))
            ner_score = calculate_ner_score.get_ner_score(data, json_type='underscore')
            ner_scores["file_path"] += [data_path]

            for key in ner_scores_key:
                ner_scores[key] += [ner_score[key]]

            ner_scores["has_summary"] += [1 if data["summary"] else 0]
            ner_scores["skills_count"] += [len(data['skills']['parsed']["all"])]
            ner_scores["experiences_count"] += [len(data["experiences"])]
            ner_scores["educations_count"] += [len(data["educations"])]

        ner_scores["file_path"] += ["Total","Avergae"]

        for key in ner_scores_key:
            ner_scores[key] += [sum(ner_scores[key]), sum(ner_scores[key])/len(ner_scores[key])]

        ner_scores["has_summary"] += [sum(ner_scores["has_summary"]), sum(ner_scores["has_summary"])/len(ner_scores["has_summary"])]
        ner_scores["skills_count"] += [sum(ner_scores["skills_count"]), sum(ner_scores["skills_count"])/len(ner_scores["skills_count"])]
        ner_scores["experiences_count"] += [sum(ner_scores["experiences_count"]), sum(ner_scores["experiences_count"])/len(ner_scores["experiences_count"])]
        ner_scores["educations_count"] += [sum(ner_scores["educations_count"]), sum(ner_scores["educations_count"])/len(ner_scores["educations_count"])]

        df = pd.DataFrame.from_dict(ner_scores)
        df.to_csv("stats_ner_score.csv", index=False) 

    def _export_profile(self):
        res = export_result.Export_result(self.profile_to_process)
        err = self.profile_to_process.fill_documents_from_api(self.api)
        if err is not None:
            res.setFailure(err)
            return res
        for doc in self.profile_to_process.documents:
            doc.export_jsons_path = self._generate_export_jsons_path(doc)
            doc.export_path = self._generate_export_path(doc)
            res.addResultDoc(self._export_document(doc))
        self.generate_stat(doc)
        return res
