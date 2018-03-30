# -*- coding: utf-8 -*-
# Copyright 2018 Alexandre Freitas
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Module containing HTML handling methods.

"""

from io import StringIO
from lxml import etree


def xpath(content, expr):
    """Runs a XPath query against HTML content.

    Parameters
    ----------
    content : str
        HTML content to be searched.
    expr : str
        XPath expression to search for.

    Returns
    -------
    list of :obj:`object`
        Node list that matches `expr`.

    """
    parser = etree.HTMLParser()
    tree = etree.parse(StringIO(content), parser)
    node_list = tree.xpath(expr)
    result = []
    for node in node_list:
        result += [node]
    return result
