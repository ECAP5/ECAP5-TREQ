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

# pylint: disable=line-too-long

import re
import markdown

STYLE = """
body {
    font: 400 16px/1.5 "Helvetica Neue", Helvetica, Arial, sans-serif;
    color: #111;
    background-color: #fbfbfb;
    -webkit-text-size-adjust: 100%;
    -webkit-font-feature-settings: "kern" 1;
    -moz-font-feature-settings: "kern" 1;
    -o-font-feature-settings: "kern" 1;
    font-feature-settings: "kern" 1;
    font-kerning: normal;
    padding: 30px;
}

@media only screen and (max-width: 600px) {
    body {
        padding: 5px;
    }
    body>#content {
        padding: 0px 20px 20px 20px !important;
    }
}

body>#content {
    margin: 0px;
    max-width: 900px;
    border: 1px solid #e1e4e8;
    padding: 10px 40px;
    padding-bottom: 20px;
    border-radius: 2px;
    margin-left: auto;
    margin-right: auto;
}

summary {
    cursor: pointer;
    text-decoration: underline;
}

hr {
    color: #bbb;
    background-color: #bbb;
    height: 1px;
    flex: 0 1 auto;
    margin: 1em 0;
    padding: 0;
    border: none;
}

.hljs-operator {
    color: #868686;
    /* There is a bug where the syntax highlighter would pick no color for e.g. `&&` symbols in the code samples. Let's overwrite this */
}


/**
 * Links
 */

a {
    color: #0366d6;
    text-decoration: none;
}

a:visited {
    color: #0366d6;
}

a:hover {
    color: #0366d6;
    text-decoration: underline;
}

pre {
    background-color: #f6f8fa;
    border-radius: 3px;
    font-size: 85%;
    line-height: 1.45;
    overflow: auto;
    padding: 16px;
}


/**
  * Code blocks
  */

code {
    background-color: rgba(27, 31, 35, .05);
    border-radius: 3px;
    font-size: 85%;
    margin: 0;
    word-wrap: break-word;
    padding: .2em .4em;
    font-family: SFMono-Regular, Consolas, Liberation Mono, Menlo, Courier, monospace;
}

pre>code {
    background-color: transparent;
    border: 0;
    display: inline;
    line-height: inherit;
    margin: 0;
    overflow: visible;
    padding: 0;
    word-wrap: normal;
    font-size: 100%;
}


/**
 * Blockquotes
 */

blockquote {
    margin-left: 30px;
    margin-top: 0px;
    margin-bottom: 16px;
    border-left-width: 3px;
    padding: 0 1em;
    color: #828282;
    border-left: 4px solid #e8e8e8;
    padding-left: 15px;
    font-size: 18px;
    letter-spacing: -1px;
    font-style: italic;
}

blockquote * {
    font-style: normal !important;
    letter-spacing: 0;
    color: #6a737d !important;
}


/**
 * Tables
 */

table {
    border-spacing: 2px;
    display: block;
    font-size: 14px;
    overflow: auto;
    width: 100%;
    margin-bottom: 16px;
    border-spacing: 0;
    border-collapse: collapse;
}

td {
    padding: 6px 13px;
    border: 1px solid #dfe2e5;
}

th {
    font-weight: 600;
    padding: 6px 13px;
    border: 1px solid #dfe2e5;
}

tr {
    background-color: #fff;
    border-top: 1px solid #c6cbd1;
}

table tr:nth-child(2n) {
    background-color: #f6f8fa;
}


/**
 * Others
 */

img {
    max-width: 100%;
}

p {
    line-height: 24px;
    font-weight: 400;
    font-size: 16px;
    color: #24292e;
}

ul {
    margin-top: 0;
}

li {
    color: #24292e;
    font-size: 16px;
    font-weight: 400;
    line-height: 1.5;
}

li+li {
    margin-top: 0.25em;
}

* {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol";
    color: #24292e;
}

a:visited {
    color: #0366d6;
}

h1,
h2,
h3 {
    border-bottom: 1px solid #eaecef;
    color: #111;
    /* Darker */
}

code>* {
    font-family: Consolas, "Liberation Mono", Menlo, Courier, monospace !important;
}

.markdown-alert {
    padding: 0.5rem 1rem;
    margin-bottom: 15px;
    color: inherit;
    border-left: .25em solid #d0d7de;
}

.markdown-alert-caution {
    border-left-color: #cf222e;
}

.markdown-alert-warning {
    border-left-color: #9a6700;
}

.markdown-alert-important {
    border-left-color: #8250df;
}

.markdown-alert-title {
    display: flex;
    font-weight: 500;
    align-items: center;
    line-height: 1;
}

.markdown-alert-caution .markdown-alert-title {
    color: #d1242f;
}

.markdown-alert-warning .markdown-alert-title {
    color: #9a6700;
}

.markdown-alert-important .markdown-alert-title {
    color: #8250df;
}

.markdown-alert svg {
    margin-right: 0.5rem;
    width: 16px;
    height: 16px;
    display: inline-block;
    overflow: visible;
    vertical-align: text-bottom;
}

.markdown-alert-caution svg {
    fill: #cf222e;
}

.markdown-alert-warning svg {
    fill: #9a6700;
}

.markdown-alert-important svg {
    fill: #8250df;
}

.markdown-alert>:first-child {
    margin-top: 0;
}

.markdown-alert>:last-child {
    margin-bottom: 0;
}

samp {
    font-family: ui-monospace,SFMono-Regular,SF Mono,Menlo,Consolas,Liberation Mono,monospace;
    font-size: 85%;
}
"""

