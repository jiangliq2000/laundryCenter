import os, sys
import struct
import logfile

dataNum = 2
pumpLen = 4
pumpNum = 8
programLen = pumpLen * pumpNum
programNum = 20
washerLen = programLen * programNum
washerNum = 4
fileLen = washerLen * washerNum

washerData = range(washerNum)
programData = range(programNum)
pumpData = range(pumpNum)
## 42330 = 0xa55a
recordHead = 42330

dataFile= [[[[0 for x in range(dataNum)]for y in range(pumpNum)] for z in range(programNum)] for w in range(washerNum)]

def ReadFile(filename):
    fd = open(filename, "rb")
    
    for washInd in range(washerNum):
        for progInd in range(programNum):
            for pumpInd in range(pumpNum):
                value = fd.read(4)
                a, b = struct.unpack("2H", value)
                dataFile[washInd][progInd][pumpInd] = [a,b]
    fd.close()
    

def ChangeToASCIIFile(asciiFile):
    fd = open(asciiFile, "w")
    for i in range(programNum):
        for j in range(pumpNum):
            valueLine = "%d,%d,%d,%d,%d,%d,%d,%d,\n" % (dataFile[0][i][j][0],dataFile[0][i][j][1], \
                                                       dataFile[1][i][j][0],dataFile[1][i][j][1], \
                                                       dataFile[2][i][j][0],dataFile[2][i][j][1], \
                                                       dataFile[3][i][j][0],dataFile[3][i][j][1])
            fd.write(valueLine)


    
    fd.close()


def ChangeToBin(asciiFile):
    fd = open(asciiFile, "r")
    for i in range(programNum):
        for j in range(pumpNum):
            eachLine = fd.readline()
            valueLine = eachLine.split(",")                
            dataFile[0][i][j][0] = int(valueLine[0])
            dataFile[0][i][j][1] = int(valueLine[1])
            dataFile[1][i][j][0] = int(valueLine[2])
            dataFile[1][i][j][1] = int(valueLine[3])
            dataFile[2][i][j][0] = int(valueLine[4])
            dataFile[2][i][j][1] = int(valueLine[5])
            dataFile[3][i][j][0] = int(valueLine[6])
            dataFile[3][i][j][1] = int(valueLine[7])
    fd.close()
    #print "dataFile is ", dataFile


def WriteFile(filename):

    fd = open(filename, "wb")
    for washInd in range(washerNum):
        for progInd in range(programNum):
            for pumpInd in range(pumpNum):
                [a, b] = dataFile[washInd][progInd][pumpInd]
                value = struct.pack("HH",a,b)
                fd.write(value)
    fd.close()



### below is IO function for display page.
""" temp file format

machine_id, content, time,  pump1, pump2, pump3, pump4, pump5, pump6, pump7, pump8, wash_cnt

"""

record_frm = "HBHBBH"
record_len = 66
dict_frm = {}




def Dis_ReadRecord(fd):
    """ read record and assign to dict_frm"""
    #define a temp array to store pump data include time and bool flag
    pump_data = {}
    #1.read record head, machineid and seq
    value = fd.read(2)
    a, = struct.unpack("H", value) 
    if a!= recordHead:
        return -1
    dict_frm['head'] = a
    value = fd.read(1)
    a, = struct.unpack("B", value) 
    dict_frm['machine_id'] = a
    value = fd.read(2)
    a, = struct.unpack("H", value) 
    dict_frm['seq'] = a

    
    
    #2. read data_dev
    ## first read dev_id, type, and wash_cnt
    value = fd.read(4)
    a,b,c = struct.unpack("BBH",value)
    dict_frm['devid'] = a
    dict_frm['type'] = b
    dict_frm['wash_cnt'] = c

    ## now read pump data
    for i in range(pumpNum):
        value = fd.read(5)
        a,b,c,d,e = struct.unpack("BBBBB", value)
        pump_data['valid'] = a
        pump_data['wash_type'] = b
        pump_data['start_h'] = c
        pump_data['start_m'] = d
        pump_data['start_s'] = e
        value = fd.read(2)
        f, = struct.unpack("H", value) 
        pump_data['vol'] = f
        
        pump_index="pumpInd_%d" % i
        dict_frm[pump_index] = pump_data.copy()
    #3. read crc , current don't need this para
    value = fd.read(1)
    a = struct.unpack("B",value)
    dict_frm['crc'] = a
    return 0

    
    
