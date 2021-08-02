class CubeOperationUtils():
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
    
    ### 큐브 ID 처리
    def process_cube_ID(self, cube_ID, connection_number):
        if isinstance(cube_ID, str) and cube_ID.lower() == "all":
            cube_ID = 0xFF
        else:
            self.integer_check(cube_ID, "all") # 정수 체크
            cube_ID = int(cube_ID) # 정수로 변환 
            if not (1 <= cube_ID and cube_ID <= 8):
                raise ValueError("Cube ID must be between 1 to 8.")
            elif cube_ID > connection_number:
                raise ValueError("Cube ID must be less than or equal to connection number.")
            cube_ID -= 1 # (1 to 8 -> 0 to 7)
        return cube_ID
    
    ### 메소드 체크
    def check_method(self, method, cube_ID, group_id, get_robot_status, set_robot_status):
        if not isinstance(method, str):
            raise ValueError("Method value must be str.")
        elif method.lower() != "oneshot" and method.lower() != "periodic" and method.lower() != "stop":
            raise ValueError("Method value must be \"oneshot\", \"periodic\", or \"stop\".")
        else:
            connection_number = get_robot_status(group_id, "controller_status", "connection_number")
            if method.lower() == "periodic":
                if cube_ID == 0xFF:
                    for i in range(connection_number):
                        set_robot_status(group_id, "controller_status", "get_sensor_mode[{}]".format(i), "\"periodic\"")
                else:
                    set_robot_status(group_id, "controller_status", "get_sensor_mode[{}]".format(cube_ID), "\"periodic\"")
            elif method.lower() == "oneshot": 
                if cube_ID == 0xFF:
                    prev_mode = get_robot_status(group_id, "controller_status", "get_sensor_mode")
                    periodic_flag = False
                    for i in range(connection_number):
                        if prev_mode[i] == "periodic":
                            periodic_flag = True
                        set_robot_status(group_id, "controller_status", "get_sensor_mode[{}]".format(i), "\"oneshot\"")
                    if periodic_flag:
                        print("Warning. All periodic get_sensor in group ID will be stop.")
                else:
                    prev_mode = get_robot_status(group_id, "controller_status", "get_sensor_mode[{}]".format(cube_ID))
                    if prev_mode == "periodic":
                        raise ValueError("Cannot set get_sensor mode as \"oneshot\", if the current get_sensor mode is \"periodic\".")
                    else:
                        set_robot_status(group_id, "controller_status", "get_sensor_mode[{}]".format(cube_ID), "\"oneshot\"")
            else: # method.lower() == "stop"
                if cube_ID == 0xFF:
                    prev_mode = get_robot_status(group_id, "controller_status", "get_sensor_mode")
                    not_periodic_flag = False
                    for i in range(connection_number):
                        if prev_mode[i] != "periodic":
                            not_periodic_flag = True
                        set_robot_status(group_id, "controller_status", "get_sensor_mode[{}]".format(i), "\"oneshot\"")
                    if not_periodic_flag:
                        print("Warning. All cube will give sensor data.")
                else:
                    prev_mode = get_robot_status(group_id, "controller_status", "get_sensor_mode[{}]".format(cube_ID))
                    if prev_mode != "periodic":
                        raise ValueError("Cannot set get_sensor mode as \"stop\", if the current get_sensor mode is not \"periodic\".")
                    else:
                        set_robot_status(group_id, "controller_status", "get_sensor_mode[{}]".format(cube_ID), "\"oneshot\"")

    def process_period(self, method, period):
        if method.lower() == "periodic":
            if not isinstance(period, (int, float)):
                raise ValueError("Period value must be int or float.")
            elif not (0.01 <= period <= 1):
                raise ValueError("Period value must be in between 0.01 to 1 (sec).")
            return round(period*100)
        else:
            return 0

    @staticmethod
    def proc_group_id(self_group_id, group_id):
        if group_id == None:
            return self_group_id # None or int
        else:
            return group_id # Not None, int
            
                

