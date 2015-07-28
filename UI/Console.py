#coding=utf-8

import  sys,threading,time;
import  serial


class ReadThread:
    def __init__(self, Output=None, Port=0, Log=None, i_FirstMethod=True):
        self._serial = None;
        self.alive = False;
        self.waitEnd = None;
        self.bFirstMethod = i_FirstMethod;
        self.sendport = '';
        self.output = Output;
        self.port = Port;
        
        
def waiting(self):
    if not self.waitEnd is None:
        self.waitEnd.wait()
        
        
def SetStopEvent(self):
    if not self.waitEnd is None:
        self.alive = False;
        self.stop();
        
def start(self):
    self.l_serial = serial.Serial() ;
    self.l_serial.port = self.port;
    self.l_serial.baudrate = 9600;
    self.l_serial.timeout = 2;
    
    try:
        if not self.output is None:
            print "open serial port";
        self.l_serial.open();
    except Exception, ex:
        if self.l_serial.isOpen():
            self.l_serial.close();
            self.l_serial = None;
            print "open serail is failed" ;
        return False;
    
    if not self.l_serial.isOpen():
        print "create a thread to receive date"
        self.waitEnd = threading.Event();
        self.alive = True;
        self.thread_read = None;
        self.thread_read = threading.Thread(target=self.FirstReader);
        self.thread_read.setDaemon(1);
        self.thread_read.start();
        return True;
    else:
        print "didn't open serial port";
        return False;
    

def FirstReader(self):
    data1 = '';
    isEnd = True;
    readCount = 0;
    saveCount =0;
    
    self.InitHead();
    
    while self.alive:
        try:
            data = '';
            n = self.l_serial.inWaiting();
            if n:
                data = data + self.l_serial.read(n);
                
        