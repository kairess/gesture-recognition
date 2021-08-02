from protocols.byteutils import ByteUtils
from protocols.protocolutils import ProtocolUtils

class MusicProtocol():
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

    def SetMusicNotesInAction_SetMusicNotes_bytes(self, cube_ID, pianokey_list, duration_list, rest_list, \
            group_id=None, pause=False) -> bytes:
        group_id = ProtocolUtils.proc_group_id(self._group_id, group_id)
        hexlist = [0xFF, 0xFF, 0x01, 0x00, 0x00, 0xA1, 0xE8, 0x00, 0x0B, 0x00, 0x00]
        ### set discovery group
        hexlist = ProtocolUtils.set_group_id(hexlist, group_id)
        ### set cube ID (0 to 7)
        hexlist = ProtocolUtils.set_cube_ID(hexlist, cube_ID)
        ### set pause
        if pause:
            ### pause protocol
            hexlist[10] = 1 
        else:
            ### play protocol
            hexlist[10] = 0
        ### set data size (stepper)
        hexlist[7:9] = ByteUtils().int_to_hexlist(11 + 3*len(pianokey_list), 2)
        ### PianoKeyInEqualTemperedScaleE ?
        #hexlist[9] = 0 
        ### set pianokey, duration, rest
        for i in range(len(pianokey_list)):
            hexlist.append(pianokey_list[i])
            hexlist.append(duration_list[i])
            hexlist.append(rest_list[i])
        return bytes(hexlist)

    def SetMusicNotesInAction_AggregateSetMusicNotes_bytes(self, group_id, *in_bytes) -> bytes:
        group_id = ProtocolUtils.proc_group_id(self._group_id, group_id)
        hexlist = [0xAA, 0xAA, 0x01, 0xAA, 0x10, 0xA2, 0xE8, 0x00, 0x0B, 0x00, 0x00]
        ### set discovery group
        hexlist = ProtocolUtils.set_group_id(hexlist, group_id)
        ### set connection number
        hexlist = ProtocolUtils.set_connection_number(hexlist, self.connection_number)
        ### get total data size
        total_length = 0
        for i in range(len(in_bytes)):
            total_length = total_length + len(in_bytes[i])
        ### set total data size
        hexlist[7:9] = ByteUtils().int_to_hexlist(11 + total_length, 2) 
        ### attatch in_bytes
        for i in range(len(in_bytes)):
            hexlist.extend(list(in_bytes[i]))
        return bytes(hexlist)
        
    def SetMusicNotesInAction_PlayMusicNotes_bytes(self, cube_ID, play, group_id=None) -> bytes:
        group_id = ProtocolUtils.proc_group_id(self._group_id, group_id)
        hexlist = [0xFF, 0xFF, 0x01, 0x00, 0x00, 0xE8, 0xE8, 0x00, 0x0A, 0x02]
        ### set discovery group
        hexlist = ProtocolUtils.set_group_id(hexlist, group_id)
        ### set cube ID (0 to 7)
        hexlist = ProtocolUtils.set_cube_ID(hexlist, cube_ID)
        ### set plat
        if play:
            ### resume (play: 0, resuem: 2 [차이점?])
            hexlist[9] = 2 
        else:
            ### pause
            hexlist[9] = 1
        return bytes(hexlist)