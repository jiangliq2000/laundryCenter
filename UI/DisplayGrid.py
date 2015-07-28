#coding=utf-8

import wx
import wx.grid
import codecs 
import sys
import logfile
import wx.lib.ogl as ogl


row_Head = [u"累计数量", " "]
totalColLabels = [u"洗衣车数",u"洗涤液1\n(ml)",  u"洗涤液2\n(ml)",u"洗涤液3\n(ml)",\
                  u"洗涤液4\n(ml)",u"洗涤液5\n(ml)",u"洗涤液6\n(ml)",u"洗涤液7\n(ml)",u"洗涤液8\n(ml)"]
rowLabels = [u"洗衣机 #", "Washer #", "Washer #", "Washer #"]
colLabels = [u"洗衣\n机号", u"洗涤\n内容", u"开始加液\n时间", u"液体\n类型", u"洗涤液1\n(ml)", u"液体\n类型", u"洗涤液2\n(ml)",u"液体\n类型", u"洗涤液3\n(ml)",u"液体\n类型", \
                                                        u"洗涤液4\n(ml)",u"液体\n类型", u"洗涤液5\n(ml)",u"液体\n类型", u"洗涤液6\n(ml)",u"液体\n类型", \
                                                        u"洗涤液7\n(ml)",u"液体\n类型", u"洗涤液8\n(ml)"]
RecordNum = 100
washerNum = 4
colLen = len(colLabels)
recordLen = len(rowLabels)

### define wash_type
TPYE_OFFSET = 14

dict_washType = { 1:u"01白毛巾",2:u"02颜色毛巾",3:u"03白床单",4:u"04颜色床单",\
                  5:u"05白台布",6:u"06颜色台布",7:u"07厨衣",8:u"08浅制服",\
                  9:u"09深制服",10:u"10新草布",11:u"11毛巾回洗",12:u"12床单回洗",\
                  13:u"13台布回洗",14:u"14床罩回洗",15:u"15抹布",16:u"16自定义1",\
                  17:u"17自定义2",18:u"18自定义3",19:u"19自定义4",20:u"20自定义5"} 
dict_liqType = { 0:u"N/A",1:u"碱液", 2:u"助剂", 3:u"氧漂",4:u"氯漂", 5:u"柔软剂", 6:u"酸剂",7:u"水处理",8:u"乳化剂"}



class DisplayGrid(wx.grid.Grid):
    def __init__(self, parent):
        wx.grid.Grid.__init__(self, parent, -1)
        # define the line count
        self.lineCount = 2
        self.CreateGrid(2+recordLen*RecordNum, colLen)
        # set first and second row to head row
        
        # 2+record*recordLen+row : the real position for row in display page.
        #  2 -- mean head,  record - mean record num, 

        for rd in range(RecordNum):
            for row in range(recordLen):
                seq = "%d" % (row + 1)
                self.SetRowLabelValue(rd*recordLen + row, "%d" %(rd*4+row+1))
        for col in range(colLen):
            self.SetColLabelValue(col, colLabels[col])

        #set value to cell    
        """
        for row in range(rowLen):
            for col in range(colLen):
                if row >= 2:
                    self.SetCellValue(row, col, "0")
        """                
        self.EnableEditing(False)
        
    def ClearAll(self):
        for row in range(recordLen*RecordNum):
            for col in range(colLen):
                self.SetCellValue(row, col, "")
        
        
    def ReadDataFomFile(self, fname, gridTotal):
        """ read data from file"""
        logfile.info("--- now start to open file and load data to display ---")
        try:
            f = open(fname, 'r')
            logfile.info("--- open file %s is successful --- " % fname)
            
            row = 0
            sumCol = [ 0 for x in range(9)]
            
            #self.SetDefaultCellAlignment(wx.CENTRE,wx.CENTRE)
                 
            
            for eachLine in f :    
                ## stats line count
                self.lineCount = self.lineCount + 1
                valueLine = eachLine.split(",")
                sumCol[0] = sumCol[0] + 1
                sumCol[1] = sumCol[1] + int(valueLine[4])
                sumCol[2] = sumCol[2] + int(valueLine[6])
                sumCol[3] = sumCol[3] + int(valueLine[8])
                sumCol[4] = sumCol[4] + int(valueLine[10])
                sumCol[5] = sumCol[5] + int(valueLine[12])
                sumCol[6] = sumCol[6] + int(valueLine[14])
                sumCol[7] = sumCol[7] + int(valueLine[16])
                sumCol[8] = sumCol[8] + int(valueLine[18])
                
                
                
                for col in range(colLen):
                    #print "current front is ", self.GetCellFont(row, col)
                    # need special handle for wash type
                    if col == 0:
                        self.SetCellValue(row, col, "%d" % (int(valueLine[col])+1))
                    elif col == 1:
                        index = int(valueLine[col])
                        #print "index is %d \n" %index
                        self.SetCellValue(row, col, dict_washType[index] )
                    elif col==3 or col==5 or col==7 or col==9 or col==11 or col==13 or col==15 or col==17:
                        index = int(valueLine[col])
                        if index >8 or index <0:
                            return -1
                        self.SetCellValue(row, col, dict_liqType[index] )
                    else:
                        self.SetCellValue(row, col, valueLine[col])
                    self.SetCellTextColour(row, col,"brown")
                    #self.SetCellAlignment(row, col, wx.CENTRE,wx.CENTRE)
                row = row + 1
            # display sum    
            for i in range(len(sumCol)):
                font = wx.Font(10 ,wx.DECORATIVE, wx.NORMAL, wx.BOLD)
                gridTotal.SetCellValue(0, i, "%d" % sumCol[i])
                gridTotal.SetCellFont(0, i, font)
                gridTotal.SetCellTextColour(0, i, "blue")

            
            f.close()
            return 0
        except IOError:
                wx.MessageBox(u"打开文件 %s 失败." % fname, u"错误",style = wx.OK | wx.ICON_ERROR )
        
    def SaveDataToFile(self, fname):
        """ Save data to file"""
        try:
            fd = open(fname,"w")
        except IOError, e:          
            logfile.info(e)
            wx.MessageBox(u"保存失败，请先关闭该文件(%s)." % fname, u"错误!",style = wx.OK | wx.ICON_ERROR )
            return
        
        fd.write(codecs.BOM_UTF8)
        
        default_Encoding = sys.getdefaultencoding()
        reload(sys)  
        sys.setdefaultencoding('utf8')        
        fd.write(u",洗衣机号,洗涤内容,开始加液时间,洗涤液1(ml),洗涤液2(ml),洗涤液3(ml),洗涤液4(ml),洗涤液5(ml),洗涤液6(ml),洗涤液7(ml),洗涤液8(ml)\n")
        valueArry = [ u'' for x in range(colLen)]
        for i in range(self.lineCount):
            if i == 0:
                valueLine = u"累计量"
            elif i == 1:
                valueLine = u""
            else:
                valueLine = u"洗衣机号"
            for j in range(colLen):
                valueArry[j] = self.GetCellValue(i,j)
                valueLine = valueLine + u"," + valueArry[j]
            fd.write(valueLine + '\n')
        fd.close()
        wx.MessageBox(u"保存文件完成", u"成功!", style = wx.OK)
        reload(sys)  
        sys.setdefaultencoding(default_Encoding) 
        
        




