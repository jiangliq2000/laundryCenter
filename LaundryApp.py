#coding=utf-8

#----------------------------------------------------------------------
# A very simple wxPython example.  Just a wx.Frame, wx.Panel,
# wx.StaticText, wx.Button, and a wx.BoxSizer, but it shows the basic
# structure of any wxPython application.
#----------------------------------------------------------------------

import os, sys, time, re
import wx
import psutil
import traceback
from UI import logfile, LaundryFrame

home = os.path.dirname(os.path.abspath(sys.argv[0]))




def Check_exist():
    appNum = 0
    for p in psutil.process_iter():
        pinfo = p.as_dict(attrs=['pid', 'name'])
        print pinfo['name']
        if pinfo['name'] == 'LaundryApp.exe':            
            appNum += 1
    if appNum >= 2:
        logfile.info("---- detect app is running, pid=" + str(pinfo['pid']) + " exit ---- ")
        app = wx.App()
        wx.MessageBox(u"该程序已经运行，请退出再重新启动" , u"警告", style = wx.OK)
        return -1
    return 0

    


class LaundryApp(wx.App):
    def OnInit(self):        
        self.frame = LaundryFrame.LaundryFrame(None, -1,u"洗衣房液体分配器数据分析与配置")
        self.SetTopWindow(self.frame)
        self.frame.Maximize(True)
        self.frame.Show(True)
        #self.frame.ShowFullScreen(True, wx.FULLSCREEN_NOBORDER | wx.FULLSCREEN_NOCAPTION | wx.FULLSCREEN_NOMENUBAR | wx.FULLSCREEN_NOSTATUSBAR | wx.FULLSCREEN_NOTOOLBAR)
            
        return True
            

def main():
    if sys.platform.startswith('win32'):
        
        filename = os.path.join(home, time.strftime("%Y%m%d")+"_DataGen.log")
        reportfile  = os.path.join(home, time.strftime("%Y%m%d")+"_DataGen.report.txt")
    else:
        filename = os.path.join(os.environ['HOME'], ".DataGen", time.strftime("%Y%m%d")+"_DataGen.log")
        reportfile  = os.path.join(os.environ['HOME'], time.strftime("%Y%m%d")+"_DataGen.report.txt")



    logfile.install(filename)
    #logfile.install('stdout')
        
    ## if there exist an instance for this program, exit it.
    

    if (Check_exist() == -1):
        sys.exit(-1)  
     
    try:      
        app = LaundryApp()
        app.MainLoop()
        
    except:
        s = traceback.format_exc()
        f = open(reportfile, 'a+')
        f.write(s)
        f.close()
        

if __name__ == '__main__':
    main()

