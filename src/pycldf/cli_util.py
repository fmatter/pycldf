import pathlib
import argparse

from clldutils.clilib import PathType
from csvw.utils import is_url
import requests

from pycldf import Dataset, Database

__all__ = [
    'add_dataset', 'get_dataset',
    'UrlOrPathType', 'FlagOrPathType', 'strtobool',
    'add_database', 'get_database',
    'add_catalog_spec',
]

#
# Copied from distutils.util - because we don't want to deal with deprecation warnings.
#
def strtobool(val):  # pragma: no cover
    """Convert a string representation of truth to true (1) or false (0).

    True values are 'y', 'yes', 't', 'true', 'on', and '1'; false values
    are 'n', 'no', 'f', 'false', 'off', and '0'.  Raises ValueError if
    'val' is anything else.
    """
    val = val.lower()
    if val in ('y', 'yes', 't', 'true', 'on', '1'):
        return 1
    elif val in ('n', 'no', 'f', 'false', 'off', '0'):
        return 0
    else:
        raise ValueError("invalid truth value %r" % (val,))


class FlagOrPathType(PathType):
    def __call__(self, string):
        try:
            return bool(strtobool(string))
        except ValueError:
            return super().__call__(string)


class UrlOrPathType(PathType):
    def __call__(self, string):
        if is_url(string):
            if self._must_exist:
                sc = requests.head(string).status_code
                if sc != 200:
                    raise argparse.ArgumentTypeError(
                        'URL {} does not exist [HTTP {}]!'.format(string, sc))
            return string
        return super().__call__(string)


def add_dataset(parser):
    parser.add_argument(
        'dataset',
        metavar='DATASET',
        help="Dataset specification (i.e. URL or path to a CLDF metadata file or to the data file)",
        type=UrlOrPathType(type='file'),
    )


def get_dataset(args):
    if pathlib.Path(args.dataset).suffix == '.json':
        return Dataset.from_metadata(args.dataset)
    return Dataset.from_data(args.dataset)


def add_database(parser, must_exist=True):
    add_dataset(parser)
    parser.add_argument(
        'db',
        metavar='SQLITE_DB_PATH',
        help='Path to the SQLite db file',
        type=PathType(type='file', must_exist=must_exist),
    )
    parser.add_argument('--infer-primary-keys', action='store_true', default=False)


def get_database(args):
    return Database(get_dataset(args), fname=args.db, infer_primary_keys=args.infer_primary_keys)


def add_catalog_spec(parser, name):
    parser.add_argument(
        '--' + name,
        metavar=name.upper(),
        type=PathType(type='dir'),
        help='Path to repository clone of {0} data'.format(name.capitalize()))
    parser.add_argument(
        '--{0}-version'.format(name),
        help='Version of {0} data to checkout'.format(name.capitalize()),
        default=None)
