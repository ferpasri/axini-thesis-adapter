import sys
import time
from threading import Thread
from decimal import *
from datetime import date
from .sut import Sut

sys.path.insert(0, './api')
import label_pb2

"""
Domain specific adapter component. These are all the specific adapter methods
that need to be implemented for a specific SUT.

When a response is received from the SUT, the adapter_core.send_response
method should be called
"""
class Handler:
    def __init__(self, logger):
        self.adapter_core = None # callback to adapter; register separately
        self.configuration = []
        self.sut = None

        # Passed by reference to the SUT
        self.responses = []
        self.stop_sut_thread = False
        self.sut_thread = None

        # Initialize logger
        self.logger = logger


    """
    Set the adapter core object reference.
    param [AdapterCore] adapter_core
    """
    def register_adapter_core(self, adapter_core):
        self.adapter_core = adapter_core


    """
    Thread that manages the sut actions
    param [lambda function] stop
    """
    def running_sut(self, stop):
        while True:
            if stop():
                break

            response = self.responses[:1]

            if response != []:
                self.responses.pop(0)
                self.response_received(response[0])
            else:
                time.sleep(0.1)


    """
    SUT SPECIFIC

    The SUT has produced a response which needs to be passed on to AMP.
    param[[key, type, value]]
    """
    def response_received(self, response):
        self.logger.debug("Handler", "response received: {}".format(response))
        self.adapter_core.send_response(self.response(response),
            None, time.time_ns())


    """
    SUT SPECIFIC

    Prepare the SUT to start testing.
    """
    def start(self):
        self.responses = []

        self.sut = Sut(self.responses, self.logger)

        self.stop_threads = False
        self.sut_thread = Thread(target=self.running_sut,
            args=(lambda : self.stop_sut_thread, ))
        self.sut_thread.start()


    """
    SUT SPECIFIC

    Prepare the SUT for the next test case.
    return [Dict, String] [response, exception_message]
    """
    def reset(self):
        self.logger.info("Handler", "Resetting the sut for new test cases")
        
        return self.sut
        # TODO: reset?
        # if self.sut != None:
            # return self.sut.ble_reset()


    """
    SUT SPECIFIC

    Stop the SUT from testing.
    """
    def stop(self):
        self.logger.info("Handler", "Stopping the plugin adapter from plugin handler")
        # TODO: reset?
        # self.sut.ble_reset
        self.sut.stop()
        self.sut = None

        self.stop_sut_thread = True
        self.sut_thread.join()
        self.sut_thread = None

        self.logger.debug("Handler", "Finished stopping the plugin adapter from plugin handler")


    """
    TODO ADD ARRAY AND HASH TYPES

    Generate a protobuff label object with default type values.
    param [String] label_name
    param [label_pb2.Label.LabelType] label_type
    param [dict] parameters
    return [label_pb2.Label]
    """
    def generate_type_label(self, label_name, label_type, parameters = {}):
        pb_params = []

        # Create all the google protobuff Label:Paramater objects
        for param_name, param_type in parameters.items():
            pb_value = self.instantiate_label_value(param_type)[0]

            param = label_pb2.Label.Parameter(name=param_name, value=pb_value)
            pb_params += [param]

        pb_label = label_pb2.Label(label=label_name,
                               type=label_type,
                               channel="extern",
                               parameters=pb_params)

        pb_label.timestamp = time.time_ns()

        return pb_label


    """
    TODO ADD ARRAY AND HASH TYPES

    Generate a protobuf Label containing parameters with filled in values.
    param [String] label_name
    param [label_pb2.Label.LabelType] label_type
    param [dict] parameters_type
    param [dict] parameters_value
    return [label_pb2.Label]
    """
    def generate_value_label(self, label_name, label_type, parameters_type, parameters_value):
        pb_params = []

        # Create all the google protobuff Label:Paramater objects
        for param_name, param_type in parameters_type.items():
            value = parameters_value.get(param_name)
            pb_value = label_pb2.Label.Parameter.Value()

            if param_type == "string":
                pb_value.string = value
            elif param_type == "integer":
                pb_value.integer = value
            elif param_type == "decimal":
                pb_value.decimal = value
            elif param_type == "boolean":
                pb_value.boolean = value
            elif param_type == "date":
                pb_value.date = value
            elif param_type == "time":
                pb_value.time = value
            elif param_type == "array":
                pb_value.array = value
            else:
                self.logger.warning("Handler", "UNKNOWN TYPE FOR PARAM/STIMULUS in generate value: {}".format(param_type))

            param = label_pb2.Label.Parameter(name=param_name, value=pb_value)
            pb_params += [param]

        pb_label = label_pb2.Label(label=label_name,
                               type=label_type,
                               channel="extern",
                               parameters=pb_params)

        pb_label.timestamp = time.time_ns()

        return pb_label


    """
    Generate a protobuf Stimulus Label.
    return [label_pb2.Label]
    """
    def stimulus(self, label_name, parameters={}):
        return self.generate_type_label(label_name, 0, parameters)


    """
    Generate a protobuf Response Label.
    return [label_pb2.Label]
    """
    def response(self, label_name, parameters_type, parameters_value=None):
        if parameters_value == None:
            return self.generate_type_label(label_name, 1, parameters_type)
        else:
            return self.generate_value_label(label_name, 1, parameters_type,
                parameters_value)


    """
    SUT SPECIFIC

    Processes a stimulus of a given Label message. This method also sets the
    timestamp and physical label on the Label object. The BrokerConnection
    handles the confirmation to TestManager itself.
    param [label_pb2.Label] label
    return [String] The physical label.
    """
    def stimulate(self, label):
        physical_label = None

        label_name = label.label

        if label_name == "landing_page_button_click":
            self.sut.landing_page_button_click()
        # if label_name == "startSession":
        #     self.sut.set_device_id(self.get_param_value(label, 'Device_id'))
        # elif label_name == "scan":
        #     self.sut.enable_ble_scanning(
        #         self.get_param_value(label, 'Event_Code'),
        #         self.get_param_value(label, 'Reply_Len'),
        #         self.get_param_value(label, 'Scan_Enable'),
        #         self.get_param_value(label, 'Filter_Duplicates'),
        #         self.get_param_value(label, 'OGF_LE_CTL'),
        #         self.get_param_value(label, 'OCF_LE_Set_Scan_Enable'))
        # elif label_name == "setScanParams":
        #     self.sut.set_ble_scan_parameter(
        #         self.get_param_value(label, 'Event_Code'),
        #         self.get_param_value(label, 'Reply_Len'),
        #         self.get_param_value(label, 'LE_Scan_Type'),
        #         self.get_param_value(label, 'LE_Scan_Interval'),
        #         self.get_param_value(label, 'LE_Scan_Window'),
        #         self.get_param_value(label, 'Own_Address_Type'),
        #         self.get_param_value(label, 'Scanning_Filter_Policy'),
        #         self.get_param_value(label, 'OGF_LE_CTL'),
        #         self.get_param_value(label, 'OCF_LE_Set_Scan_Parameter'))
        # elif label_name == "advertise":
        #     self.sut.enable_ble_advertising(
        #         self.get_param_value(label, 'Event_Code'),
        #         self.get_param_value(label, 'Reply_Len'),
        #         self.get_param_value(label, 'Advertising_Enable'),
        #         self.get_param_value(label, 'OGF_LE_CTL'),
        #         self.get_param_value(label, 'OCF_LE_Set_Advertising_Enable'))
        # elif label_name == "setAdvertisingParams":
        #     self.sut.set_ble_advertise_parameter(
        #         self.get_param_value(label, 'Event_Code'),
        #         self.get_param_value(label, 'Reply_Len'),
        #         self.get_param_value(label, 'Advertising_Interval_Min'),
        #         self.get_param_value(label, 'Advertising_Interval_Max'),
        #         self.get_param_value(label, 'Advertising_Type'),
        #         self.get_param_value(label, 'Own_Address_Type'),
        #         self.get_param_value(label, 'Peer_Address_Type'),
        #         self.get_param_value(label, 'Advertising_Channel_Map'),
        #         self.get_param_value(label, 'Advertising_Filter_Policy'),
        #         self.get_param_value(label, 'OGF_LE_CTL'),
        #         self.get_param_value(label, 'OCF_LE_Set_Advertise_Parameter'))
        # elif label_name == "createConnection":
        #     self.sut.create_le_connection(
        #         self.get_param_value(label, 'Event_Code'),
        #         self.get_param_value(label, 'Reply_Len'),
        #         self.get_param_value(label, 'LE_Scan_Interval'),
        #         self.get_param_value(label, 'LE_Scan_Window'),
        #         self.get_param_value(label, 'Initiator_Filter_Policy'),
        #         self.get_param_value(label, 'Peer_Address_Type'),
        #         self.get_param_value(label, 'Own_Address_Type'),
        #         self.get_param_value(label, 'Conn_Interval_Min'),
        #         self.get_param_value(label, 'Conn_Interval_Max'),
        #         self.get_param_value(label, 'Conn_Latency'),
        #         self.get_param_value(label, 'Supervision_Timeout'),
        #         self.get_param_value(label, 'Minimum_CE_Length'),
        #         self.get_param_value(label, 'Maximum_CE_Length'),
        #         self.get_param_value(label, 'OGF_LE_CTL'),
        #         self.get_param_value(label, 'OCF_LE_Create_Connection'))
        # elif label_name == "createConnectionCancel":
        #     self.sut.create_le_connection_cancel(
        #         self.get_param_value(label, 'Event_Code'),
        #         self.get_param_value(label, 'Reply_Len'),
        #         self.get_param_value(label, 'OGF_LE_CTL'),
        #         self.get_param_value(label, 'OCF_LE_Create_Connection_Cancel'))
        # elif label_name == "inquiry":
        #     self.sut.inquiry(
        #         self.get_param_value(label, 'Inquiry_Length'),
        #         self.get_param_value(label, 'Max_Responses'),
        #         self.get_param_value(label, 'OGF_LINK_CTL'),
        #         self.get_param_value(label, 'OCF_INQUIRY'))
        # elif label_name == "read_remote_name":
        #     self.sut.read_remote_name(
        #         self.get_param_value(label, 'Address'))

        return physical_label


    """
    SUT SPECIFIC

    The labels supported by the adapter.
    return [label_pb2.Label]
    """
    def supported_labels(self):
        return [
                # The stimuli
                self.stimulus('landing_page_button_click'),

                # The responses
                self.response('landing_page_button_clicked', {'data': "string"}),
                # self.response('element_data', {
                #     'id': "string",
                #     'text': "string",
                # })
              ]


    """
    Instantiate a label type. In case a struct is wanted, define a dictionary
    using the wanted keys with instantiated values.
    param [String] param_type
    return [label_pb2.Label.Parameter.Value]
    """
    def instantiate_label_value(self, param_type):
        pb_value = label_pb2.Label.Parameter.Value()
        value = None

        # Check for array data type
        if isinstance(param_type, list):
            value = self.instantiate_label_value(param_type[0])[1]
            pb_value.array = value
            return pb_value

        if param_type == "string":
            pb_value.string = 'string'
            value = 'string'
        elif param_type == "integer":
            pb_value.integer = 1
            value = 1
        elif param_type == "decimal":
            pb_value.decimal = Decimal(1.0)
            value = Decimal(1.0)
        elif param_type == "boolean":
            pb_value.boolean = True
            value = True
        elif param_type == "date":
            pb_value.date = date.today()
            value = date.today()
        elif param_type == "time":
            pb_value.time = time.time_ns()
            value = time.time_ns()
        else:
            self.logger.warning("Handler", "UNKNOWN TYPE FOR PARAM/STIMULUS in generate type: {}".format(param_type))

        return pb_value, value


    """
    Obtain the value of a parameter from a label.
    param [label_pb2.Label] label
    param [String] param_name
    return [value]
    """
    def get_param_value(self, label, param_name):
        for param in label.parameters:
            if param.name == param_name:
                if param.value.HasField("string"):
                    return param.value.string
                elif param.value.HasField("integer"):
                    return param.value.integer
                elif param.value.HasField("decimal"):
                    return param.value.decimal
                elif param.value.HasField("boolean"):
                    return param.value.boolean
                elif param.value.HasField("date"):
                    return param.value.date
                elif param.value.HasField("time"):
                    return param.value.time
                elif param.value.HasField("array"):
                    return param.value.array
                elif param.value.HasField("struct"):
                    return param.value.struct
                elif param.value.HasField("hash_value"):
                    return param.value.hash_value
                else:
                    message = "Received an unknown label type"
                    self.broker_connection.close(reason=message)
                    return 0

        message = "Could not find param " + param_name + " in label " + label
        self.broker_connection.close(reason=message)
