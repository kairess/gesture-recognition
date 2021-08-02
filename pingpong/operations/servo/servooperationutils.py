import copy

class ServoOperationUtilsCheck():
    ### 리스트에 같은 원소가 있는지 확인
    def check_same_element(self, input_list) -> None:
        for i in range(len(input_list)-1):
            if input_list[i] in input_list[i+1:]:
                raise ValueError("All elements must be different each other in list.")

    ### 실수 체크
    def float_check(self, number, option=None) -> None:
        if not isinstance(number, (int, float)):
            is_float = False
        else:
            is_float = True
        if not is_float:
            if option:
                raise ValueError("Please enter float number, or \"" + str(option) + "\"!")
            else:
                raise ValueError("Please enter float number!")

    ###  정수 체크
    def integer_check(self, number, option=None) -> None:
        if not isinstance(number, int):
            is_integer = False
        else:
            is_integer = True
        if not is_integer:
            if option:
                raise ValueError("Please enter integer number, or \"" + str(option) + "\"!")
            else:
                raise ValueError("Please enter integer number!")

    ### pause 리스트 체크
    def check_pause_list(self, pause_list):
        if pause_list == [] or pause_list == ():
            raise ValueError("pause_list must not be empty list (or tuple).")
        for pause in pause_list:
            if not isinstance(pause, bool):
                raise ValueError("pause_list elements must be bool.")

    ### speed 옵션 체크
    def check_speed_option(self, speed_option):
        if not isinstance(speed_option, str):
            raise ValueError("speed_option must be str.")
        elif speed_option.upper() != "RPM" and speed_option.upper() != "SPS":
            raise ValueError("Unknown speed_option.")

    ### step 옵션 체크
    def check_step_option(self, step_option):
        if not isinstance(step_option, str):
            raise ValueError("step_option must be str.")
        elif step_option.upper() != "CYCLE" and step_option.upper() != "STEP":
            raise ValueError("Unknown step_option.")

    ### sync 옵션 체크
    def check_sync_option(self, sync):
        if not isinstance(sync, bool):
            raise ValueError("sync must be bool.")

    ### wait 체크
    def check_wait(self, wait, run_option):
        if run_option == "continue":
            if not isinstance(wait, (int, float)):
                raise ValueError("wait must be int or float in continue mode.")
            elif wait < 0:
                raise ValueError("wait must be positive.")
        else:
            if not isinstance(wait, (int, float, str)):
                raise ValueError("wait must be int, float, or str.")
            elif isinstance(wait, (int, float)) and wait < 0:
                raise ValueError("wait must be positive.")
            elif isinstance(wait, str) and wait.lower() != "step" and wait.lower() != "schedule":
                raise ValueError("Unknown wait option.")

    ### 길이 체크
    def len_check(self, input_list, cube_ID_list, connection_number, mode_name, list_name, run_number, run_option):
        if run_option != "point":
            if cube_ID_list[0] != 0xFF:
                if len(input_list) != 1 and len(input_list) != len(cube_ID_list):
                    raise ValueError("In {} mode, {} must have the same length as cube_ID_list, or have 1 length.".format(mode_name, list_name))
            elif len(input_list) != connection_number and len(input_list) != 1:
                raise ValueError("In {} mode with all cube IDs, {} must have the same length as connection number, or have 1 length.".format(mode_name, list_name))
        else:
            if len(input_list) != 1 and len(input_list) != run_number:
                raise ValueError("{} must have the same length as cube_ID_list, or have 1 length.".format(list_name))

    ### list_of_list 체크 함수
    def check_list_of_list(self, input_list, mode_name, list_name, run_option):
        if run_option.lower != "point":
            for input_list_element in input_list:
                if not isinstance(input_list_element, (list, tuple)):
                    raise ValueError("In {} mode, all elements of {} must be list or tuple.".format(mode_name, list_name)) 
        else:
            for input_list_element in input_list:
                if not isinstance(input_list_element, (list, tuple)):
                    raise ValueError("All elements of {} must be list or tuple.".format(list_name))

    ### 내부 원소 리스트 길이 체크 함수
    def len_check_elemental_list(self, input_list1, input_list2, mode_name, input_list1_name, input_list2_name):
        error_str = "In {} mode, each length of elements of {} and {} must be equal.".format(mode_name, input_list1_name, input_list2_name)
        if len(input_list1) == 1:
            for input_list2_element in input_list2:
                if len(input_list2_element) != len(input_list1[0]):
                    raise ValueError(error_str)
        elif len(input_list2) == 1:
            for input_list1_element in input_list1:
                if len(input_list1_element) != len(input_list2[0]):
                    raise ValueError(error_str)
        else:
            for input_list1_element, input_list2_element in zip(input_list1, input_list2):
                if len(input_list1_element) != len(input_list2_element):
                    raise ValueError(error_str)

    ### sync 모드 내부 원소 길이 체크 함수
    def len_check_elemental_list_in_sync(self, sync, input_list1, input_list2, mode_name, input_list1_name, input_list2_name):
        if sync:
            error_str = "In {} mode, each length of elements of {} must be equal."
            for input_list1_element in input_list1:
                if len(input_list1_element) != len(input_list1[0]):
                    raise ValueError(error_str.format(mode_name, input_list1_name))
            for input_list2_element in input_list2:
                if len(input_list2_element) != len(input_list2[0]):
                    raise ValueError(error_str.format(mode_name, input_list2_name))

    ### servo angle 체크
    def check_servo_angle(self, angle):
        if not isinstance(angle, int):
            raise ValueError("Servo angle must be int, and in between 0 to 180 (deg).")
        elif angle < 0 or 180 < angle:
            raise ValueError("Servo angle must be int, and in between 0 to 180 (deg).")

    ### servo angle list 원소 체크
    def check_servo_angle_list(self, servo_angle_list):
        for angle_elem_list in servo_angle_list:
            for angle in angle_elem_list:
                self.check_servo_angle(angle)

    ### servo duration 원소 체크
    def check_servo_duration(self, servo_duration):
        for duration_elem_list in servo_duration:
            for duration in duration_elem_list:
                if not isinstance(duration, (int, float)):
                    raise ValueError("Servo duration must be int or float, and in between 0 to 65.535 (sec).")
                elif duration < 0 or 65.535 < duration:
                    raise ValueError("Servo duration must be int or float, and in between 0 to 65.535 (sec).")


