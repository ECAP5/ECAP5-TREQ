#           __        _
#  ________/ /  ___ _(_)__  ___
# / __/ __/ _ \/ _ `/ / _ \/ -_)
# \__/\__/_//_/\_,_/_/_//_/\__/
# 
# Copyright (C) Clément Chaine
# This file is part of ECAP5-TREQ <https://github.com/ECAP5/ECAP5-TREQ>
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

# pylint: disable=missing-function-docstring

import pytest
from mock import patch, Mock, mock_open, call
import re

from ecap5_treq.html import markdown_to_html, process_alerts

#
# Tests targetting functions in log module
#

@patch("ecap5_treq.html.STYLE", "style")
@patch("ecap5_treq.html.process_alerts", return_value="processed")
@patch("markdown.markdown", return_value="html")
def test_markdown_to_html(stub_markdown, stub_process_alerts):
    """Unit test for the markdown_to_html function
    """
    result = markdown_to_html("content")

    stub_process_alerts.assert_called_once_with("content")
    stub_markdown.assert_called_once_with("processed")
    assert result == "<html><head><meta charset=\"utf-8\"><style>style</style></head><body>html</body></html>"

@patch("ecap5_treq.html.REPLACE_WARNING", r'\1')
@patch("ecap5_treq.html.REPLACE_CAUTION", r'\1')
@patch("ecap5_treq.html.REPLACE_IMPORTANT", r'\1')
def test_process_alerts():
    content = "> [!CAUTION]\n> test\n\n> [!WARNING]\n> test\n\n> [!IMPORTANT]\n> test\n"
    result = process_alerts(content)
    assert result == "test\n\ntest\n\ntest\n"

