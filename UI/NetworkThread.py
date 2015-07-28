#coding=utf-8
import wx
import os, time, threading
import struct
import socket
#from SocketServer import ThreadingTCPServer, StreamRequestHandler
from SocketServer import TCPServer, ThreadingMixIn, StreamRequestHandler  
import traceback
import inspect
import ctypes
import logfile 


## define 4 buffer
global threadPool
threadPool = []
global socketPool
socketPool = []
deviceIdDict = {}

#global connectionDict 
connectionDict = {}


def _async_raise(tid, exctype):
    """raises the exception, performs cleanup if needed"""
    if not inspect.isclass(exctype):
        exctype = type(exctype)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        # """if it returns a number greater than one, you're in trouble, 
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")

def stop_thread(thread):
    _async_raise(thread.ident, SystemExit)


 
def GetNetDataDir():

    #logfile.info("current date is %s" % curTimeStr)
    
    PathName = os.getcwd() + '\\NetData'  
    logfile.info("--- GeNet DataDir --- :  pathname is  %s" %PathName)
    ret = os.path.exists(PathName)
    if ret == False:
        logfile.info("--- NetData Directory don't exit, will create it ---")
        os.mkdir(PathName)
    else:
        logfile.info("--- NetData directory alway exit ---")
    return PathName
    
def IsExistDataFile(devIdStr):
    ''' input:  deviceId
        return:  if exist,  return file Name
                if not exist, return -1
    '''
    # get network data direcotry
    #pathName = GetNetDataDir()
    #dataFname = GetNetDataDir() + "\\" + time.strftime("%Y%m%d") +"-" + devIdStr + ".rtp"
    dataFname = dirRevFile + "\\" + time.strftime("%Y%m%d") +"-" + devIdStr + ".rtp"
    if os.path.isfile(dataFname):
        return dataFname
    else:
        return -1  


def ScanData(rd):
    '''input : raw data
       return: file head position
    '''
    for i in range (len(rd)-1):
        t1, = struct.unpack("B", rd[i])
        t2, = struct.unpack("B", rd[i+1])
        if (t1==0x5A) and (t2==0xA5):
            return i    
        if (t1==0x48) and (t2==0x54):
            logfile.info("--- heartbeat bad frame ---")
            return i
    return 0
        


def printLog(msg):
    wx.CallAfter(mainFrame.printlogToConPan,msg)
    #bufferList.putLog(MSG)
       


def SetNtsConnect(IpPort, dID):
    wx.CallAfter(mainFrame.SetNtsConnect, IpPort, dID)


def UpdateNtsConnect(IpPort, dID):
    wx.CallAfter(mainFrame.UpdateNtsConnect,IpPort, dID)


def SetNtsDiscon(IpPort, dID):
    wx.CallAfter(mainFrame.SetNtsDiscon, IpPort, dID)
                             

def UpdateHTFlag(IpPort, dID):
    print "device id is %d" % dID
    wx.CallAfter(mainFrame.UpdateNtsConnect, IpPort, dID)


