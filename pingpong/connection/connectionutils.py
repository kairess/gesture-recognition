import serial
import serial.tools.list_ports
import time

class ConnectionUtils():
    # 포트 찾기
    @staticmethod
    def find_bluetooth_dongle(connect_bytes) -> str:
        not_found_flag = False
        PORT = ""
        while not PORT:
            ports = list(serial.tools.list_ports.comports())
            port_len = len(ports)
            for i in range(port_len):
                p = ports[i]
                print(p)
                try:
                    # 9600으로 한 번 보내기 (이전에 연결 했었다가 다시 115200으로 PingPongDongle_connect_bytes를 보내면 응답을 안 받음.)
                    ser = serial.serial_for_url(str(p.device), baudrate=9600, timeout=0.5, write_timeout=1) 
                    ser.write(connect_bytes)
                    ser.close()
                    time.sleep(1) # 1초 sleep (바로 하면 안 받음)
                    ser = serial.serial_for_url(str(p.device), baudrate=115200, timeout=1, write_timeout=0.5)
                    ser.write(connect_bytes)
                    data = ser.read(11)
                    ser.close()
                    if data == connect_bytes:
                        print("Found device: " + str(p.description))
                        PORT = str(p.device)
                        return PORT
                    elif data == b"":
                        #print("PingPongDongle_connect_bytes timeout. (1 secs.)")
                        #print('data = b""')
                        pass
                    else:
                        print("What device is this?")
                except Exception as error:
                    if type(error) in (serial.serialutil.SerialTimeoutException, serial.serialutil.SerialException):
                        try:
                            ser.close()
                        except UnboundLocalError:
                            pass
                        except Exception as error:
                            raise error
                        #print("something wrong")
                    else:
                        raise error
            if not_found_flag == False:
                print("Device not found. Please connect the BluetoothUSB, or shut down other port connected program.")
                print("Reconnecting serial...")
                not_found_flag = True

    # 시리얼 연결
    @staticmethod
    def connect_serial_URL(port) -> serial:
        try:
            ser = serial.serial_for_url(port, baudrate=115200, timeout=None) # baurate 9600 does not work. baudrate is 115200.
            return ser
        except KeyboardInterrupt as error: # KeyboardInterrupt 에러 발생
            raise error
        except Exception as error1:
            print("ConnectionUtils Line 61", type(error1), ",", str(error1))
            return None