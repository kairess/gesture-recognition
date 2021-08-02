from protocols.generateprotocol import GenerateProtocol
from operations.servo.servooperationutils import ServoOperationUtils
import time

class ServoOperation():
    def __init__(self, number, group_id, robot_status, start_check, write):
        self._GenerateProtocolInstance = GenerateProtocol(number, group_id)
        self._robot_status = robot_status
        self._start_check_copy = start_check
        self._write_copy = write

    ### robot_status 얻기
    def _get_robot_status(self, group_id, status, variable):
        return eval("self._robot_status[{}].{}.{}".format(group_id, status, variable))

    ### robot_status 설정
    def _set_robot_status(self, group_id, status, variable, value):
        exec("self._robot_status[{}].{}.{} = {}".format(group_id, status, variable, value))
    
    ### 1개 큐브 서보 모터 작동
    def run_single_servo(self, cube_ID, angle, group_id=None):
        """
        1개 (또는 모두) 큐브 서보 모터 작동

        cube_ID: 1 to 8, 또는 \"all\".
        angle: int, 0 to 180.
        group_id: 작동시킬 큐브가 소속된 그룹 (0 to 7?). None이면 0xFF.
        """
        group_id = ServoOperationUtils.proc_group_id(self._GenerateProtocolInstance._group_id, group_id)
        ### start 체크
        self._start_check_copy()
        ### 연결 개수
        connection_number = self._robot_status[group_id].controller_status.connection_number
        ### cube ID 처리
        cube_ID = ServoOperationUtils().process_cube_ID(cube_ID, connection_number)
        ### angle 체크
        ServoOperationUtils().check_servo_angle(angle)
        ### status 등록
        if cube_ID == 0xFF:
            for i in range(connection_number):
                self._robot_status[group_id].controller_status.servo_mode[i] = "single"
                self._robot_status[group_id].controller_status.servo_angle[i] = angle
        else:
            self._robot_status[group_id].controller_status.servo_mode[cube_ID] = "single"
            self._robot_status[group_id].controller_status.servo_angle[cube_ID] = angle
        ### byte 쓰기
        # timeout = 1 sec (default)
        sending_bytes = self._GenerateProtocolInstance.SetSingleServo(cube_ID, angle, timeout=1, group_id=group_id)
        self._write_copy(sending_bytes) 
        ### sleep
        time.sleep(0.2)

    ### 서보 모터 agg 작동
    def run_servo_schedule(self, 
        cube_ID_list="all", 
        servo_angle_list=None,
        servo_duration=None,
        pause_list=False,
        speed_list=None, 
        step_list=None, 
        time_list=None, 
        group_id=None, 
        speed_option="RPM", 
        step_option="CYCLE", 
        sync=False, 
        time_option=None,
        wait=0) -> None:
        group_id = ServoOperationUtils.proc_group_id(self._GenerateProtocolInstance._group_id, group_id)
        ### 연결 개수
        connection_number = self._robot_status[group_id].controller_status.connection_number
        ### 시작 체크
        self._start_check_copy()
        ### cube_ID, speed, step, pause 리스트화
        cube_ID_list = ServoOperationUtils().to_list(cube_ID_list)
        servo_angle_list = ServoOperationUtils().to_list(servo_angle_list)
        servo_duration = ServoOperationUtils().to_list(servo_duration)
        pause_list = ServoOperationUtils().to_list(pause_list)
        speed_list = ServoOperationUtils().to_list(speed_list)
        step_list = ServoOperationUtils().to_list(step_list)
        time_list = ServoOperationUtils().to_list(time_list)
        ### 큐브 ID 리스트 처리
        cube_ID_list = ServoOperationUtils().process_cube_ID_list(cube_ID_list, connection_number)
        ### run_number 정의
        run_number = ServoOperationUtils().set_run_number(cube_ID_list, connection_number)
        ### pause 리스트 체크
        ServoOperationUtils().check_pause_list(pause_list)
        ### speed 옵션 체크
        ServoOperationUtils().check_speed_option(speed_option)
        ### step 옵션 체크
        ServoOperationUtils().check_step_option(step_option)
        ### sync 옵션 체크
        ServoOperationUtils().check_sync_option(sync)
        ### time 옵션 체크 & 처리
        time_option = ServoOperationUtils().check_time_option(time_option)
        ### wait 체크
        ServoOperationUtils().check_wait(wait, run_option="schedule")
        ### 디폴트 체크 & 처리
        if servo_duration == [None]:
            duration_option = False
        else:
            duration_option = True
        servo_angle_list, servo_duration = ServoOperationUtils().set_default_servo(input_list=[servo_angle_list, servo_duration, speed_list, step_list, time_list], option_list=[duration_option, time_option], run_option="schedule")
        ### servo angle list의 list of list 체크 (list of list만 받음.)
        ServoOperationUtils().check_list_of_list(servo_angle_list, mode_name="schedule", list_name="servo_angle_list", run_option="schedule")
        ### servo angle list 원소 체크 (int, 0 to 180 (deg))
        ServoOperationUtils().check_servo_angle_list(servo_angle_list)
        ### servo angle list 길이 체크
        ServoOperationUtils().len_check(servo_angle_list, cube_ID_list, connection_number, mode_name="schedule", list_name="servo_angle_list", run_number=run_number, run_option="schedule")
        ### duration list의 list of list 체크 (int, float는 acceptable. None, [None]은 default. list는 list of list만 받음.)
        ServoOperationUtils().check_list_of_list(servo_duration, mode_name="schedule", list_name="servo_duration", run_option="schedule")
        ### duration list 원소 체크  (int or float, 0 to 65.535 (sec))
        ServoOperationUtils().check_servo_duration(servo_duration)
        ### duration list 길이 체크
        ServoOperationUtils().len_check(servo_duration, cube_ID_list, connection_number, mode_name="schedule", list_name="servo_duration", run_number=run_number, run_option="schedule")
        ### servo angle list와 duration의 길이 일치 체크
        if len(servo_duration) != 1 or (len(servo_duration) == 1 and len(servo_duration[0]) != 1):
            ServoOperationUtils().len_check_elemental_list(servo_angle_list, servo_duration, mode_name="schedule", input_list1_name="servo_angle_list", input_list2_name="servo_duration")
        ### duration 변환
        if duration_option:
            speed_list, step_list = ServoOperationUtils().convert_servo_duration(servo_duration, servo_angle_list, run_number)
            speed_option = "RPM"
            step_option = "CYCLE"
            time_option = "none"
        ### time 옵션 분기 설정
        ### time 옵션 없음
        if time_option.lower() == "none":
            ### speed, step 리스트가 list of list인지 체크 (dataframe, array 이용? (numpy, pandas 등 사용))
            ServoOperationUtils().check_list_of_list(speed_list, mode_name="schedule", list_name="speed_list", run_option="schedule")
            ServoOperationUtils().check_list_of_list(step_list, mode_name="schedule", list_name="step_list", run_option="schedule")
            ### speed, step 리스트 길이 체크
            ServoOperationUtils().len_check(speed_list, cube_ID_list, connection_number, mode_name="schedule", list_name="speed_list", run_number=run_number, run_option="schedule")
            ServoOperationUtils().len_check(step_list, cube_ID_list, connection_number, mode_name="schedule", list_name="step_list", run_number=run_number, run_option="schedule")
            ### 내부 원소 길이 체크
            ServoOperationUtils().len_check_elemental_list(speed_list, step_list, mode_name="schedule", input_list1_name="speed_list", input_list2_name="step_list")
            ### servo angle list 내부 원소 길이 체크
            ServoOperationUtils().len_check_elemental_list(speed_list, servo_angle_list, mode_name="schedule", input_list1_name="speed_list", input_list2_name="servo_angle_list")
            ### sync 모드일 때 내부 원소 길이 체크
            ServoOperationUtils().len_check_elemental_list_in_sync(sync, speed_list, step_list, mode_name="schedule sync", input_list1_name="speed_list", input_list2_name="step_list")
            ### 속도, 스텝 제한
            speed_list, sleep_list = ServoOperationUtils().limit_speed(speed_list, speed_option, run_number, sync, run_option="schedule")
            step_list, speed_list = ServoOperationUtils().limit_step(step_list, speed_list, sleep_list, step_option, run_number, sync, run_option="schedule")
        ### time 옵션 speed 모드
        elif time_option.lower() == "speed":
            ### time, speed 리스트가 list of list인지 체크 (dataframe, array 이용? (numpy, pandas 등 사용))
            ServoOperationUtils().check_list_of_list(time_list, mode_name="schedule", list_name="time_list", run_option="schedule")
            ServoOperationUtils().check_list_of_list(speed_list, mode_name="schedule", list_name="speed_list", run_option="schedule")
            ### time, speed 리스트 길이 체크
            ServoOperationUtils().len_check(time_list, cube_ID_list, connection_number, mode_name="schedule", list_name="time_list", run_number=run_number, run_option="schedule")
            ServoOperationUtils().len_check(speed_list, cube_ID_list, connection_number, mode_name="schedule", list_name="speed_list", run_number=run_number, run_option="schedule")
            ### 내부 원소 길이 체크
            ServoOperationUtils().len_check_elemental_list(time_list, speed_list, mode_name="schedule", input_list1_name="time_list", input_list2_name="speed_list")
            ### servo angle list 내부 원소 길이 체크
            ServoOperationUtils().len_check_elemental_list(time_list, servo_angle_list, mode_name="schedule", input_list1_name="time_list", input_list2_name="servo_angle_list")
            ### sync 모드일 때 내부 원소 길이 체크
            ServoOperationUtils().len_check_elemental_list_in_sync(sync, time_list, speed_list, mode_name="schedule sync", input_list1_name="time_list", input_list2_name="speed_list")
            ### 시간 변환, 속도, 스텝 제한
            speed_list, sleep_list = ServoOperationUtils().limit_speed(speed_list, speed_option, run_number, sync, run_option="schedule")
            step_list, _, speed_option, step_option = ServoOperationUtils().convert_time_list(time_list, speed_list, step_list=None, speed_option=speed_option, step_option=None, run_number=run_number, sync=sync, run_option="schedule", time_option="speed")
            step_list, speed_list = ServoOperationUtils().limit_step(step_list, speed_list, sleep_list, step_option="STEP", run_number=run_number, sync=sync, run_option="schedule")
        ### time 옵션 step 모드
        elif time_option.lower() == "step":
            ### time, step 리스트가 list of list인지 체크 (dataframe, array 이용? (numpy, pandas 등 사용))
            ServoOperationUtils().check_list_of_list(time_list, mode_name="schedule", list_name="time_list", run_option="schedule")
            ServoOperationUtils().check_list_of_list(step_list, mode_name="schedule", list_name="step_list", run_option="schedule")
            ### time, step 리스트 길이 체크
            ServoOperationUtils().len_check(time_list, cube_ID_list, connection_number, mode_name="schedule", list_name="time_list", run_number=run_number, run_option="schedule")
            ServoOperationUtils().len_check(step_list, cube_ID_list, connection_number, mode_name="schedule", list_name="step_list", run_number=run_number, run_option="schedule")
            ### 내부 원소 길이 체크
            ServoOperationUtils().len_check_elemental_list(time_list, step_list, mode_name="schedule", input_list1_name="time_list", input_list2_name="step_list")
            ### servo angle list 내부 원소 길이 체크
            ServoOperationUtils().len_check_elemental_list(time_list, servo_angle_list, mode_name="schedule", input_list1_name="time_list", input_list2_name="servo_angle_list")
            ### sync 모드일 때 내부 원소 길이 체크
            ServoOperationUtils().len_check_elemental_list_in_sync(sync, time_list, step_list, mode_name="schedule sync", input_list1_name="time_list", input_list2_name="step_list")
            ### 시간 변환, 속도, 스텝 제한
            speed_list, step_list, speed_option, step_option = ServoOperationUtils().convert_time_list(time_list, speed_list=None, step_list=step_list, speed_option=None, step_option=step_option, run_number=run_number, sync=sync, run_option="schedule", time_option="step")
            speed_list, sleep_list = ServoOperationUtils().limit_speed(speed_list, speed_option, run_number, sync, run_option="schedule")
            step_list, speed_list = ServoOperationUtils().limit_step(step_list, speed_list, sleep_list, step_option="STEP", run_number=run_number, sync=sync, run_option="schedule")
        ### pause 길이 체크
        ServoOperationUtils().len_check(pause_list, cube_ID_list, connection_number, mode_name="schedule", list_name="pause_list", run_number=run_number, run_option="schedule")
        ### 바이트 확장
        cube_ID_list, speed_list, step_list, pause_list, servo_angle_list = ServoOperationUtils().expand_bytes(cube_ID_list, connection_number, run_number, speed_list, step_list, pause_list, servo_angle_list)
        ### servo timeout list 만들기 (default: 1초)
        servo_timeout_list = [[1]*x for x in map(len, servo_angle_list)]
        ### sync 모드 처리
        speed_list, step_list = ServoOperationUtils().check_time_sync_none(speed_list, step_list, sync, run_number, run_option="schedule")
        ### wait 변환 (wait = "step" 또는 "schedule"이면 현재 run_option에 맞춰서 알아서 계산)
        if isinstance(wait, str):
            wait = ServoOperationUtils().convert_wait(speed_list, step_list, pause_list, run_option="step")
        ### 작동 처리 (group_id 처리 해야함)
        sending_bytes = b""
        for i, cube_ID_element in enumerate(cube_ID_list):
            ### stepper status 등록
            self._robot_status[group_id].controller_status.stepper_mode[cube_ID_element] = "point"
            self._robot_status[group_id].controller_status.stepper_schedule_point_start[cube_ID_element] = [0]
            self._robot_status[group_id].controller_status.stepper_schedule_point_end[cube_ID_element] = [len(speed_list[i])-1]
            self._robot_status[group_id].controller_status.stepper_schedule_point_repeat[cube_ID_element] = [1]
            self._robot_status[group_id].controller_status.stepper_speed_schedule[cube_ID_element] = speed_list[i]
            self._robot_status[group_id].controller_status.stepper_step_schedule[cube_ID_element] = step_list[i]
            self._robot_status[group_id].controller_status.stepper_pause[cube_ID_element] = pause_list[i]
            self._robot_status[group_id].controller_status.stepper_schedule_sync_on[cube_ID_element] = sync
            ### servo status 등록
            self._robot_status[group_id].controller_status.servo_mode[cube_ID_element] = "point"
            self._robot_status[group_id].controller_status.servo_angle_schedule[cube_ID_element] = servo_angle_list[i]
            self._robot_status[group_id].controller_status.servo_timeout_schedule[cube_ID_element] = servo_timeout_list[i]
            ### bytes 붙이기
            sending_bytes += self._GenerateProtocolInstance.SetScheduledSteps_bytes(cube_ID_element, speed_list[i], step_list[i], group_id, True,
                step_type=4, servo_angle_list=servo_angle_list[i], servo_angle_timeout_list=servo_timeout_list[i])
        if connection_number > 1:
            sending_bytes = self._GenerateProtocolInstance.SetAggregateSteps_bytes(group_id, sending_bytes)
        ### 스케줄 설정 작동
        self._write_copy(sending_bytes) 
        ### 1개 이상이면 agg 설정이 올 때까지 잡아두기
        ServoOperationUtils().wait_until_agg_set(self._get_robot_status, self._set_robot_status, group_id, connection_number)
        ### 포인트로 작동
        time.sleep(0.2)
        sending_bytes = b""
        for i, cube_ID_element in enumerate(cube_ID_list):
            sending_bytes += self._GenerateProtocolInstance.SetScheduledPoints_bytes(cube_ID_element, [0], [len(speed_list[i])-1], [1], group_id, 
                pause_list[i], step_type=4)
        if connection_number > 1:
            sending_bytes = self._GenerateProtocolInstance.SetAggregateSteps_bytes(group_id, sending_bytes)
        self._write_copy(sending_bytes)
        ### sleep
        if wait != 0:
            time.sleep(wait + 0.3)
        time.sleep(0.2)

    def set_servo_schedule(self, cube_ID_list="all", servo_angle_list=None, servo_duration=None, pause_list=True, speed_list=None, step_list=None, 
        time_list=None, group_id=None, speed_option="RPM", step_option="CYCLE", sync=False, time_option=None, wait=0) -> None:
        self.run_servo_schedule(cube_ID_list=cube_ID_list, servo_angle_list=servo_angle_list, servo_duration=servo_duration, pause_list=pause_list, 
            speed_list=speed_list, step_list=step_list, time_list=time_list, group_id=group_id, speed_option=speed_option, 
            step_option=step_option, sync=sync, time_option=time_option, wait=wait)

    def play_servo_schedule(self, 
        cube_ID_list="all", 
        repeat_list=[[1]], 
        start_point_list=[[None]], 
        stop_point_list=[[None]], 
        start_and_stop_list=[[None]], 
        pause_list=False, 
        group_id=None, 
        sync=False, 
        wait=0) -> None:
        """
        Play motors with set schedule.
        """
        group_id = ServoOperationUtils.proc_group_id(self._GenerateProtocolInstance._group_id, group_id)
        ### 연결 개수
        connection_number = self._robot_status[group_id].controller_status.connection_number
        ### start 체크
        self._start_check_copy()
        ### start, stop, repeat 리스트화
        start_point_list = ServoOperationUtils().to_list(start_point_list)
        stop_point_list = ServoOperationUtils().to_list(stop_point_list)
        repeat_list = ServoOperationUtils().to_list(repeat_list)
        cube_ID_list = ServoOperationUtils().to_list(cube_ID_list)
        pause_list = ServoOperationUtils().to_list(pause_list)
        start_and_stop_list = ServoOperationUtils().to_list(start_and_stop_list)
        ### 큐브 ID 리스트 처리
        cube_ID_list = ServoOperationUtils().process_cube_ID_list(cube_ID_list, connection_number)
        ### run_number 정의
        run_number = ServoOperationUtils().set_run_number(cube_ID_list, connection_number)
        ### 스케줄 셋 체크
        for cube_ID_element in cube_ID_list:
            if self._robot_status[group_id].controller_status.stepper_speed_schedule[cube_ID_element] == []: # 스케줄이 비었음
                raise ValueError("Set schedule before play.")
        ### pause 리스트 체크
        ServoOperationUtils().check_pause_list(pause_list)
        ### sync 옵션 체크
        ServoOperationUtils().check_sync_option(sync)
        ### wait 체크
        ServoOperationUtils().check_wait(wait, run_option="point")
        ### 변환 & 디폴트 값 넣기
        start_point_list, stop_point_list = ServoOperationUtils().set_default_servo(input_list=[start_point_list, stop_point_list, start_and_stop_list], option_list=None, run_option="point")
        ### list of list 체크
        ServoOperationUtils().check_list_of_list(start_point_list, mode_name="point", list_name="start_point_list", run_option="point")
        ServoOperationUtils().check_list_of_list(stop_point_list, mode_name="point", list_name="stop_point_list", run_option="point")
        ServoOperationUtils().check_list_of_list(repeat_list, mode_name="point", list_name="repeat_list", run_option="point")
        ### list 길이 체크
        ServoOperationUtils().len_check(start_point_list, cube_ID_list, connection_number, mode_name="point", list_name="start_point_list", run_number=run_number, run_option="point")
        ServoOperationUtils().len_check(stop_point_list, cube_ID_list, connection_number, mode_name="point", list_name="stop_point_list", run_number=run_number, run_option="point")
        ServoOperationUtils().len_check(repeat_list, cube_ID_list, connection_number, mode_name="point", list_name="repeat_list", run_number=run_number, run_option="point")
        ServoOperationUtils().len_check(pause_list, cube_ID_list, connection_number, mode_name="point", list_name="pause_list", run_number=run_number, run_option="point")
        ### 리스트 확장
        if cube_ID_list[0] == 0xFF:
            cube_ID_list = [i for i in range(connection_number)]
        if len(start_point_list) == 1: # 길이가 1이면 run_number 개수만큼 늘림
            start_point_list = ServoOperationUtils().list_product_copy(start_point_list, run_number)
        if len(stop_point_list) == 1: # 길이가 1이면 run_number 개수만큼 늘림
            stop_point_list = ServoOperationUtils().list_product_copy(stop_point_list, run_number)
        if len(repeat_list) == 1: # 길이가 1이면 run_number 개수만큼 늘림
            repeat_list = ServoOperationUtils().list_product_copy(repeat_list, run_number)
        if len(pause_list) == 1: # 길이가 1이면 run_number 개수만큼 늘림
            pause_list = pause_list*run_number
        ### 원소 길이 체크
        for start_point_list_element, stop_point_list_element, repeat_list_element in zip(start_point_list, stop_point_list, repeat_list):
            if len(start_point_list_element) != len(stop_point_list_element) or len(start_point_list_element) != len(repeat_list_element):
                raise ValueError("Start list number, stop list, and repeat list number must be the same.")       
        ### sync 모드 체크
        if sync:
            if not self._robot_status[group_id].controller_status.stepper_schedule_sync_on[cube_ID_element]:
                raise ValueError("In sync mode, set schedule must be in sync mode.")
            else:
                for start_point_list_element, stop_point_list_element in zip(start_point_list, stop_point_list):
                    if start_point_list_element != start_point_list[0] or \
                        stop_point_list_element != stop_point_list_element[0]:
                        raise ValueError("In sync mode, each point schedule must be the same.")
        ### 스케줄 셋 체크 
        speed_length_list = list(map(len, self._robot_status[group_id].controller_status.stepper_speed_schedule))
        for i, cube_ID_element in enumerate(cube_ID_list):
            for j in range(len(start_point_list[i])):
                if isinstance(stop_point_list[i][j], str) and stop_point_list[i][j].lower() == "end":
                    stop_point_list[i][j] = speed_length_list[cube_ID_element]-1 # end이면 제일 뒤에 인덱스(stop은 마지막 인덱스)
                ServoOperationUtils().integer_check(start_point_list[i][j])
                ServoOperationUtils().integer_check(stop_point_list[i][j])
                ServoOperationUtils().integer_check(repeat_list[i][j])
                if start_point_list[i][j] < 0 or stop_point_list[i][j] < 0 \
                    or speed_length_list[cube_ID_element]-1 < start_point_list[i][j] \
                    or speed_length_list[cube_ID_element]-1 < stop_point_list[i][j]:
                    raise ValueError("Unavailable point index. Schedule does not have that index.")
                elif stop_point_list[i][j] < start_point_list[i][j]:
                    raise ValueError("Start index must be less than or equal to stop index.")
                if repeat_list[i][j] < 0 or 255 < repeat_list[i][j]:
                    raise ValueError("Unavailable number. Repeat must be positive, or smaller than 256.")
        ### wait 처리
        if isinstance(wait, str):
            wait = ServoOperationUtils().convert_wait_point(cube_ID_list, self._robot_status, group_id, start_point_list, stop_point_list, repeat_list, pause_list)
        ### 작동 처리 (group_id 처리 해야함)
        sending_bytes = b""
        for i, cube_ID_element in enumerate(cube_ID_list):
            ### stepper status 등록
            self._robot_status[group_id].controller_status.stepper_mode[cube_ID_element] = "point"
            self._robot_status[group_id].controller_status.stepper_pause[cube_ID_element] = pause_list[i]
            self._robot_status[group_id].controller_status.stepper_schedule_point_start[cube_ID_element] = start_point_list[i]
            self._robot_status[group_id].controller_status.stepper_schedule_point_end[cube_ID_element] = stop_point_list[i]
            self._robot_status[group_id].controller_status.stepper_schedule_point_repeat[cube_ID_element] = repeat_list[i]
            ### servo status 등록
            self._robot_status[group_id].controller_status.servo_mode[cube_ID_element] = "point"
            ### 포인트 설정
            sending_bytes += self._GenerateProtocolInstance.SetScheduledPoints_bytes(cube_ID_element, start_point_list[i], stop_point_list[i], 
                repeat_list[i], group_id, pause_list[i], step_type=4)
        ### 바이트 쓰기, 작동
        if connection_number > 1:
            sending_bytes = self._GenerateProtocolInstance.SetAggregateSteps_bytes(group_id, sending_bytes)
        self._write_copy(sending_bytes)
        ### sleep
        if wait != 0:
            time.sleep(wait + 0.3)
        time.sleep(0.2)