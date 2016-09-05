import socket
from tornado.tcpserver import TCPServer    
from tornado.ioloop  import IOLoop
import tornado.web
import json

cha = 'A'
chb = 'b'
chc = 'c'
chw = 'w'

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
        global cha, chb, chc ,chw
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
            if('chw'==ss[0]):
                delay(1000)
                if('chc'==ss[0]):
                    self._stream.write(b'UNLK')
        except Exception as e:
            print('error',e)
        self.read_message()
    
    def on_close(self):    
        print ("left the system.", self._address )
    

# ---TCP socket handler
class TCP_Handler(TCPServer):    
    def handle_stream(self, stream, address):   
        print ("New connection :", address, stream)
        Connection(stream, address)

# ---pack---
#a ='cha'
#b ='chb'
#c ='chc'

def get_data():
    
    Jdata = json.dumps({'buf' : [cha,chb,chc]})
    return Jdata

# ---http handle
class Web_Handler(tornado.web.RequestHandler):
    def get(self):
        callback = self.get_argument('callback')
        #print(callback)
        #tp = self.get_argument('tp')
        #print(tp)
        webdata=get_data()
        self.write("{0}({1})".format(callback, webdata))
    
app = tornado.web.Application([(r"/", Web_Handler), ])

if __name__ == "__main__":
    
    server = TCP_Handler()    
    server.listen(8000)
    
    app.listen(8888)
    IOLoop.instance().start()
