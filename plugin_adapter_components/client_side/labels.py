from typing import Mapping, Optional

message = Mapping[str, dict, Optional[dict]]

client_stimulus: message = {
    'landing_page_button_click': {{"data": "string"}},
}

client_response: message = {
    'landing_page_button_click': {{"data": "string"}},
}
