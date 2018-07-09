"""Manage print operation."""

import random
import threading
import sys

VERBOSE_LEVEL_SILENT = 'silent'
VERBOSE_LEVEL_NORMAL = 'normal'
VERBOSE_LEVEL_VERBOSE = 'verbose'

SIZE_PROGRESS_BAR = 35


class Printer(object):
    """Manage print operation."""

    def __init__(self, exp_supervisor):
        """Init."""
        self.e_supervisor = exp_supervisor
        self.logfile = None
        if exp_supervisor.logfile:
            self.logfile = open(exp_supervisor.logfile, mode='w')

        # Convinience :)
        self.v_level = self.e_supervisor.v_level
        self.lock_printer = threading.Lock()

    # _p_print_* prepare a string for print later
    def _p_print_start(self):
        if self.v_level == VERBOSE_LEVEL_SILENT:
            return ""
        to_print = ""
        if self.v_level == VERBOSE_LEVEL_VERBOSE:
            to_print += "source_ids: \n"
            for source_id in self.e_supervisor.source_ids:
                to_print += "{}\n".format(source_id)
        to_print += "{} sources to export.".format(len(self.e_supervisor.source_ids))
        return to_print

    def _calc_percentage_processed(self, value, max, on=100):
        return int((value * on) / max)

    def _p_print_update_progress_bar(self, n_proceed, n_start):
        percent_proceed = self._calc_percentage_processed(
            n_proceed, n_start)
        progress_bar_processed = self._calc_percentage_processed(
            n_proceed, n_start, SIZE_PROGRESS_BAR)
        random_pic = random.randint(0, 5)

        bar = ''
        bar2 = ''
        for i in range(SIZE_PROGRESS_BAR):
            c = ' '
            if i < progress_bar_processed:
                c = '='
            bar += c
        bar = '[{}]'.format(bar)

        # Little points after the progress bar to be sure it hasn't crash (yet) :)
        for z in range(5):
            c = '.'
            if z == random_pic:
                c = ' '
            bar2 += c

        to_print = '{} %{} {}     \r'.format(bar, percent_proceed, bar2)
        return to_print

    def _p_print_normal_update(self):
        to_print = ""
        n_source_left = len(self.e_supervisor.p_retriever.source_ids)
        n_source_proceeed = self.e_supervisor.n_start_sources - n_source_left
        to_print += "source: {} ".format(self.e_supervisor.current_source) + self._p_print_update_progress_bar(
            n_source_proceeed, self.e_supervisor.n_start_sources)
        to_print = to_print[:-1]

        n_profile_proceed = self.e_supervisor.n_start_profiles_to_export - len(self.e_supervisor.profiles_to_export)
        to_print += " - profiles: " + self._p_print_update_progress_bar(
            n_profile_proceed, self.e_supervisor.n_start_profiles_to_export)
        return to_print

    def _p_print_verbose_update(self, profile_res, add_percentage=False):
        n_source_left = len(self.e_supervisor.p_retriever.source_ids)
        n_source_proceeed = self.e_supervisor.n_start_sources - n_source_left
        n_profile_proceed = self.e_supervisor.n_start_profiles_to_export - len(self.e_supervisor.profiles_to_export)

        percent_source = self._calc_percentage_processed(n_source_proceeed, self.e_supervisor.n_start_sources)
        percent_profile = self._calc_percentage_processed(n_profile_proceed, self.e_supervisor.n_start_profiles_to_export)
        to_print = ""
        if add_percentage:
            to_print = "source->[%{}] - profile->[%{}] - ".format(percent_source, percent_profile)
        to_print += "{}\n".format(profile_res.to_json())
        return to_print

    def _p_print_end_source(self, is_all=False):
        failed = []
        to_print = ""
        for res in self.e_supervisor.export_result:
            if is_all or not res.is_success:
                failed.append(res)
        if len(failed) == 0:
            return ""
        for fail in failed:
            to_print += "{}\n".format(fail.to_json())
        return to_print

    def _p_print_end(self):
        n_failed = self.e_supervisor.n_global_profile_with_fail
        n_proceed = self.e_supervisor.n_global_exported_profile
        n_succeed = n_proceed - n_failed
        to_print = "total profile exported: {}\ntotal profile failed: {}\ntotal profile_proceed: {}".format(n_succeed, n_failed, n_proceed)
        return to_print

    def print_something(self, to_print, is_err=False, is_no_end=False):
        """Print on term."""
        # use of the printer lock to avoid message mixing
        # (pretty useless a the moment)
        self.lock_printer.acquire()
        out = sys.stdout
        end = '\n'
        if is_err:
            out = sys.stderr
        if is_no_end:
            end = ''
        print(to_print, file=out, end=end, flush=True)
        self.lock_printer.release()

    def print_start(self):
        """Print at start of the process."""
        if self.v_level == VERBOSE_LEVEL_SILENT:
            return
        to_print = self._p_print_start()
        self.print_something(to_print)

    def print_update(self, profile_res):
        """Print when a profile has been exported."""
        if self.logfile and profile_res is not None:
            to_print = self._p_print_verbose_update(profile_res)
            self.logfile.write(to_print)
        if self.v_level == VERBOSE_LEVEL_SILENT:
            return
        if self.v_level == VERBOSE_LEVEL_NORMAL:
            self.print_something(self._p_print_normal_update(), is_no_end=True)
            return
        if profile_res is not None:
            self.print_something(self._p_print_verbose_update(profile_res, add_percentage=True), is_no_end=True)

    def print_end_source(self):
        """Print when a source has been exported."""
        if self.v_level == VERBOSE_LEVEL_SILENT:
            return
        if self.v_level == VERBOSE_LEVEL_VERBOSE:
            self.print_something(self._p_print_end_source(True), is_err=True)
            return
        to_print = "\nSource '{}' finished\n".format(self.e_supervisor.current_source)
        to_print_err = self._p_print_end_source()
        if to_print_err == "":
            self.print_something(to_print)
            return
        to_print += "failed profiles:\n"
        self.print_something(to_print_err, is_err=True)

    def print_end(self):
        """Print when process is finished."""
        if self.v_level == VERBOSE_LEVEL_SILENT:
            return
        self.print_something(self._p_print_end())
