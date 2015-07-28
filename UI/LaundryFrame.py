#coding=utf-8

#----------------------------------------------------------------------
# A very simple wxPython example.  Just a wx.Frame, wx.Panel,
# wx.StaticText, wx.Button, and a wx.BoxSizer, but it shows the basic
# structure of any wxPython application.
#----------------------------------------------------------------------

import os
import re
import wx
import time
import StatusBar
import DisplayGrid, ConfigOne, IO, NetworkThread, logfile



class LaundryFrame(wx.Frame):
    """
    This is LaundryFrame.
    """
    
    def __init__(
            self, parent, ID, title, pos=(150,80),
            size=wx.DefaultSize, style=wx.DEFAULT_FRAME_STYLE
            ):
    
        wx.Frame.__init__(self, parent, ID, title, pos, wx.Size(1500,800), style)
        
        # Create the menubar
        menuBar = wx.MenuBar()
        # define a dataStr, to store file date
        self.dateStr = u""
        # and a menu 
        menu_file = wx.Menu()
        menu_config = wx.Menu()
        menu_merge = wx.Menu()
        #menu_Console = wx.Menu()
        menu_Stats = wx.Menu()
        #menu_config3 = wx.Menu()

        # add an item to the menu, using \tKeyName automatically
        # creates an accelerator, the third param is some help text
        # that will show up in the statusbar
        menu_file.Append(201, u"导入", u"导入文件")
        menu_file.Append(202, u"另存为", u"另存为")
        menu_file.Append(wx.ID_EXIT, u"退出", u"退出程序")
        
        menu_config.Append(101, u"20套程序配置", u"配置数据1")
        menu_config.Append(102, u"配置2", u"配置数据2")
        menu_config.Append(103, u"配置3", u"配置数据3")
        
        menu_merge.Append(301, u"合并原始数据", u"合并原始数据")
        
        #menu_Console.Append(401, u"打开串口", u"打开串口")
        menu_Stats.Append(501, u"统计", u"统计")
        #menu_Network.Append(502, u"断开网络连接", u"断开网络连接")
        # bind the menu event to an event handler
        self.Bind(wx.EVT_MENU, self.OnTimeToClose, id=wx.ID_EXIT)
        self.Bind(wx.EVT_MENU, self.OnOpenFile, id=201)
        self.Bind(wx.EVT_MENU, self.OnSaveAs, id=202)
        self.Bind(wx.EVT_MENU, self.OnMerge, id=301)
        #self.Bind(wx.EVT_MENU, self.OnConsole, id=401)
        self.Bind(wx.EVT_MENU, self.OnStats, id=501)
        #self.Bind(wx.EVT_MENU, self.OnStopNetwork, id=502)
        # bind the menu events to handlers
        self.Bind(wx.EVT_MENU, self.MenuConf101, id=101)
        self.Bind(wx.EVT_MENU, self.MenuConf102, id=102)
        self.Bind(wx.EVT_MENU, self.MenuConf103, id=103)
       

        # and put the menu on the menubar
        menuBar.Append(menu_file, u"&文件")
        menuBar.Append(menu_merge, u"&合并")
        menuBar.Append(menu_config, u"&配置")
        #menuBar.Append(menu_Console, u"&串口(Console)")
        menuBar.Append(menu_Stats, u"&统计")
        
        self.SetMenuBar(menuBar)
       
        
        self.ToggleMergeMenu()
        menubar = self.GetMenuBar()
        enable = menubar.IsEnabled(102)
        menubar.Enable(102, not enable)

        menubar = self.GetMenuBar()
        enable = menubar.IsEnabled(103)
        menubar.Enable(103, not enable)

        #menubar = self.GetMenuBar()
        #enable = menubar.IsEnabled(501)
        #menubar.Enable(501, not enable)
        

        # added status bar
        self.sb = StatusBar.CustomStatusBar(self)
        self.SetStatusBar(self.sb)
         
         
         
        # create a timer
        self.timer1 = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnTimer1Event, self.timer1)
        # timer = 10seconds
        self.timer1.Start(10000) 
                

        # Now create the Panel to put the other controls on.
        self.panel = wx.Panel(self)

        mainSizer = wx.BoxSizer(wx.VERTICAL)      
        
     
          

        # First create the controls
        topLbl = wx.StaticText(self.panel, -1, u"洗衣房加液历史数据溯源分析", pos=(20,20))
        topLbl.SetFont(wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD))

        # start to static text 
        txtSizer = wx.BoxSizer(wx.HORIZONTAL)
        txtSizer.Add((30,40), 1)
        txtSizer.Add(topLbl)
        txtSizer.Add((30,40), 1)
        mainSizer.Add(txtSizer, 1, wx.EXPAND|wx.BOTTOM, 5)
        # end to static text       
        
        
        # start to grid display
        self.gridTotal = DisplayGrid.DisplayTotalGrid(self.panel)
        self.gridTotal.AutoSizeColumns(True)
        mainSizer.Add(self.gridTotal, 10, wx.EXPAND|wx.TOP|wx.BOTTOM, 5)
        
        
        self.grid = DisplayGrid.DisplayGrid(self.panel)
        #self.grid.AutoSizeColumns(True)
        #mainSizer.Add(self.grid, 10, wx.EXPAND|wx.TOP|wx.BOTTOM, 5)
        mainSizer.Add(self.grid, 10, wx.BOTTOM, 5)
        mainSizer.SetItemMinSize(self.grid, (1600,400))
        # end grid display
        
            
        # start to network part
        vbox1 = wx.BoxSizer(wx.VERTICAL)
        NetLbl = wx.StaticText(self.panel, -1, u"网络连接状态显示", pos=(20,20))
        NetLbl.SetFont(wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD))
        vbox1.Add(NetLbl,2,wx.ALIGN_CENTER|wx.CENTER,10)
        
        ##  added connection status display, four  StaticText
        #### when receive heart beat, will update isConnectDict
        self.isConnectDict = {}
        self.ntsDict={}
        ntsSizer = wx.BoxSizer(wx.HORIZONTAL)
        ntsSizer.Add((2,2),1)
        for i in range(4):            
            ntsText = wx.StaticText(self.panel, -1, u"  无设备连接  ", pos=(80*(i+1),40),style=wx.ALIGN_CENTER)
            ntsText.SetBackgroundColour("gray")
            ntsText.SetForegroundColour("brown")
            ntsText.SetFont(wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD))
            self.ntsDict[ntsText] = None
            ntsSizer.Add(ntsText)
            ntsSizer.Add((100,40),4)
         
        vbox1.Add(ntsSizer,1,wx.ALIGN_CENTER,10)
        self.conPan = DisplayGrid.ConPanel(self.panel, lText=("output window"))
        self.conPan.SetBackgroundColour('#4f5049')
        #self.conPan.Fit()
        vbox1.Add(self.conPan,20,wx.ALL,4)
        vbox1.SetItemMinSize(self.conPan, (920,10))
        mainSizer.Add(vbox1, 1, wx.BOTTOM, 5)
        #mainSizer.Add(ntsSizer, 5, wx.BOTTOM, 5)
        #  end netwrok part
        

        
        #FinallySizer = wx.BoxSizer(wx.HORIZONTAL)
        #FinallySizer.Add(mainSizer, 15, wx.EXPAND|wx.TOP|wx.BOTTOM, 5)
        #FinallySizer.Add(vbox1, 10, wx.EXPAND|wx.TOP|wx.BOTTOM, 10)
        #self.panel.SetSizer(FinallySizer)
        
        self.panel.SetSizer(mainSizer)
        self.dirRec = self.CreateRecFileDir()
        self.startListen()
    
    def CreateRecFileDir(self):
        # get current time
        #curTimeStr = time.strftime("%Y-%m-%d")
        #logfile.info("current date is %s" % curTimeStr)
        #print "current time is %s" % curTimeStr
                
        dirStr = os.getcwd() + '\\NetData'   
        print "dirStr is %s" % dirStr
        ret = os.path.exists(dirStr)
        if ret == False:
            ret1 = os.mkdir(dirStr)
            if ret1 == False:
                logfile.info("--- create NetData directory is failed ! please attenation!! ---")
            else:
                logfile.info("--- create NetData file directory ---")
        else:
            logfile.info("--- NetData Dir exit ---")
        
        return dirStr          

        
    def startListen(self):
        logfile.info("--- start to listen... ---")
        logfile.info("--- dirRev is %s... ---" % self.dirRec)
        self.ltThread = NetworkThread.ListenThread(self)
        self.ltThread.setDaemon(True)
        self.ltThread.start()
        

    def OnTimeToClose(self, evt):
        """Event handler for the button click."""
        logfile.info("--- close this program , see ya later! ---")
        self.Close()

    def OnOpenFile(self, evt):
        """Event handler for the button click."""
        logfile.info("--- open a dat file to display ---")
        
        # This is how you pre-establish a file filter so that the dialog
        # only shows the extension(s) you want it to.
        wildcard = "display data (*.rtp)|*.rtp|" \
                   "All files (*.*)|*.*"        
        
        
        # Create the dialog. In this case the current directory is forced as the starting
        # directory for the dialog, and no default file name is forced. 
        # Finally, if the directory is changed in the process of getting files, this
        # dialog is set up to change the current working directory to the path chosen.
        dlg = wx.FileDialog(
            self, message="Choose a file",
            defaultDir=os.getcwd(), 
            defaultFile="",
            wildcard=wildcard,
            style=wx.OPEN | wx.CHANGE_DIR
            )

        # Show the dialog and retrieve the user response. If it is the OK response, 
        # process the data.
        if dlg.ShowModal() == wx.ID_OK:
            # This returns a Python list of files that were selected.
            # here, first need clear all data on the grid.
            self.grid.ClearAll()
            self.gridTotal.ClearTotalAll()
            path = dlg.GetPath()
            fnameList = re.split(r'\\', path)
            fName = fnameList[len(fnameList)-1]
            fDate = fName.split('.')[0]
            print "fDate is ", fDate
            # need judge filename
            #if len(fDate)!=8 or re.findall(r'\D',fDate):
            # remove the len != 8, because new file name format is  yearMonDay-deviceId.rtp
            #if re.findall(r'\d{8}-\d+',fDate):  
            #changed 2015.01.26, to supoort xxxxxxxx.rtp and xxxxxxxx-xxx.rtp
            if re.findall(r'\d{8}',fDate):
                logfile.info("--- file name format is correct .... ---")                
            else:
                wx.MessageBox(u"文件选择有误，请重新选择（文件名格式：XXXXXXXX-XXX.rtp, X 为年月日数字），您选的文件名：%s" % fName, u"错误", style = wx.OK)
                return            
            rdNum = IO.Dis_ReadFile(path, "newtmpfile")
            # judge if file record is correct
            if rdNum == -1:
                wx.MessageBox(u"错误：文件格式已经被破坏，请重新选择正确文件", u"错误", style = wx.OK)
                return
            elif rdNum > 100:
                wx.MessageBox(u"注意：由于文件记录数大于100帧，只显示前100帧", u"提示", style = wx.OK)
                return
            ## merge orignal file to create a new file
            #IO.Dis_MergeFile("newtmpfile", "mergefile")
            
            # met issue when read record 
            if (self.grid.ReadDataFomFile("newtmpfile", self.gridTotal) == -1):
                wx.MessageBox(u"液体类型索引错误。该文件格式可能已经被破坏，原有显示也被清零，请重新选择文件打开。" , u"错误",style = wx.OK )
                self.grid.ClearAll()
                self.gridTotal.ClearTotalAll()
                return
            
            self.dateStr = u"日期：%s年%s月%s日" % (fDate[:4], fDate[4:6], fDate[6:8]) 
            ## get the deviceId
            if len(fDate)!=8:
                deviceId = re.split(r'-', fDate)[1]
            else:
                deviceId = "NULL"
            dvIDStr = u"分配器设备号: " + deviceId
            self.dateLbl = wx.StaticText(self.panel, -1, self.dateStr+ u" 原始加料数据  \n" + dvIDStr,pos =(10,10),size=(250,35),style=wx.TE_READONLY | wx.TE_PROCESS_TAB )
            self.dateLbl.SetFont(wx.Font(11, wx.SWISS, wx.NORMAL, wx.BOLD))
            
            # refresh grid
            self.grid.AutoSizeColumns(True)


        # Compare this with the debug above; did we change working dirs?
        print "CWD: %s\n" % os.getcwd()

        # Destroy the dialog. Don't do this until you are done with it!
        # BAD things can happen otherwise!
        dlg.Destroy()
        
        # enable "merge menu"
        self.ToggleMergeMenu()
        
        
        
        
    def OnSaveAs(self, evt):
        """ save a dat file to new file"""
        if self.grid.lineCount <= 2 or self.grid.lineCount > (2+DisplayGrid.recordLen*DisplayGrid.RecordNum):
            wx.MessageBox(u"空文件不能存储，请先打开rpt文件", u"错误",style = wx.OK | wx.ICON_ERROR )
            return        
        # This is how you pre-establish a file filter so that the dialog
        # only shows the extension(s) you want it to.
        wildcard = "display data (*.csv)|*.csv|" \
                   "All files (*.*)|*.*"        

                
        # Create the dialog. In this case the current directory is forced as the starting
        # directory for the dialog, and no default file name is forced. This can easilly
        # be changed in your program. This is an 'save' dialog.
        #
        # Unlike the 'open dialog' example found elsewhere, this example does NOT
        # force the current working directory to change if the user chooses a different
        # directory than the one initially set.
        dlg = wx.FileDialog(
            self, message="Save file as ...", defaultDir=os.getcwd(), 
            defaultFile="", wildcard=wildcard, style=wx.SAVE
            )

        # This sets the default filter that the user will initially see. Otherwise,
        # the first filter in the list will be used by default.
        dlg.SetFilterIndex(2)

        # Show the dialog and retrieve the user response. If it is the OK response, 
        # process the data.
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            print "You selected %s files:" % path
            self.grid.SaveDataToFile(path)
            #self.grid.AutoSize()

            # Normally, at this point you would save your data using the file and path
            # data that the user provided to you, but since we didn't actually start
            # with any data to work with, that would be difficult.
            # 
            # The code to do so would be similar to this, assuming 'data' contains
            # the data you want to save:
            #
            # fp = file(path, 'w') # Create file anew
            # fp.write(data)
            # fp.close()
            #
            # You might want to add some error checking :-)
            #

        # Destroy the dialog. Don't do this until you are done with it!
        # BAD things can happen otherwise!
        dlg.Destroy()
        
    def OnConfigDat(self, evt):
        """ creat a new window for configing dat"""
        print "creat a new window for configing dat"
        self.win = ConfigOne.Cfg1Frame(self, -1, u"配置界面", size=(350, 230), style = wx.DEFAULT_FRAME_STYLE)
        print " construct ConfigOne"
        self.win.Show(True)
         
        

    def OnStats(self, evt):
        """ creat a new window for stats dat"""
        print "creat a new window for configing dat"
        self.win = ConfigOne.StatsFrame(self, -1, u"统计界面", pos=(500, 400), size=(616, 250), style = wx.DEFAULT_FRAME_STYLE)
        #print " construct ConfigOne"
        self.win.Show(True)
         
        

    
    def MenuConf101(self, event):
        print "creat a new window for configing dat 111"
        print "event is " , event
        menubar = self.GetMenuBar()
        enable = menubar.IsEnabled(101)
        menubar.Enable(101, not enable)
        #self.win = ConfigOne.Cfg1Frame(self, -1, u"配置界面", size=(760, 310), style = wx.DEFAULT_FRAME_STYLE )
        self.win = ConfigOne.Cfg1Frame(self, -1, u"配置界面", pos=(300, 240), size=(760, 310), style = wx.DEFAULT_FRAME_STYLE | wx.FRAME_FLOAT_ON_PARENT )
        self.win.Show(True)

        
       
    def MenuConf102(self, event):
        print "creat a new 2 window for configing dat"
        menubar = self.GetMenuBar()
        enable = menubar.IsEnabled(102)
        menubar.Enable(102, not enable)
        

        
    def MenuConf103(self, event):
        print "creat a new 3 window for configing dat"   
        menubar = self.GetMenuBar()
        enable = menubar.IsEnabled(103)
        menubar.Enable(103, not enable)
        
        
    def OnMerge(self, event):
        """ merge orignal file and display new file"""
        IO.NewDis_MergeFile("newtmpfile", "mergefile")
        self.grid.ClearAll()
        self.gridTotal.ClearTotalAll()
        # met issue when read record 
        if (self.grid.ReadDataFomFile("mergefile",self.gridTotal) == -1):
            wx.MessageBox(u"合并失败。该文件格式可能已经被破坏，原有显示也被清零，请重新选择文件打开。" , u"错误：合并失败",style = wx.OK )
            self.grid.ClearAll()
            self.gridTotal.ClearTotalAll()
            self.ToggleMergeMenu()
            return
        #dateStr = u"日期：%s年%s月%s日" % (fDate[:4], fDate[4:6], fDate[6:8])
        self.dateLbl.SetLabel(self.dateStr + u" 合并后加料数据")
        #print "displayStr is ", displayStr
        #self.dateLbl = wx.StaticText(self.panel, -1, dateStr,pos =(10,10),size=(150,35),style=wx.TE_READONLY | wx.TE_PROCESS_TAB )
        #self.dateLbl.SetFont(wx.Font(12, wx.SWISS, wx.NORMAL, wx.BOLD))
        
        self.grid.AutoSizeColumns(True)
        self.ToggleMergeMenu()
        
    def ToggleMergeMenu(self):
        menubar = self.GetMenuBar()
        enable = menubar.IsEnabled(301)
        menubar.Enable(301, not enable)
        
        
    ## --------------------------------------------------------------------------------------    
        #    ntsDict  construct
        #    { "key": {"IpPort":[deviceId, flag, requestSocket]}}
        #    key:  staticText handle
        #    IpPort:  client IP+PORT
        #    flag: 0 -- disconnection ,  1 -- connection
        #    requestSocket :   socket which listening server generate for client      
    ## -------------------------------------------------------------------------------------
               
    def OnTimer1Event(self, evt):
        # check if tcp conncetion still is active.
        
        for key in self.ntsDict:
            if self.ntsDict[key] is not None:
                #print "ntsdict is " , self.ntsDict[key]
                for ipt in self.ntsDict[key]:
                    if(self.ntsDict[key][ipt][1] == 0):
                        ### it mean don't recieve heart beat within 10 seconds, the connection isn't normal, display to disconnection
                        ## ntsDict[key][ipt][2] is a socket,                        
                        self.ntsDict[key] = None
                        #key.SetLabel(u"无连接\n"+"IP is NULL")
                        #key.SetBackgroundColour("gray")
                        #key.SetForegroundColour("brown")
                        #key.SetFont(wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD))                        
                        self.SetLabel(key,0, None)                        
                        self.printlogToConPan("---" + ipt + u"心跳已丢失，连接已断开\n")
                        
                    else:
                        ### set flag to 0
                        self.ntsDict[key][ipt][1] = 0
                    
        
    def SetLabel(self, key, flag, text):
        # falg 0 -- set disconnection,  1 -- set connection
        if flag == 0:
            key.SetLabel(u"  无设备连接  ")
            key.SetBackgroundColour("gray")
            key.SetForegroundColour("brown")
            key.SetFont(wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD))
        elif flag == 1:
            if type(text) == type(1):
                TextLabel = (u"设备:%d 已连接" % text)
                key.SetFont(wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD))
            elif type(text) == type('1'):
                TextLabel = u"设备已连接\n" + text 
                key.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD))
            else:
                return
            key.SetLabel(TextLabel)
            key.SetBackgroundColour("green")
            key.SetForegroundColour("brown")
            #key.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
        else:
            pass
            
        
    def printlogToConPan(self,msg):
        curtime = time.strftime("%Y-%m-%d-%H:%M:%S")
        MSG = curtime + ":  " + msg        
        self.conPan.putLog(MSG)
    
    

        
    def SetNtsConnect(self,*IpDevid):
        IpPort = IpDevid[0]
        devId = IpDevid[1]
        for key in self.ntsDict:
            if self.ntsDict[key] is None:
                #key.SetLabel(TextLabel)
                #key.SetBackgroundColour("green")
                #key.SetForegroundColour("brown")
                #key.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD))
                if devId is None:
                    self.SetLabel(key, 1, IpPort)
                else:
                    self.SetLabel(key, 1, devId)
                self.ntsDict[key] = {IpPort:1}
                #### for List, first element is devId,  
                #### second mean heart beat flag, 1 -- heart beat is OK, 0 -- heart beat is broken
                #### third mean if print log ,  0 --- print,  1-- don't print
                self.ntsDict[key][IpPort]=[devId, 1]
                break
        #print self.ntsDict
            
    def UpdateNtsConnect(self,*IpDevid):
        IpPort=IpDevid[0]
        devId = IpDevid[1]
        #print "updatent devId is ", devId
        for key in self.ntsDict:
            if (self.ntsDict[key] is not None) and (self.ntsDict[key].has_key(IpPort)):
                #self.ntsDict[key][IpPort] = [devId, 1]
                self.ntsDict[key][IpPort][0] = devId
                self.ntsDict[key][IpPort][1] = 1
                #self.ntsDict[key][IpPort][2] = cSocket
                self.SetLabel(key, 1, devId)
                return
                
        self.SetNtsConnect(IpPort, devId)
        self.printlogToConPan("---" + IpPort + u"心跳恢复，连接可用\n")
            
    
    def SetNtsDiscon(self, *IpDevid):
        IpPort=IpDevid[0]
        devId = IpDevid[1]      
        for key in self.ntsDict:
            if self.ntsDict[key] is not None:
                if self.ntsDict[key].has_key(IpPort):
                    self.ntsDict[key] = None
                    #key.SetLabel(u"无设备连接")
                    #key.SetBackgroundColour("gray")
                    #key.SetForegroundColour("brown")
                    #key.SetFont(wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD))
                    self.SetLabel(key, 0, None)
                    break
        ##  when hearbeat is lost, close this socket
