"""Tetration Analytics Rest API Python client"""

import hashlib
import hmac
from datetime import datetime
import base64
import warnings
import requests


class RestClient(object):
    """
    A high-level client class for communication with Tetration API server.
    Provides query requests.

    Attributes:
        server_endpoint: String of server URL to query
        uri_prefix: String prefix of URI Path
        api_key: String of hex API key provided by Tetration key generation UI.
        api_secret: String of hex API secret provided by Tetration key
        generation UI.
        verify: Boolean for SSL verification of requests.
        session: requests.Session object to execute requests

    Constants:
        SUPPORTED_METHODS: list of supported HTTP methods
    """

    SUPPORTED_METHODS = ['GET', 'PUT', 'POST', 'DELETE', 'PATCH']

    def __init__(self, server_endpoint, api_key, api_secret, **kwargs):
        """
        Init begins a persistent requests.Session and can be accessed by
        attribute RestClient.session.

        Example use case:
        rc = RestClient("http://example-server-endpoint.com",
                        "5d2088d1e20da0b8aebbbc5e648df68a", # api_key
                        "315b8f99adc4edbaa4e9b7ef3ef492a349156fce", # api_secret
                        verify = False) # disable SSL certification verification


        Args:
            server_endpoint: String of the server URL to query
            api_key: String of hex API key provided by Tetration key generation UI.
            api_secret: String of hex API secret provided by Tetration key
            generation UI.
            kwargs:
                api_version: API Version
                verify: Boolean to verify SSL cerfications.
        """
        self.server_endpoint = server_endpoint
        self.uri_prefix = '/openapi/' + kwargs.get('api_version', 'v1')
        self.api_key = api_key
        self.api_secret = api_secret
        self.verify = kwargs.get('verify', True)
        self.session = requests.Session()

    def signed_http_request(self, http_method, uri_path, args=None):
        """
        Send a signed http request to the server. Returns a requests.Response.

        Args:
            http_method: String HTTP method like 'GET', 'PUT', 'POST', ...
            uri_path: Additional string URI path for query
            args: Additional dictionary of arguments
                "params": Additional dictionary of parameters for GET and PUT
                "json_body": String JSON body
                "timeout": Float of timeout in seconds

        Returns:
            requests.Response object for the request
        """
        if http_method not in self.SUPPORTED_METHODS:
            warnings.warn('HTTP method "%s" is unsupported. Returning None' %
                          http_method)
            return None

        args = {} if args is None else args
        params = args.get('params')
        json_body = args.get('json_body', '')
        timeout = args.get('timeout')

        unprep_req = requests.Request(
            http_method, self.server_endpoint + uri_path, params=params,
            data=json_body)
        req = self.session.prepare_request(unprep_req)

        if http_method == 'POST' or http_method == 'PUT':
            checksum = hashlib.sha256(req.body).hexdigest()
            req.headers['X-Tetration-Cksum'] = checksum

        req.headers['User-Agent'] = 'Cisco Tetration Python client'
        req.headers['Content-Type'] = 'application/json'
        time_fmt = '%Y-%m-%dT%H:%M:%S+0000'
        req.headers['Timestamp'] = datetime.utcnow().strftime(time_fmt)
        # The time format above is hardcoded with +0000 for the time offset.
        # Use ISO 8601 standard?
        req.headers['Id'] = self.api_key

        self.add_auth_header(req)
        return self.session.send(req, timeout=timeout, verify=self.verify)

    def get(self, uri_path='', **kwargs):
        """
        Get request to the server. Returns a requests.Response.

        Args:
            uri_path: Additional string URI path for query
            kwargs:
                params: Additional dictionary of parameters for GET
                json_body: String JSON body
                timeout: Float of timeout in seconds

        Returns:
            requests.Response object for the request
        """
        return self.signed_http_request(
            http_method='GET', uri_path=self.uri_prefix + uri_path, args=kwargs)

    def post(self, uri_path='', **kwargs):
        """
        POST request to the server. Returns a requests.Response.

        Args:
            uri_path: Additional string URI path for query
            kwargs:
                json_body: String JSON body
                timeout: Float of timeout in seconds

        Returns:
            requests.Response object for the request
        """
        return self.signed_http_request(
            http_method='POST', uri_path=self.uri_prefix + uri_path,
            args=kwargs)

    def put(self, uri_path='', **kwargs):
        """
        PUT request to the server. Returns a requests.Response.

        Args:
            uri_path: Additional string URI path for query
            kwargs:
                json_body: String JSON body
                timeout: Float of timeout in seconds

        Returns:
            requests.Response object for the request
        """
        return self.signed_http_request(
            http_method='PUT', uri_path=self.uri_prefix + uri_path, args=kwargs)

    def delete(self, uri_path='', **kwargs):
        """
        DELETE request to the server. Returns a requests.Response.

        Args:
            uri_path: Additional string URI path for query
            kwargs:
                json_body: String JSON body
                timeout: Float of timeout in seconds

        Returns:
            requests.Response object for the request
        """
        return self.signed_http_request(
            http_method='DELETE', uri_path=self.uri_prefix + uri_path,
            args=kwargs)

    def patch(self, uri_path='', **kwargs):
        """
        PATCH request to the server. Returns a requests.Response.

        Args:
            uri_path: Additional string URI path for query
            kwargs:
                json_body: String JSON body
                timeout: Float of timeout in seconds

        Returns:
            requests.Response object for the request
        """
        return self.signed_http_request(
            http_method='PATCH', uri_path=self.uri_prefix + uri_path,
            args=kwargs)

    def add_auth_header(self, req):
        """
        Adds the authorization header to the requests.PreparedRequest

        Args:
            req: requests.PreparedRequest for which to update the
            Authorization header.
        """

        # The signature uses an AWS/Azure-like scheme.
        signer = hmac.new(self.api_secret,
                          digestmod=hashlib.sha256)
        signer.update(req.method + '\n')
        signer.update(req.path_url + '\n')
        signer.update(req.headers.get('X-Tetration-Cksum', '') + '\n')
        signer.update(req.headers.get('Content-Type', '') + '\n')
        signer.update(req.headers.get('Timestamp', '') + '\n')

        signature = base64.b64encode(signer.digest())
        req.headers['Authorization'] = signature
