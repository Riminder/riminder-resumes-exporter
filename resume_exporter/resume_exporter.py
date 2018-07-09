#!/usr/bin/python3
"""Export profiles files from the platform to a given file."""

import argparse
import os
import sys

import riminder

from resume_exporter import api_utils
from resume_exporter import export_supervisor
from resume_exporter import printer


def parse_args():
    """Parse command line argument."""
    argsParser = argparse.ArgumentParser(description='Send resume to the platform.')
    argsParser.add_argument('--source_ids', nargs='*', default=None)
    argsParser.add_argument('--api_key', default=None)
    argsParser.add_argument('--target', default=None, required=True)
    argsParser.add_argument('--verbose', action='store_const', const=True, default=False)
    argsParser.add_argument('--silent', action='store_const', const=True, default=False)
    argsParser.add_argument('--n-worker', default=3)
    argsParser.add_argument('--logfile', default=None, required=False)
    args = argsParser.parse_args()
    return args


def get_all_source_ids(api):
    """Get all source id for a given key."""
    res = []
    resp, err = api_utils.exec_api_call(lambda: api.source.list())
    if err is not None:
        err = "Cannot get sources: {}".format(err)
        return (None, err)
    for source in resp:
        res.append(source['source_id'])
    return (res, None)


def get_from_stdin(message):
    """Prompt a message and wait for user input."""
    print(message, end='', flush=True)
    res = sys.stdin.readline()
    res = res[:-1]
    return res


def get_user_data(args):
    """Get command line missing datas."""
    if args.api_key is None:
        args.api_key = get_from_stdin('api secret key: ')
    if args.source_ids is None:
        api = riminder.Riminder(args.api_key)
        source_ids, err = get_all_source_ids(api)
        if err is not None:
            return (args, err)
        args.source_ids = source_ids
    args.v_level = printer.VERBOSE_LEVEL_NORMAL
    if args.silent:
        args.v_level = printer.VERBOSE_LEVEL_SILENT
    if args.verbose:
        args.v_level = printer.VERBOSE_LEVEL_VERBOSE
    return (args, None)


def main():
    """Well..."""
    args = parse_args()
    args, err = get_user_data(args)
    if err is not None:
        raise BaseException("Error during startup: {}".format(err))

    if not os.path.isdir(args.target):
        raise BaseException("'{}' is not a directory.".format(args.target))

    if args.n_worker < 1:
        raise BaseException("{} is not a valid n_worker, must be greater than 0".format(args.n_worker))

    export_sup = export_supervisor.Export_supervisor(args)
    export_sup.start()


if __name__ == '__main__':
    main()
