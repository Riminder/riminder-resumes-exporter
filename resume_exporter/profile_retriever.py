"""Class that manage profile retrieving process."""

from resume_exporter import profile_entity
from resume_exporter import api_utils


# 12 decembre 2012
BASE_DATE_START = "1356059704"


class ProfileRetriever(object):
    """Profile retriever manage profile getting process."""

    def __init__(self, api, source_ids):
        """Init."""
        self.n_sources = len(source_ids)
        self.source_ids = source_ids
        self.api = api

    def _get_profiles_base(self, source_ids, page):
        """Get profiles from a given page (see /profiles)."""
        date_start = BASE_DATE_START
        resp, err = api_utils.exec_api_call(lambda: self.api.profile.list(source_ids=source_ids, limit=1000, date_start=date_start, page=page))
        if err is not None:
            err = "Cannot get profiles from api: {} (source: {} - page: {})".format(err, source_ids, page)
            raise BaseException(err)
        profiles = []
        # put profile's data in a profile_entity object
        for r_profile in resp['profiles']:
            p = profile_entity.Profile_entity(
                r_profile['profile_id'],
                r_profile['source']['source_id'],
                r_profile['source']['name'])
            profiles.append(p)
        return profiles

    def _get_profiles(self, source_ids):
        """Manage get profile datas process."""
        date_start = BASE_DATE_START
        # do the operation once at start to know the number of profiles
        # associated with the sources
        resp, err = api_utils.exec_api_call(lambda: self.api.profile.list(source_ids=source_ids, limit=1000, date_start=date_start))
        if err is not None:
            err = "Cannot get profiles from api: {} (source: {})".format(err, source_ids)
            raise BaseException(err)
        max_page = resp['maxPage']
        profiles = []
        for page_idx in range(max_page):
            page_idx += 1
            profiles += self._get_profiles_base(source_ids, page_idx)
        return profiles

    def get_next_profiles(self):
        """Get profiles for the next source."""
        if len(self.source_ids) == 0:
            return None, None
        source_id = [self.source_ids.pop()]

        return (self._get_profiles(source_id), source_id)