def Dis_WriteRecord(fd_out):
    """ write one record to file from dict_frm""" 
    # compare every time, select the min time, here exist eight time
    # 1. conver time to seconds
    startTime = 23*3600 + 59*60 + 59
    indexTime = 'pumpInd_0'
    for i in range(pumpNum):
        pump_index="pumpInd_%d" % i
        tmpTime = dict_frm[pump_index]['start_h'] * 3600 + dict_frm[pump_index]['start_m'] * 60 + dict_frm[pump_index]['start_s']
        if tmpTime != 0 and tmpTime < startTime:
            startTime = tmpTime
            indexTime = pump_index
    if startTime == 23*3600 + 59*60 + 59:
        logfile.info("--- this record is invalid because time = 0 ---")
    
    
    if dict_frm[indexTime]['start_h'] < 10:
        time_h = "0%d" % dict_frm[indexTime]['start_h']
    else:
        time_h = "%d" % dict_frm[indexTime]['start_h']
        
    if dict_frm[indexTime]['start_m'] < 10:
        time_m = "0%d" % dict_frm[indexTime]['start_m']
    else:
        time_m = "%d" % dict_frm[indexTime]['start_m']
    if dict_frm[indexTime]['start_s'] < 10:
        time_s = "0%d" % dict_frm[indexTime]['start_s']
    else:
        time_s = "%d" % dict_frm[indexTime]['start_s']
      
    vol_str = "%d, %d, %d, %d, %d, %d, %d, %d" %(dict_frm['pumpInd_0']['vol'], dict_frm['pumpInd_1']['vol'], dict_frm['pumpInd_2']['vol'], dict_frm['pumpInd_3']['vol'], \
                 dict_frm['pumpInd_4']['vol'], dict_frm['pumpInd_5']['vol'], dict_frm['pumpInd_6']['vol'], dict_frm['pumpInd_7']['vol'])
    # recalcuate time
    """
    diff_time = [ 0 for x in range(8)]
    for i in range(pumpNum):
        pump_index="pumpInd_%d" % i
        diff_time[i] = (dict_frm[pump_index]['end_h'] - dict_frm[pump_index]['start_h'] ) * 3600 +  \
                                (dict_frm[pump_index]['end_m'] - dict_frm[pump_index]['start_m'] ) * 60 + \
                                (dict_frm[pump_index]['end_s'] - dict_frm[pump_index]['start_s'] ) 
    """
    valueline = "%d, %d, %s:%s:%s, %d, %d, %d, %d, %d, %d, %d, %d,%d, %d, %d, %d, %d, %d, %d, %d, %d \n" \
                %(dict_frm['devid'],dict_frm['type'], time_h,time_m,time_s, \
                 dict_frm['pumpInd_0']['wash_type'], dict_frm['pumpInd_0']['vol'],dict_frm['pumpInd_1']['wash_type'],dict_frm['pumpInd_1']['vol'],\
                 dict_frm['pumpInd_2']['wash_type'], dict_frm['pumpInd_2']['vol'],dict_frm['pumpInd_3']['wash_type'],dict_frm['pumpInd_3']['vol'],\
                 dict_frm['pumpInd_4']['wash_type'], dict_frm['pumpInd_4']['vol'],dict_frm['pumpInd_5']['wash_type'],dict_frm['pumpInd_5']['vol'],\
                 dict_frm['pumpInd_6']['wash_type'], dict_frm['pumpInd_6']['vol'],dict_frm['pumpInd_7']['wash_type'],dict_frm['pumpInd_7']['vol'],\
                 dict_frm['wash_cnt'])
    fd_out.write(valueline)

volPos_start = 4
volOffset = 8 * 2
vol1_off = volPos_start 
vol2_off = volPos_start + 2
vol3_off = vol2_off + 2
vol4_off = vol3_off + 2
vol5_off = vol4_off + 2
vol6_off = vol5_off + 2
vol7_off = vol6_off + 2
vol8_off = vol7_off + 2
RecordMaxNum = 100
ColMaxNum = 20




