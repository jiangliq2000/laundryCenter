#coding=utf-8

import  os, re
import  wx
import wx.grid
import IO
import DisplayGrid


ColNum_Cfg1Display = 8
RowNum_Cfg1Display = 8
NumProgram = 20
size_panelDisplay = (830, 310)
"""
     

colTitle = ["Wash1_delay","Wash1_Vol","Wash2_delay","Wash2_Vol", \
            "Wash3_delay","Wash3_Vol","Wash4_delay","Wash4_Vol"]
            
rowTitle = ["PUMP #1", "PUMP #2","PUMP #3","PUMP #4", \
            "PUMP #5", "PUMP #6","PUMP #7","PUMP #8"]


"""

rowTitle = [u"1号泵", u"2号泵",u"3号泵",u"4号泵", \
            u"5号泵", u"6号泵",u"7号泵",u"8号泵"]


colTitle = [u"1号机—延时",u"1号机—剂量",u"2号机—延时",u"2号机—剂量", \
            u"3号机—延时",u"3号机—剂量",u"4号机—延时",u"4号机—剂量"]
       


dict_ProgType = { 0:u"01白毛巾",1:u"02颜色毛巾",2:u"03白床单",3:u"04颜色床单",\
                  4:u"05白台布",5:u"06颜色台布",6:u"07厨衣",7:u"08浅制服",\
                  8:u"09深制服",9:u"10新草布",10:u"11毛巾回洗",11:u"12床单回洗",\
                  12:u"13台布回洗",13:u"14床罩回洗",14:u"15抹布",15:u"16自定义1",\
                  16:u"17自定义2",17:u"18自定义3",18:u"19自定义4",19:u"20自定义5"} 



DataOnePage = [[0 for x in range(ColNum_Cfg1Display)]for y in range(RowNum_Cfg1Display)]


