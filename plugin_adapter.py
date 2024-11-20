import socket
import sys
import argparse

from plugin_adapter_components.logger import Logger
from plugin_adapter_components.adapter_core import AdapterCore
from plugin_adapter_components.broker_connection import BrokerConnection
from plugin_adapter_components.handler import Handler

"""
Custom function to convert string to boolean
"""
def str2bool(value):
    if value.lower() in ('true', 't', '1'):
        return True
    elif value.lower() in ('false', 'f', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError("Boolean value expected (True/False).")

"""
Start the plugin adapter to connect with AMP.
"""
def start_plugin_adapter(name, url, token, log_level, extra_logs, headless):
    logger = Logger()
    logger.log_level(log_level & logger.LOG_ALL)

    broker_connection = BrokerConnection(url, token, extra_logs, logger)
    handler = Handler(logger, headless)

    adapter_core = AdapterCore(name, broker_connection, handler, logger)

    broker_connection.register_adapter_core(adapter_core)
    handler.register_adapter_core(adapter_core)

    adapter_core.start()


if __name__ == '__main__':
    print("Parsing arguments")
    parser = argparse.ArgumentParser()
    parser.add_argument('-c','--channel',
        help='Model channel name: "channel_name"', required=True)
    parser.add_argument('-n','--name',
        help='User\'s name reference: "user_name"', required=True)
    parser.add_argument('-u','--url',
        help='AMP Adapter URL reference: "wss://..."', required=True)
    parser.add_argument('-t','--token',
        help='AMP Adapter Token: "kjhsdkhk..."', required=True)
    parser.add_argument('-ll','--log_level',
        help='AMP Adapter logger level: 1 = error, 2 = warning, 4 = info, 8 = debug or 15 = all', required=False)
    parser.add_argument('-el','--extra_logs',
        help='Show extra logs related to the socket: True', required=False)
    parser.add_argument('--headless',
        help='Run web tests in headless mode', required=False)

    args = parser.parse_args()

    # Create the user name as displayed on the adapter page of AMP
    name = args.channel + "@" + args.name

    if args.log_level == None:
        log_level = Logger.LOG_INFO
    else:
        log_level = int(args.log_level)

    extra_logs = args.extra_logs
    if args.extra_logs == None or args.extra_logs != "True":
        extra_logs = False

    if args.headless is None:
        headless = True
    else:
        headless = args.headless if isinstance(args.headless, bool) else str2bool(args.headless)

    start_plugin_adapter(name, args.url, args.token, log_level, extra_logs, headless)