class TCPStreamHandlerr(StreamRequestHandler):
    #def setup(self):
    #    self.connection = self.request
    #    self.connection.settimeout(60)
    #    if self.disable_nagle_algorithm:
    #        self.connection.setsockopt(socket.IPPROTO_TCP,
    #                                   socket.TCP_NODELAY, True)
    #    self.rfile = self.connection.makefile('rb', self.rbufsize)
    #    self.wfile = self.connection.makefile('wb', self.wbufsize)
    #
    #def finish(self):
    #    print " called finish"
    #    self.request.close()
    #  
    def handle(self):
        #socketPool.append(self.request)
        #print "socket is " , self.request
        #cur_thread = threading.currentThread()
        #threadPool.append(cur_thread)
        
        # get network data direcotry
        #pathName = GetNetDataDir()
        # open current day data file, name should be year+month+day.rtp
        # get current day
        #curTimeStr = time.strftime("%Y%m%d")
        #dataFname = time.strftime("%Y%m%d") + ".rtp"
        #logfile.info("--- data file path is %s ---" % (pathName+"\\" + dataFname))
        
        # update the network connection status
        SetNtsConnect(str(self.client_address), None)
        
        #fdata = open(pathName+"\\"+dataFname, "ab+")
        logfile.info("--- connected from ", self.client_address )
        connectMsg = u"--- 收到(" + str(self.client_address)+ u")连接\n"
        printLog(connectMsg)
       
        while True:
            try:
                Rawdata = self.rfile.read(68)
                if Rawdata == None or len(Rawdata) == 0:
                    logfile.info("--- no data receive from (%r):%r ---" % (self.client_address, Rawdata))
                    break;  
    
                ### if this frame is destory, need calc 
                fh1,  = struct.unpack("B", Rawdata[0])
                fh2,  = struct.unpack("B", Rawdata[1])
                ### for heart beat message, the fh3 is deviceid
                fh3,  = struct.unpack("B", Rawdata[2])
                
                ### if it is heart beat, set flag and skip it
                if (fh1 == 0x48) and (fh2 == 0x54):                    
                    UpdateHTFlag(str(self.client_address), fh3)
                    #print "receive ht, fh3 is %d\n" % fh3
                    continue
                
                ### handle the valid data
                if (fh1 != 0x5A)  or (fh2 != 0xA5):
                    # scan this data and check the head position
                    logfile.info("--- this frame is destory, need detect file head position ---")
                    fdPos = ScanData(Rawdata)
                    if fdPos == 0:
                        logfile.info("--- can not find file head in this frame, discard it ---")
                        continue
                    else:
                        logfile.info("--- start to read second part to construct a new frame, secondPos is %d ---" % fdPos)
                        #print "fdpos is ", fdPos
                        SecondData = self.rfile.read(fdPos)
                        data=Rawdata[fdPos:] + SecondData                
                else:
                    logfile.info("--- this frame is OK, start to process it ---")
                    data = Rawdata
                                            
                ### after reconstruct frame, we need judge if it is heartbeat frame.
                fh1,  = struct.unpack("B", data[0])
                fh2,  = struct.unpack("B", data[1])
                ### for heart beat message, the fh3 is deviceid
                fh3,  = struct.unpack("B", data[2])
                
                ### if it is heart beat, set flag and skip it
                if (fh1 == 0x48) and (fh2 == 0x54):                    
                    UpdateHTFlag(str(self.client_address), fh3)
                    #print "receive ht, fh3 is %d\n" % fh3
                    continue                     
                
                
                # write log to textCtrl
                deviceId, = struct.unpack("B", data[2:3])                
                UpdateNtsConnect(str(self.client_address), deviceId)
                logfile.info("--- receive from (%r)-deviceId:%d,  %r ---" % (self.client_address, deviceId, data))
                                
                ret = IsExistDataFile(("%s" % deviceId))
                
                if ret == -1:
                    # file don't exist, create filename 
                    dataFileName = dirRevFile + "\\" + time.strftime("%Y%m%d") +"-" + ("%s" % deviceId) + ".rtp"
                else:
                    # file exit, open it
                    dataFileName =  ret                
                fdata = open(dataFileName, "ab+")
                fdata.write(data[:-2])
                fdata.close()
                                

                printLog(u"分配器编号: %d, 接收到一次加料数据 \n" %deviceId)  
                               
            except:
                traceback.print_exc()
                break
        
        SetNtsDiscon(str(self.client_address), None) 
        disconnectMsg = u"--- 连接断开： " + str(self.client_address) + "\n"        
        
        
        printLog(disconnectMsg)
        
        logfile.info("--- now connection is lost. ---")




class Server(ThreadingMixIn, TCPServer):  pass
    #def __init__(self, msg):



class ListenThread(threading.Thread):
    def __init__(self, selfUIFrame):
        threading.Thread.__init__(self)
        global bufferList, bufferDict,dirRevFile,mainFrame
        mainFrame = selfUIFrame
        self.window = mainFrame.conPan
        self.timeToQuit = threading.Event()
        self.timeToQuit.clear()
        # bufferDict used to store  StaticText handler
        
        bufferDict = mainFrame.ntsDict
        bufferList = self.window
        dirRevFile = mainFrame.dirRec
        logfile.info("--- dir revfile directory is %s  ---" % dirRevFile)
        
    def run(self):

        ## get local ip
        ipList = socket.gethostbyname_ex(socket.gethostname())
        for i in ipList:
            logfile.info("--- all ips are %s ---" % i)
        iplocal = socket.gethostbyname(socket.gethostname())
        logfile.info("--- iplocal is %s --- " % iplocal)        
        
        host = iplocal
        #host = '192.168.0.7'
        port = 9999
        addr = (host, port)
        #tcpStHandler = TCPStreamHandlerr(self.window[0])
        try:
            self.server = Server(addr, TCPStreamHandlerr)
            logfile.info("--- start to run network serering ---")
            curtime = time.strftime("%Y-%m-%d-%H:%M:%S")
            self.window.putLog(curtime+":"+u"本机ip("+ host + u")等待客户机连接..\n")
            self.server.serve_forever()
        except:
            logfile.info("--- bind 192.168.0.10 failed ---")
            curtime = time.strftime("%Y-%m-%d-%H:%M:%S")
            self.window.putLog(curtime+":"+u" 本地ip地址绑定失败，请检查网络连接，然后重启本程序\n")
        
           

        
    
    def writeLog(self):
        print " write network output"
        
    def stop(self):
        # exit connection thread
        for i in range (len(threadPool)):            
            threadTmp = threadPool[i]
            threadPool.remove(threadTmp)
            stop_thread(threadTmp)        
        #exit main thread
        #stop_thread(self)
        self.server.server_close()
        self.timeToQuit.set()
        stop_thread(self)
        #self.server.shutdown() 

        





if __name__ == "__main__":
    host = ""       #主机名，可以是ip,像localhost的主机名,或""
    port = 9999     #端口
    addr = (host, port)
    
    #ThreadingTCPServer从ThreadingMixIn和TCPServer继承
    #class ThreadingTCPServer(ThreadingMixIn, TCPServer): pass
    server = Server(addr, TCPStreamHandlerr)
    server.serve_forever()




