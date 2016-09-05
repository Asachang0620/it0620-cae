import socket
from tornado.tcpserver import TCPServer    
from tornado.ioloop  import IOLoop
import tornado.web
import json

cha = 'A'
chb = 'b'
chc = 'c'
# --- My IP address
myIP = socket.gethostbyname(socket.gethostname())
print('Backend Server: {}:8888'.format(myIP))
# ---Tcp connection
class Connection(object):
    def __init__(self, stream, address):
        self._stream = stream
        self._address = address
        
        self._stream.set_close_callback(self.on_close)
        # self._stream.write(b'hello')
        self.read_message()
        
    def read_message(self):
        self._stream.read_bytes(1024, self.broadcast_messages, partial=True)
        
    def broadcast_messages(self, data):
        global cha, chb, chc
        try:
            data = data.decode().strip()
            #print(cha, end='\t')
            ss = data.split(',')
            if('CHA' == ss[0]):
                print(ss)
                cha = data
            if('CHB' == ss[0]):
                print(ss)
                chb = data
            if('CHC' == ss[0]):
                print(ss)
                chc = data
        except:
            print('error')
        self.read_message()
    
    def on_close(self):    
        print ("left the system.", self._address )
    

# ---TCP socket handler
class TCP_Handler(TCPServer):    
    def handle_stream(self, stream, address):   
        print ("New connection :", address, stream)
        Connection(stream, address)

# ---pack---
b,c =22,33
a ='CHA'
def get_data():
    #global a,b,c
    Jdata = json.dumps({'buf' : [cha,chb]})
    return Jdata

# ---http handle
class Web_Handler(tornado.web.RequestHandler):
    def get(self):
        callback = self.get_argument('callback')
        #print(callback)
        tp = self.get_argument('tp')
        #print(tp)
        Tdata=get_data()
        self.write("{0}({1})".format(callback, Tdata))
    
app = tornado.web.Application([(r"/", Web_Handler), ])

if __name__ == "__main__":
    
    server = TCP_Handler()    
    server.listen(8000)
    
    app.listen(8888)
    IOLoop.instance().start()