class ServoOperationUtilsProcess():
    ### RPM 속도 제한
    def truncate_RPM_speed(self, speed: float, raise_error=False) -> int or float:
        """truncate speed between -30 to 30 RPM"""
        if not raise_error:
            if speed < -30: 
                speed = -30
                print("Warning. Maximum speed is +-30 RPM.")
            elif -3 < speed and speed < 3:
                distance = [abs(speed+3), abs(speed), abs(speed-3)]
                if speed != 0: 
                    print("Warning. Minimum speed is +-3 RPM.")
                speed = [-3, 0, 3][distance.index(min(distance))]
            elif speed > 30:
                speed = 30
                print("Warning. Maximum speed is +-30 RPM.")
            return speed
        else:
            if speed < -30 or speed > 30: 
                raise ValueError("Maximum speed is +-30 RPM.")
            elif -3 < speed and speed < 3 and speed != 0:
                raise ValueError("Minimum speed is +-3 RPM.")
            return speed

    ### SPS 속도 제한
    def truncate_SPS_speed(self, speed: int, raise_error=False) -> int:
        """truncate speed between -1000 to 1000 SPS"""
        if not raise_error:
            if speed < -1000: 
                speed = -1000
                print("Warning. Maximum speed is +-1000 SPS.")
            elif -100 < speed and speed < 100:
                distance = [abs(speed+100), abs(speed), abs(speed-100)]
                if speed != 0: 
                    print("Warning. Minimum speed is +-100 SPS.")
                speed = [-100, 0, 100][distance.index(min(distance))]
            elif speed > 1000:
                speed = 1000
                print("Warning. Maximum speed is +-1000 SPS.")
            return speed
        else:
            if speed < -1000 or speed > 1000: 
                raise ValueError("Maximum speed is +-1000 SPS.")
            elif -100 < speed and speed < 100 and speed != 0:
                raise ValueError("Minimum speed is +-100 SPS.")
            return speed

    ### cycle 스텝 제한
    def truncate_cycle_step(self, step: float, raise_error=False) -> int or float:
        """truncate step between 0 to 32.7675 cycle (65535 steps)"""
        if not raise_error:
            if step < 0:
                step = 0
                print("Warning. Minimum step cycle is 0.")
            elif step > 32.7675:
                step = 32.7675
                print("Warning. Maximum step cycle is 32.7675.")
            return step
        else:
            if step < 0:
                raise ValueError("Minimum step cycle is 0.")
            elif step > 32.7675:
                raise ValueError("Maximum step cycle is 32.7675.")
            return step

    ### step 스텝 제한
    def truncate_step_step(self, step: float, raise_error=False) -> int or float:
        """truncate step between 0 to 32.7675 cycle (65535 steps)"""
        if not raise_error:
            if step < 0:
                step = 0
                print("Warning. Minimum step is 0.")
            elif step > 65535:
                step = 65535
                print("Warning. Maximum step is 65535.")
            return step
        else:
            if step < 0:
                raise ValueError("Minimum step is 0.")
            elif step > 65535:
                raise ValueError("Maximum step is 65535.")
            return step

    ### 큐브 ID 처리
    def process_cube_ID(self, cube_ID, connection_number):
        if isinstance(cube_ID, str) and cube_ID.lower() == "all":
            cube_ID = 0xFF
        else:
            ServoOperationUtilsCheck().integer_check(cube_ID, "all") # 정수 체크
            cube_ID = int(cube_ID) # 정수로 변환 
            if not (1 <= cube_ID and cube_ID <= 8):
                raise ValueError("Cube ID must be between 1 to 8.")
            elif cube_ID > connection_number:
                raise ValueError("Cube ID must be less than or equal to connection number.")
            cube_ID -= 1 # (1 to 8 -> 0 to 7)
        return cube_ID
    
    ### 큐브 ID 리스트 처리
    def process_cube_ID_list(self, cube_ID_list, connection_number):
        if cube_ID_list == [] or cube_ID_list == ():
            raise ValueError("cube ID must not be empty list.")
        for i in range(len(cube_ID_list)):
            cube_ID_list[i] = self.process_cube_ID(cube_ID_list[i], connection_number)
            if cube_ID_list[i] == 0xFF and len(cube_ID_list) != 1:
                raise ValueError("If cube ID is all, input must not be length-above-2 list.")
        ServoOperationUtilsCheck().check_same_element(cube_ID_list) # 같은 원소가 있으면 error
        #if cube_ID_list[0] == 0xFF:
        #    cube_ID_list = [x for x in range(1, connection_number+1)] # all이면 확장
        return cube_ID_list
    
    ### time 옵션 체크 & 처리
    def check_time_option(self, time_option):
        if time_option == None:
            time_option = "none"
        elif not isinstance(time_option, str):
            raise ValueError("time_option must be str or None.")
        elif time_option.lower() != "none" and time_option.lower() != "speed" and time_option.lower() != "step":
            raise ValueError("Unknown time_option.")
        return time_option

    ### 디폴트 설정 & 체크
    def set_default_servo(self, input_list, option_list, run_option):
        if run_option.lower() == "schedule":
            ### 값 가져오기
            servo_angle_list = input_list[0]
            servo_duration = input_list[1]
            speed_list = input_list[2]
            step_list = input_list[3]
            time_list = input_list[4]
            duration_option = option_list[0]
            time_option = option_list[1]
            ### 서보 각도 설정
            if servo_angle_list == [None]:
                #servo_angle_list = [[0]] # 디폴트(default)는 0도로 맞춤.
                raise ValueError("In schedule mode, servo_angle_list must be entered.")
            ### 디폴트 체크
            if not duration_option:
                servo_duration = [[1]] # 디폴트(default)는 1초로 맞춤.
                if time_option.lower() == "none":
                    #if speed_list != [None] or step_list != [None]: # default off
                    if (speed_list != [None] and step_list == [None]) or (speed_list == [None] and step_list != [None]):
                        raise ValueError("In schedule, no-duration, and time-none mode, both speed_list and step_list must be entered.")
                elif time_option.lower() == "speed":
                    #if time_list != [None] or speed_list != [None]: # default off
                    if (time_list != [None] and speed_list == [None]) or (time_list == [None] and speed_list != [None]):
                        raise ValueError("In schedule, no-duration, and time-speed mode, both time_list and speed_list must be entered.")
                elif time_option.lower() == "step":
                    #if time_list != [None] or step_list != [None]: # default off
                    if (time_list != [None] and step_list == [None]) or (time_list == [None] and step_list != [None]):
                        raise ValueError("In schedule, no-duration, and time-step mode, both time_list and step_list must be entered.")
            else:
                ### duration이 list of list가 아니면 list를 하나 더 씌움.
                if len(servo_duration) == 1:
                    if not isinstance(servo_duration[0], (list, tuple)):
                        servo_duration = [servo_duration]
                if speed_list != [None] or step_list != [None] or time_list != [None]:
                    print("Warning. If servo_duration is entered, speed_list, step_list, and time_list are ignored.")
            return servo_angle_list, servo_duration
        ### 포인트 모드
        elif run_option.lower() == "point":
            start_point_list = input_list[0]
            stop_point_list = input_list[1]
            start_and_stop_list = input_list[2]
            if start_point_list == [[None]] and stop_point_list == [[None]]: # 스타트, 스탑 포인트 체크
                if start_and_stop_list != [[None]]:
                    start_point_list = []
                    stop_point_list = []
                    for start_and_stop_list_element in start_and_stop_list:
                        if not isinstance(start_and_stop_list_element, (list, tuple)):
                            raise ValueError("start_and_stop_list elements must be list or tuple.")
                        start_point_list_out, stop_point_list_out = ServoOperationUtilsConvert().convert_start_and_stop_list(start_and_stop_list_element)
                        start_point_list.append(start_point_list_out)
                        stop_point_list.append(stop_point_list_out)
                else:
                    start_point_list, stop_point_list = [[0]], [["end"]] # 디폴트 0(처음), end(끝)
            elif start_and_stop_list != [[None]]:
                print("Warning. start_point_list and stop_point_list are ignored. start_and_stop_list is accepted.")
                start_point_list = []
                stop_point_list = []
                for start_and_stop_list_element in start_and_stop_list:
                    if not isinstance(start_and_stop_list_element, (list, tuple)):
                        raise ValueError("start_and_stop_list elements must be list or tuple.")
                    start_point_list_out, stop_point_list_out = ServoOperationUtilsConvert().convert_start_and_stop_list(start_and_stop_list_element)
                    start_point_list.append(start_point_list_out)
                    stop_point_list.append(stop_point_list_out)
            elif start_point_list == [[None]]:
                start_point_list = [[0]]
            elif stop_point_list == [[None]]:
                stop_point_list = [["end"]]
            return start_point_list, stop_point_list

    @staticmethod
    def proc_group_id(self_group_id, group_id):
        if group_id == None:
            return self_group_id # None or int
        else:
            return group_id # Not None, int


