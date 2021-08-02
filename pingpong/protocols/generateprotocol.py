from protocols.motorprotocol import MotorProtocol
from protocols.musicprotocol import MusicProtocol
from protocols.ledmatrixprotocol import LEDMatrixProtocol
from protocols.cubeprotocol import CubeProtocol
from protocols.byteutils import ByteUtils

class GenerateProtocol(MotorProtocol, MusicProtocol, LEDMatrixProtocol, CubeProtocol):
    #FF FF FF FF 00 00 A8 00 0A 01
    PingPong_disconnect_hexlist = [0xFF, 0xFF, 0xFF, 0xFF, 0x00, 0x00, 0xA8, 0x00, 0x0A, 0x01]
    PingPong_disconnect_bytes = bytes(PingPong_disconnect_hexlist)

    def __init__(self, number, group_id):
        self.connection_number = number
        self._group_id = group_id
        MotorProtocol.__init__(self, number, group_id)
        MusicProtocol.__init__(self, number, group_id)
        LEDMatrixProtocol.__init__(self, number, group_id)
        CubeProtocol.__init__(self, number, group_id)

    # For instance function
    def _process_cube_ID(self, cube_ID):
        if str(cube_ID).lower() == "all":
            cube_ID = 0xFF
        else:
            ByteUtils().integer_check(cube_ID, "all") # 정수 체크
            cube_ID = int(cube_ID) # 정수로 변환 
            if not (1 <= cube_ID and cube_ID <= 8):
                raise ValueError("Cube ID must be between 1 to 8.")
            elif cube_ID > self.connection_number:
                raise ValueError("Cube ID must be less than or equal to connection number.")
            cube_ID -= 1 # (1 to 8 -> 0 to 7)
        return cube_ID

    # For instance function
    def _if_all_function(self, func, not_all_arg, all_cond) -> None:
        if all_cond:
            for idx in range(self.connection_number):
                func(idx)
        else:
            func(not_all_arg)

    @staticmethod
    def DongleInAction_bytes() -> bytes:
        #DD DD DD DD 00 01 DA 00 0B 00 0D
        DongleInAction_hexlist = [0xDD, 0xDD, 0xDD, 0xDD, 0x00, 0x01, 0xDA, 0x00, 0x0B, 0x00, 0x0D]
        return bytes(DongleInAction_hexlist)

    def PingPongGn_connect_bytes(self) -> bytes:
        if self.connection_number == 1: # 1개
            #DD DD 00 00 00 00 DA 00 0B 00 00
            PingPongG1_connect_hexlist = [0xDD, 0xDD, 0x00, 0xDD, 0x00, 0x00, 0xDA, 0x00, 0x0B, 0x00, 0x00]
            if self._group_id != None:
                group_id = int("0x"+str(self._group_id), 16)
                PingPongG1_connect_hexlist[2] = group_id
            return bytes(PingPongG1_connect_hexlist)
        else: # 2개 이상
            #FF FF 00 FF 20 00 AD 00 0B 0A 00
            PingPongGn_connect_hexlist = [0xFF, 0xFF, 0x00, 0xFF, 0x20, 0x00, 0xAD, 0x00, 0x0B, 0x0A, 0x00] 
            PingPongGn_connect_hexlist[4] = self.connection_number*16 # connection number
            if self._group_id != None:
                group_id = int("0x"+str(self._group_id), 16)
                PingPongGn_connect_hexlist[2] = group_id
                PingPongGn_connect_hexlist[9] = 0x1A
                PingPongGn_connect_hexlist[10] = group_id
            return bytes(PingPongGn_connect_hexlist)
