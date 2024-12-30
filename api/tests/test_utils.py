
from http import HTTPStatus

from api.utils import add_headers_to_response


def test_add_headers_single_value():
    response = {"id": "1234"}
    add_headers = {"Token": "1234"}
    new_response = add_headers_to_response(response, add_headers)
    assert new_response == (response, HTTPStatus.OK, add_headers)

def test_add_headers_pair():
    add_headers = {"Token": "1234"}
    response = ("Hello", HTTPStatus.OK)
    new_response = add_headers_to_response(response, add_headers)
    assert new_response == (response[0], response[1], add_headers)

def test_add_headers_tuple():
    add_headers = {"Token": "1234"}
    response = ("Hello", HTTPStatus.OK, {"Content-Type": "text"})
    new_response = add_headers_to_response(response, add_headers)
    assert new_response == (response[0], response[1], {**response[2], **add_headers})

def test_add_headers_response(app):
    data = ("Hello", HTTPStatus.OK, {"Content-Type": "text"})
    add_headers = {"Token": "1234"}
    response = app.make_response(data)
    expected_response = app.make_response((data[0], data[1], {**data[2], **add_headers}))
    new_response = add_headers_to_response(response, add_headers)
    assert new_response.response == expected_response.response
    assert new_response.status_code == expected_response.status_code
    assert new_response.headers == expected_response.headers

