import math

#TODO: create the decode

class Encoder :

    def __init__(self, data):
        self._data = data

    def _encode(self):                          #return encoded data
        return self.encode_data(self._data)
    
    def _encode_data(self,data):       
        if (type(data) == int):                 #encode int
            return self._encode_int(data)
        
        elif (type(data)==str):                 #encode str
            return self._encode_str(data)
        
        elif type(data) == bytes:               #encode bytes
            return self._encode_bytes(data)

        elif type(data) == dict:                #encode dictionary
            return self._encode_dict(data)  
        elif type(data) == list:
            return self._encode_list(data)      #encode list
        else:
            return None


        
        def _encode_int(self, val: int):
               return str.encode('i' + str(data) + 'e')

        def _encode_str(self, val: str):
            return str.encode( str(len(data)) + ':' + data)

        def _encode_bytes(self, val: str):
            myarr = bytearray()
            myarr+= str.encode(str(len(data)))
            myarr+=b':'
            myarr+=data
            return myarr
        
        def _encode_dict(self, data: dict):
            myarr = bytearray('d', 'utf-8')
            for key, val in data.items():
                mykey = self.encode_data(key)
                myval = self.encode_data(val)
            
                myarr+=mykey
                myarr+=myval
            myarr+=b'e'
            return myarr
        
        def _encode_list(self, data: list) :
            myarr = bytearray('l', 'utf-8')
            myarr+= b''.join([self.encode_data(element) for element in data])
            myarr +=b'e'
            return myarr

            
                
    