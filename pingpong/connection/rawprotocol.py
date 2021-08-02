from connection.serialprotocol import Protocol
from connection.utils import Utils
from connection.processprotocol import ProcessProtocol
import time
import serial

# 프로토콜
class rawProtocol(Protocol, ProcessProtocol):
    def __init__(self):
        self.init_buffer()
        self.set_timeout()
        self.is_full_connect = False
        self.robot_disconnect_flag = False
        self.is_point_set = False
        self.transport = None
        ProcessProtocol.__init__(self, self.buffer, self.buffer_size, self.is_full_connect, self.robot_disconnect_flag, self.transport) # 여기 변수들은 ProcessProtocol 멤버 변수와 자동으로 동기화 됨.

    # 버퍼 초기화
    def init_buffer(self) -> None:
        self.buffer = b""
        self.buffer_size = 0

    # 버퍼 더하기
    def add_buffer(self, data):
        self.buffer += data

    # 타임아웃 시간 정하기
    def set_timeout(self, sec=1) -> None:
        self.timeout = sec

    # 모두 연결 설정
    def set_is_full_connect(self, TF: bool) -> None:
        self.is_full_connect = TF

    # 로봇 연결 해제 설정
    def set_robot_disconnect_flag(self, TF: bool) -> None:
        self.robot_disconnect_flag = TF

    # 연결 시작시 발생
    def connection_made(self, transport) -> None:
        self.transport = transport # transport 설정, ReaderThread의 instance를 가져옴.
        self.running = True
        print("Serial connected.")

    # 연결 종료시 발생
    def connection_lost(self, exc) -> None:
        self.transport._init_robot_status("all")
        self.set_is_full_connect(False)
        try:
            self.transport.serial.close() # serial 연결 종료
        except Exception as error:
            raise error
        print("Serial disconnected. Sleep 3 seconds.")
        not_raise = (type(None), serial.serialutil.SerialException)
        if type(exc) not in not_raise:
            raise exc # 오류 확인용. try 때문에 traceback이 안 됨.
        time.sleep(3)

    #데이터가 들어오면 이곳에서 처리함.
    def data_received(self, data) -> None:
        if self.buffer == b"":
            self.previous_time = time.time()
        elif time.time()-self.previous_time > self.timeout: # 타임아웃
            print("Timeout. Initialize buffer.")
            print("Timeout buffer:", Utils().bytes_to_hex_str(self.buffer))
            self.init_buffer()
            self.previous_time = time.time()
        
        self.add_buffer(data) # 버퍼 받기
        if len(self.buffer) == 9: # 버퍼 사이즈 계산
            self.buffer_size = Utils().twobyte_hexlist_to_int(self.buffer[7], self.buffer[8])
        
        if len(self.buffer) == self.buffer_size: # 버퍼 얻음
            # print("Buffer:", Utils().bytes_to_hex_str(self.buffer)) # 버퍼 프린트
            self.process_data(self.transport._group_id) # 데이터 처리 및 명령
            self.init_buffer() # 버퍼 초기화
            self.evaluate_connection(self.transport._group_id) # 연결 평가
    
    # 데이터 보낼 때 함수
    def write(self, data) -> None:
        if self.running:
            self.transport.write(data)
        else:
            print("Not running.")
    
    # 종료 체크
    def is_done(self) -> bool:
        return self.running