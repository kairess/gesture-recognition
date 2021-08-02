class Utils():
    # hex into spaced & upper string
    @staticmethod
    def bytes_to_hex_str(bytesinput) -> str:
        # insert between string
        def insert_str(string, str_to_insert, index):
            return string[:index] + str_to_insert + string[index:]
        # make into string
        stroutput = bytesinput.hex()
        for i in range(int(len(str(bytesinput.hex()))/2-1)):
            stroutput = insert_str(stroutput, " ", 3*i+2)
        stroutput = stroutput.upper()
        return stroutput

    # 실수 체크
    @staticmethod
    def float_check(number, option=None) -> None:
        if not isinstance(number, (int, float)):
            is_float = False
        else:
            is_float = True
        if not is_float:
            if option:
                raise ValueError("Please enter float number, or \"" + str(option) + "\"!")
            else:
                raise ValueError("Please enter float number!")

    #  정수 체크
    @staticmethod
    def integer_check(number, option=None) -> None:
        if not isinstance(number, int):
            is_integer = False
        else:
            is_integer = True
        if not is_integer:
            if option:
                raise ValueError("Please enter integer number, or \"" + str(option) + "\"!")
            else:
                raise ValueError("Please enter integer number!")

    # 2바이트 헥스 리스트를 integer로 변환
    @staticmethod
    def twobyte_hexlist_to_int(byte1, byte2) -> int:
        return int(hex(byte1)[2:] + hex(byte2)[2:], 16)
    
    # 리스트로 변환
    @staticmethod
    def to_list(input_data) -> list:
        if isinstance(input_data, (list, tuple)):
            return list(input_data)
        elif isinstance(input_data, (int, float, str, bool)) or input_data == None:
            return [input_data]
        else:
            raise ValueError("Error. Enter list, or tuple, or int, or float, or str, or bool, or None.")

    # 같은 원소가 있는지 확인
    @staticmethod
    def check_same_element(input_list) -> None:
        for i in range(len(input_list)-1):
            if input_list[i] in input_list[i+1:]:
                raise ValueError("All elements must be different each other in list.")

    # 모든 cube id가 있는지 확인
    @staticmethod
    def all_cube_in_check(input_list, connection_number) -> bool:
        check = True
        for i in range(connection_number):
            check = (i in input_list) and check
        return check

    ### 리스트 포인터(id)를 다르게 복사
    @staticmethod
    def list_product_copy(input_list, number) -> list:
        input_list = input_list[0]
        out_list = []
        i = 0
        while i < number:
            new_list = [0]*len(input_list)
            for j in range(len(input_list)):
                new_list[j] = input_list[j]
            out_list.append(new_list)
            i += 1
        return out_list

    ### 그룹 id 확인
    @staticmethod
    def check_group_id(group_id: int or str or None):
        if type(group_id) == int:
            pass
        elif type(group_id) == str:
            group_id = int(group_id)
        elif group_id == None:
            return None
        else:
            raise ValueError("group_id must be int or str or None.")
        not_id = (11, 22, 33, 44, 55, 66)
        if not 0 < group_id < 77:
            raise ValueError("group_id must be in between 0 to 77. (1 <= group_id <= 76)")
        elif group_id in not_id:
            raise ValueError("group_id must not be 11, 22, 33, 44, 55, or 66.")
        else:
            return group_id

    ### bytedata에서 값 얻기 (자이로 값)
    def getSignedIntfromByteData(self, data: int) -> int:
        if data >= 128:
            data -= 256
        return data
    
    ### 가속도 값 얻기
    def getACCDataToDegreeMinus90To90fromByteData(self, data: int) -> int:
        data = self.getSignedIntfromByteData(data)
        if data > 90:
            data = 90
        elif data < -90:
            data = -90
        return data
        

    
