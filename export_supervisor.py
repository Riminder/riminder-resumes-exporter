"""DIE."""

import threading
import time

import riminder

import profile_retriever
from export_worker import Export_worker

VERBOSE_LEVEL_SILENT = 'silent'
VERBOSE_LEVEL_NORMAL = 'normal'
VERBOSE_LEVEL_VERBOSE = 'verbose'

# normal start
# $n source to export

# verbose start
# $source ids to export

# normal update
# $progressBar sources %$percent_sources
#
# source: $name id: $name
# $progressBar profile source %$percent_profiles

# verbose update
# json  data profile
# json data source (stat ?)

# normal end source
# json profile with failed docs

# verbose end source
# json all profiles

# all full end
# n total profile exported
# n total profile failed

# logfile same as verbose update


class Export_supervisor(object):

    def __init__(self, args):
        self.api = riminder.Riminder(args.api_key)
        self.n_worker = args.n_worker
        self.workers = {}
        self.lock_worker = threading.Lock()

        self.source_ids = args.source_ids

        self.target = args.target
        self.v_level = args.v_level
        self.logfile = None
        if args.logfile is not None:
            self.logfile = args.logfile

        self.p_retriever = profile_retriever.ProfileRetriever(self.api, self.source_ids)
        self.profiles_to_export = []
        self.n_profiles_to_export = 0
        self.n_profile_with_fail = 0
        self.export_result = []

        self.n_global_exported_profile = 0
        self.n_global_profile_with_fail = 0

    def _set_worker_profile(self, workerID):
        if len(self.profiles_to_export) == 0:
            return
        self.workers[workerID].set_profile(self.profiles_to_export.pop(), self.worker_callback)

    def _init_workers(self):
        for i in range(self.n_worker):
            self.workers[i] = Export_worker(i, self.api, self.target)
            # Give a file before start a worker to avoid the workers to die instantly
            self._set_worker_profile(i)

    def worker_callback(self, workerID, result):
        self.lock_worker.acquire()
        self.export_result.append(result)
        if not result.is_success:
            self.n_profile_with_fail += 1
            self.n_global_profile_with_fail += 1
        self.n_global_exported_profile += 1
        self._set_worker_profile(workerID)

        # TODO: print update
        self.lock_worker.release()

    def _process_a_source(self):
        self.n_profiles_to_export = 0
        self.n_profile_with_fail = 0
        self.export_result = []
        self._init_workers()
        self.lock_worker.acquire()
        # TODO: print progress bar
        for idx, w in enumerate(self.workers):
            self.workers[idx].start()
            time.sleep(0.1)
        self.lock_worker.release()
        for idx, w in enumerate(self.workers):
            self.workers[idx].join()
        # TODO: print end source

    def start(self):
        # TODO:  print start
        self.profiles_to_export = self.p_retriever.get_next_profiles()
        while self.profiles_to_export is not None:
            self._process_a_source()
            self.profiles_to_export = self.p_retriever.get_next_profiles()
        # TODO: print end
