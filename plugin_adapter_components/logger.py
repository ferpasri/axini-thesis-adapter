"""
This class contains funcations that can be used as an API to interact
with a local Bluetooth Low Energy System on your device.

The way this is done is by interacting with the Host Controller Interface
of a BLE-chip through PyBluez.

"""

import inspect
import types
from typing import cast
from datetime import datetime

class Logger:
    #Constants used to indicate the log level
    LOG_ERROR       = 1
    LOG_WARNING     = 2
    LOG_INFO        = 3
    LOG_DEBUG       = 4
    LOG_ALL         = 4


    def __init__(self):
        self.logLevel = self.LOG_WARNING     # By default show only the warnings and errors


    """
    Set logging level to any of the following values or a combination of each
    param [Integer] level
    """
    def log_level(self, level):
        self.logLevel = level


    """
    Dump a logger info message to the stdout
    param [String] class_name; shall be the class name of the function calling the logger
    param [String] msg; shall contain message to log
    """
    def info(self, class_name, msg):
        if self.LOG_INFO <= self.logLevel:
            fname = inspect.currentframe().f_back.f_code.co_name
            m = "[{}] INFO    {}::{}: {}".format(self.timestamp(), class_name, fname, msg)
            self.log_entry(self.LOG_INFO, m)


    """
    Dump a logger debug message to the stdout
    param [String] class_name; shall be the class name of the function calling the logger
    param [String] msg; shall contain message to log
    """
    def debug(self, class_name, msg):
        if self.LOG_DEBUG <= self.logLevel:
            fname = inspect.currentframe().f_back.f_code.co_name
            m = "[{}] DEBUG   {}::{}: {}".format(self.timestamp(), class_name, fname, msg)
            self.log_entry(self.LOG_DEBUG, m)


    """
    Dump a logger warning message to the stdout
    param [String] class_name; shall be the class name of the function calling the logger
    param [String] msg; shall contain message to log
    """
    def warning(self, class_name, msg):
        if self.LOG_WARNING <= self.logLevel:
            fname = inspect.currentframe().f_back.f_code.co_name
            m = "[{}] WARNING {}::{}: {}".format(self.timestamp(), class_name, fname, msg)
            self.log_entry(self.LOG_WARNING, m)


    """
    Dump a logger error message to the stdout
    param [String] class_name; shall be the class name of the function calling the logger
    param [String] msg; shall contain message to log
    """
    def error(self, class_name, msg):
        if self.LOG_ERROR <= self.logLevel:
            fname = inspect.currentframe().f_back.f_code.co_name
            m = "[{}] ERROR   {}::{}: {}".format(self.timestamp(), class_name, fname, msg)
            self.log_entry(self.LOG_ERROR, m)


    """
    Write the log message to the stdout (future to log file?)
    param [String] class_name; shall be the class name of the function calling the logger
    param [String] msg; shall contain message to log
    """
    def log_entry(self, level, msg):
        if level <= self.logLevel:
            print(msg)


    """
    Retrieve the actual timestamp to be added to each log entry
    """
    def timestamp(self):
        return datetime.now()
