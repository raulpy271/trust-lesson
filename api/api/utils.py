
from http import HTTPStatus

from flask import Response

def add_headers_to_response(response, headers):
    if isinstance(response, (str, dict, list)):
        return (response, HTTPStatus.OK, headers)
    elif isinstance(response, tuple):
        if len(response) == 2:
            return (response[0], response[1], headers)
        if len(response) == 3:
            response[2].update(headers)
            return response
    elif isinstance(response, Response):
        response.headers.update(headers)
        return response
    else:
        raise Exception("Cannot add headers to response: " + str(response))



