#!/usr/bin/env python3
#
#     Copyright (C) 2017, 2018, Jose Manuel Martí Martínez
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU Affero General Public License as
#     published by the Free Software Foundation, either version 3 of the
#     License, or (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the GNU Affero General Public License
#     along with this program. If not, see <https://www.gnu.org/licenses/>.
#
"""
Get needed taxdump files from NCBI.
"""

import argparse
from ftplib import FTP
import sys
from zipfile import ZipFile

from recentrifuge.config import LICENSE, NODES_FILE, NAMES_FILE, ZIPFILE
from recentrifuge.config import TAXDUMP_PATH

__version__ = '0.0.3'
__author__ = 'Jose Manuel Martí'
__date__ = 'Aug 2018'


def main():
    """Main entry point to script."""
    # Argument Parser Configuration
    parser = argparse.ArgumentParser(
        description='Get needed taxdump files from NCBI servers',
        epilog=f'%(prog)s  - Release {__version__} - {__date__}' + LICENSE,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        '-V', '--version',
        action='version',
        version=f'%(prog)s release {__version__} ({__date__})'
    )
    parser.add_argument(
        '-n', '--nodespath',
        action='store',
        metavar='PATH',
        default=TAXDUMP_PATH,
        help=('path for the nodes information files (nodes.dmp and names.dmp' +
              ' from NCBI')
    )

    # Parse arguments
    args = parser.parse_args()

    # Program header
    print(f'\n=-= {sys.argv[0]} =-= v{__version__} - {__date__}'
          f' =-= by {__author__} =-=\n')
    sys.stdout.flush()

    # Load NCBI nodes, names and build children
    print(f'\033[90mDownloading {ZIPFILE} from NCBI...\033[0m', end='')
    sys.stdout.flush()
    ftp = FTP('ftp.ncbi.nlm.nih.gov')
    ftp.login()
    ftp.cwd('/pub/taxonomy/')
    ftp.retrbinary('RETR ' + ZIPFILE, open(ZIPFILE, 'wb').write)
    ftp.quit()
    print('\033[92m OK! \033[0m\n')

    filezip = ZipFile(ZIPFILE)
    for filename in [NODES_FILE, NAMES_FILE]:
        print(f'\033[90mExtracting "{filename}"...', end='')
        try:
            filezip.extract(filename, path=args.nodespath)
        except KeyError:
            print('\n\033[91mERROR!\033[0m')
        else:
            print('\033[92m OK! \033[0m')


if __name__ == '__main__':
    main()