def markdown_to_html(content: str) -> str:
    """Converts a github markdown to html
    
    :param content: the markdown string
    :type content: str

    :returns: an html string
    :rtype: str
    """
    content = process_alerts(content)
    html = "<html><head><meta charset=\"utf-8\"><style>{}</style></head><body>".format(STYLE)
    html += markdown.markdown(content)
    html += "</body></html>"
    return html

REPLACE_WARNING = r'<div class="markdown-alert markdown-alert-warning"><p class="markdown-alert-title"><svg class="octicon octicon-alert mr-2" viewBox="0 0 16 16" version="1.1" width="16" height="16" aria-hidden="true"><path d="M6.457 1.047c.659-1.234 2.427-1.234 3.086 0l6.082 11.378A1.75 1.75 0 0 1 14.082 15H1.918a1.75 1.75 0 0 1-1.543-2.575Zm1.763.707a.25.25 0 0 0-.44 0L1.698 13.132a.25.25 0 0 0 .22.368h12.164a.25.25 0 0 0 .22-.368Zm.53 3.996v2.5a.75.75 0 0 1-1.5 0v-2.5a.75.75 0 0 1 1.5 0ZM9 11a1 1 0 1 1-2 0 1 1 0 0 1 2 0Z"></path></svg>Warning</p><p>\1</p></div>'
REPLACE_CAUTION = r'<div class="markdown-alert markdown-alert-caution"><p class="markdown-alert-title"><svg class="octicon octicon-stop mr-2" viewBox="0 0 16 16" version="1.1" width="16" height="16" aria-hidden="true"><path d="M4.47.22A.749.749 0 0 1 5 0h6c.199 0 .389.079.53.22l4.25 4.25c.141.14.22.331.22.53v6a.749.749 0 0 1-.22.53l-4.25 4.25A.749.749 0 0 1 11 16H5a.749.749 0 0 1-.53-.22L.22 11.53A.749.749 0 0 1 0 11V5c0-.199.079-.389.22-.53Zm.84 1.28L1.5 5.31v5.38l3.81 3.81h5.38l3.81-3.81V5.31L10.69 1.5ZM8 4a.75.75 0 0 1 .75.75v3.5a.75.75 0 0 1-1.5 0v-3.5A.75.75 0 0 1 8 4Zm0 8a1 1 0 1 1 0-2 1 1 0 0 1 0 2Z"></path></svg>Caution</p><p>\1</p></div>'
REPLACE_IMPORTANT = r'<div class="markdown-alert markdown-alert-important"><p class="markdown-alert-title"><svg class="octicon octicon-report mr-2" viewBox="0 0 16 16" version="1.1" width="16" height="16" aria-hidden="true"><path d="M0 1.75C0 .784.784 0 1.75 0h12.5C15.216 0 16 .784 16 1.75v9.5A1.75 1.75 0 0 1 14.25 13H8.06l-2.573 2.573A1.458 1.458 0 0 1 3 14.543V13H1.75A1.75 1.75 0 0 1 0 11.25Zm1.75-.25a.25.25 0 0 0-.25.25v9.5c0 .138.112.25.25.25h2a.75.75 0 0 1 .75.75v2.19l2.72-2.72a.749.749 0 0 1 .53-.22h6.5a.25.25 0 0 0 .25-.25v-9.5a.25.25 0 0 0-.25-.25Zm7 2.25v2.5a.75.75 0 0 1-1.5 0v-2.5a.75.75 0 0 1 1.5 0ZM9 9a1 1 0 1 1-2 0 1 1 0 0 1 2 0Z"></path></svg>Caution</p><p>\1</p></div>'

def process_alerts(content: str) -> str:
    """Converts a github markdown alerts to html
    
    :param content: the markdown string
    :type content: str

    :returns: an html string with converted alerts
    :rtype: str
    """
    content = re.sub(r'> \[\!CAUTION\]\n> (.*)', REPLACE_CAUTION, content)
    content = re.sub(r'> \[\!WARNING\]\n> (.*)', REPLACE_WARNING, content)
    content = re.sub(r'> \[\!IMPORTANT\]\n> (.*)', REPLACE_IMPORTANT, content)
    return content 