# merge rule: 
#
def Dis_MergeFile(fin, fout):
    """ merge multiple line for orignal output file 
    """
    LineNum_dict = { }
    fd_in = open(fin, "r")
    fd_out = open(fout, "w")
    os.system('attrib +h fout')
    lineNum = 0
    totalList = [ 0 for x in range(8)]
    ## 100 -- mean max record num
    ## 20 - mean col num
    mergeDataFile = [[-1 for x in range(ColMaxNum)] for y in range(RecordMaxNum+1)]
    
    for valueLine in fd_in:
        lineNum = lineNum + 1
        #mergeDataFile[lineNum] = valueLine
                
        tmpList = valueLine.split(',')
        print "tmpList is ", tmpList
        print "tmpList[-1][0] is ", tmpList[-1]
        key = "%d" % int(tmpList[0]) +"+" + "%d" % int(tmpList[len(tmpList)-1])
        value = lineNum
        LineNum_dict.setdefault(key,[]).append(value)
        # read every line of input file  to  mergeDataFile list
        mergeDataFile[lineNum] = tmpList[:]
        #mergeDataFile[2][5] = "1000"
        #newline = ",".join(mergeDataFile[lineNum])
        #print " join is ", newline
        #fd_out.write(",".join(mergeDataFile[lineNum]))
    #print "dict is ", LineNum_dict
    #print "line num is ", lineNum
        
    for k in LineNum_dict.keys():
        value = LineNum_dict[k] 
        #print "value len is ", len(value)
        # first line 
        totalList[0] = int(mergeDataFile[value[0]][vol1_off])
        totalList[1] = int(mergeDataFile[value[0]][vol2_off])
        totalList[2] = int(mergeDataFile[value[0]][vol3_off])
        totalList[3] = int(mergeDataFile[value[0]][vol4_off])
        totalList[4] = int(mergeDataFile[value[0]][vol5_off])
        totalList[5] = int(mergeDataFile[value[0]][vol6_off])
        totalList[6] = int(mergeDataFile[value[0]][vol7_off])
        totalList[7] = int(mergeDataFile[value[0]][vol8_off])
        
        
        for i in range(1,len(value)):
            totalList[0] = totalList[0] + int(mergeDataFile[value[i]][vol1_off])
            totalList[1] = totalList[1] + int(mergeDataFile[value[i]][vol2_off])
            totalList[2] = totalList[2] + int(mergeDataFile[value[i]][vol3_off])
            totalList[3] = totalList[3] + int(mergeDataFile[value[i]][vol4_off])
            totalList[4] = totalList[4] + int(mergeDataFile[value[i]][vol5_off])
            totalList[5] = totalList[5] + int(mergeDataFile[value[i]][vol6_off])
            totalList[6] = totalList[6] + int(mergeDataFile[value[i]][vol7_off])
            totalList[7] = totalList[7] + int(mergeDataFile[value[i]][vol8_off])
            
            ## if vol value is not equal zero, we must update the wash type to the first line
            ## for example, the first line liquid type [4] = N/A, but seconde lie, the liquid type[4] = 'lu biao'
            ## so we must update 'lu biao' to  N/A
            for j in range(8):
                tmpvol = vol1_off + 2*j
                if int(mergeDataFile[value[i]][tmpvol]) != 0:                    
                    mergeDataFile[value[0]][tmpvol-1] = mergeDataFile[value[i]][tmpvol-1] 
            
            
            
            #print "value line is ", value[i]+1
            mergeDataFile[value[i]][0] = '-1'
                   
        mergeDataFile[value[0]][vol1_off] = "%d" % totalList[0]
        mergeDataFile[value[0]][vol2_off] = "%d" % totalList[1]
        mergeDataFile[value[0]][vol3_off] = "%d" % totalList[2]
        mergeDataFile[value[0]][vol4_off] = "%d" % totalList[3]
        mergeDataFile[value[0]][vol5_off] = "%d" % totalList[4]
        mergeDataFile[value[0]][vol6_off] = "%d" % totalList[5]
        mergeDataFile[value[0]][vol7_off] = "%d" % totalList[6]
        mergeDataFile[value[0]][vol8_off] = "%d" % totalList[7]
        
            
        
    for i in range(1, lineNum+1):
        #print "mergeDataFile[i][0] is",mergeDataFile[i][0]
        if mergeDataFile[i][0] != '-1':  
            fd_out.write(",".join(mergeDataFile[i]))
            
    fd_in.close()
    fd_out.close()


