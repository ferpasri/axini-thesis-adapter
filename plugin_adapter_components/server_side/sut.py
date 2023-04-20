import json
from datetime import datetime
from xml.etree import ElementTree
from .http_adapter_labels import Get, Post, Answer

class HttpSut:
    """
    Constructor
    """
    def __init__(self, logger, response_received):
        self.logger = logger
        self.response_received = response_received

    """
    Special function: class name
    """
    def __name__(self):
        return "Sut"

    """
    Perform any cleanup if the selenium has stopped
    """
    def stop(self):
        self.logger.info("Sut", "Http requests to the server have been stopped")

    """
    Parse the SUT's response and add it to the response stack from the
    Handler class.
    """
    def handle_response(self, response):
        self.logger.debug("Sut", "Add response: {}".format(response))
        code = int(response.status_code)
        headers = dict(response.headers)
        body = response.text
        timestamp = datetime.now()

        if 'xml' in headers.get('content-type', ''):
            document = ElementTree.fromstring(body)
            hash = ElementTree.ElementTree(document).getroot().attrib
            print(hash)
            response_label = Answer(code, json.dumps(headers), json.dumps(hash))
            # response_label = Labels.answer.instantiate({
            #     'code': code,
            #     'headers': json.dumps(headers),
            #     'body': json.dumps(hash),
            # }, timestamp)

            self.logger.info(f"Answer is an XML message: {hash}")
        else:
            response_label = Answer(code, json.dumps(headers), body)
            # response_label = Labels.answer.instantiate({
            #     'code': code,
            #     'headers': json.dumps(headers),
            #     'body': body,
            # }, timestamp)

            self.logger.info(f"Answer is a JSON message: {body}")

        physical_label = body

        self.response_received(response)

    def perform_post_request(self, body, headers, uri):
        self.logger.info(f"POST request for endpoint: {uri}")
        try:
            response = self.requests.post(uri, data=body, headers=headers)
            self.logger.info(f"POST answer for endpoint: {uri}")
            self.handle_response(response)
        except Exception as e:
            # TODO: handle error
            print(str(e))
            # self.adapter_core.send_error(str(e))

    def perform_get_request(self, headers, uri):
        self.logger.info(f"GET request for endpoint: {uri}")

        try:
            response = self.requests.get(uri, headers=headers)
            self.logger.info(f"GET answer for endpoint: {uri}")
            self.handle_response(response)
        except Exception as e:
            # TODO: handle error
            print(str(e))
            # self.adapter_core.send_error(str(e))
