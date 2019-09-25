import os
import json
import numpy as np
import pandas as pd


def check_if_exists(value):
    if value:
        if value == "None":
            return False
        else:
            return True
    else:
        return False


def check_if_desc_exists(value):
    if value:
        if value == "None" or not len([c for c in value if c.isalnum()]):
            return False
        else:
            return True
    else:
        return False


def get_ner_score(profile, json_type="underscore"):
    infos_score, person_score, email_score, phone_score, address_score = ner_infos_score(profile, json_type)
    exp_score, exp_title_score, exp_desc_score, exp_company_score, exp_start_date_score, exp_end_date_score = ner_exp_score(profile, json_type)
    edu_score, edu_title_score, edu_desc_score, edu_school_score, edu_start_date_score, edu_end_date_score = ner_edu_score(profile, json_type)

    expedus_score = 0.5 * (exp_score + edu_score)

    if infos_score == 0 and expedus_score == 0:
        ner_score = 0
    elif infos_score == 0:
        ner_score = expedus_score
    elif expedus_score == 0:
        ner_score = infos_score
    else:
        ner_score = 0.5 * (infos_score + expedus_score)

    return_score = {
        "infos_score": infos_score,
        "person_score": person_score,
        "email_score": email_score,
        "phone_score": phone_score,
        "address_score": address_score,
        "exp_score": exp_score,
        "exp_title_score": exp_title_score,
        "exp_desc_score": exp_desc_score,
        "exp_company_score": exp_company_score,
        "exp_start_date_score": exp_start_date_score,
        "exp_end_date_score": exp_end_date_score,
        "edu_score": edu_score,
        "edu_title_score": edu_title_score,
        "edu_desc_score": edu_desc_score,
        "edu_school_score": edu_school_score,
        "edu_start_date_score": edu_start_date_score,
        "edu_end_date_score": edu_end_date_score
    }

    return return_score


def ner_infos_score(profile, json_type="underscore"):
    infos_score = 0
    person_score = 0
    email_score = 0
    phone_score = 0
    address_score = 0

    if check_if_exists(profile['name']) or check_if_exists(profile['email']) or check_if_exists(profile['phone']) or check_if_exists(profile['location_text']):
        infos_score = 0.
        if check_if_exists(profile['name']):
            person_score = 1
            infos_score += 0.25
        if check_if_exists(profile['email']):
            email_score = 1
            infos_score += 0.25
        if check_if_exists(profile['phone']):
            phone_score = 1
            infos_score += 0.25
        if check_if_exists(profile['location_text']):
            address_score = 1
            infos_score += 0.25

    return infos_score, person_score, email_score, phone_score, address_score


def sub_score(N, nb_tags):
    return 1.0 - 1.0 * abs(N - nb_tags) / max(N, nb_tags)


def ner_exp_score(profile, json_type="underscore"):
    start_date_name = 'start_date' if json_type == "underscore" else 'startDate'
    end_date_name = 'end_date' if json_type == "underscore" else 'endDate'

    exp_score = 0
    title_score = 0
    desc_score = 0
    company_score = 0
    start_date_score = 0
    end_date_score = 0

    exp_scores = 0
    title_scores = 0
    desc_scores = 0
    company_scores = 0
    start_date_scores = 0
    end_date_scores = 0

    n_experiences = len(profile['experiences'])

    for exp in profile['experiences']:
        if check_if_exists(exp['title']) or check_if_desc_exists(exp['description']) or check_if_exists(exp['company']) or check_if_exists(exp[start_date_name]) or check_if_exists(exp[end_date_name]):
            if check_if_exists(exp['title']):
                title_scores += 1
                exp_scores += 0.2
            if check_if_desc_exists(exp['description']):
                desc_scores += 1
                exp_scores += 0.2
            if check_if_exists(exp['company']):
                company_scores += 1
                exp_scores += 0.2
            if check_if_exists(exp[start_date_name]):
                start_date_scores += 1
                exp_scores += 0.2
            if check_if_exists(exp[end_date_name]):
                end_date_scores += 1
                exp_scores += 0.2
    
    if n_experiences:
        exp_score = float(exp_scores) / float(n_experiences)
        title_score = float(title_scores) / float(n_experiences) if title_scores > 0 else 0
        desc_score = float(desc_scores) / float(n_experiences) if desc_scores > 0 else 0
        company_score = float(company_scores) / float(n_experiences) if company_scores > 0 else 0
        start_date_score = float(start_date_scores) / float(n_experiences) if start_date_scores > 0 else 0
        end_date_score = float(end_date_scores) / float(n_experiences) if end_date_scores > 0 else 0

    return exp_score, title_score, desc_score, company_score, start_date_score, end_date_score


def ner_edu_score(profile, json_type="underscore"):
    start_date_name = 'start_date' if json_type == "underscore" else 'startDate'
    end_date_name = 'end_date' if json_type == "underscore" else 'endDate'

    edu_score = 0
    title_score = 0
    desc_score = 0
    school_score = 0
    start_date_score = 0
    end_date_score = 0

    edu_scores = 0
    title_scores = 0
    desc_scores = 0
    school_scores = 0
    start_date_scores = 0
    end_date_scores = 0

    n_educations = len(profile['educations'])

    for edu in profile['educations']:
        if check_if_exists(edu['title']) or check_if_desc_exists(edu['description']) or check_if_exists(edu['school']) or check_if_exists(edu[start_date_name]) or check_if_exists(edu[end_date_name]):
            if check_if_exists(edu['title']):
                title_scores += 1
                edu_scores += 0.2
            if check_if_desc_exists(edu['description']):
                desc_scores += 1
                edu_scores += 0.2
            if check_if_exists(edu['school']):
                school_scores += 1
                edu_scores += 0.2
            if check_if_exists(edu[start_date_name]):
                start_date_scores += 1
                edu_scores += 0.2
            if check_if_exists(edu[end_date_name]):
                end_date_scores += 1
                edu_scores += 0.2
    
    if n_educations:
        edu_score = float(edu_scores) / float(n_educations)
        title_score = float(title_scores) / float(n_educations) if title_scores > 0 else 0
        desc_score = float(desc_scores) / float(n_educations) if desc_scores > 0 else 0
        school_score = float(school_scores) / float(n_educations) if school_scores > 0 else 0
        start_date_score = float(start_date_scores) / float(n_educations) if start_date_scores > 0 else 0
        end_date_score = float(end_date_scores) / float(n_educations) if end_date_scores > 0 else 0

    return edu_score, title_score, desc_score, school_score, start_date_score, end_date_score