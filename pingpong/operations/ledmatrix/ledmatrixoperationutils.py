class LEDMatrixOperationUtils():
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

    ### 픽셀 좌표 체크
    def check_pixel_coord(self, coord):
        if not isinstance(coord, int):
            raise ValueError("Coordinates must be int.")
        elif not (0 <= coord <= 7):
            raise ValueError("Coordinates must be in between 0 to 7.")
    
    ### on/off 체크
    def check_onoff(self, onoff):
        if not isinstance(onoff, bool):
            raise ValueError("On/off value must be bool.")

    ### string 체크
    def check_string(self, string):
        if not isinstance(string, str):
            raise ValueError("String must be str.")
        elif not (1 <= len(string) <= 20):
            raise ValueError("String length must be in between 1 to 20.")
        for c in string:
            if ord(c) > 127:
                raise ValueError("String characters must be in ASCII.")

    ### scroll period 체크 & 처리
    def process_scroll_period(self, scroll, string_length):
        if not isinstance(scroll, (int, float)):
            raise ValueError("Scroll time value must be int or float.")
        elif scroll < 0:
            raise ValueError("Scroll time value must be positive.")
        scroll = round(scroll / (string_length / 8)) # 시간 체크
        if scroll > 200:
            scroll = 200
            print("Warning. Maximum value of (scroll_time / string_length * 8) is 200.")
        elif scroll == 0:
            scroll = 1
            print("Warning. Minimum value of (scroll_time / string_length * 8) is 1.")
        return scroll
        
    ### picture 체크 & 처리
    def process_picture(self, picture):
        if not isinstance(picture, (list, tuple)):
            raise ValueError("Picture must be list.")
        if len(picture) != 8:
            raise ValueError("Picture must be 8 by 8 list of list (matrix).")
        picture_list = [0]*8
        for j, pic_elem_list in enumerate(picture):
            if not isinstance(picture, (list, tuple)):
                raise ValueError("Picture must be 8 by 8 list of list (matrix).")
            elif len(pic_elem_list) != 8:
                raise ValueError("Picture must be 8 by 8 list of list (matrix).")
            picture_list_element = 0
            for i, pic_pixel in enumerate(pic_elem_list):
                if not (pic_pixel is 0 or pic_pixel is 1):
                    raise ValueError("Picture elements must be 0 or 1.")
                else:
                    picture_list_element += (2**i)*pic_pixel
            picture_list[(j+1)%8] = picture_list_element
        return picture_list

    @staticmethod
    def proc_group_id(self_group_id, group_id):
        if group_id == None:
            return self_group_id # None or int
        else:
            return group_id # Not None, int
            
            
    