class MergeData():
    def __init__(self):
        self.num = 0
        self.DataList = []
        
    def Insert(self, data):
        logfile.info("--- start to insert one record, wash_cnt=%s... ---" % data[-1])
        self.num = self.num + 1
        self.DataList.append(data)
        #print "dataList is ", self.DataList
        
    def GetLineNum(self):
        return self.num
    
    def GetOneRecord(self,index):
        return self.DataList[index]
        
    def Merge(self, data):
        logfile.info("--- start to merge one record, wash_cnt=%s... ---" % data[-1])
        lineNum = -1
        #print "self num is %d " % self.num
        # 1. located which line will be merge
        for i in range(self.num, 0, -1):
            #print "i is %d" % i
            if data[0] == self.DataList[i-1][0] :
                lineNum = i-1
                break
        # if linenum == 0, it mean we cannot find the merge line
        if lineNum == -1:
            return -1
        # 2. merge data
        #print "merge line num is %d \n"  % lineNum
        totalList = [ 0 for x in range(8)]
        totalList[0] = int(self.DataList[lineNum][vol1_off]) + int(data[vol1_off])
        totalList[1] = int(self.DataList[lineNum][vol2_off]) + int(data[vol2_off])
        totalList[2] = int(self.DataList[lineNum][vol3_off]) + int(data[vol3_off])
        totalList[3] = int(self.DataList[lineNum][vol4_off]) + int(data[vol4_off])
        totalList[4] = int(self.DataList[lineNum][vol5_off]) + int(data[vol5_off])
        totalList[5] = int(self.DataList[lineNum][vol6_off]) + int(data[vol6_off])
        totalList[6] = int(self.DataList[lineNum][vol7_off]) + int(data[vol7_off])
        totalList[7] = int(self.DataList[lineNum][vol8_off]) + int(data[vol8_off])
        for j in range(8):
            tmpvol = vol1_off + 2*j
            if int(data[tmpvol]) != 0:                    
                self.DataList[lineNum][tmpvol-1] = data[tmpvol-1]
        
        self.DataList[lineNum][vol1_off] = "%d" % totalList[0]
        self.DataList[lineNum][vol2_off] = "%d" % totalList[1]
        self.DataList[lineNum][vol3_off] = "%d" % totalList[2]
        self.DataList[lineNum][vol4_off] = "%d" % totalList[3]
        self.DataList[lineNum][vol5_off] = "%d" % totalList[4]
        self.DataList[lineNum][vol6_off] = "%d" % totalList[5]
        self.DataList[lineNum][vol7_off] = "%d" % totalList[6]
        self.DataList[lineNum][vol8_off] = "%d" % totalList[7]       



def NewDis_MergeFile(fin, fout):
    """ merge multiple line for orignal output file 
    """
    fd_in = open(fin, "r")
    fd_out = open(fout, "w")
    os.system('attrib +h fout')
    merge_data = MergeData()
    totalList = [ 0 for x in range(8)]
    ## 100 -- mean max record num
    ## 20 - mean col num
    #mergeDataFile = [[-1 for x in range(ColMaxNum)] for y in range(RecordMaxNum+1)]
    
    prevList = []
    currentList = []
    
    for valueLine in fd_in:        
        currentList = valueLine.strip('\n').split(',')
        #print " current List is " , currentList
        if prevList == [] :
            # if prevList is NULL, currentList is first line, insert
            merge_data.Insert(currentList)
        else:
            # judge if need insert or merge
            #print "prevList is not null"
            if currentList[-1] == prevList[-1]:
                merge_data.Merge(currentList)
            else:
                merge_data.Insert(currentList)            
        prevList = currentList
        #print "prevList is ", prevList

        
    for i in range(merge_data.GetLineNum()):
        fd_out.write(",".join(merge_data.GetOneRecord(i)) + '\n')
            
    fd_in.close()
    fd_out.close()





def Dis_ReadFile(fname_in, fname_out):
    """ read .rpt file to display """
    fd_in = open(fname_in, "rb")
    fd_out = open(fname_out, "w")
    os.system('attrib +h fname_out')
    # to hide the temp file, here is fname_out
    #os.system('attrib +h fname_out')
    
    #1. judge how many records,   the total byte / record len
    fd_in.readlines()    
    file_len = fd_in.tell()
    num = file_len / record_len
    
    if num > 100:
        recordNum = 100
    else:
        recordNum = num
    
    #2 select head and tail to judge if file is complete
    fd_in.seek(0)
    value = fd_in.read(2)
    a, = struct.unpack("H", value) 
    fd_in.seek(file_len -66)
    value = fd_in.read(2)
    b, = struct.unpack("H", value)
    
    if a != recordHead and b !=recordHead:
        return -1
    
    fd_in.seek(0)
    for i in range(recordNum):
        if Dis_ReadRecord(fd_in) == -1:
            return -1
        Dis_WriteRecord(fd_out)
    fd_in.close()
    fd_out.close()
    return num
        
    



def test(filename):
    fd = open(filename, "rb")
    fd.readlines()
    print "count byte is " , fd.tell()
    fd.seek(0)
    print "count byte is " , fd.tell()
    fd.close()

if __name__ == '__main__':
    """
    ReadFile("WASH.dat")
    WriteFile("writewash1.dat")
    ChangeToASCIIFile("wrascc.dat")
    ChangeToBin("wrascc.dat")
    WriteFile("writewsh2.dat")
    print "read and write is finished!"


    #Dis_ReadFile("20121126.rtp", "20121126.txt")
    fd = open("20121203.rtp", "rb")
    fd.seek(66)
    value = fd.read(66)
    fd1 = open("test1-rd.rtp","wb")
    fd1.write(value)
    fd.close()
    fd1.close()
    """
    #Dis_MergeFile("newtmpfile", "mergefile")



   
