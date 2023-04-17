import sys
import time
from .state_machine import StateMachine
import logging

sys.path.insert(0, './api')
import announcement_pb2
import configuration_pb2
import message_pb2
import label_pb2

"""
The {AdapterCore} holds the {StateMachine} of the plugin adapter. It
communicates with the {BrokerConnection} and the plugin adapter {Handler}.

This class implements the core of a plugin-adapter. It handles the connection
to the broker (@broker_connection) and the connection to the sut (via
@handler).
One can see the {AdapterCore} as the generic part of the adapter and the
{Handler} as the implementation specific part of the adapter.
"""
class AdapterCore():
    def __init__(self, name, broker_connection, handler, logger):
        self.name = name
        self.broker_connection = broker_connection
        self.handler = handler
        self.logger = logger
        self.state_machine = StateMachine()


    """ Start the adapter core which will open a connection with AMP. """
    def start(self):
        if self.state_machine.is_disconnected():
            self.logger.info("AdapterCore", "Connecting to broker")
            self.broker_connection.connect()
        else:
            self.logger.info("AdapterCore", "Connection started while already connected")


    """ Broker call back for when the connection is openen with AMP. """
    def broker_connection_opened(self):
        if self.state_machine.is_disconnected():
            self.state_machine.set_connected()

            self.broker_connection.send_announcement(self.name,
                self.handler.supported_labels(), self.handler.configuration)

            self.state_machine.set_announced()
        else:
            self.logger.info("AdapterCore", "Connection opened while already connected")


    """
    TODO DO SOMETHING WITH CONFIGURATION

    Broker call back when a Configuration Message is received from AMP.
    param [configuration_pb2.Configuration] configuration
    """
    def configuration_received(self, configuration):
        if self.state_machine.is_announced():
            self.logger.info("AdapterCore", "Configuration received")
            self.state_machine.set_configured()

            # Start the SUT
            self.logger.info("AdapterCore", "Connecting to the SUT")
            try:
                self.handler.start()
            except Exception as e:
                self.logger.error("AdapterCore", "Error connection to the SUT: {}".format(e))
                self.send_error(str(e))
                return

            self.logger.debug("AdapterCore", "Sending ready")
            self.broker_connection.send_ready()
            self.state_machine.set_ready()
        elif self.state_machine.is_connected():
            message = "Configuration received while not yet announced"
            self.logger.error("AdapterCore", "{}".format(message))
            self.send_error(message)
        else:
            message = "Configuration received while already configured"
            self.logger.error("AdapterCore", "{}".format(message))
            self.send_error(message)


    """
    Broker call back when a Label Message is received from AMP.
    param [label_pb2.Label] label
    param [Integer] correlation_id
    """
    def label_received(self, label, correlation_id):
        if self.state_machine.is_ready():
            # Check if type label_pb2.Label.LabelType.STIMULUS
            if label.type != 0:
                message = "Label is not a stimulus"
                self.logger.error("AdapterCore", "{}".format(message))
                self.send_error(message)

            try:
                # Perform the stimulus action which could trigger a
                # response.
                self.logger.debug("AdapterCore", "Stimulating label: {}".format(label.label))
                physical_label = self.handler.stimulate(label)
            except Exception as e:
                logging.exception(e)
                e = str(e)
                self.logger.error("AdapterCore", "exception: {}".format(e))
                self.send_error("error while stimulating the SUT: " + e)

            # Confirm the label
            self.logger.debug("AdapterCore", "Confirming stimulus label: {}".format(label.label))
            self.broker_connection.send_stimulus(label, physical_label,
                time.time_ns(), correlation_id)
        else:
            message = "Label received while not ready"
            self.logger.error("AdapterCore", "{}".format(message))
            self.send_error(message)


    """ Broker call back when a Reset Message is received. """
    def reset_received(self):
        if self.state_machine.is_ready():
            self.logger.debug("AdapterCore", "Reset message received")

            try:
                # TODO: possibly handle SUT if it   cant reset
                # print(self.handler)
                self.handler.reset()
                # print(response)

                # if response[1] != '':
                #     message = "Resetting the SUT failed due to: " + response[1]
                #     self.logger.error("AdapterCore", "{}".format(message))
                #     self.send_error(message)
                #     return
            except Exception as e:
                message = "Error while resetting connection to the SUT: " + str(e)
                self.logger.error("AdapterCore", "{}".format(message))
                self.send_error(message)
                return

            self.logger.debug("AdapterCore", "Sending ready")
            self.broker_connection.send_ready()
            self.state_machine.set_ready()
        else:
            message = 'Reset received while not ready'
            self.logger.error("AdapterCore", "{}".format(message))
            self.send_error(message)


    """
    Broker call back when a Error Message is received.
    param [String] message
    """
    def error_received(self, message):
        self.state_machine.set_error()
        message = "Error message received" + message
        self.logger.error("AdapterCore", "{}".format(message))
        # NOTE: we do not send an error message back.
        self.broker_connection.close(reason=message)


    """
    Send an error to the broker_connection and close the connection
    param [String] message
    """
    def send_error(self, message):
        if self.handler != None:
            self.handler.stop_threads = True

        self.broker_connection.send_error(message)
        self.broker_connection.close(reason=message)


    """
    Send the response from the SUT back to AMP
    param [label_pb2.Label] pb_label
    param [String] physical_label
    param [Integer] timestamp
    """
    def send_response(self, pb_label, physical_label, timestamp):
        # Check if type is label_pb2.Label.LabelType.RESPONSE
        if pb_label.type == 1:
            self.broker_connection.send_response(pb_label, physical_label,
                timestamp)
        else:
            message = "Response label is not of type"
            self.logger.error("AdapterCore", "{}".format(message))
            self.send_error("Response label is not of type")
