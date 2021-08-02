from protocols.protocolutils import ProtocolUtils

class CubeProtocol():
    def __init__(self, number, group_id):
        self.connection_number = number
        self._group_id = group_id
    
    def GetSensors_bytes(self, cube_ID, action_method, group_id=None):
        group_id = ProtocolUtils.proc_group_id(self._group_id, group_id)
        hexlist = [0xFF, 0xFF, 0xFF, 0x00, 0x00, 0xC8, 0xB8, 0x00, 0x0B, 0x00, 0x01]
        ### set discovery group
        hexlist = ProtocolUtils.set_group_id(hexlist, group_id)
        ### set cube ID
        hexlist = ProtocolUtils.set_cube_ID(hexlist, cube_ID)
        ### set action method (0 -> single or stop sampling, 1 to 100 -> sample period 0.01s to 1.0s)
        hexlist[9] = action_method
        ### set get method (0 -> default, 1 -> 8bit real)
        #hexlist[10] = get_method
        return bytes(hexlist)
