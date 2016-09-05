import socket
from tornado.tcpserver import TCPServer    
from tornado.ioloop  import IOLoop
import tornado.web
import tornado.websocket 
import json
import time

alert = 0
trigger =0
trigger_b = 0

# --- Car Position
class position:
    pass

ps = position()

ps.initial = 0
ps.recent = 0
ps.dest = 0

#--- Position mapping
def pos_map_number(argument):
    switcher = {
        'A': 1,
        'a': 2,
        'B': 3,
        'b': 4,
        'C': 5,
        'c': 6,
    }
    return switcher.get(argument, "nothing")



myIP = socket.gethostbyname(socket.gethostname())
print ('Backend Server: {}:8888'.format(myIP))

# --- TCP Connection
"""0: 直走
1: 右轉
2: 停
3: 啟動"""
# ------------------------
clients_TCP = []
class Connection(object):
    def __init__(self, stream, address):
        clients_TCP.append(self)
        #clients_T = clients_TCP
        print(clients_TCP)
        self._stream = stream    
        self._address = address

        self._stream.set_close_callback(self.on_close)
        self.read_message()

    def read_message(self):
        self._stream.read_bytes(1024,self.broadcast_messages,partial=True)

    def broadcast_messages(self, data):
        global alert, trigger, trigger_b
        startime = 0
        timepass = 0
        #try:
        data = data.decode().strip()

        print("recieved:"+data)

        if data is 'd':
            alert = 1
            print("alert="+str(alert))
            #self._stream.write(data)

        if ((data is 'a') or 
        (data is 'b') or (data is 'c') or 
        (data is 'A') or (data is 'B') or (data is 'C')):
            print("recieved data: "+data)
            num = pos_map_number(data)
            print('num'+str(num))
            if ps.dest is 0:
                pass
            else:
                echo = judge(num)
                print("line 68, echo="+str(echo))
                echo=str(echo)
                self._stream.write(echo.encode('utf-8'))
                startime = time.perf_counter()
                trigger_b = 1                            #trigger_b在web client端沒有按下destination之前為0, 按下去之後為1

        if trigger_b is 1:
            end = time.perf_counter()
            if startime is 0:
                pass
            else:
                timepass = end - startime
            if timepass >= 1.0:
                self._stream.write(b'y')
            else:
                if data is 'y':
                    print('trigger b is now 0')
                    trigger_b = 0                        #抵達終點之後, trigger_b設為0
                            
        self.read_message()

    def on_close(self):
        print ("A user has left the chat room.",self._address)

# --- judge direction
def judge(rec):
    global ps
    ps.recent = rec
    print('ps.recent:'+str(ps.recent)+'ps.dest:'+str(ps.dest))
    x = ps.dest-ps.recent
    print('x='+str(x))

    if (x is 1) or (x is-5):
        return 1
    elif x is 0:
        ps.initial = ps.recent
        return 2
    else:
        return 0


# --- TCP handler
class TCP_Handler(TCPServer):
    def handle_stream(self, stream, address):
        print("New connection : ", address, stream )
        Connection(stream, address)

# --- pack ---------------------

def get_data(p):
    data = json.dumps({'buf': p})
    return data

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        global alert, ps, trigger
        callback = self.get_argument('callback')
        #print(callback)
        #self.write("Hello "+tp)
        da = self.get_argument('data')
        print(da)
        #self.write("{0}".format(ps))
        if (da is 'A') or (da is'B') or (da is 'C'):
            ps.dest = pos_map_number(da)                    #決定終點
            print('html ps.dest:'+str(ps.dest))
            print("hello: "+callback)
            data = get_data(da)
            print("I am data1: "+data)
            self.write("{0}({1})".format(callback, data))                                                    
            trigger = 1
#--------------
class ResponseH(tornado.web.RequestHandler):
    def open(self):
        print ('new connection')            
        
#----- websocket handler
clients = []

class WSHandler(tornado.websocket.WebSocketHandler):    
    def open(self):
        global clients
        print ('new connection')
        clients.append(self)
        print(clients)
        #self.on_message()
        #self.on_message()
    def on_message(self, message):
        self.write_message(u"You said: " + message)
 
    def on_close(self):
        print ('connection closed')
 
    def check_origin(self, origin):
        return True

## check the queue for pending messages, and rely that to all connected clients
def checkQueue():
    global alert, clients, trigger, clients_TCP
    if alert is 1:
        print('alert:')
        print(clients)
        for c in clients:
            c.write_message('e')
            #print(clients)
            alert = 0
            print("sending alert")

    if trigger is 1:
        print('trigger:')
        print(clients_TCP)
        for ct in clients_TCP:
            echo='3'
            ct._stream.write(echo.encode('utf-8'))
            trigger = 0

#------Http handler
    
app = tornado.web.Application([(r"/", MainHandler), (r'/echo', WSHandler),])

if __name__ == "__main__":
# ---- TCP ------------------
    server = TCP_Handler()
    server.listen(8000)
    app.listen(8888)

# ---- websocket------------
    mainLoop = IOLoop.instance()
    scheduler_interval = 1000
    scheduler = tornado.ioloop.PeriodicCallback(checkQueue, scheduler_interval, io_loop = mainLoop)
    scheduler.start()
    mainLoop.start()
