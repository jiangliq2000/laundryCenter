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



def printLog(msg):
    ## judge where console data is from?
    curtime = time.strftime("%Y-%m-%d-%H:%M:%S")
    MSG = curtime + ":  " + msg
    bufferList.putLog(MSG)
        
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
    return 0
        


def SetNtsConnect(IpPort):
    for key in bufferDict:
        if bufferDict[key] is None:
            key.SetLabel(u"收到连接：\n"+IpPort)
            key.SetBackgroundColour("green")
            key.SetForegroundColour("brown")
            key.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD))
            bufferDict[key] = {IpPort:1}
            break
        

def SetNtsDiscon(IpPort):
    for key in bufferDict:
        if bufferDict[key] is not None:
            if bufferDict[key].has_key(IpPort):
                bufferDict[key] = None
                key.SetLabel(u"无连接\n"+"IP is NULL")
                key.SetBackgroundColour("gray")
                key.SetForegroundColour("brown")
                key.SetFont(wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD))
                break
                             


class TCPStreamHandlerr(StreamRequestHandler):

    def handle(self):
        socketPool.append(self.request)
        #print "socket is " , self.request
        cur_thread = threading.currentThread()
        threadPool.append(cur_thread)
        # get network data direcotry
        #pathName = GetNetDataDir()
        # open current day data file, name should be year+month+day.rtp
        # get current day
        #curTimeStr = time.strftime("%Y%m%d")
        #dataFname = time.strftime("%Y%m%d") + ".rtp"
        #logfile.info("--- data file path is %s ---" % (pathName+"\\" + dataFname))
        
        # update the network connection status
        SetNtsConnect(str(self.client_address))
        
        #fdata = open(pathName+"\\"+dataFname, "ab+")
        logfile.info("--- connected from ", self.client_address )
        connectMsg = u"--- 收到(" + str(self.client_address)+ u")连接\n"
        printLog(connectMsg)
        conNum = -1
        while True:
            try:
                
                ## for debug
                #data = self.rfile.read(1)
                #logfile.info("--- receive from (%r):%r ---" % (self.client_address, data))
                #continue                
                ##end of debug
                               
                
                Rawdata = self.rfile.read(68)
                if Rawdata == None or len(Rawdata) == 0:
                    logfile.info("--- no data receive from (%r):%r ---" % (self.client_address, Rawdata))
                    break;  
                
                ### if this frame is destory, need calc 
                fh1,  = struct.unpack("B", Rawdata[0])
                fh2,  = struct.unpack("B", Rawdata[1])
                #print "fh1 is ", fh1
                #print "fh2 is ", fh2
                
                
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
                                            
                
                #print "thread name is %s" % self.getName()
                # write log to textCtrl
                deviceId, = struct.unpack("B", data[2:3])                
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
                                
                ### output log to text control to display
                # 1. if this deviceId is record in deviceIdDic
                #if deviceIdDict.has_key(deviceId):
                #   conNum = deviceIdDict[deviceId]
                #else:
                    # don't exit this deviceId, added it to dict and correlative to one output window
                    ## get current console window List
                    #conNumList = deviceIdDict.values()
                    #for i in range (4):
                        #if conNumList.count(i) == 0:
                           # store the relation for devcieId and console window
                           #deviceIdDict[deviceId] = i
                           #conNum = i
                           #break
                #if conNum == -1:
                    #logfile.info("--- this deviceId cannot relative to any of console window, please check, will close this TCP connection ---")

                printLog(u"分配器编号: %d, 接收到一次加料数据 \n" %deviceId)    
                
                # write record to network data file
                #self.wfile.write("hello\n")
                #logfile.info("--- finish to send data ---")

                #self.wfile.write(data.upper())
                
            except:
                traceback.print_exc()
                break
        
        SetNtsDiscon(str(self.client_address)) 
        disconnectMsg = u"--- 连接断开： " + str(self.client_address) + "\n"
        
        
        
        printLog(disconnectMsg)
        
        logfile.info("--- now connection is lost. ---")
        
        threadPool.remove(cur_thread)
        




class Server(ThreadingMixIn, TCPServer):  pass
    #def __init__(self, msg):



class ListenThread(threading.Thread):
    def __init__(self, window, ntsDict, dirRev):
        threading.Thread.__init__(self)
        self.window = window
        self.timeToQuit = threading.Event()
        self.timeToQuit.clear()
        # bufferDict used to store  StaticText handler
        global bufferList, bufferDict
        bufferList = window
        bufferDict = ntsDict
        global dirRevFile
        dirRevFile = dirRev
        logfile.info("--- dirrevfile directory is %s  ---" % dirRevFile)
        
    def run(self):

        ## get local ip
        ipList = socket.gethostbyname_ex(socket.gethostname())
        for i in ipList:
            logfile.info("--- all ips are %s ---" % i)
        iplocal = socket.gethostbyname(socket.gethostname())
        logfile.info("--- iplocal is %s --- " % iplocal)        
        
        host = iplocal
        #host = '192.168.0.10'
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



