import os
import json
import pandas as pd

from calculate_ner_score import get_ner_score

data_dir = "stats_data/"

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
   ner_score = get_ner_score(data, json_type='underscore')
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