#-*- coding:utf-8 -*-
from abc import ABCMeta
import serial
import threading
import time
from connection.connectionutils import ConnectionUtils
from connection.utils import Utils
from protocols.generateprotocol import GenerateProtocol

class Protocol(metaclass=ABCMeta): # metaclass: abstract
    """\
    Protocol as used by the ReaderThread. This base class provides empty
    implementations of all methods.
    """

    def connection_made(self, transport) -> None:
        """Called when reader thread is started"""

    def data_received(self, data) -> None:
        """Called with snippets received from the serial port"""

    def connection_lost(self, exc) -> None:
        """\
        Called when the serial port is closed or the reader loop terminated
        otherwise.
        """
        if isinstance(exc, Exception):
            raise exc


class ReaderThread(threading.Thread):
    """\
    Implement a serial port read loop and dispatch to a Protocol instance (like
    the asyncio.Protocol) but do it with threads.
    Calls to close() will close the serial port but it is also possible to just
    stop() this thread and continue the serial port instance otherwise.
    """
    def __init__(self, serial_instance, protocol_factory, connection_number, group_id):
        """\
        Initialize thread.
        Note that the serial_instance' timeout is set to one second!
        Other settings are not changed.
        """
        super(ReaderThread, self).__init__()
        self.daemon = True
        self.serial = serial_instance
        self.protocol_factory = protocol_factory
        self.alive = True
        self._lock = threading.Lock()
        self._connection_made = threading.Event()
        self.protocol = None
        self.end_flag = False
        self._connection_number = connection_number # full connection number
        self._group_id = group_id
        self.is_schedule_set = False
        self.is_point_set = False

    def stop(self) -> None:
        """Stop the reader thread"""
        self.alive = False
        try:
            if hasattr(self.serial, 'cancel_read'):
                self.serial.cancel_read()
        except KeyboardInterrupt as error: # KeyboardInterrupt 에러 발생
            raise error
        except:
            pass
        self.join(2)
    
    def run(self) -> None:
        """Reader loop"""
        if not hasattr(self.serial, 'cancel_read'):
            self.serial.timeout = 1
        self.protocol = self.protocol_factory()

        try:
            self.protocol.connection_made(self)
        except KeyboardInterrupt as error: # KeyboardInterrupt 에러 발생
            raise error
        except Exception as e:
            print("SerialProtocol Line 81", type(e), ",", str(e))
            self.alive = False
            self.protocol.connection_lost(e)
            self._connection_made.set()
            return
        error = None
        self._connection_made.set()
        while not self.end_flag: # 무한 루프 for 블루투스 동글
            #print("Threadworking")
            if not self.serial or (not self.serial.is_open and not self.alive): # 블루투스 동글이 끊겼을 때
                self.reconnect()
            while self.alive and self.serial and self.serial.is_open: # 무한 루프 for 시리얼 읽기
                try:
                    # read all that is there or wait for one byte (blocking)
                    #data = self.serial.read(self.serial.in_waiting or 1)
                    #data = self.serial.readline()
                    data = self.serial.read(1) # get 1 bytes per packet
                except KeyboardInterrupt as error: # KeyboardInterrupt 에러 발생
                    raise error
                except serial.SerialException as e:
                    # probably some I/O problem such as disconnected USB serial
                    # adapters -> exit
                    error = e
                    break
                else:
                    if data:
                        # make a separated try-except for called used code
                        try:
                            self.protocol.data_received(data)
                        except KeyboardInterrupt as error: # KeyboardInterrupt 에러 발생
                            raise error
                        except Exception as e:
                            print("SerialProtocol Line 113", type(e), ",", str(e))
                            error = e
                            break
            self.alive = False
            self.protocol.connection_lost(error)

    def write(self, data) -> None:
        """Thread safe writing (uses lock)"""
        with self._lock:
            print("Write data:", Utils().bytes_to_hex_str(data))
            self.serial.write(data)

    def close(self) -> None:
        """Close the serial port and exit reader thread (uses lock)"""
        # use the lock to let other threads finish writing
        try:
            with self._lock:
                # first stop reading, so that closing can be done on idle port
                self.end_flag = True
                self.stop()
        except KeyboardInterrupt as error: # KeyboardInterrupt 에러 발생
            raise error
        finally:
            self.serial.close()
            
    def connect(self) -> None:
        """
        Wait until connection is set up and return the transport and protocol
        instances.
        """
        if self.alive:
            self._connection_made.wait()
            if not self.alive:
                raise RuntimeError('connection_lost already called')
            return (self, self.protocol)
        else:
            raise RuntimeError('already stopped')

    # - -  context manager, returns protocol

    def reconnect(self) -> None:
        #print("reconnect")
        connection_number = self._connection_number
        group_id = self._group_id
        try:
            PORT = ConnectionUtils().find_bluetooth_dongle(GenerateProtocol.DongleInAction_bytes())
            self.serial = ConnectionUtils().connect_serial_URL(PORT)
            self.write(GenerateProtocol(connection_number, group_id).PingPongGn_connect_bytes())
            self.alive = True
        except KeyboardInterrupt as error: # KeyboardInterrupt 에러 발생
            raise error
        except Exception as error:
            print("SerialProtocol Line 165", type(error), ",", str(error))
            self.protocol.connection_lost(error)
    
    def set_robot_disconnect_flag(self, TF: bool) -> None:
        self.protocol.set_robot_disconnect_flag(TF)

    def __enter__(self) -> Protocol:
        """\
        Enter context handler. May raise RuntimeError in case the connection
        could not be created.
        """
        self.start()
        self._connection_made.wait()
        if not self.alive:
            raise RuntimeError('connection_lost already called')
        return self.protocol

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Leave context: close port"""
        self.close()