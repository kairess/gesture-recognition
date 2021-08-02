class ByteUtils():
    # unsigned16 으로 변환
    def unsigned16(self, n) -> int:
        return n & 0xFFFF # "bitwise &(and)" 연산자

    # integer를 n 바이트 헥스 리스트로 변환
    def int_to_hexlist(self, number, n_bytes) -> list:
        hex_number = hex(number)[2:] # str
        if len(hex_number)%(2*n_bytes) != 0:
            hex_number = "0"*(2*n_bytes-len(hex_number)%(2*n_bytes)) + hex_number 
        if len(hex_number) > 2*n_bytes:
            raise ValueError("n_bytes is smaller than integer to hex.")
        hex_list = [int(hex_number[-2:], 16)]
        for i in range(1, n_bytes):
            hex_list =  [int(hex_number[-2*(i+1):-2*i], 16)] + hex_list
        return hex_list

    #  정수 체크
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