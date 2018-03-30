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

"""Package for db access methods.




"""

__all__ = ['dm', 'foundation']

import cx_Oracle
import re
import dm


def get_connection(username, password, dsn):
    """Returns a connection to the db.

    Parameters
    ----------
    username : str
        Username to authenticate on db.
    password : str
        Password to authenticate on db.
    dsn : str
        Database Data Source Name on Oracle™ Easy Connect Format.

    Returns
    -------
    :[obj]:`Connection`
        cx_Oracle Connection object.

    """
    return cx_Oracle.connect(username, password, dsn)


def jdbc_to_dsn(url):
    """Converts a JDBC URL into an Oracle™ Easy Connect valid DSN.

    Parameters
    ----------
    url : str
        JDBC connection string that describes the db. As PPM is developed in Java, connection strings are stored
        on the configuration file using JDBC format.

    Returns
    -------
    str
        Valid Oracle™ DSN in Easy Connect format.

    """
    m = re.match(r'jdbc:oracle:thin:@(//)?(.+):(\d+)([:|/])(.+)', url)
    if m is None or len(m.groups()) != 5:
        raise ValueError('Invalid connection string.')
    else:
        host = m.groups()[1]
        port = m.groups()[2]
        if m.groups()[3] == ':':
            sid = m.groups()[4]
            return cx_Oracle.makedsn(host, port, sid=sid)
        elif m.groups()[3] == '/':
            service_name = m.groups()[4]
            return cx_Oracle.makedsn(host, port, service_name=service_name)


def run_query(con, sql, *args, **kwargs):
    """Runs a SQL query on the db.

    Parameters
    ----------
    con : :[obj]:`Connection`
        A valid cx_Oracle Connection object.
    sql : str
        SQL query to run.
    *args
        Variable length argument list.
    **kwargs
        Arbitrary keyword arguments.

    Returns
    -------
    :obj:`object`
        Query results.

    Raises
    ------
    TypeError
        If `cur` is not an instance of cx_Oracle.Cursor.

    """
    if not isinstance(con, cx_Oracle.Connection):
        raise TypeError('con must be an instance of cx_Oracle.Connection.')
    cur = con.cursor()
    return cur.execute(sql, args, kwargs)
