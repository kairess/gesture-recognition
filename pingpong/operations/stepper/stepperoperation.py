from protocols.generateprotocol import GenerateProtocol
from operations.stepper.stepperoperationutils import StepperOperationUtils
from operations.stepper.stepperoperationbase import ContinuousStepperOperation, SingleStepsStepperOperation, ScheduledStepsStepperOperation, ScheduledPointsStepperOperation
import time, copy

class StepperOperation(ContinuousStepperOperation, SingleStepsStepperOperation, ScheduledStepsStepperOperation, ScheduledPointsStepperOperation):
    def __init__(self, number, group_id, robot_status, start_check, write):
        self._GenerateProtocolInstance = GenerateProtocol(number, group_id)
        self._robot_status = robot_status
        self._start_check_copy = start_check
        self._write_copy = write
        ContinuousStepperOperation.__init__(self, number, group_id, robot_status, start_check, write)
        SingleStepsStepperOperation.__init__(self, number, group_id, robot_status, start_check, write)
        ScheduledStepsStepperOperation.__init__(self, number, group_id, robot_status, start_check, write)
        ScheduledPointsStepperOperation.__init__(self, number, group_id, robot_status, start_check, write)

    # 모터 동작 (deprecated)
    def run_motor_prev(self, cube_ID, speed, step_cycle=None, pause=False, group_id=None, option="continue") -> None:
        group_id = StepperOperationUtils.proc_group_id(self._GenerateProtocolInstance._group_id, group_id)
        ### start 체크
        self._start_check_copy()

        ### cube_ID, speed, step 리스트화
        cube_ID_list = StepperOperationUtils().to_list(cube_ID)
        speed_list = StepperOperationUtils().to_list(speed)
        step_cycle_list = StepperOperationUtils().to_list(step_cycle)

        ### 옵션 체크, 속도, 스텝 길이 처리
        if not isinstance(option, str):
             raise ValueError("option must be str.")
        elif option.lower() == "continue":
            if not (len(speed_list) == 1):
                raise ValueError("In Continue mode, speed must have 1 element.")
        elif option.lower() == "step":
            if not (len(speed_list) == len(step_cycle_list) == 1):
                raise ValueError("In Step mode, speed and step_cycle must have 1 element.")
        elif option.lower() == "schedule":
            if not (len(speed_list) == len(step_cycle_list)):
                raise ValueError("In Schedule mode, speed and step must have same length.")
            elif len(speed_list) == 0 or len(step_cycle_list) == 0:
                raise ValueError("In Schedule mode, speed and step must not be empty list.")
        else:
            raise ValueError("Unknown option.")
        
        ### 일시정지 처리
        if not isinstance(pause, bool):
            raise ValueError("pause must be bool.")
        
        ### 큐브 ID 처리
        if cube_ID_list == [] or cube_ID_list == ():
            raise ValueError("cube ID must not be empty list.")
        StepperOperationUtils().check_same_element(cube_ID_list) # 같은 원소가 있으면 error
        for i in range(len(cube_ID_list)):
            cube_ID_list[i] = self._GenerateProtocolInstance._process_cube_ID(cube_ID_list[i])
            if cube_ID_list[i] == 0xFF and len(cube_ID_list) != 1:
                raise ValueError("If cube ID is all, input must not be length-above-2 list.")
        
        ### 속도 처리
        sleep_list = [False]*len(speed_list)
        for i in range(len(speed_list)):
            if (str(speed_list[i]).lower() in ["stop", "sleep"]) or speed_list[i] == 0: # 스피드가 0이면 sleep 모드
                speed_list[i] = 0
                sleep_list[i] = True # i번째는 sleep 모드
            else:
                StepperOperationUtils().float_check(speed_list[i], "stop")
                speed_list[i] = self._GenerateProtocolInstance.truncate_RPM_speed(speed_list[i]) # speed 자르기
                speed_list[i] = self._GenerateProtocolInstance.RPM_to_SPS(speed_list[i]) # 단위를 RPM에서 SPS로 변경

        ### 스텝 처리 (speed=0이면, step_cycle 초만큼 쉼.)
        step = [0]*len(step_cycle_list)
        if option.lower() == "step" or option.lower() == "schedule":
            for i in range(len(step_cycle_list)):
                if sleep_list[i]:
                    step_cycle_list[i] /= 2 # sleep이면 2로 나누면 초 단위가 됨.
                StepperOperationUtils().float_check(step_cycle_list[i], "stop")
                step_cycle_list[i] = self._GenerateProtocolInstance.truncate_cycle_step(step_cycle_list[i]) # step 자르기
                step[i] = self._GenerateProtocolInstance.cycle_to_step(step_cycle_list[i]) # 단위를 cycle에서 step으로 변경

        ### 작동 처리 (group_id 처리 해야함)
        ### 컨티뉴 모드
        if option.lower() == "continue": 
            if speed_list[0] == 0:
                print("Stop motor(s).")
            for cube_ID_element in cube_ID_list:
                ### status 등록
                def reg_stat(x):
                    self._robot_status[group_id].controller_status.stepper_mode[x] = "continue"
                    self._robot_status[group_id].controller_status.stepper_speed[x] = speed_list[0]
                    self._robot_status[group_id].controller_status.stepper_pause[x] = pause
                self._GenerateProtocolInstance._if_all_function(reg_stat, cube_ID_element, cube_ID_element == 0xFF)
                ### 동작
                self._write_copy(self._GenerateProtocolInstance.SetContinuousSteps_bytes(cube_ID_element, speed_list[0], group_id, pause))
                # time.sleep(0.2)
        ### 스텝 모드
        elif option.lower() == "step": 
            for cube_ID_element in cube_ID_list:
                ### status 등록
                def reg_stat(x):
                    self._robot_status[group_id].controller_status.stepper_mode[x] = "step"
                    self._robot_status[group_id].controller_status.stepper_speed[x] = speed_list[0]
                    self._robot_status[group_id].controller_status.stepper_step[x] = step[0]
                    self._robot_status[group_id].controller_status.stepper_pause[x] = pause
                self._GenerateProtocolInstance._if_all_function(reg_stat, cube_ID_element, cube_ID_element == 0xFF)
                ### 동작
                self._write_copy(self._GenerateProtocolInstance.SetSingleSteps_bytes(cube_ID_element, speed_list[0], step[0], group_id, pause))
                # time.sleep(0.2)
        ### 스케줄 모드
        elif option.lower() == "schedule": 
            for cube_ID_element in cube_ID_list:
                ### status 등록
                def reg_stat(x):
                    self._robot_status[group_id].controller_status.stepper_mode[x] = "point"
                    self._robot_status[group_id].controller_status.stepper_schedule_point_start[x] = [0]
                    self._robot_status[group_id].controller_status.stepper_schedule_point_end[x] = [len(speed_list)]
                    self._robot_status[group_id].controller_status.stepper_schedule_point_repeat[x] = [1]
                    self._robot_status[group_id].controller_status.stepper_speed_schedule[x] = speed_list
                    self._robot_status[group_id].controller_status.stepper_step_schedule[x] = step[0]
                    self._robot_status[group_id].controller_status.stepper_pause[x] = pause
                self._GenerateProtocolInstance._if_all_function(reg_stat, cube_ID_element, cube_ID_element == 0xFF)
                ### pause=True 상태로 스케줄 설정
                self._write_copy(self._GenerateProtocolInstance.SetScheduledSteps_bytes(cube_ID_element, speed_list, step, group_id, True))
                # time.sleep(0.2)
                ### 포인트로 설정
                self._write_copy(self._GenerateProtocolInstance.SetScheduledPoints_bytes(cube_ID_element, [0], [len(speed_list)], [1], group_id, True))
                # time.sleep(0.2)
            ### 재생
            if not pause:
                for cube_ID_element in cube_ID_list:
                    self._write_copy(self._GenerateProtocolInstance.SetPauseSteps_bytes(False, cube_ID_element, group_id))
                    # time.sleep(0.2)
        else:
            raise ValueError("cannot reach")
        
    # 모터 일시정지
    def pause_motor(self, cube_ID=None, group_id=None, group_mode=False) -> None:
        self._start_check_copy()
        group_id = StepperOperationUtils.proc_group_id(self._GenerateProtocolInstance._group_id, group_id)

        cube_ID_list = StepperOperationUtils().to_list(cube_ID)

        #### 그룹 모드 나중에 #############################################33
        ### 큐브 ID 처리
        if cube_ID_list == [] or cube_ID_list == ():
            raise ValueError("cube ID must not be empty list.")
        StepperOperationUtils().check_same_element(cube_ID_list) # 같은 원소가 있으면 error
        for i in range(len(cube_ID_list)):
            cube_ID_list[i] = self._GenerateProtocolInstance._process_cube_ID(cube_ID_list[i])
            if cube_ID_list[i] == 0xFF and len(cube_ID_list) != 1:
                raise ValueError("If cube ID is all, input must not be length-above-2 list.")

        ### 작동 처리 함수
        def proc_op(x):
            self._robot_status[group_id].controller_status.stepper_pause[x] = True
            ### 작동
            self._write_copy(self._GenerateProtocolInstance.SetPauseSteps_bytes(True, x, group_id, group_mode))
            # time.sleep(0.2)

        ### 작동 처리
        for cube_ID_element in cube_ID_list: 
            self._GenerateProtocolInstance._if_all_function(proc_op, cube_ID_element, cube_ID_element == 0xFF)

    
    # 모터 재생
    def play_paused_motor(self, cube_ID=None, group_id=None, group_mode=False) -> None:
        """
        Play only paused stepper/servo motor operation.
        """
        group_id = StepperOperationUtils.proc_group_id(self._GenerateProtocolInstance._group_id, group_id)
        ### 시작 체크, 리스트 처리
        self._start_check_copy()
        cube_ID_list = StepperOperationUtils().to_list(cube_ID)
 
        #### 그룹 모드 나중에 #############################################33
        ### 큐브 ID 처리
        if cube_ID_list == []:
            raise ValueError("cube ID must not be empty list.")
        StepperOperationUtils().check_same_element(cube_ID_list) # 같은 원소가 있으면 error
        for i in range(len(cube_ID_list)):
            cube_ID_list[i] = self._GenerateProtocolInstance._process_cube_ID(cube_ID_list[i])
            if cube_ID_list[i] == 0xFF and len(cube_ID_list) != 1:
                raise ValueError("If cube ID is all, input must not be length-above-2 list.")
        
        ### 작동 처리 함수
        def proc_op(x):
            if self._robot_status[group_id].controller_status.stepper_pause[x] == False: 
                print("Warning. play_paused_motor operation is ignored. Set paused motor operation before play.")
            else:
                ### status 저장
                self._robot_status[group_id].controller_status.stepper_pause[x] = False
                ### 작동
                self._write_copy(self._GenerateProtocolInstance.SetPauseSteps_bytes(False, x, group_id, group_mode))
                # time.sleep(0.2)

        ### 작동 처리
        for cube_ID_element in cube_ID_list:
            self._GenerateProtocolInstance._if_all_function(proc_op, cube_ID_element, cube_ID_element == 0xFF)

    
    ### aggregate 모드 모터 실행
    def run_motor(self, 
        cube_ID_list="all", 
        speed_list=None, 
        step_list=None, 
        pause_list=False, 
        time_list=None, 
        group_id=None, 
        run_option="continue", 
        speed_option="RPM", 
        step_option="CYCLE", 
        sync=False, 
        time_option=None,
        wait=0) -> None:
        """
        Run stepper motors as aggregate mode.
        speed_list: Integer, range from +- 100 to +- 1000, or 0. The unit is SPS(step per second?), or RPM(rotation per minute). 
        run_option: \"continue\", \"step\", \"schedule\"
        speed_option: \"RPM\", \"SPS\"
        step_option: \"CYCLE\", \"STEP\"
        sync: synchronous mode, True or False
        time_option: None, \"speed\", \"step\"
        wait: time(sec), \"step\", \"schedule\"
        """
        group_id = StepperOperationUtils.proc_group_id(self._GenerateProtocolInstance._group_id, group_id)
        ### run 옵션 처리
        if not isinstance(run_option, str):
            raise ValueError("run_option must be str.")
        elif run_option.lower() != "continue" and run_option.lower() != "step" and run_option.lower() != "schedule":
            raise ValueError("run_option must be \"continue\", \"step\", or \"schedule\".")

        ### 작동
        if run_option.lower() == "continue":
            self.run_motor_continue(cube_ID_list, speed_list, pause_list, group_id, speed_option, wait)
            return None
        elif run_option.lower() == "step":
            self.run_motor_step(cube_ID_list, speed_list, step_list, pause_list, time_list, group_id, speed_option, step_option, sync, time_option, wait)
            return None
        elif run_option.lower() == "schedule":
            self.run_motor_schedule(cube_ID_list, speed_list, step_list, pause_list, time_list, group_id, speed_option, step_option, sync, time_option, wait)
            return None

    # 모터 멈춤
    def stop_motor(self, cube_ID_list="all", group_id=None) -> None:
        self.run_motor(cube_ID_list=cube_ID_list, speed_list=0, group_id=group_id) # continue mode

    

    