import time
import struct
import unicodedata
from threading import Thread
from .logger import Logger


"""
This class contains funcations that can be used as an API to interact
with a local Bluetooth Low Energy System on your device.

The way this is done is by interacting with the Host Controller Interface
of a BLE-chip through PyBluez.

We can interact with this interface using HCI commands that accept a binary
string as command paramaters. The specifications of BLE then contain information
about the memory size of these individual parameters.

In this context, we use the 'struct' module for (un)packing binary data.
Cheat Sheet to (un)pack parameters:
1 octet  == B (unsigned char)
2 octets == H (unsigned short)
4 octets == L (unsigned long)
8 octets == Q (unsigned long long)

For dealing with undefined memory sizes we split the number into their
respective sub parts
"""
class Sut:
    """
    Constructor
    """
    def __init__(self, responses, logger):
        self.responses = responses
        self.logger = logger
        self.dev_id = -1
        self.hci_socket = None

        # WARNING: Hardcoded peer address
        self.ble_peer_address = 0x300000000000


    """
    Special function: class name
    """
    def __name__(self):
        return "Sut"


    """
    Perform any cleanup if the SUT is closed
    """
    def stop(self):
        self.logger.info("Sut", "BT connection is closed and SUT is stopped")
        # bt.hci_close_dev(self.hci_socket.fileno())


    """
    Parse the SUT's response and add it to the response stack from the
    Handler class.
    """
    def handle_response_status(self, function_name, response):
        if response[1] != '':
            self.logger.error("Sut", "Error in function {} failed due to: {}".format(function_name, response[1]))

        self.logger.debug("Sut", "Add response from {}: {}".format(function_name, self.parse_status_code(response[0])))
        self.responses.append(self.parse_status_code(response[0]))


    """ Set the response formats for the plugin adapter. """
    def parse_status_code(self, bin_code):
        code = struct.unpack("<B", bin_code)[0]
        return ["status", {"code": "integer"}, {"code": code}]


    """ Parse the SUT's reponse on events and put it on the Handlers stack """
    def handle_inquiry_event_data(self, function_name, status, event_code, sub_event_code, data):
        response = [ "inquiry_event", { "status":"integer", "event_code":"integer", "sub_event_code":"integer", "data":"string" },
                   { "status" : status, "event_code" : event_code, "sub_event_code" : sub_event_code, "data" : data } ]
    
        self.logger.debug("Sut", "Add response from {}: {}".format(function_name, response))
        self.responses.append(response)


    """ Parse the SUT's reponse on events and put it on the Handlers stack """
    def handle_read_remote_name_data(self, function_name, status, data):
        response = [ "remote_name", { "status":"integer", "data":"string" },
               { "status" : status, "data" : data } ]
    
        self.logger.debug("Sut", "Add response from {}: {}".format(function_name, response))
        self.responses.append(response)


    """
    Store the device id and create the BLE socket as received
    by the model.
    """
    def set_device_id(self, device_id):
        # Socket ID of BLE
        self.dev_id = device_id
        # self.hci_socket = bt.hci_open_dev(self.dev_id)


    """
    HCI Command description:
    hci_send_req(hci_sock, ogf, ocf, event, reply len, [params], [timeout])

    Where each command is assigned a 2 byte Opcode used to uniquely identify different:
    - the OpCode Group Field (OGF)
    - OpCode Command Field (OCF)

    event: the event code of the expected response type.

    reply len: amount of return values you expect.

    [params]: Optional, needs to be a packed binary string (therefore pack)

    params: These are the individual HCI command params for which the input domains
            are defined within the BLE specifications.

    Below OpCodes according to bluetooth specifications 4.2

    OGF_Controller_Baseband         = 0x03
    OGF_LE_CTL                      = 0x08
    OCF_Set_Event_Mask              = 0x0001
    OCF_Reset                       = 0x0003
    OCF_LE_Set_Scan_Parameter       = 0x000B
    OCF_LE_Set_Advertise_Parameter  = 0x0006
    OCF_LE_Set_Advertising_Enable   = 0x000A
    OCF_LE_Set_Scan_Enable          = 0x000C
    OCF_LE_Create_Connection        = 0x000D
    OCF_LE_Create_Connection_Cancel = 0x000E
    """

    """
    HCI_Reset (Utility)
    - The Reset command will reset the Controller and the Link Manager on the BR/
      EDR Controller, the PAL on an AMP Controller, or the Link Layer on an LE
      Controller.
    """
    def ble_reset(self, ogf_controller_baseband = 0x03, ocf_reset = 0x0003):
        try:
            self.logger.debug("Sut", "Resetting the SUT")
            response = [struct.pack("<B", 0xFF), ""]

            # response[0] = bt.hci_send_req(self.hci_socket,
            #                               ogf_controller_baseband,
            #                               ocf_reset,
            #                               bt.EVT_CMD_COMPLETE,
            #                               1)
        except Exception as e:
            response[0] = struct.pack("<B", 0xFF)
            response[1] = str(e)

        return [self.parse_status_code(response[0]), response[1]]


    """
    HCI Read remote name

    Read the user friendly name of the device using the given address.
    btAddress contains the device address as a srting value using a format '00:AA:77:BB:99:FF'.
    """
    def read_remote_name(self, btAddress):
        # Retreive a user friendly name for the given address
        try:
            self.logger.debug("Sut", "Read remote name for address {}".format(btAddress))
            # remote_name = bt.hci_read_remote_name(self.hci_socket, btAddress)
            # self.handle_read_remote_name_data("read remote name", 0x00, remote_name)

        except Exception as e:
            self.handle_read_remote_name_data("read remote name", 0xFF, "Exception while reading user friendly name: " + str(e))


    """
    HCI_LE_Set_Scan_Enable command (Model):
    - This command allows you to enable and disable advertising.

    Parameters (size):
    - LE_Scan_Enable (1 octet)
    - Filter_Duplicates (1 octet)
    """
    def enable_ble_scanning(self, event_code, reply_len, scan_enable, filter_duplicates,
             ogf_le_ctl, ocf_le_set_scan_enable):
        self.logger.debug("Sut", "Trying to set scanning")

        try:
            response = [struct.pack("<B", 0xFF), ""]

            scan_enable_param = struct.pack("<BB",
                                            scan_enable,
                                            filter_duplicates)

            # response[0] = bt.hci_send_req(self.hci_socket,
            #                               ogf_le_ctl,
            #                               ocf_le_set_scan_enable,
            #                               event_code,
            #                               reply_len,
            #                               scan_enable_param)
        except Exception as e:
            response[0] = struct.pack("<B", 0xFF)
            response[1] = str(e)

        return self.handle_response_status("enable_ble_scanning", response)


    """
    HCI_LE_Set_Scan_Parameters (Model):
    - This command allows you to set the configurations related to advertising.

    Parameters (size):
    - LE_Scan_Type (1 octet)
    - LE_Scan_Interval (2 octets)
    - LE_Scan_Window (2 octets)
    - Own_Address_Type (1 octet)
    - Scanning_Filter_Policy (1 octet)
    """
    def set_ble_scan_parameter(self, event_code, reply_len, scan_type,
                               scan_interval, scan_window, own_adress_type,
                               scanning_filter_policy, ogf_le_ctl,
                               ocf_le_set_scan_parameter):
        self.logger.debug("Sut", "Trying to set scan params")

        try:
            response = [struct.pack("<B", 0xFF), ""]

            scan_set_params = struct.pack("<BHHBB",
                                        scan_type,
                                        scan_interval,
                                        scan_window,
                                        own_adress_type,
                                        scanning_filter_policy)

            # response[0] = bt.hci_send_req(self.hci_socket,
            #                               ogf_le_ctl,
            #                               ocf_le_set_scan_parameter,
            #                               event_code,
            #                               reply_len,
            #                               scan_set_params)
        except Exception as e:
            response[0] = struct.pack("<B", 0xFF)
            response[1] = str(e)

        return self.handle_response_status("set_ble_scan_parameter", response)


    """
    HCI_LE_Set_Advertising_Enable (Model):
    - This command allows you to enable and disable advertising.

    Parameters (size):
    - Advertising_Enable (1 octet)
    """
    def enable_ble_advertising(self, event_code, reply_len,
                               advertising_enable, ogf_le_ctl,
                               ocf_le_set_advertising_enable):
        self.logger.debug("Sut", "Trying to set advertising")

        try:
            response = [struct.pack("<B", 0xFF), ""]

            ad_enable_param = struct.pack("<B", advertising_enable)

            # response[0] = bt.hci_send_req(self.hci_socket,
            #                               ogf_le_ctl,
            #                               ocf_le_set_advertising_enable,
            #                               event_code,
            #                               reply_len,
            #                               ad_enable_param)
        except Exception as e:
            response[0] = struct.pack("<B", 0xFF)
            response[1] = str(e)

        return self.handle_response_status("enable_ble_advertising", response)


    """
    HCI_LE_Set_Advertising_Parameters (Model):
    This command allows you to set the configurations related to advertising.

    Parameters (size):
    - Advertising_Interval_Min (2 octets)
    - Advertising_Interval_Max (2 octets)
    - Advertising_Type (1 octet)
    - Own_Address_Type (1 octet)
    - Peer_Address_Type (1 octet)
    - Peer_Address (6 octets)
    - Advertising_Channel_Map (1 octet)
    - Advertising_Filter_Policy (1 octet)
    """
    def set_ble_advertise_parameter(self, event_code, reply_len,
                                    advertising_interval_min,
                                    advertising_interval_max,
                                    advertising_type, own_adress_type,
                                    peer_address_type,
                                    advertising_channel_map,
                                    advertising_filter_policy,
                                    ogf_le_ctl, ocf_le_set_advertise_parameter):
        self.logger.debug("Sut", "Trying to set advertise params")

        try:
            response = [struct.pack("<B", 0xFF), ""]

            # Peer adress needs to be packed into 6 bytes however
            # this is not directly possible with struct so we pack it into a 2 and 4
            # byte (HL)
            first_2_peer_address = self.ble_peer_address >> 16 & 0xffff
            last_4_peer_address = self.ble_peer_address & 0xffffffff

            advertise_set_params = struct.pack("<HHBBBHLBB",
                                                advertising_interval_min,
                                                advertising_interval_max,
                                                advertising_type,
                                                own_adress_type,
                                                peer_address_type,
                                                first_2_peer_address,
                                                last_4_peer_address,
                                                advertising_channel_map,
                                                advertising_filter_policy)

            # response[0] = bt.hci_send_req(self.hci_socket,
            #                               ogf_le_ctl,
            #                               ocf_le_set_advertise_parameter,
            #                               event_code,
            #                               reply_len,
            #                               advertise_set_params)
        except Exception as e:
            response[0] = struct.pack("<B", 0xFF)
            response[1] = str(e)

        return self.handle_response_status("set_ble_advertise_parameter", response)


    """
    HCI_LE_Create_Connection (Model):
    - This command allows a device to initiate a BLE connection

    Parameters (size):
    - LE_Scan_Interval (2 octets)
    - LE_Scan_Window (2 octets)
    - Initiator_Filter_Policy (1 octet)
    - Peer_Address_Type (1 octet)
    - Peer_Address (6 octets)
    - Own_Address_Type (1 octet)
    - Conn_Interval_Min (2 octets)
    - Conn_Interval_Max (2 octets)
    - Conn_Latency (2 octets)
    - Supervision_Timeout (2 octets)
    - Minimum_CE_Length (2 octets)
    - Maximum_CE_Length (2 octets)
    """
    def create_le_connection(self, event_code, reply_len, le_scan_interval,
                             le_scan_window, initiator_filter_policy,
                             peer_address_type, own_address_type,
                             conn_interval_min, conn_interval_max,
                             conn_latency, supervision_timeout,
                             minimum_ce_length, maximum_ce_length,
                             ogf_le_ctl, ocf_le_create_connection):
        self.logger.debug("Sut", "Trying to create a connection")
        try:
            response = [struct.pack("<B", 0xFF), ""]

            # Peer adress needs to be packed into 6 bytes however
            # this is not directly possible with struct so we pack it into a 2 and 4
            # byte (HL)
            first_2_peer_address = self.ble_peer_address >> 16 & 0xffff
            last_4_peer_address = self.ble_peer_address & 0xffffffff

            create_connection_param = struct.pack("<HHBBHLBHHHHHH",
                                                  le_scan_interval,
                                                  le_scan_window,
                                                  initiator_filter_policy,
                                                  peer_address_type,
                                                  first_2_peer_address,
                                                  last_4_peer_address,
                                                  own_address_type,
                                                  conn_interval_min,
                                                  conn_interval_max,
                                                  conn_latency,
                                                  supervision_timeout,
                                                  minimum_ce_length,
                                                  maximum_ce_length)

            # response[0] = bt.hci_send_req(self.hci_socket,
            #                               ogf_le_ctl,
            #                               ocf_le_create_connection,
            #                               event_code,
            #                               reply_len,
            #                               create_connection_param)
        except Exception as e:
            response[0] = struct.pack("<B", 0xFF)
            response[1] = str(e)

        return self.handle_response_status("create_le_connection", response)


    """
    HCI_LE_Create_Connection_Cancel (Model)
    - Funtion to stop the creation of a connection after it has been initiated.
    """
    def create_le_connection_cancel(self, event_code, reply_len, ogf_le_ctl,
                                    ocf_le_create_connection_cancel):
        self.logger.debug("Sut", "Trying connection cancel")

        try:
            response = [struct.pack("<B", 0xFF), ""]

            # response[0] = bt.hci_send_req(self.hci_socket,
            #                               ogf_le_ctl,
            #                               ocf_le_create_connection_cancel,
            #                               event_code, reply_len)
        except Exception as e:
            response[0] = struct.pack("<B", 0xFF)
            response[1] = str(e)

        return self.handle_response_status("create_le_connection_cancel", response)


    """
    HCI_LINK_INQUIRY (Model)
    - Funtion to initiate an inquiry and receive events from the controller.

    Parameters (size):
    - inquire_length (1 octet)
    - max_responses (1 octet)
    """
    # TODO: decouple the inquiry command from the inquire_events generated by BT controller
    # Create a thread to decouple the command from the execution of the inquiry command in the SUT.
    def inquiry(self, 
                #event_code,
                #reply_len,
                inquire_length,
                max_responses,
                ogf_link_ctl,
                ocf_inquiry):

        try:
            response_status = [struct.pack("<B", 0xFF), ""]

            # # Allow all events to be handled
            # flt = bt.hci_filter_new()
            # bt.hci_filter_all_ptypes(flt)
            # bt.hci_filter_all_events(flt)
            # self.hci_socket.setsockopt(bt.SOL_HCI, bt.HCI_FILTER, flt)

            # WARNING: Used hardcoded assignment number 0x9e8b33
            # inquiry_params = struct.pack("BBBBB", 0x33, 0x8b, 0x9e, inquire_length, max_responses)

            # Send an inquiry command to the controller and wait for the responses
            # bt.hci_send_cmd(self.hci_socket, ogf_link_ctl, ocf_inquiry, inquiry_params)

            # Initiate a infinite loop and wait for the inquiry command to complete
            while True:
                # pkt = self.hci_socket.recv(3+bt.HCI_MAX_EVENT_SIZE+1)
                # ptype, event, plen = struct.unpack("<BBB", pkt[:3])
                # self.logger.debug("Sut", "Received event with packet type: {} event code: {} and packet length {}".format(ptype, event, plen))
                # event_params = pkt[3:]

                # Handle command complete info
                # if event == bt.EVT_CMD_COMPLETE:
                #     self.logger.debug("Sut", "Received EVT_CMD_COMPLETE")
                #     response, pnum, opcode = struct.unpack("<BBH", pkt[3:])
                #     response_status[0] = struct.pack("<B", response)
                #     self.handle_response_status("inquiry", response_status)
                #     self.logger.debug("Sut", "Status {} Number of packets: {} Opcode: {}".format(response_status[0], pnum, opcode))

                # Handle command status info is send as soon as the controller has started the inquiry process
                # elif event == bt.EVT_CMD_STATUS:
                #     self.logger.debug("Sut", "Received EVT_CMD_STATUS")
                #     response, pnum, opcode = struct.unpack("<BBH", pkt[3:])
                #     response_status[0] = struct.pack("<B", response)
                #     self.handle_response_status("inquiry", response_status)
                #     self.logger.debug("Sut", "Status {} Number of packets: {} Opcode: {}".format(response_status[0], pnum, opcode))

                # Handle information of scanned devices
                # elif event == bt.EVT_INQUIRY_RESULT:
                #     self.logger.debug("Sut", "Received EVT_INQUIRY_RESULT")
                #     pkt = pkt[3:]
                #     nrsp = bluetooth.get_byte(pkt[0])
                #     for i in range(nrsp):
                #         addr = bt.ba2str(pkt[1+6*i:1+6*i+6])
                #         self.handle_inquiry_event_data('inquiry', 0x00, ocf_inquiry, bt.EVT_INQUIRY_RESULT, addr)
                #         self.logger.debug("Sut", "Found device address {} (no RSSI)".format(addr))

                # Handle information of scanned devices including and RSSI
                # elif event == bt.EVT_INQUIRY_RESULT_WITH_RSSI:
                #     self.logger.debug("Sut", "Received EVT_INQUIRY_RESULT_WITH_RSSI")
                #     pkt = pkt[3:]
                #     nrsp = bluetooth.get_byte(pkt[0])
                #     for i in range(nrsp):
                #         addr = bt.ba2str(pkt[1+6*i:1+6*i+6])
                #         rssi = bluetooth.byte_to_signed_int(bluetooth.get_byte(pkt[1 + 13 * nrsp + i]))
                #         self.handle_inquiry_event_data('inquiry', 0x00, ocf_inquiry, bt.EVT_INQUIRY_RESULT_WITH_RSSI, addr)
                #         self.logger.debug("Sut", "Found device address {} RSSI {}".format(addr, rssi))

                # Handle a inquiry complete command and break the loop afterwards
                # elif event == bt.EVT_INQUIRY_COMPLETE:
                #     self.logger.debug("Sut", "Received EVT_INQUIRY_COMPLETE")
                #     status = bluetooth.get_byte(pkt[3])
                #     self.handle_inquiry_event_data("inquiry", status, ocf_inquiry, bt.EVT_INQUIRY_COMPLETE, "")
                #     self.logger.debug("Sut", "Status: {}".format(status))
                #     break

        except Exception as e:
            response_status[0] = struct.pack("<B", 0xFF)
            response_status[1] = str(e)
            self.handle_response_status("inquiry", response_status)
