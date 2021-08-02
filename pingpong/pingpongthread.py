# Environment: Windows x64, Python x64 3.6.6

from connection.serialprotocol import ReaderThread
from connection.connectionutils import ConnectionUtils
from connection.utils import Utils
from connection.rawprotocol import rawProtocol
from protocols.generateprotocol import GenerateProtocol
from operations.operationderived import OperationDerived
# from ai.aiderived import AiDerived
from robotstatus import RobotStatus
import time

class SingletonMeta(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonMeta, cls).__call__(*args, **kwargs)
        else:
            print("Warning. Instance of PingPongThread is singleton. You cannnot change arguments.")
        return cls._instances[cls]
    
    def __del__(self):
        self._instance = None

class PingPongThread(ReaderThread, OperationDerived, metaclass=SingletonMeta):
    _is_start = False
    def __init__(self, number, group_id=None, tensorflow_no_warnings=True):
        Utils.integer_check(number)
        group_id = Utils.check_group_id(group_id)
        if 1 <= number and number <= 8: # 1개 이상 8개 이하 
            self._robot_status = {}
            self._robot_status[group_id] = RobotStatus(number, group_id) # 로봇 상태 저장 (dict의 key는 discovery group)
        else:
            raise ValueError("PingPong robot can connect only with 1 to 8 robots.")
        self._GenerateProtocolInstance = GenerateProtocol(number, group_id) # GenrateProtocol instance 생성
        OperationDerived.__init__(self, number, group_id, self._robot_status, self._start_check, self._write) # MotorOperation 초기화
        # AiDerived.__init__(self, tensorflow_no_warnings) # AI 클래스 초기화
        self.PORT = ConnectionUtils.find_bluetooth_dongle(self._GenerateProtocolInstance.DongleInAction_bytes()) # 동글 포트 찾기
        self._play_once_dict = {group_id: True}

    def __del__(self) -> None:
        try:
            self.close()
        except KeyboardInterrupt as error: # KeyboardInterrupt 에러 발생
            raise error
        except:
            pass
        PingPongThread._is_start = False

    def _proc_group_id(self, group_id):
        if len(self._robot_status.keys()) == 1 and group_id == None:
            return list(self._robot_status.keys())[0]
        elif type(group_id) == str and group_id.lower() == "all":
            return "all"
        else:
            return group_id

    def __getitem__(self, key, group_id=None):
        group_id = self._proc_group_id(group_id)
        if key in self._robot_status[group_id].controller_status.__dict__.keys():
            return self._robot_status[group_id].controller_status.__dict__[key]
        elif key in self._robot_status[group_id].processed_status.__dict__.keys():
            return self._robot_status[group_id].processed_status.__dict__[key]
        else:
            raise ValueError("There is no \"{}\" item of group_id \"{}\" in the robot status!".format(key, group_id))

    # 시작 체크
    def _start_check(self):
        if not PingPongThread._is_start:
            raise ValueError("Thread did not start! Please start() before do something, or end thread.")

    # 로봇 연결
    def _connect_robot_thread(self, group_id=None) -> None:
        group_id = self._proc_group_id(group_id)
        ser = None
        while True:
            ser = ConnectionUtils.connect_serial_URL(self.PORT)
            if ser:
                break
            else:
                self.PORT = ConnectionUtils.find_bluetooth_dongle(self._GenerateProtocolInstance.DongleInAction_bytes())
        connection_number = self._robot_status[group_id].controller_status.connection_number
        ReaderThread.__init__(self, ser, rawProtocol, connection_number, group_id)
        ReaderThread.start(self)
        self._write(self._GenerateProtocolInstance.PingPongGn_connect_bytes())

    # 쓰기
    def _write(self, protocol_bytes) -> None:
        try:
            ReaderThread.write(self, protocol_bytes)
        except KeyboardInterrupt as error: # KeyboardInterrupt 에러 발생
            raise error
        except:
            print("Cannot write.")

    def _init_robot_status(self, group_id="all") -> None:
        group_id = self._proc_group_id(group_id)
        if isinstance(group_id, str) and group_id.lower() == "all":
            for key in self._robot_status.keys():
                self._robot_status[key] = RobotStatus(self._robot_status[key].controller_status.connection_number, key)
        else:
            self._robot_status[group_id] = RobotStatus(self._robot_status[group_id].controller_status.connection_number, group_id)

    # 쓰레드 시작
    def start(self, group_id=None) -> None:
        group_id = self._proc_group_id(group_id)
        if not PingPongThread._is_start:
            PingPongThread._is_start = True
            self._connect_robot_thread(group_id)
        else:
            raise ValueError("PingPongThread instance cannot start above 1.")
    
    # 쓰레드 종료
    def end(self) -> None:
        self._start_check()
        self.disconnect_master_robot()
        self.close()
        self._init_robot_status()
        print("End thread.")
        PingPongThread._is_start = False

        ## end flag -> serial 보수 ########################
    
    # 로봇 연결 해제
    def disconnect_master_robot(self, group_id="all") -> None:
        group_id = self._proc_group_id(group_id)
        self._start_check()
        def discon_op(x):
            if self._robot_status[x].processed_status.connected_number > 0:
                self._write(self._GenerateProtocolInstance.PingPong_disconnect_bytes)
                time.sleep(2) # 응답 기다림
                self.set_robot_disconnect_flag(True)
                print("Disconnect master robot.")
                # 1개는 해제 응답을 안 받음. 2개 이상은 해제 응답을 받음.
            else:
                print("Master robot is not connected.")
            self._init_robot_status(x) # 로봇 상태 초기화
        if isinstance(group_id, str) and group_id.lower() == "all":
            for key in self._robot_status.keys():
                discon_op(key)
        else:
            discon_op(group_id)
        
    # deprecated?
    def reconnect_robot(self) -> None:
        print("Reconnect with robots.")
        #self.ReaderThreadInstance.serial.close()
        #self.ReaderThreadInstance.reconnect()
        self._write(self._GenerateProtocolInstance.PingPongGn_connect_bytes())

    def get_is_start(self) -> bool:
        if PingPongThread._is_start: # copy
            return True
        else:
            return False
        
    def get_robot_status(self, group_id=None) -> dict: 
        group_id = self._proc_group_id(group_id)
        status = \
            {
                "controller_status": self._robot_status[group_id].controller_status.__dict__.copy(),
                "processed_status": self._robot_status[group_id].processed_status.__dict__.copy()
            }
        return status

    # 완전 연결까지 기다림
    def wait_until_full_connect(self, group_id="all") -> None:
        group_id = self._proc_group_id(group_id)
        self._start_check()
        if group_id.lower() == "all":
            for key in self._robot_status.keys():
                while self._robot_status[key].controller_status.connection_number != \
                    self._robot_status[key].processed_status.connected_number:
                    pass
        elif type(group_id) == int:
            while self._robot_status[group_id].controller_status.connection_number != \
                self._robot_status[group_id].processed_status.connected_number:
                pass
        else:
            raise ValueError("group_id must be int or 'all'.")
        time.sleep(1)

    # 한 번만 동작
    def play_once_full_connect(self, group_id=None):
        group_id = self._proc_group_id(group_id)
        connection_number = self._robot_status[group_id].controller_status.connection_number
        connected_robots_number = self._robot_status[group_id].processed_status.connected_number
        if connection_number != connected_robots_number:  # full connection에서 떨어지면 리셋
            self._play_once_dict[group_id] = True
            return False
        else:
            if self._play_once_dict[group_id]:
                self._play_once_dict[group_id] = False
                time.sleep(1)
                return True
            else:
                return False

    # RPM을 SPS로 변환
    def RPM_to_SPS(self, RPM):
        if not isinstance(RPM, (int, float)):
            raise ValueError("RPM must be float or int value")
        else:
            return self._GenerateProtocolInstance.RPM_to_SPS(RPM)

    # SPS를 RPM으로 변환
    def SPS_to_RPM(self, SPS):
        if not isinstance(SPS, int):
            raise ValueError("SPS must be int value")
        else:
            return self._GenerateProtocolInstance.RPM_to_SPS(SPS)

    # time_seconds 초 동안 기다림
    def wait(self, time_seconds):
        if not isinstance(time_seconds, (int, float)):
            raise ValueError("time_seconds must be int or float.")
        elif time_seconds < 0:
            raise ValueError("time_seconds must positive value.")
        # time.sleep(time_seconds)

