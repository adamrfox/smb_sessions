#!/usr/bin/python
"""Example code for making PAPI calls for OneFS management."""

import string
import base64
import httplib
import ssl


def call(host, port, method, uri, body, targtype, content, username, pword):
    """
    Function to handle calls through the OneFS API
    
    Example: papi_call('172.16.10.10', 8080, 'GET', '/platform/1/protocols/smb/shares', '', "any", "text/plain", 'root', 'a')
    """

    headers = {}

    headers['Authorization'] = 'Basic ' + string.strip(base64.encodestring(username + ":" + pword))
    headers['content-type'] = content
    headers['x-isi-ifs-target-type'] = targtype

    # Make a connection to the server
    connection = httplib.HTTPSConnection(host, port, context=ssl._create_unverified_context())

    connection.request(method, uri, body, headers)
    connection.sock.settimeout(30)
    response = connection.getresponse()
    json_resp = response.read()

    # Close the connection
    connection.close()
    connection = None

    return response.status, response.reason, json_resp
    