class Cfg1Frame(wx.Frame):
    def __init__(
            self, parent, ID, title, pos=wx.DefaultPosition,
            size=wx.DefaultSize, style=wx.DEFAULT_FRAME_STYLE
            ):
        wx.Frame.__init__(self, parent, ID, title, pos, size, style)
        self.panel = wx.Panel(self, -1)
                
        self.noteBook = wx.Notebook(self.panel)  
        self.programList = range(NumProgram)
        for i in range (NumProgram):
            self.programList[i] = Program1(self.noteBook)
            self.noteBook.AddPage(self.programList[i], dict_ProgType[i])
          
         
        
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.mainSizer.Add(self.noteBook, 20, wx.EXPAND|wx.TOP|wx.BOTTOM, 5)

        btn_Open = wx.Button(self.panel, -1, u"导入数据")
        btn_Save = wx.Button(self.panel, -1, u"导出数据")
        btn_Clear = wx.Button(self.panel, -1, u"清除当前页")
        btn_Clear_All = wx.Button(self.panel, -1, u"清除所有页")
        
        btnSizer = wx.BoxSizer(wx.HORIZONTAL)
        btnSizer.Add((20,20), 1)
        btnSizer.Add(btn_Open)
        btnSizer.Add(btn_Clear)
        btnSizer.Add(btn_Clear_All)
        #btnSizer.Add((20,20), 1)
        btnSizer.Add(btn_Save)
        btnSizer.Add((20,20), 1)
        
        self.mainSizer.Add(btnSizer, 4, wx.EXPAND|wx.BOTTOM, 5)        
        
        self.panel.SetSizer(self.mainSizer)

        # bind the button events to handlers
        self.Bind(wx.EVT_BUTTON, self.OnOpenFile, btn_Open)
        self.Bind(wx.EVT_BUTTON, self.OnSaveAs, btn_Save)
        self.Bind(wx.EVT_BUTTON, self.OnClear, btn_Clear)
        self.Bind(wx.EVT_BUTTON, self.OnClearAll, btn_Clear_All)
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
        
        """
        button = wx.Button(panel, 1003, "Close Me")
        button.SetPosition((15, 15))
        self.Bind(wx.EVT_BUTTON, self.OnCloseMe, button)
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
        """
        
    def OnOpenFile(self, evt):
        """Event handler for the button click.
        size = self.mainSizer.GetSize()
        print "size is " , size 
        """
        wildcard = "display data (*.cfg)|*.cfg|" 

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
            path = dlg.GetPath()
            self.UpdateNoteBook(path)
        

        
        # Destroy the dialog. Don't do this until you are done with it!
        # BAD things can happen otherwise!
        dlg.Destroy()
        #self.UpdateNoteBook(path)
    
    def OnSaveAs(self, evt):
        """Event handler for the button click."""
        wildcard = "display data (*.cfg)|*.cfg|"    
        dlg = wx.FileDialog(self, message="Save file as ...", defaultDir=os.getcwd(), 
                    defaultFile="", wildcard=wildcard, style=wx.SAVE)
        
        dlg.SetFilterIndex(2)
        
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.WriteToFile(path)
        dlg.Destroy()
        
    
    def OnClear(self, evt):
        """clear one page data to 0"""
        # add a dialog to confirm if real clear all message
        mess = wx.MessageBox("Are you sure to clear this page data", style = wx.YES_NO | wx.ICON_EXCLAMATION)
        if mess == wx.YES:
            DataOnePage = [[0 for x in range(ColNum_Cfg1Display)]for y in range(RowNum_Cfg1Display)]
            curSel = self.noteBook.GetSelection()
            self.programList[curSel].Update(DataOnePage)
                #self.programList[i].ForceRefresh()
            
    def OnClearAll(self, evt):
        """clear all data to 0"""
        mess = wx.MessageBox("Are you sure to clear all data", style = wx.YES_NO | wx.ICON_EXCLAMATION)
        if mess == wx.YES:
            DataOnePage = [[0 for x in range(ColNum_Cfg1Display)]for y in range(RowNum_Cfg1Display)]
            for i in range(NumProgram):
                self.programList[i].Update(DataOnePage)
            
    

    def OnCloseMe(self, event):
        self.Close(True)
        

    def OnCloseWindow(self, event):
        mess = wx.MessageBox("Are you sure to exit this configuration page ", style = wx.YES_NO | wx.ICON_EXCLAMATION)
        if mess == wx.YES:
            ParentFrame = wx.FindWindowByName(u"洗衣房液体分配器数据分析与配置")
            menubar = ParentFrame.GetMenuBar()
            menubar.Enable(101, True)
            self.Destroy()
    
    def UpdateNoteBook(self, filename):
        IO.ReadFile(filename)
        IO.ChangeToASCIIFile("ascciitmp.dat")
        fd = open("ascciitmp.dat", "r")
        for i in range(NumProgram):
            for j in range(RowNum_Cfg1Display):
                #fd.readline(i*RowNum_Cfg1Display)
                eachLine = fd.readline()
                valueLine = eachLine.split(",")
                DataOnePage[j] = [int(valueLine[0]),int(valueLine[1]),int(valueLine[2]),int(valueLine[3]), \
                                                   int(valueLine[4]),int(valueLine[5]),int(valueLine[6]),int(valueLine[7])]
            
            
            self.programList[i].Update(DataOnePage)
            
        fd.close()
        
            
    def WriteToFile(self, filename):
        fd = open("ascciitmp.dat", "w")
        for i in range(NumProgram):            
            self.programList[i].GetValue(DataOnePage)
            for x in range(RowNum_Cfg1Display):
                    valueLine = "%d,%d,%d,%d,%d,%d,%d,%d,\n" % (DataOnePage[x][0],DataOnePage[x][1],DataOnePage[x][2],\
                                                               DataOnePage[x][3],DataOnePage[x][4],DataOnePage[x][5],\
                                                               DataOnePage[x][6],DataOnePage[x][7])
                    print "valueLine is ", valueLine
                    fd.write(valueLine)
                    
        fd.close()        
        
        IO.ChangeToBin("ascciitmp.dat")
        IO.WriteFile(filename)

  
