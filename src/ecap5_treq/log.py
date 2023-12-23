#           __        _
#  ________/ /  ___ _(_)__  ___
# / __/ __/ _ \/ _ `/ / _ \/ -_)
# \__/\__/_//_/\_,_/_/_//_/\__/
# 
# Copyright (C) Clément Chaine
# This file is part of ECAP5-TREQ <https://github.com/cchaine/ECAP5-TREQ>
# 
# ECAP5-TREQ is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# ECAP5-TREQ is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with ECAP5-TREQ.  If not, see <http://www.gnu.org/licenses/>.

import sys

def log_imp(msg: str) -> None:
    """Logs an important message

    The logged messages are printed and stored in a static table ``log_imp.msgs``.

    :param msg: The message to log
    """
    print("IMPORTANT:", msg, file=sys.stderr)

    log_imp.msgs += [msg]
# Initialize the log table
log_imp.msgs = []

def log_warn(msg: str) -> None:
    """Logs a warning message

    The logged messages are printed and stored in a static table ``log_warn.msgs``.

    :param msg: The message to log
    """
    print("WARN:", msg, file=sys.stderr)

    log_warn.msgs += [msg]
# Initialize the log table
log_warn.msgs = []

def log_error(msg: str) -> None:
    """Logs an error message

    The logged messages are printed and stored in a static table ``log_error.msgs``.

    :param msg: The message to log
    """
    print("ERROR:", msg, file=sys.stderr)

    log_error.msgs += [msg]
# Initialize the log table
log_error.msgs = []