class DisplayTotalGrid(wx.grid.Grid):
    def __init__(self, parent):
        wx.grid.Grid.__init__(self, parent, -1)
        # define the line count
        #self.lineCount = 2
        self.CreateGrid(1, len(totalColLabels))
        # set first and second row to head row
        #self.SetRowLabelValue(0, row_Head[0])
        ##self.SetRowSize(0, 60)
        self.SetRowLabelValue(0, row_Head[0])
        
        # 2+record*recordLen+row : the real position for row in display page.
        #  2 -- mean head,  record - mean record num, 

        for col in range(len(totalColLabels)):
            self.SetColLabelValue(col, totalColLabels[col])
            
        #set value to cell    
               
        self.EnableEditing(False)
        
    def ClearTotalAll(self):
        for col in range(len(totalColLabels)):
            self.SetCellValue(0, col, "")







rowLabels_pump = [u"流量", u"洗涤类型", u"首泵"]
colLabels_pump = [u"泵 1", u"泵 2", u"泵 3",u"泵 4",\
                  u"泵 5", u"泵 6", u"泵 7",u"泵 8",\
                  u"1号机",u"2号机",u"3号机",u"4号机" ]


class DisplayPump(wx.grid.Grid):
    def __init__(self, parent):
        wx.grid.Grid.__init__(self, parent, -1)
        self.CreateGrid(3, 12)
        for i in range(3):
            self.SetRowLabelValue(i, rowLabels_pump[i])
        for i in range(12):
            self.SetColLabelValue(i, colLabels_pump[i])
        
        self.EnableEditing(False)
        


class ConPanel(wx.Panel):
    def __init__(self, parent, id=-1, lText='output window', size=(300, 300)):
        wx.Panel.__init__(self, parent, id)
        
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        conTx = wx.StaticText(self,label=lText)
        self.conTc = wx.TextCtrl(self, style=wx.TE_MULTILINE) 
        hbox.Add(conTx,0,wx.EXPAND|wx.ALL,10)
        hbox.Add(self.conTc,2,wx.EXPAND|wx.ALL,10)
        self.SetSizer(hbox)
        
    def putLog(self, msg):
        self.conTc.AppendText(msg)

class NtsBoard(wx.Panel):
    def __init__(self, parent, id=-1, size=(400,300)):
        wx.Panel.__init__(self, parent, id)
        
        # 创建画布
        canvas = ogl.ShapeCanvas(self)
        canvas.SetBackgroundColour("yellow")
        
        # 创建图像
        diagram = ogl.Diagram()
        # marry the two ...
        canvas.SetDiagram(diagram)
        diagram.SetCanvas(canvas)
        
        # 创建圆
        # create some standard shapes ...
        # (check how creation order affects overlap)
        circle = ogl.CircleShape(100.0) # radius
        circle.SetX(75.0)  # center x
        circle.SetY(75.0)
        circle.SetPen(wx.RED_PEN)
        circle.SetBrush(wx.CYAN_BRUSH)
        # 将圆添加到画布
        canvas.AddShape(circle)
        # 创建文本
        text = ogl.TextShape(250, 30)  # (w, h)
        text.SetX(180)  # center x
        text.SetY(240)
        text.AddText("you can drag the circle or the text")
     
        # 将文本添加到画布
        canvas.AddShape(text)
        # 显示画布上的内容
        diagram.ShowAll(True)
        # 创建sizer
        # use v box sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        # 将画布添加到sizer
        # canvas will grow as frame is stretched
        sizer.Add(canvas, 1, wx.GROW)
        # 设置sizer
        self.SetSizer(sizer)
     

    def update(self):
        pass