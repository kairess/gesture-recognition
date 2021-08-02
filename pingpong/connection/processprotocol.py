import time
from connection.utils import Utils

class ProcessProtocol():
    def __init__(self, buffer, buffer_size, is_full_connect, robot_disconnect_flag, transport):
        self.buffer = buffer
        self.buffer_size = buffer_size
        self.is_full_connect = is_full_connect
        self.robot_disconnect_flag = robot_disconnect_flag
        self.transport = transport

    ### 연결 평가
    def evaluate_connection(self, group_id=None) -> None: 
        connection_number = self.transport._robot_status[group_id].controller_status.connection_number
        connected_robots_number = self.transport._robot_status[group_id].processed_status.connected_number
        ### 모두 연결
        if not self.is_full_connect and connected_robots_number == connection_number: 
            print("Fully connected.") 
            self.is_full_connect = True
        ### 전부 연결되지 않았을 때 & disconnect가 아닐 때
        elif connected_robots_number != connection_number and not self.robot_disconnect_flag: 
            ### 이전에 전부 연결되었다면 & 마스터가 끊어진 것이 아니라면
            if self.is_full_connect and connected_robots_number != 0: 
                print("Robot disconnected after full connection. Close all connection.") # 모두 연결 이후에 슬레이브 로봇 연결이 끊어지면 다시 연결이 안됨.
                self.transport.serial.close() # 시리얼 닫음 (transport의 close 함수를 사용하면 작동이 안 됨.)
                self.transport.reconnect()
                self.is_full_connect = False
                self.transport._init_robot_status(group_id)
            ### 이외
            else:
                self.is_full_connect = False
        #### 전부 연결되지 않았을 때 & disconnect일 때
        elif connected_robots_number != connection_number and self.robot_disconnect_flag: 
            # 시리얼 안 닫음.
            self.is_full_connect = False
            self.transport._robot_status[group_id].controller_status.connection_number = 0
            self.robot_disconnect_flag = False
        ### 아무것도 아니면 그대로 내보냄
        else: 
            pass

    # OP 코드 처리
    def process_data(self, group_id=None) -> None:
        OP_code = self.buffer[6]
        if OP_code == 0xDA: # 1개 연결
            return self._robot_connection_1(group_id)
        elif OP_code == 0xAD: # 2개 이상 연결
            return self._robot_connection_1up(group_id)
        elif OP_code == 0xCA: # 스케줄 설정
            return self._stepper_schedule(group_id)
        elif OP_code == 0xCB: # 포인트 설정
            return self._stepper_point(group_id)
        elif OP_code == 0xCD: # agg 설정
            return self._set_agg(group_id)
        elif OP_code == 0xB8: # 센서 데이터
            return self._get_sensor_data(group_id)
        else:
            return self._unregistered()

    def _unregistered(self) -> None:
        #print("Operation is not registered.")
        return None

    def _robot_connection_1(self, group_id) -> int:
        connection_number = self.transport._robot_status[group_id].controller_status.connection_number
        connected_robots_number = self.transport._robot_status[group_id].processed_status.connected_number
        if len(self.buffer) == 11:
            if connection_number == 1 and self.buffer[9] != 0xC0:
                print("Connected with a master robot.") # 로봇 연결
                ### 설정
                self.transport._robot_status[group_id].processed_status.MAC_address[0] = self.buffer[0] # MAC 주소
                self.transport._robot_status[group_id].processed_status.MAC_address[1] = self.buffer[1]
                self.transport._robot_status[group_id].processed_status.connected_number = 1
                return None
            elif self.buffer[9] == 0xC0: # 연결 해제
                if connected_robots_number > 0: # 이미 연결된 로봇이 있음
                    print("Disconnected with a master robot.") 
                else: # 연결된 로봇이 없음
                    print("Disconnected with previous connection.")
                print("Reconnecting with serial...")
                self.transport.serial.close() # 시리얼 닫음 (transport의 close 함수는 사용하면 작동이 안 됨.)
                time.sleep(2) # sleep 2 seconds
                self.transport.reconnect() # 재연결
                ### 설정
                self.transport._init_robot_status(group_id)
                return None
            else:
                return self._unregistered()
        else:
            return self._unregistered()

    def _robot_connection_1up(self, group_id) -> int:
        connection_number = self.transport._robot_status[group_id].controller_status.connection_number
        if connection_number > 1:
            if len(self.buffer) == 11: # 마스터 로봇
                print("Connected with a master robot.") # 로봇 연결
                ### 설정
                self.transport._robot_status[group_id].processed_status.MAC_address[0] = self.buffer[0] # MAC 주소
                self.transport._robot_status[group_id].processed_status.MAC_address[1] = self.buffer[1]
                self.transport._robot_status[group_id].processed_status.connected_number = 1
                return None
            elif len(self.buffer) == 18: # 슬레이브 로봇
                for i in range(8):
                    if self.buffer[10+i] == 0x0F:
                        print("Connected robots:", i) # (i-1)대 slave 로봇 연결
                        ### 설정
                        self.transport._robot_status[group_id].processed_status.connected_number = i
                        return None
                print("Connected robots: 8")# 7대 slave 로봇 연결
                ### 설정
                self.transport._robot_status[group_id].processed_status.connected_number = 8
                return None
            else:
                return self._unregistered()
        else:
            return self._unregistered()

    def _stepper_schedule(self, group_id) -> None:
        ######################################################################타임아웃 & 버퍼 잘림 수정 & 아래도 수정 (첫 번째 버퍼는 스케줄 set이 아님.)
        if len(self.buffer) == 15:
            print("Schedule set.")
            self.transport._robot_status[group_id].processed_status.stepper_schedule_set[0] = True 
        elif len(self.buffer) == 17:
            #cube_ID = self.buffer[3] 
            ### master cube의 재생 내역만 나타남.
            schedule_idx = Utils().twobyte_hexlist_to_int(self.buffer[13], self.buffer[14])
            play_idx = self.buffer[15]
            repeat_number = self.buffer[16]
            print("Schedule index:", schedule_idx)
            print("Point play index:", play_idx)
            print("Point repeat number:", repeat_number)
            if self.buffer[12] == 1: # schedule의 pause 여부, 1은 pause
                self.transport._robot_status[group_id].processed_status.stepper_played_pause[0] = True 
            elif self.buffer[12] == 2: # 2는 resume
                self.transport._robot_status[group_id].processed_status.stepper_played_pause[0] = False
            self.transport._robot_status[group_id].processed_status.stepper_played_schedule_idx[0] = schedule_idx 
            self.transport._robot_status[group_id].processed_status.stepper_played_point_idx[0] = play_idx
            self.transport._robot_status[group_id].processed_status.stepper_played_repeat_idx[0] = repeat_number
            return None
        else:
            return self._unregistered
    
    def _stepper_point(self, group_id) -> None:
        if len(self.buffer) == 15:
            print("Point set.")
            self.transport._robot_status[group_id].processed_status.stepper_point_set[0] = True # 1번만 작동함
            return None
        else:
            return self._unregistered

    def _set_agg(self, group_id) -> None:
        self.transport._robot_status[group_id].processed_status.stepper_agg_set = True
        print("Aggregator set.")
        return None
    
    def _get_sensor_data(self, group_id) -> None:
        connection_number = self.transport._robot_status[group_id].controller_status.connection_number
        ### 큐브 ID
        if connection_number > 1:
            cube_ID = self.buffer[3]
        else:
            cube_ID = 0
        ### 버튼 상태
        button = self.buffer[11]
        ### 자이로 센서 값
        x1 = Utils().getSignedIntfromByteData(self.buffer[12])
        x2 = Utils().getSignedIntfromByteData(self.buffer[13])
        x3 = Utils().getSignedIntfromByteData(self.buffer[14])
        ### 가속도 센서 값
        xx = Utils().getACCDataToDegreeMinus90To90fromByteData(self.buffer[15])
        yy = -Utils().getACCDataToDegreeMinus90To90fromByteData(self.buffer[16])
        zz = Utils().getACCDataToDegreeMinus90To90fromByteData(self.buffer[17])
        # (자이로, 가속도가 바뀌었나?)
        ### 근접 센서 값
        prox = self.buffer[18]
        ### AIN (외부 센서) 값
        ad = self.buffer[19]
        ### status 등록
        self.transport._robot_status[group_id].processed_status.button[cube_ID] = button
        self.transport._robot_status[group_id].processed_status.sensor_gyro_xyz[cube_ID] = [x1, x2, x3]
        self.transport._robot_status[group_id].processed_status.sensor_acc_xyz[cube_ID] = [xx, yy, zz]
        prox_old = self.transport._robot_status[group_id].processed_status.sensor_prox[cube_ID]
        self.transport._robot_status[group_id].processed_status.sensor_prox_old[cube_ID] = prox_old
        self.transport._robot_status[group_id].processed_status.sensor_prox[cube_ID] = prox
        self.transport._robot_status[group_id].processed_status.AIN[cube_ID] = ad
        ### print
        #print("CubeID:", cube_ID+1, ", Button:", button, ", Gyro:", [x1, x2, x3], ", Acc:", [xx, yy, zz], ", Prox:", prox, ", AIN:", ad)
        return None