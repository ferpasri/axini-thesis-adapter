import json
from datetime import datetime
from urllib.parse import urljoin
from xml.etree import ElementTree
from .http_adapter_labels import Labels

from tm_sts import Label, InstantiatedLabel
from plugin_adapter import Handler
from configuration import Configurable


class PluginAdapterHandler(Handler, Configurable):
    def __init__(self):
        super().__init__()

    def start(self):
        pass

    def reset(self):
        pass

    def stop(self):
        pass

    def stimulate(self, ilabel: InstantiatedLabel) -> str:
        label_name = ilabel.label.name

        physical_label = label_name

        endpoint = ilabel.valuation['endpoint']
        path = ilabel.valuation['path']
        headers = json.loads(ilabel.valuation['headers'])

        uri = urljoin(endpoint, path)

        if label_name == 'get':
            self.perform_get_request(headers, uri)
        elif label_name == 'post':
            body = ilabel.valuation.get('body')
            physical_label = body

            self.perform_post_request(body, headers, uri)
        else:
            raise Exception(f"Unsupported stimulus {label_name!r}")

        return physical_label

    def supported_labels(self):
        return Labels.labels

    def send_answer(self, response):
        code = int(response.status_code)
        headers = dict(response.headers)
        body = response.text
        timestamp = datetime.now()

        if 'xml' in headers.get('content-type', ''):
            document = ElementTree.fromstring(body)
            hash = ElementTree.ElementTree(document).getroot().attrib
            response_label = Labels.answer.instantiate({
                'code': code,
                'headers': json.dumps(headers),
                'body': json.dumps(hash),
            }, timestamp)

            self.logger.info(f"Answer is an XML message: {hash}")
        else:
            response_label = Labels.answer.instantiate({
                'code': code,
                'headers': json.dumps(headers),
                'body': body,
            }, timestamp)

            self.logger.info(f"Answer is a JSON message: {body}")

        physical_label = body
        self.adapter_core.send_response(response_label, physical_label, timestamp)

    def perform_post_request(self, body, headers, uri):
        self.logger.info(f"POST request for endpoint: {uri}")
        try:
            response = self.requests.post(uri, data=body, headers=headers)
            self.logger.info(f"POST answer for endpoint: {uri}")
            self.send_answer(response)
        except Exception as e:
            self.adapter_core.send_error(str(e))

    def perform_get_request(self, headers, uri):
        self.logger.info(f"GET request for endpoint: {uri}")

        try:
            response = self.requests.get(uri, headers=headers)
            self.logger.info(f"GET answer for endpoint: {uri}")
            self.send_answer(response)
        except Exception as e:
            self.adapter_core.send_error(str(e))
