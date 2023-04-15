import websocket
import sys
import ssl

sys.path.insert(0, './api')
import announcement_pb2
import configuration_pb2
import message_pb2

"""
The {BrokerConnection} holds the connection with the broker. It is responsible
for handling the websocket as well as encoding/decoding the Protobuf messages.

The {BrokerConnection} calls back on the {AdapterCore}.
"""
class BrokerConnection:
    """
    param [String] url The websocket URL of the AMP instance that
    should be connected to.
    param [String] token; Token to authorize with.
    param [Boolean] extra_logs
    """
    def __init__(self, url, token, extra_logs, logger):
        self.url = url
        self.token = token
        self.adapter_core = None # callback to adapter; register separately
        self.websocket = None # reference to websocket; initialized on #connect
        self.extra_logs = extra_logs
        self.logger = logger


    """
    Set the adapter core object reference.
    param [AdapterCore] adapter_core
    """
    def register_adapter_core(self, adapter_core):
        self.adapter_core = adapter_core


    """ Handler for when the connection is openen with AMP.
    param [WebSocketApp] ws
    """ 
    def on_open(self, ws):
        self.logger.info("BrokerConnection", "Successfully opened a connection")
        self.adapter_core.broker_connection_opened()


    """
    Handler for when the connection is closed with AMP.
    param [WebSocketApp] ws
    param [Integer] close_status_code
    param [String] close_msg
    """
    def on_close(self, ws, close_status_code, close_msg):
        self.logger.info("BrokerConnection", "Stopped connection with code: {}".format(close_status_code))
        self.logger.info("BrokerConnection", "The stop reason is: {}".format(close_msg))
        self.websocket.close()

        # Stop the SUT response handler thread
        if self.adapter_core != None and self.adapter_core.handler != None:
            self.adapter_core.handler.stop_sut_thread = True


    """
    Handler for when a message is received from AMP.
    param [WebSocketApp] ws
    param [bytes] message
    """
    def on_message(self, ws, message):
        self.logger.debug("BrokerConnection", "Received a message")
        self.parse_and_handle_message(message)


    """
    Handler for when an error occurs with the connection to AMP
    param [WebSocketApp] ws
    param [String] err
    """
    def on_error(self, ws, err):
        print(err)
        self.logger.error("BrokerConnection", "Got a connection error: {}".format(str(err)))
        self.adapter_core.send_error(str(err))

        self.logger.debug("BrokerConnection", "Closing the connection...")
        self.websocket.close()


    """
    TODO Handle configurations

    Send an announcement_pb2.Announcement to AMP.
    param [String] name
    param [[label_pb2.Label]] pb_supported_labels
    param [configuration_pb2.Configuration] configuration
    """
    def send_announcement(self, name, pb_supported_labels, configuration):
        self.logger.info("BrokerConnection", "Announcing")
        pb_configuration = configuration_pb2.Configuration(items=[])

        pb_announcement = announcement_pb2.Announcement(name=name,
            labels=pb_supported_labels, configuration=pb_configuration)

        pb_message = message_pb2.Message(announcement=pb_announcement)

        self.send_message(pb_message)


    """ Send a message_pb2.Ready message to AMP. """
    def send_ready(self):
        pb_ready = message_pb2.Message.Ready()
        pb_message = message_pb2.Message(ready=pb_ready)
        self.send_message(pb_message)


    """
    Confirm a received stimulus by sending it back to AMP.
    param [label_pb2.Label] pb_label
    param [String] physical_label
    param [Integer] timestamp
    param [Integer] correlation_id
    """
    def send_stimulus(self, pb_label, physical_label, timestamp, correlation_id):
        self.logger.debug("BrokerConnection", "Sending stimulus")

        if physical_label:
            pb_label.physical_label = physical_label

        pb_label.timestamp = timestamp
        pb_label.correlation_id = correlation_id

        self.send_message(message_pb2.Message(label=pb_label))


    """
    Send the SUT's response back to AMP.
    param [label_pb2.Label] pb_label
    param [String] physical_label
    param [Integer] timestamp
    """
    def send_response(self, pb_label, physical_label, timestamp):
        self.logger.debug("BrokerConnection", "Sending response")

        if physical_label != None:
            pb_label = physical_label

        pb_label.timestamp = timestamp

        self.send_message(message_pb2.Message(label=pb_label))


    """
    Send an Error message to AMP.
    param [String] message
    """
    def send_error(self, message):
        pb_error = message_pb2.Message.Error(message=message)
        self.send_message(message_pb2.Message(error=pb_error))


    """ Connect to AMP. """
    def connect(self):
        self.logger.info("BrokerConnection", "Connecting to AMP")

        if self.extra_logs:
            websocket.enableTrace(True)

        # Use lambda functions to correctly pass the self variable.
        self.websocket = websocket.WebSocketApp(self.url,
            on_open= lambda ws: self.on_open(ws),
            on_close= lambda ws, close_status_code, close_msg: self.on_close(ws, close_status_code, close_msg),
            on_message= lambda ws,msg: self.on_message(ws, msg),
            on_error=lambda ws,msg: self.on_error(ws, msg),
            header={"Authorization":"Bearer " + self.token})

        self.websocket.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})


    """
    Close the websocket with the given response close code and close
    reason.
    param [String] reason
    param [Integer] code
    """
    def close(self, reason="", code=-1):
        if self.websocket != None:
            self.logger.info("BrokerConnection", "Closing the connection due to: {}".format(reason))
            self.logger.info("BrokerConnection", "With error code: {}".format(code))
            self.websocket.close()

            # Stop the SUT response handler thread
            if self.adapter_core != None and self.adapter_core.handler != None:
                self.adapter_core.handler.stop_sut_thread = True
        else:
            self.logger.warning("BrokerConnection", "No websocket initialized to close")


    """
    Parses and handles a byte array from the web-socket into
    the correct protobuff object.
    param [bytes] message
    """
    def parse_and_handle_message(self, message):
        pb_message = message_pb2.Message()

        try:
            pb_message.ParseFromString(message)
        except Exception as e:
            self.logger.error("BrokerConnection", "Could not decode message due to: {}".format(e))

        if pb_message.HasField("configuration"):
            self.logger.debug("BrokerConnection", "Received a configuration")
            self.adapter_core.configuration_received(pb_message.configuration)
        elif pb_message.HasField("error"):
            self.logger.debug("BrokerConnection", "Received an error")
            self.adapter_core.error_received(message.error.message)
        elif pb_message.HasField("label"):
            self.logger.debug("BrokerConnection", "Received a label")
            self.adapter_core.label_received(pb_message.label,
                pb_message.label.correlation_id)
        elif pb_message.HasField("reset"):
            self.logger.debug("BrokerConnection", "Received a reset")
            self.adapter_core.reset_received()
        elif pb_message.HasField("ready"):
            self.logger.debug("BrokerConnection", "Received ready, this should not be send")
        else:
            self.logger.debug("BrokerConnection", "Unknown message type: {}".format(pb_message))


    """
    Sends the given `protobuff message` to AMP
    param [message_pb2.Message] pb_message
    """
    def send_message(self, pb_message):
        if self.websocket is None:
            self.logger.warning("BrokerConnection", "No connection to websocket (yet). Is the adapter connected to AMP?")
        else:
            try:
                # send a protobuff message using binary data.
                self.websocket.send(pb_message.SerializeToString(),
                    websocket.ABNF.OPCODE_BINARY)
                self.logger.debug("BrokerConnection", "Success send")
            except Exception as e:
                self.logger.error("BrokerConnection", "Failed sending message, exception: {}".format(e))