class ServoOperationUtilsSet():
    ### run_number 설정
    def set_run_number(self, cube_ID_list, connection_number):
        if cube_ID_list[0] == 0xFF:
            run_number = connection_number
        else:
            run_number = len(cube_ID_list)
        return run_number


class ServoOperationUtilsConvert():
    ### 리스트 포인터(id)를 다르게 복사
    def list_product_copy(self, input_list, number) -> list:
        input_list = input_list[0] # ex) [[2, 3, 4, 5]]
        out_list = [] # ex) number=3, [[2, 3, 4, 5], [2, 3, 4, 5], [2, 3, 4, 5]]
        i = 0
        while i < number:
            new_list = [0]*len(input_list)
            for j in range(len(input_list)):
                new_list[j] = input_list[j]
            out_list.append(new_list)
            i += 1
        return out_list

    # 리스트로 변환
    def to_list(self, input_data) -> list:
        if isinstance(input_data, (list, tuple)):
            return list(input_data)
        elif isinstance(input_data, (int, float, str, bool)) or input_data == None:
            return [input_data]
        else:
            raise ValueError("Error. Enter list, or tuple, or int, or float, or str, or bool, or None.")

    ### RPM을 SPS로 변환
    def RPM_to_SPS(self, RPM: float) -> int or None:
        if 3 <= RPM and RPM <= 30:
            SPS = 50*(-60/RPM+22)
        elif -30 <= RPM and RPM <= -3:
            SPS = 50*(-60/RPM-22)
        elif RPM == 0:
            SPS = 0
        else:
            print("Warning: RPM must be between +-3 to +- 30, or 0.")
            return None
        return round(SPS) # -1000 to 1000

    ### SPS를 RPM으로 변환
    def SPS_to_RPM(self, SPS: int) -> float or None:
        if 100 <= SPS and SPS <= 1000:
            RPM = 60/(-SPS/50+22)
        elif -1000 <= SPS and SPS <= 100:
            RPM = -60/(SPS/50+22)
        elif SPS == 0:
            RPM = 0
        else:
            print("Warning: SPS must be between +-100 to +- 1000, or 0.")
            RPM = None  
        return RPM # -300 to 300

    ### cycle을 step으로 변환
    def cycle_to_step(self, cycle) -> int:
        step = cycle*2000
        return round(step)

    ### step을 cycle로 변환
    def step_to_cycle(self, step) -> float:
        cycle = step/2000
        return cycle
    
    ### 속도 제한 (RPM, SPS)
    def limit_speed(self, speed_list, speed_option, run_number, sync, run_option):
        ### truncate 에러 체크
        raise_error = sync and run_option.lower() != "continue" and run_number > 1 # sync 모드이고, continue 모드가 아니면 에러 체크
        ### 스케줄 모드 확인
        if run_option.lower() == "schedule":
            is_schedule = True
        else:
            is_schedule = False
        ### schedule 모드가 아니면 list of list화
        if not is_schedule:
            speed_list = [speed_list]
            sleep_list = [[False]*len(speed_list[0])]
        else:
            sleep_list = [[False]*len(speed_list[x]) for x in range(len(speed_list))]
        ### RPM 모드
        if speed_option.upper() == "RPM":
            ### 속도 체크 & 변환
            for i in range(len(speed_list)):
                for j in range(len(speed_list[i])):
                    if (isinstance(speed_list[i][j], str) and speed_list[i][j].lower() in ["stop", "sleep"]) or speed_list[i][j] == 0: # 스피드가 0이면 sleep 모드
                        speed_list[i][j] = 0
                        sleep_list[i][j] = True
                    if not is_schedule and isinstance(speed_list[i][j], (list, tuple)):
                        raise ValueError("In {} mode, elements of lists cannot be list or tuple.".format(run_option.lower()))
                    ServoOperationUtilsCheck().float_check(speed_list[i][j], "stop or sleep")
                    speed_list[i][j] = ServoOperationUtilsProcess().truncate_RPM_speed(speed_list[i][j], raise_error) # speed 자르기
                    speed_list[i][j] = self.RPM_to_SPS(speed_list[i][j]) # 단위를 RPM에서 SPS로 변경
        ### SPS 모드
        elif speed_option.upper() == "SPS":
            ### 속도 체크
            for i in range(len(speed_list)):
                for j in range(len(speed_list[i])):
                    if (isinstance(speed_list[i][j], str) and speed_list[i][j].lower() in ["stop", "sleep"]) or speed_list[i][j] == 0: # 스피드가 0이면 sleep 모드
                        speed_list[i][j] = 0
                        sleep_list[i][j] = True
                    speed_list[i][j] = round(speed_list[i][j])
                    ServoOperationUtilsCheck().float_check(speed_list[i][j])
                    speed_list[i][j] = ServoOperationUtilsProcess().truncate_SPS_speed(speed_list[i][j], raise_error) # speed 자르기
        ### schedule 모드이면 겉 list 제거
        if not is_schedule:
            speed_list = speed_list[0]
            sleep_list = sleep_list[0]                
        return speed_list, sleep_list

    ### 스텝 제한 함수 (CYCLE, STEP)
    def limit_step(self, step_list, speed_list, sleep_list, step_option, run_number, sync, run_option):
        ### truncate 에러 체크
        raise_error = sync and run_option != "continue" and run_number > 1 # sync 모드이고, continue 모드가 아니면 에러 체크
        ### 스케줄 모드 확인
        if run_option.lower() == "schedule":
            is_schedule = True
        else:
            is_schedule = False
        ### schedule 모드가 아니면 list of list화
        if not is_schedule:
            step_list = [step_list]
            speed_list = [speed_list]
            sleep_list = [sleep_list]
        ### 1줄일 때 복제
        if len(speed_list) == 1:
            speed_list = self.list_product_copy(speed_list, run_number)
            sleep_list = self.list_product_copy(sleep_list, run_number)
        elif len(step_list) == 1:
            step_list = self.list_product_copy(step_list, run_number)
        ### CYCLE 모드
        if step_option.upper() == "CYCLE":
            ### 사이클 체크 & 변환 
            for i in range(len(step_list)):
                for j in range(len(step_list[i])):
                    if sleep_list[i][j]:
                        step_list[i][j] /= 2 # sleep이면 2로 나누고 step으로 변환하면 초 단위가 됨.
                    ServoOperationUtilsCheck().float_check(step_list[i][j])
                    if step_list[i][j] < 0: 
                        step_list[i][j] = -step_list[i][j] # step이 -이면 speed를 -로 바꾸기
                        speed_list[i][j] = -speed_list[i][j]
                    step_list[i][j] = ServoOperationUtilsProcess().truncate_cycle_step(step_list[i][j], raise_error) # cycle 자르기
                    step_list[i][j] = self.cycle_to_step(step_list[i][j]) # 단위를 cycle에서 step으로 변경
        ### STEP 모드
        elif step_option.upper() == "STEP":
            ### 스텝 체크 & 변환 
            for i in range(len(step_list)):
                for j in range(len(step_list[i])):
                    ServoOperationUtilsCheck().integer_check(step_list[i][j]) # step은 integer이어야 함.
                    if step_list[i][j] < 0: 
                        step_list[i][j] = -step_list[i][j] # step이 -이면 speed를 -로 바꾸기
                        speed_list[i][j] = -speed_list[i][j]
                    step_list[i][j] = ServoOperationUtilsProcess().truncate_step_step(step_list[i][j], raise_error) # cycle 자르기
        ### schedule 모드가 아니면 겉 list 제거
        if not is_schedule:
            step_list = step_list[0]
            speed_list = speed_list[0]
        return step_list, speed_list

    ### time_list 변환
    def convert_time_list(self, time_list, speed_list, step_list, speed_option, step_option, run_number, sync, run_option, time_option):
        ### 스케줄 모드 확인
        if run_option.lower() == "schedule":
            is_schedule = True
        else:
            is_schedule = False
        ### 스케줄 모드가 아니면 list of list화
        if not is_schedule:
            time_list = [time_list]
            out_list = [[None]*run_number]
            speed_list = [speed_list]
            step_list = [step_list]
        ### 스케줄 모드이면 바이트 확장, 리턴 초기화
        else:
            if time_option.lower() == "speed":
                if len(speed_list) == 1:
                    speed_list = self.list_product_copy(speed_list, run_number) # speed 리스트 확장
                out_list = [[None]*len(speed_list[x]) for x in range(len(speed_list))] # 초기화
            elif time_option.lower() == "step":
                if len(step_list) == 1:
                    step_list = self.list_product_copy(step_list, run_number) # step 리스트 확장
                    og_step_list = list(copy.deepcopy(step_list))
                out_list = [[None]*len(step_list[x]) for x in range(len(step_list))] # 초기화
        ### time 리스트 바이트 확장
        if len(time_list) == 1:
            time_list = self.list_product_copy(time_list, run_number)
        ### 타임 옵션 체크
        ### 타임 옵션 speed 모드: 타임 리스트 체크 및 스텝 리스트 작성
        if time_option.lower() == "speed": # speed 단위: SPS, time 단위: sec, speed_limit 이후
            ### time 리스트: 0보다 크고, 65535 스텝 이상이 될 수 없음.
            for i in range(len(time_list)):
                ### 내부 원소 길이는 이미 정리 함. (len_check)
                for j in range(len(time_list[i])):
                    ServoOperationUtilsCheck().float_check(time_list[i][j])
                    if time_list[i][j] < 0:
                        raise ValueError("Time cannot smaller than 0.")
                    ### step_list 작성, 단위는 STEP
                    if speed_list[i][j] == 0:
                        out_list[i][j] = round(time_list[i][j]*1000)
                        if out_list[i][j] > 65535:
                            raise ValueError("Sleep time cannot bigger than 65.535.")
                    else:
                        speed_element = self.SPS_to_RPM(speed_list[i][j])/60 # RPS
                        out_list[i][j] = abs(round(self.cycle_to_step(speed_element*time_list[i][j])))
                        if out_list[i][j] > 65535:
                            raise ValueError("Step cannot bigger than 65535. Maximum time is {} sec.".format(32.7675/speed_element))
            step_option = "STEP"
        ### 타임 옵션 step 모드: 타임 리스트 체크 및 스피드 리스트 작성
        elif time_option.lower() == "step": # step 단위: STEP, time 단위: sec, step_limit 이전
            ### 사이클 체크 & 변환 
            if step_option.upper() == "CYCLE":
                raise_error = sync and run_number > 1 # truncate 에러 발생
                for i in range(len(step_list)):
                    for j in range(len(step_list[i])):
                        if isinstance(step_list[i][j], str): 
                            if not (step_list[i][j].lower() in ["stop", "sleep"]): # sleep 모드
                                raise ValueError("Unknown option in step_list. step_list elements must be int, float, or str with \"stop\" or \"sleep\" option.")
                            else:
                                step_list[i][j] = 0
                        else:
                            ServoOperationUtilsCheck().float_check(step_list[i][j])
                            step_list[i][j] = ServoOperationUtilsProcess().truncate_cycle_step(step_list[i][j], raise_error) # cycle 자르기
                            step_list[i][j] = self.cycle_to_step(step_list[i][j]) # 단위를 cycle에서 step으로 변경
                step_option = "STEP"
            ### time 리스트: 0보다 크고, +- 30 이상 +- 3 이하 스피드가 될 수 없음.
            for i in range(len(time_list)):
                ### 내부 원소 길이는 이미 정리 함. (len_check)
                for j in range(len(time_list[i])):
                    ### time 리스트 체크
                    ServoOperationUtilsCheck().float_check(time_list[i][j])
                    if time_list[i][j] < 0:
                        raise ValueError("Time cannot smaller than 0.")
                    ### speed_list 작성, 단위는 SPS
                    if step_list[i][j] == 0: # ***step이 0이면 sleep 모드로 정함
                        step_list[i][j] = round(time_list[i][j]*1000) # step 변경
                        if step_list[i][j] > 65535:
                            raise ValueError("Sleep time cannot bigger than 65.535 sec.")
                        out_list[i][j] = 0
                    else:
                        step_element = self.step_to_cycle(step_list[i][j]) # step to cycle
                        RPM = step_element/time_list[i][j]*60 # cycle to RPM
                        if RPM < -30 or -3 < RPM < 3 or RPM > 30: # 오류
                            og_step = og_step_list[i][j]
                            raise ValueError("Speed cannot bigger than +-30 RPM or smaller than +-3 RPM. Maximum time is {} sec, and minimum time is {} sec of step {}.".format(abs(step_element*20), abs(step_element*2), og_step))
                        out_list[i][j] = round(self.RPM_to_SPS(RPM)) # RPM to SPS
            speed_option = "SPS"
        ### 스케줄 모드가 아니면 겉 list 제거
        if not is_schedule:
            out_list = out_list[0]
            step_list = step_list[0]        
        return out_list, step_list, speed_option, step_option

    ### 바이트 확장 or 축소
    def expand_bytes(self, cube_ID_list, connection_number, run_number, *input_list):
        input_list_copy = list(copy.deepcopy(input_list))
        ### all이면 모든 cube ID로 늘림
        if cube_ID_list[0] == 0xFF:
            cube_ID_list = [i for i in range(connection_number)]
        ### 길이가 1이면 run_number 개수만큼 늘림
        for i in range(len(input_list_copy)):
            if len(input_list_copy[i]) == 1:
                input_list_copy[i] *= run_number
        ### 리스트 붙이기 (return은 cube_ID_list와 input_list의 원소 리스트들)
        out_list = []
        out_list += [cube_ID_list]
        out_list += input_list_copy
        return tuple(out_list)

    ### sync 체크 함수 (time_option이 none일 때 사용, limit과 expand 이후)
    def check_time_sync_none(self, speed_list, step_list, sync, run_number, run_option):
        ### 스케줄 모드 확인
        if run_option.lower() == "schedule":
            is_schedule = True
        else:
            is_schedule = False
        ### sync 계산
        len_changed = False
        if sync and run_number > 1:
            ### 스텝 모드 (speed: SPS, step: STEP)
            if not is_schedule:
                step_element_idx0 = self.step_to_cycle(step_list[0])
                speed_element_idx0 = self.SPS_to_RPM(speed_list[0])
                for i in range(1, len(speed_list)):
                    step_element_idxi = self.step_to_cycle(step_list[i])
                    speed_element_idxi = self.SPS_to_RPM(speed_list[i])
                    if abs(step_element_idx0/speed_element_idx0)-abs(step_element_idxi/speed_element_idxi) > 0.001:
                        raise ValueError("Step is not syncronous. Time offset of each step must be less than 0.001 sec.")
            ### 스케줄 모드 (speed: SPS, step: STEP)
            else:
                # len(speed_list) == len(step_list) == run_number
                offset_list = [0]*len(speed_list)
                offset_flag = False
                j = 0
                while j < len(speed_list[0]): # len(speed_list[0])가 계속 변함
                    step_element_idx0j_step = step_list[0][j]
                    step_element_idx0j_cycle = self.step_to_cycle(step_list[0][j])
                    speed_element_idx0j = self.SPS_to_RPM(speed_list[0][j])
                    i = 1
                    while i < len(speed_list):
                        step_element_idxij_step = step_list[i][j]
                        step_element_idxij_cycle = self.step_to_cycle(step_list[i][j])
                        speed_element_idxij = self.SPS_to_RPM(speed_list[i][j])
                        if speed_element_idx0j == 0 and speed_element_idxij == 0:
                            offset = abs(step_element_idx0j_step/1000)-abs(step_element_idxij_step/1000)
                        elif speed_element_idx0j == 0:
                            offset = abs(step_element_idx0j_step/1000)-abs(step_element_idxij_cycle/speed_element_idxij)
                        elif speed_element_idxij == 0:
                            offset = abs(step_element_idx0j_cycle/speed_element_idx0j)-abs(step_element_idxij_step/1000)
                        else:
                            offset = abs(step_element_idx0j_cycle/speed_element_idx0j)-abs(step_element_idxij_cycle/speed_element_idxij)
                        if abs(offset) > 0.001:
                            raise ValueError("Schedule is not syncronous. Time offset of each schedule must be less than 0.001 sec.")
                        offset_list[i] += offset
                        if offset_list[i] > 0.001:
                            len_changed = True
                            if not offset_flag:
                                for k in range(len(speed_list)):
                                    speed_list[k].insert(j+1, 0)
                                    step_list[k].insert(j+1, 0)
                                offset_flag = True
                            step_list[i][j+1] += 1 # 1 ms
                            offset_list[i] -= 0.001
                        elif offset_list[i] < -0.001:
                            len_changed = True
                            if not offset_flag:
                                for k in range(len(speed_list)):
                                    speed_list[k].insert(j+1, 0)
                                    step_list[k].insert(j+1, 1)
                                offset_flag = True
                            step_list[i][j+1] -= 1 # 1 ms
                            offset_list[i] += 0.001
                        i += 1
                    if offset_flag:
                        j += 2
                    else:
                        j += 1
                    offset_flag = False
            if len_changed:
                ######################## 스케줄 리스트가 바뀌면 포인트는 어떻게 하지??????????????????????????????????????????
                print("Warning. speed_list and step list length have changed due to time offset.")
                print("speed_list(in SPS):", speed_list)
                print("step_list(in STEP):", step_list)
        return speed_list, step_list
    
    ### wait 변환 함수 
    def convert_wait(self, speed_list, step_list, pause_list, run_option):
        ### 스케줄 모드 확인
        if run_option.lower() == "schedule":
            is_schedule = True
        else:
            is_schedule = False
        def cal_time(speed_element, step_element):
            if speed_element == 0:
                new_time_out = step_element/1000
            else:
                speed_element = self.SPS_to_RPM(speed_element)/60 # RPS
                step_element = self.step_to_cycle(step_element)
                new_time_out = abs(step_element/speed_element)
            return new_time_out
        # speed: SPS, step: STEP
        max_time = 0
        ### step 모드
        if not is_schedule:
            for i, (speed_element, step_element) in enumerate(zip(speed_list, step_list)):
                if pause_list[i]: # pause이면 wait 무시
                    new_time = 0
                else:
                    new_time = cal_time(speed_element, step_element)
                if new_time > max_time:
                    max_time = new_time
        ### schedule 모드
        else:
            for i in range(len(speed_list)):
                if pause_list[i]: # pause이면 wait 무시
                    new_time = 0
                else:
                    new_time = 0
                    for (speed_element, step_element) in zip(speed_list[i], step_list[i]):
                        new_time += cal_time(speed_element, step_element)
                if new_time > max_time:
                    max_time = new_time
        return max_time

    def convert_wait_point(self, cube_ID_list, robot_status, group_id, start_point_list, stop_point_list, repeat_list, pause_list):
        def cal_time(speed_element, step_element):
            if speed_element == 0:
                new_time_out = step_element/1000
            else:
                speed_element = self.SPS_to_RPM(speed_element)/60 # RPS
                step_element = self.step_to_cycle(step_element)
                new_time_out = abs(step_element/speed_element)
            return new_time_out
        # speed: SPS, step: STEP
        speed_list = []
        step_list = []
        for cube_ID_element in cube_ID_list:
            speed_list.append(robot_status[group_id].controller_status.stepper_speed_schedule[cube_ID_element])
            speed_list.append(robot_status[group_id].controller_status.stepper_step_schedule[cube_ID_element])
        ### max time 계산
        max_time = 0
        for i in range(len(start_point_list)): # i: cube ID 인덱스
            if pause_list[i]: # pause이면 wait 무시
                new_time = 0
            else:
                new_time = 0
                for j in range(len(start_point_list[i])): # j: 포인트 인덱스
                    new_time_j = 0
                    for k in range(start_point_list[i][j], stop_point_list[i][j]+1): # k: 스피드, 스텝 인덱스, +1은 마지막 인덱스 포함 때문.
                        new_time_j += cal_time(speed_list[i][k], step_list[i][k])
                    new_time_j *= repeat_list[i][j] # 반복되는 만큼 곱함
                    new_time += new_time_j
            if new_time > max_time:
                max_time = new_time
        return max_time

    ### start_and_stop_list 변환 함수
    def convert_start_and_stop_list(self, start_and_stop_list):
        # Ex)
        # [[1, 2], [3, 4]]
        # [1, 2]
        # [[1, 2], [3, 4], [5, 6]]
        # [2, [2, 3], [3], [4, 5]]
        start = []
        stop = []
        if isinstance(start_and_stop_list, (list, tuple)):
            for i in range(len(start_and_stop_list)):
                if isinstance(start_and_stop_list[i], (list, tuple)):
                    if len(start_and_stop_list[i]) == 1:
                        start_and_stop_list[i] *= 2
                    elif len(start_and_stop_list[i]) != 2:
                        raise ValueError("If start_and_stop_list elements are list of lists (or tuple), elemental lists must be 1 or 2-length list (or tuple).")
                    if not isinstance(start_and_stop_list[i][0], int) or not isinstance(start_and_stop_list[i][1], int):
                        raise ValueError("If start_and_stop_list elements are list of lists (or tuple), elemental lists must have integer elements.")
                    else:
                        ### list 등록
                        start.append(start_and_stop_list[i][0])
                        stop.append(start_and_stop_list[i][1])
                elif isinstance(start_and_stop_list[i], int):
                    ### list 등록
                    start.append(start_and_stop_list[i])
                    stop.append(start_and_stop_list[i])
                else:
                    raise ValueError("start_and_stop_list must have list or int elements.")
            return start, stop
        elif isinstance(start_and_stop_list, int):
            ### list 등록
            start = start_and_stop_list
            stop = start_and_stop_list
            return start, stop
        else:
            raise ValueError("start_and_stop_list elements must be list (or tuple), or int.")
    
    ### duration 변환
    def convert_servo_duration(self, servo_duration, servo_angle_list, run_number):
        if len(servo_angle_list) == 1:
            ### 스피드 만들기
            speed = [[0]*len(servo_angle_list[0])]*run_number
            ### 스텝 만들기
            if len(servo_duration) == 1:
                if len(servo_duration[0]) == 1:
                    step = [servo_duration[0]*len(servo_angle_list[0])]*run_number
                else:
                    step = servo_duration*run_number
            else:
                step = servo_duration.copy()
        else:
            ### 스피드 만들기
            speed = []
            for angle_elem_list in servo_angle_list:
                speed.append([0]*len(angle_elem_list))
            ### 스텝 만들기
            if len(servo_duration) == 1:
                if len(servo_duration[0]) == 1:
                    step = []
                    for angle_elem_list in servo_angle_list:
                        step.append(servo_duration[0]*len(angle_elem_list))
                else: 
                    step = servo_duration*run_number # 길이가 다른 경우는 len_check_elemental_list에서 걸러짐.
            else:
                step = servo_duration.copy()
        return speed, step


class ServoOperationUtils(ServoOperationUtilsCheck, ServoOperationUtilsProcess, ServoOperationUtilsSet, ServoOperationUtilsConvert):
    ### agg 설정이 올 때까지 잡아두기
    def wait_until_agg_set(self, get_robot_status, set_robot_status, group_id, connection_number):
        if connection_number > 1:
            while get_robot_status(group_id, status="processed_status", variable="stepper_agg_set") != True:
                pass
            set_robot_status(group_id, status="processed_status", variable="stepper_agg_set", value=False)

