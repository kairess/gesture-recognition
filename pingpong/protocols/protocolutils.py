# protocolutils.py

class ProtocolUtils():
    @staticmethod
    def set_group_id(hexlist, group_id):
        ### set discovery group ID (1 to 8)
        if group_id == None:
            hexlist[2] = 0xFF
        else:
            hexlist[2] = int("0x"+str(group_id), 16)
        return hexlist
    
    @staticmethod
    def set_cube_ID(hexlist, cube_ID):
        ### set cube ID (0 to 7)
        if str(cube_ID).lower() == 'all':
            hexlist[3] = 0xFF
        else:
            hexlist[3] = int(cube_ID) 
        return hexlist

    @staticmethod
    def set_connection_number(hexlist, connection_number):
        ### set connection number
        hexlist[4] = connection_number*16 
        return hexlist

    @staticmethod
    def proc_group_id(self_group_id, group_id):
        if group_id == None:
            return self_group_id # None or int
        else:
            return group_id # Not None, int