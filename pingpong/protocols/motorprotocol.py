from protocols.byteutils import ByteUtils
from protocols.protocolutils import ProtocolUtils

class MotorProtocol():
    def __init__(self, number, group_id):
        self.connection_number = number
        self._group_id = group_id

    def _set_pause(self, hexlist, pause, pause_location):
        ### set pause
        if pause:
            ### pause protocol
            hexlist[pause_location] = 1 
        else:
            ### resume protocol
            hexlist[pause_location] = 2 
        return hexlist

    def _generic_stepper_hexlist(self, hexlist, cube_ID, group_id, pause) -> list:
        """generic protocol (group_id, cube ID, connection number, pause)"""
        ### set discovery group
        hexlist = ProtocolUtils.set_group_id(hexlist, group_id)
        ### set cube ID 
        hexlist = ProtocolUtils.set_cube_ID(hexlist, cube_ID)
        ### set connection number
        hexlist = ProtocolUtils.set_connection_number(hexlist, self.connection_number)
        ### set pause
        hexlist = self._set_pause(hexlist, pause, 12)
        return hexlist

    def _SPS_to_hexlist(self, speed: int, n: int) -> list:
        """convert SPS to unsigned 16 hex list with n bytes"""
        unsigned_speed = ByteUtils().unsigned16(speed)
        return ByteUtils().int_to_hexlist(unsigned_speed, n)

    @staticmethod
    def RPM_to_SPS(RPM: float) -> int or None:
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

    @staticmethod
    def SPS_to_RPM(SPS: int) -> float or None:
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

    @staticmethod
    def cycle_to_step(cycle) -> int:
        step = cycle*2000
        return round(step)

    @staticmethod
    def step_to_cycle(step) -> float:
        cycle = step/2000
        return cycle

    @staticmethod
    def truncate_RPM_speed(speed: float, raise_error=False) -> int or float:
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

    @staticmethod
    def truncate_SPS_speed(speed: int, raise_error=False) -> int:
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

    @staticmethod
    def truncate_cycle_step(step: float, raise_error=False) -> int or float:
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

    @staticmethod
    def truncate_step_step(step: float, raise_error=False) -> int or float:
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
    
    def make_dummy(self, in_bytes) -> bytes:
        """make OP code into 0"""
        in_bytes_list = list(in_bytes)
        in_bytes_list[6] = 0
        return bytes(in_bytes_list)

    def SetContinuousSteps_bytes(self, cube_ID, speed, group_id=None, pause=False) -> bytes:
        group_id = ProtocolUtils.proc_group_id(self._group_id, group_id)
        ### FF FF FF 00 10 00 CC 00 0F 01 00 00 02 11 11
        hexlist = [0xFF, 0xFF, 0xFF, 0x00, 0x10, 0x00, 0xCC, 0x00, 0x0F, 0x02, 0x00, 0x00, 0x02, 0x00, 0x00]
        
        ### generic process (discovery group & cube ID & robot number & pause protocol)
        hexlist = self._generic_stepper_hexlist(hexlist, cube_ID, group_id, pause)
        ### Set mode multirole 
        #hexlist[9] 
        ### convert & set speed
        hexlist[13:15] = self._SPS_to_hexlist(round(speed), 2) 
        return bytes(hexlist)

    def SetSingleSteps_bytes(self, cube_ID, speed, step, group_id=None, pause=False) -> bytes:
        group_id = ProtocolUtils.proc_group_id(self._group_id, group_id)
        ### FF FF FF 00 10 00 C1 00 13 02 01 00 02 00 00 00 00 00 00 ~
        hexlist = [0xFF, 0xFF, 0xFF, 0x00, 0x10, 0x00, 0xC1, 0x00, 0x13, 0x02, 0x01, 0x00, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        
        ### generic process (discovery group & cube ID & robot number & pause protocol)
        hexlist = self._generic_stepper_hexlist(hexlist, cube_ID, group_id, pause) 
        ### set method (1: RelativeSingleSteps, 2: AbsoluteSingleSteps)
        #hexlist[10] = method 
        ### convert & set speed
        hexlist[13:15] = self._SPS_to_hexlist(round(speed), 2) 
        ### set start phase
        #hexlist[15:17] = [0, 0] 
        ### set step value (0 to 65535, [2000 = 1 cycle])
        hexlist[17:19] = ByteUtils().int_to_hexlist(round(step), 2) 
        return bytes(hexlist)

    def SetScheduledSteps_bytes(self, cube_ID, speed_seq_list, step_seq_list, group_id=None, pause=False, \
            step_type=0, servo_angle_list=None, servo_angle_timeout_list=None) -> bytes:
        group_id = ProtocolUtils.proc_group_id(self._group_id, group_id)
        ### FF FF FF 00 10 00 CA 00 0F 02 03 00 02 00 00 ~
        hexlist = [0xFF, 0xFF, 0xFF, 0x00, 0x10, 0x00, 0xCA, 0x00, 0x0F, 0x02, 0x03, 0x00, 0x02, 0x00, 0x00]
        
        ### generic process (discovery group & cube ID & robot number & pause protocol)
        hexlist = self._generic_stepper_hexlist(hexlist, cube_ID, group_id, pause) 
        if step_type == 0: 
            ### set data size (stepper)
            hexlist[7:9] = ByteUtils().int_to_hexlist(15 + 4*len(speed_seq_list), 2)
        elif step_type == 4:
            ### set data size (servo)
            hexlist[7:9] = ByteUtils().int_to_hexlist(15 + 6*len(speed_seq_list), 2)
        ### step type (0: FullSteps, 4: SetServo)
        hexlist[11] = step_type 
        ### CRC16 
        hexlist[13:15] = [0, 0]
        if step_type == 0: 
            ### Full Step mode
            for i in range(len(speed_seq_list)):
                ### set speed schedule
                hexlist.extend(self._SPS_to_hexlist(round(speed_seq_list[i]), 2))
                ### set step schedule (if speed = 0, sleep [step] ms.)
                hexlist.extend(ByteUtils().int_to_hexlist(round(step_seq_list[i]), 2))
        elif step_type == 4: 
            ### Servo mode
            for i in range(len(speed_seq_list)):
                ### set speed schedule of stepper motor
                hexlist.extend(self._SPS_to_hexlist(round(speed_seq_list[i]), 2))
                ### set step schedule of stepper motor
                hexlist.extend(ByteUtils().int_to_hexlist(round(step_seq_list[i]), 2))
                ### set servo angle (0 to 180 deg)
                hexlist.append(servo_angle_list[i])
                ### set servo timeout (0 to 255 sec, 256 for 21.845 min)
                hexlist.append(servo_angle_timeout_list[i])
        return bytes(hexlist)

    def SetScheduledPoints_bytes(self, cube_ID, start_point_list, stop_point_list, repeat_list, group_id=None, \
            pause=False, step_type=0) -> bytes:
        group_id = ProtocolUtils.proc_group_id(self._group_id, group_id)
        ### FF FF FF 00 10 00 CB 00 0F 02 04 00 02 00 00 ~
        hexlist = [0xFF, 0xFF, 0xFF, 0x00, 0x10, 0x00, 0xCB, 0x00, 0x0F, 0x02, 0x04, 0x00, 0x02, 0x00, 0x00]
        
        ### generic process (cube ID & robot number & pause protocol)
        hexlist = self._generic_stepper_hexlist(hexlist, cube_ID, group_id, pause) 
        ### set data size
        hexlist[7:9] = ByteUtils().int_to_hexlist(15 + 5*len(start_point_list), 2) 
        ### step type (0: FullSteps, 4: SetServo)
        hexlist[11] = step_type 
        ### CRC16 
        #hexlist[13:15] = [0, 0]
        for i in range(len(start_point_list)):
            ### set start point of schedule
            hexlist.extend(ByteUtils().int_to_hexlist(start_point_list[i], 2))
            ### set stop point of schedule
            hexlist.extend(ByteUtils().int_to_hexlist(stop_point_list[i], 2))
            ### set repeat time of schedule
            hexlist.append(repeat_list[i])
        return bytes(hexlist)

    def SetAggregateSteps_bytes(self, group_id, *in_bytes) -> bytes:
        """step motor command to master robot"""
        group_id = ProtocolUtils.proc_group_id(self._group_id, group_id)
        ### FF FF 01 AA 10 00 CD 00 12 02 00 00 00 ~
        hexlist = [0xFF, 0xFF, 0x01, 0xAA, 0x10, 0x00, 0xCD, 0x00, 0x12, 0x02, 0x00, 0x00, 0x00]
        ### set discovery group ID
        hexlist = ProtocolUtils.set_group_id(hexlist, group_id)
        ### set connection number
        hexlist = ProtocolUtils.set_connection_number(hexlist, self.connection_number)
        ### get total data size
        in_bytes_length = len(in_bytes)
        total_length = 0
        for i in range(in_bytes_length):
            total_length = total_length + len(in_bytes[i])
        ### set data number
        hexlist[7:9] = ByteUtils().int_to_hexlist(13 + total_length, 2) 
        if in_bytes[0][6] == 0xCC:
            ### Continuous Steps
            hexlist[10] = 0
        elif in_bytes[0][6] == 0xC1:
            ### Relative Single Steps
            hexlist[10] = 1
        elif in_bytes[0][6] == 0xCA:
            ### Scheduled Steps
            hexlist[10] = 3
        elif in_bytes[0][6] == 0xCB:
            ### Scheduled Points
            hexlist[10] = 4
        ### attatch in_bytes
        hexlist_bytes = bytes(hexlist)
        for i in range(in_bytes_length):
            hexlist_bytes += in_bytes[i]
        return hexlist_bytes

    def SetPauseSteps_bytes(self, pause, cube_ID=None, group_id=None, agg=False) -> bytes:
        group_id = ProtocolUtils.proc_group_id(self._group_id, group_id)
        if not agg:
            ### FF FF FF 00 10 00 C0 00 0A 02
            hexlist = [0xFF, 0xFF, 0xFF, 0x00, 0x10, 0x00, 0xC0, 0x00, 0x0A, 0x02]
            ### set discovery group
            hexlist = ProtocolUtils.set_group_id(hexlist, group_id)
            ### set cube ID 
            hexlist = ProtocolUtils.set_cube_ID(hexlist, cube_ID)
            ### set connection number
            hexlist = ProtocolUtils.set_connection_number(hexlist, self.connection_number)
            ### set pause
            hexlist = self._set_pause(hexlist, pause, 9)
        else: 
            ### aggregate mode
            ### AA AA 01 AA 10 00 C0 00 0A 02
            hexlist = [0xAA, 0xAA, 0x01, 0xAA, 0x10, 0x00, 0xC0, 0x00, 0x0A, 0x02]
            ### set discovery group
            hexlist = ProtocolUtils.set_group_id(hexlist, group_id)
            ### set connection number
            hexlist = ProtocolUtils.set_connection_number(hexlist, self.connection_number)
            ### set pause
            hexlist = self._set_pause(hexlist, pause, 9)
        return bytes(hexlist)

    def SetInstantTorque(self, is_max_torque, cube_ID=None, group_id=None, agg=False) -> bytes:
        group_id = ProtocolUtils.proc_group_id(self._group_id, group_id)
        # SPS > 700
        if not agg:
            ### FF FF FF 00 10 00 C0 00 0A 02
            hexlist = [0xFF, 0xFF, 0xFF, 0x00, 0x10, 0x00, 0xC6, 0x00, 0x0A, 0x02]
            ### set discovery group
            hexlist = ProtocolUtils.set_group_id(hexlist, group_id)
            ### set cube ID 
            hexlist = ProtocolUtils.set_cube_ID(hexlist, cube_ID)
            ### set connection number
            hexlist = ProtocolUtils.set_connection_number(hexlist, self.connection_number)
            if is_max_torque:
                ### max torque
                hexlist[9] = 1 
            else:
                ### default torque
                hexlist[9] = 0 
        else: 
            ### aggregate mode
            # AA AA 01 AA 10 00 C0 00 0A 02
            hexlist = [0xAA, 0xAA, 0x01, 0xAA, 0x10, 0x00, 0xC6, 0x00, 0x0A, 0x02]
            ### set discovery group
            hexlist = ProtocolUtils.set_group_id(hexlist, group_id)
            ### set connection number
            hexlist = ProtocolUtils.set_connection_number(hexlist, self.connection_number)
            if is_max_torque:
                ### max torque
                hexlist[9] = 1 
            else:
                ### default torque
                hexlist[9] = 0 
        return bytes(hexlist)

    def SetSingleServo(self, cube_ID, servo_value, timeout, group_id=None) -> bytes:
        group_id = ProtocolUtils.proc_group_id(self._group_id, group_id)
        hexlist = [0xFF, 0xFF, 0xFF, 0x00, 0x10, 0x00, 0xE1, 0x00, 0x0D, 0x02, 0x00, 0x00, 0x01]
        ### set discovery group
        hexlist = ProtocolUtils.set_group_id(hexlist, group_id)
        ### set cube ID 
        hexlist = ProtocolUtils.set_cube_ID(hexlist, cube_ID)
        ### set connection number
        hexlist = ProtocolUtils.set_connection_number(hexlist, self.connection_number)
        ### Method?
        #hexlist[10]
        ### set servo value (0 to 180 deg)
        hexlist[11] = servo_value
        ### set servo timeout (0 to 255 sec, 256 for 21.845 min)
        hexlist[12] = timeout
        return bytes(hexlist)