class Program1(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        #t = wx.StaticText(self, -1, "This is a PageOne object", (20,20))
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.grid = wx.grid.Grid(self)
        # print default size for row, col
        #print "default col width is : " , self.grid.GetDefaultColSize()
        #print "default row width is : " , self.grid.GetDefaultRowSize()
        #self.grid.SetDefaultRowSize(40)
        #self.grid.SetDefaultColSize(100)
        self.grid.CreateGrid(RowNum_Cfg1Display,ColNum_Cfg1Display)
        for i in range(ColNum_Cfg1Display):
            self.grid.SetColLabelValue(i, colTitle[i])
        for i in range(RowNum_Cfg1Display):
            self.grid.SetRowLabelValue(i, rowTitle[i])
        
        
        #btn_Save_as = wx.Button(self, -1, "Save as")
        #mainSizer.Add(btn_Save_as, 4, wx.EXPAND|wx.TOP|wx.BOTTOM, 5)
        mainSizer.Add(self.grid, 1, wx.EXPAND|wx.TOP|wx.BOTTOM, 5)
        self.SetSizer(mainSizer)
        
    def Update(self, data):
        for i in range(RowNum_Cfg1Display):
            for j in range(ColNum_Cfg1Display):
                self.grid.SetCellValue(i, j, "%d" % data[i][j])
    
    def GetValue(self, data):
        """ get value from grid"""
        for i in range(RowNum_Cfg1Display):
            for j in range(ColNum_Cfg1Display):
                data[i][j] = int(self.grid.GetCellValue(i, j).encode())
        
        
class StatsFrame(wx.Frame):
    def __init__(self, parent, ID, title, pos=wx.DefaultPosition,
            size=wx.DefaultSize, style=wx.DEFAULT_FRAME_STYLE
            ):
        wx.Frame.__init__(self, parent, ID, title, pos, size, style)
        self.path = os.path.abspath('.')
        print "default path i s", self.path
        self.panel = wx.Panel(self, -1)
        
        #font = wx.Font(18, wx.DECORATIVE, wx.ITALIC, wx.NORMAL)
        
        self.dateLbl = wx.StaticText(self.panel, -1, u"     年     月",pos =(1000,600),size=(250,10),style=wx.TE_READONLY | wx.TE_PROCESS_TAB ) 
        self.dateLbl.SetFont(wx.Font(12, wx.SWISS, wx.NORMAL, wx.BOLD))
        btn_path = wx.Button(self.panel, -1, u"指定路径")
        self.tx_path = wx.StaticText(self.panel,-1, self.path,style=wx.ALIGN_CENTER)
        
        pathSizer = wx.BoxSizer(wx.HORIZONTAL)
        pathSizer.Add(btn_path,0)
        pathSizer.Add(self.tx_path,0)
        
        tx_label = wx.StaticText(self.panel,-1,u"指定日期: ")
        #tx_label.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.tx_date = wx.TextCtrl(self.panel, -1, "201507",size=(60,-1),style=wx.TE_LEFT)
        self.tx_date.SetInsertionPoint(0)
        btn_exec = wx.Button(self.panel, -1, u"执行")
        
        dateSizer = wx.BoxSizer(wx.HORIZONTAL)
        dateSizer.Add(tx_label,1)
        dateSizer.Add(self.tx_date,1)
        dateSizer.Add((20,20), 5)
        dateSizer.Add(btn_exec,1)
        dateSizer.Add((20,20), 1)
        
        
        self.gridTotal = DisplayGrid.DisplayTotalGrid(self.panel)
        self.gridTotal.AutoSizeColumns(True)

        
        
        
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        
        self.mainSizer.Add(pathSizer, 10, wx.EXPAND|wx.TOP|wx.BOTTOM, 3)
        self.mainSizer.Add(dateSizer, 10, wx.EXPAND|wx.TOP|wx.BOTTOM, 3)
        self.mainSizer.Add(wx.StaticLine(self.panel), 0, wx.EXPAND|wx.TOP|wx.BOTTOM, 3)
        self.mainSizer.Add(self.dateLbl, 10, wx.EXPAND|wx.TOP|wx.BOTTOM, 3)       
        self.mainSizer.Add(self.gridTotal, 30, wx.EXPAND|wx.TOP|wx.BOTTOM, 8)

   

        #
        #btn_Clear = wx.Button(self.panel, -1, u"清除当前页")
        #btn_Clear_All = wx.Button(self.panel, -1, u"清除所有页")
        
        
        
        #btnSizer.Add(tx_label)
        #btnSizer.Add((20,20), 1) 
        #btnSizer.Add(self.tx_date)
        #btnSizer.Add((20,20), 1)
        #btnSizer.Add(btn_Open)
        #btnSizer.Add(self.tx_path)
        #btnSizer.Add((20,20), 1)
        #btnSizer.Add(btn_Save)
        
        
        #self.mainSizer.Add(btnSizer, 4, wx.EXPAND|wx.BOTTOM, 5)        
        
        self.panel.SetSizer(self.mainSizer)

        # bind the button events to handlers
        self.Bind(wx.EVT_BUTTON, self.OnOpenFile, btn_path)
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
        self.Bind(wx.EVT_BUTTON, self.OnExect, btn_exec)
        
        """
        button = wx.Button(panel, 1003, "Close Me")
        button.SetPosition((15, 15))
        self.Bind(wx.EVT_BUTTON, self.OnCloseMe, button)
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
        """
        
        
    def OnOpenFile(self, evt):
        """Event handler for the button click.
        size = self.mainSizer.GetSize()
        print "size is " , size 
        """
        dlg = wx.DirDialog(None, "choose a directory:", style=wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON)
         
        # Show the dialog and retrieve the user response. If it is the OK response, 
        # process the data.
        if dlg.ShowModal() == wx.ID_OK:
            # This returns a Python list of files that were selected.
            self.path = dlg.GetPath()
            self.tx_path.SetLabel(self.path)
            
        

        
        # Destroy the dialog. Don't do this until you are done with it!
        # BAD things can happen otherwise!
        dlg.Destroy()
        #self.UpdateNoteBook(path)

    def OnCloseMe(self, event):
        self.Close(True)
    
    def OnExect(self, evt):
        #print "now it is start to exect"
        #print "date is ", self.tx_date.GetValue()
        #print "path is %s" % self.path
        self.gridTotal.ClearTotalAll()
        self.UpdateTotalGrid(self.path, self.tx_date.GetValue())
        year = (self.tx_date.GetValue())[:4]
        month = (self.tx_date.GetValue())[4:6]
        self.dateLbl.SetLabel(u"%s 年 %s 月" %(year, month))
        
    
    def UpdateTotalGrid(self, path, ymonth):
        errFName = []
        corupFname = []
        # liqsum[0] mean machine num
        liqSum = [0,0,0,0,0,0,0,0,0]
        # 1. get all file name, 
        flist = os.listdir(path)
        # filter match file name  
        numCorrectFile = 0      
        for fname in flist:
            ## 2. handle to every single file, if it is non-support file, skip it
            if (re.findall(r'\d{8}.*',fname) == []) or (re.findall(r"\.[rR][tT][pP]+\Z", fname) == []) or (ymonth != fname[:6]):
                errFName.append(fname)
                continue                
            
            Afname = path + '/' + fname
            # if file is destory, skip it
            if IO.Dis_ReadFile(Afname, "newtmpfile") == -1:
                corupFname.append(fname)
                continue
            #print "after IO"    
            with open("newtmpfile",'r') as f:
                for line in f:
                    llist = line.split(",")
                    
                    liqSum[1]= liqSum[1] + int(llist[4])
                    liqSum[2]= liqSum[2] + int(llist[6])
                    liqSum[3]= liqSum[3] + int(llist[8])
                    liqSum[4]= liqSum[4] + int(llist[10])
                    liqSum[5]= liqSum[5] + int(llist[13])
                    liqSum[6]= liqSum[6] + int(llist[15])
                    liqSum[7]= liqSum[7] + int(llist[16])
                    liqSum[8]= liqSum[8] + int(llist[18])
            #print "now finish to handle rtp file"
            numCorrectFile += 1
        # 3. update grid  display sum    
        for i in range(1,len(liqSum)):
            font = wx.Font(10 ,wx.DECORATIVE, wx.NORMAL, wx.BOLD)
            if numCorrectFile >0:
                self.gridTotal.SetCellValue(0, i, "%d" % liqSum[i])
                self.gridTotal.SetCellFont(0, i, font)
                self.gridTotal.SetCellTextColour(0, i, "blue")
            else:
                wx.MessageBox(u"该目录下没有符合统计规则的文件(XXXXXXXX.RTP),请重新选择", u"错误", style = wx.OK)
                return
        if (corupFname != []):
            for corr in corupFname:
                corrstr = corrstr + corr + ","
            corrstr = corrstr + "\n"
            wx.MessageBox(u"请注意以下文件由于毁坏将被忽略，统计信息可能不准确：%s" % (corrstr), u"错误", style = wx.OK)
        
        


    def OnCloseWindow(self, event):
        mess = wx.MessageBox("Are you sure to exit this stats page ", style = wx.YES_NO | wx.ICON_EXCLAMATION)
        if mess == wx.YES:
            ParentFrame = wx.FindWindowByName(u"洗衣房液体分配器数据分析与配置")
            menubar = ParentFrame.GetMenuBar()
            menubar.Enable(101, True)
            self.Destroy()
    
