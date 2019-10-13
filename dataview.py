import struct

class DataView:
    def __init__(self, array, bytes_per_element=1):
        if type(array) == bytes:
            self.array = array
        self.array = bytes(array)
        self.length = len(array) 

    def get_uint_32(self, idx):
        bytes_to_read = 4
        return int.from_bytes(self.array[idx:idx+bytes_to_read], byteorder='big')

    def get_uint_16(self, idx):
        bytes_to_read = 2
        return int.from_bytes(self.array[idx:idx+bytes_to_read], byteorder='big')

    def get_uint_8(self, idx):
        bytes_to_read = 1
        return int.from_bytes(self.array[idx:idx+bytes_to_read], byteorder='big')

    def get_int_32(self, idx):
        bytes_to_read = 4
        return int.from_bytes(self.array[idx:idx+bytes_to_read], byteorder='big', signed=True)

    def get_int_16(self, idx):
        bytes_to_read = 2
        return int.from_bytes(self.array[idx:idx+bytes_to_read], byteorder='big', signed=True)

    def get_int_8(self, idx):
        bytes_to_read = 1
        return int.from_bytes(self.array[idx:idx+bytes_to_read], byteorder='big', signed=True)
    
    def get_float_32(self, idx):
        bytes_to_read = 4
        binary = self.array[idx:idx+bytes_to_read]
        return struct.unpack('>f', binary)[0]
    
    def __set_data(self, idx, data):
        size = len(data)
        _data = bytearray(self.array)
        for i in range(size):
            _data[idx + i] = data[i]
        self.array = bytes(_data)
            
    def set_int_8(self, idx, data):
        self.__set_data(idx, struct.pack(">b", data))

    def set_uint_8(self, idx, data):
        self.__set_data(idx, struct.pack(">B", data))

    def set_int_16(self, idx, data):
        self.__set_data(idx, struct.pack(">h", data))

    def set_uint_16(self, idx, data):
        self.__set_data(idx, struct.pack(">H", data))
    
    def set_int_32(self, idx, data):
        self.__set_data(idx, struct.pack(">i", data))

    def set_uint_32(self, idx, data):
        self.__set_data(idx, struct.pack(">I", data))
    
    def write_string(self, idx, data):
        self.set_uint_8(idx, len(data))
        for i, char in enumerate(data):
            char_code = ord(char)
            self.set_uint_8(idx + 1 + 2 * i + 1, 255 & char_code)
            self.set_uint_8(idx + 1 + 2 * i + 1, 255 & char_code)