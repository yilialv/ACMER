# commonly used functions to write data into database

from acmerdata import bsdata
from .models import Student, Contest, StudentContest,AddStudentqueue,CFContest,Contestforecast,Weightrating
from django.db.models import Max
import logging
import time
import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
import colorsys,random

def setContestJoinNumbers():
    list = Contest.objects.all()
    for l in list:
        sc = StudentContest.objects.filter(cname=l.cname)
        l.cnumber = len(sc)
        l.save()

def getDivByName(contestname):
    div = 0
    dic = {"Div. 1":1, "Div. 2":2, "Div. 3":3, 'Grand ':1, 'Regular':2, 'Beginner':3}
    for k,v in dic.items():
        if contestname.find(k)>=0:
            div = v
            break
    return div

def addContest(contestID,date,contest,ctype,cnumber=0,starttime=0,endtime=0):
    if contestID and int(contestID)>0:
        ct = Contest.objects.filter(cid=contestID)
    else:
        ct = Contest.objects.filter(cname=contest)
    if len(ct) == 0:
        div = getDivByName(contest)
        Contest.objects.create(cid=contestID,cname=contest,cdate=date,cdiv=div,ctype=ctype,cnumber=cnumber,starttimestamp=starttime,endtimestamp=endtime)

def addStudentContest(stuNO,realname,classname,cid,cname,cdate,rank,newRating,diff,ctype,solve="no data"):
    sc = StudentContest.objects.filter(stuNO=stuNO,cid=cid,cname=cname)
    if len(sc) == 0:
        cdiv = getDivByName(cname)
        StudentContest.objects.create(stuNO=stuNO,realName=realname,className=classname,
            cid=cid,cname=cname,cdate=cdate,cdiv=cdiv,rank=rank,newRating=newRating,diff=diff,ctype=ctype,solve=solve)
    else:
        sc[0].newRating = newRating
        sc[0].diff = diff  # for fix bug
        sc[0].save()

def addCFStatu(stuNO,realname,cid,cname,cfID):
    datalist = bsdata.getsubmitdata(cid,cfID)
    for data in datalist:
        sc = CFContest.objects.filter(subid=data['subid'])
        if len(sc) == 0 :
            cdiv = cdiv = getDivByName(cname)
            try:
                CFContest.objects.create(stuNO=stuNO,realName=realname,cid=cid,cname=cname,subid=data['subid'],index=data['index'],
                    cdiv = cdiv,code = data['code'],tag = data['tags'],statu = data['statu'],ctime=data['time'])
            except:
                CFContest.objects.create(stuNO=stuNO,realName=realname,cid=cid,cname=cname,subid=data['subid'],index=data['index'],
                cdiv = cdiv,code = 'get error',tag = data['tags'],statu = data['statu'],ctime=data['time'])
        elif sc[0].code == 'get error':
            op = CFContest.objects.get(subid=data['subid'])
            op.code = data['code']
            op.save()
        

def saveCFDataByContest():
    students = Student.objects.all()
    cfIDList = []
    stuInfoDic = {}
    for stu in students:
        cfIDList.append(stu.cfID)
        stuInfoDic[stu.cfID] = stu
    log = logging.getLogger("log")
    max_timestamp=0
    for d in Contest.objects.all():
        t=d.ctype
        dt=d.cdate 
        if(d.ctype=="cf"):
            timestamp=int(time.mktime(time.strptime(dt, "%Y-%m-%d %H:%M:%S") )) 
            if(max_timestamp<timestamp):
                max_timestamp=timestamp
            
    # print(existMaxCFID)
    log.info(max_timestamp)
    str = ""
    contestList = bsdata.getCFContestList(max_timestamp)
    for c in contestList:
        rankChangingList = bsdata.getCFContestRankingChange(c["cid"],cfIDList)
        if len(rankChangingList)>0:
            str += c["cname"] + ","
            addContest(c["cid"],c["cdate"],c["cname"],"cf",len(rankChangingList),c["starttime"],c["endtime"])
            for r in rankChangingList:
                stu = stuInfoDic[r["cfID"]]
                log.info("addStudentContest" + stu.realName)
                addStudentContest(stu.stuNO,stu.realName,stu.className,c["cid"],
                                    c["cname"],c["cdate"],r["rank"],r["newRating"],r["diff"],"cf")
                addCFStatu(stu.stuNO,stu.realName,c["cid"],c["cname"],r["cfID"])
                p = Student.objects.get(cfID=r["cfID"])
                p.cfRating=r["newRating"]
                k = int(p.cfTimes) + 1
                p.cfTimes = k
                p.save()
            setcontestsolve(c["cid"])
    return str

def saveCFdataByUser(stu):
    if stu.cfID:
        dataList = bsdata.getCFUserData(stu.cfID)
        stu.cfTimes = len(dataList)
        if(stu.cfTimes > 0):
            stu.cfRating = dataList[-1]["newRating"]
            for data in dataList:
                addContest(data["contestID"],data["date"],data["contest"],"cf")
                addStudentContest(stu.stuNO,stu.realName,stu.className,data["contestID"],
                    data["contest"],data["date"],data["rank"],data["newRating"],data["diff"],"cf")
                addCFStatu(stu.stuNO,stu.realName,data["contestID"],data["contest"],stu.cfID)
        else:
            stu.cfRating = 0
    else:
        stu.cfTimes = 0
        stu.cfRating = 0
    stu.save()

def saveACData_fixbug(stu):
    pass
def getLatestCFRating(stuNO,date):
    sclist = StudentContest.objects.filter(cdate__startswith=date,stuNO=stuNO,ctype='cf')        
    rating = 0
    for sc in sclist:
        rating = sc.newRating
    return rating

def saveACData(stu):
    if stu.acID:
        dataList = bsdata.getACUserData(stu.acID)
        stu.acTimes = len(dataList)
        if(stu.acTimes > 0):
            stu.acRating = dataList[-1]["newRating"]
            for data in dataList:
                addContest(data["contestID"],data["date"],data["contest"],"ac")
                addStudentContest(stu.stuNO,stu.realName,stu.className,data["contestID"],data["contest"],data["date"],data["rank"],data["newRating"],data["diff"],"ac")
        else:
            stu.acRating = 0
    else:
        stu.acTimes = 0
        stu.acRating = 0
    stu.save()

def saveNCData(stu):
    if stu.ncID:
        dataList=bsdata.getNCUserData(stu.ncID)
        stu.ncTimes = len(dataList)
        if stu.ncTimes > 0 :
            nrk = True
            for data in dataList:
                if nrk:
                    if data['newrating'] != 0:
                        stu.ncRating = data['newrating']
                        nrk=False
                addContest(data['contestID'],data["date"],data["contest"],"nc")
                addStudentContest(stu.stuNO,stu.realName,stu.className,data['contestID'],data["contest"],data["date"],data["rank"],data["newrating"],data["diff"],"nc",data["acnum"])
        else:
            stu.ncRating = 0
    else:
        stu.ncTimes=0
    stu.save()

def contestdatasolve(cname=0,stuNO=0):
    if(cname):
        list = StudentContest.objects.order_by('rank').filter(cname=cname)
    if(stuNO):
        list = StudentContest.objects.order_by('-cdate').filter(stuNO=stuNO)
    data =[]
    for i in list:
        if i.diff[0] != '-':
            difftype = 1
            if i.diff[0]!='+':
                diff = ''.join(['+',i.diff])
            else:
                diff = i.diff
        else:
            difftype = 0
            diff = i.diff
        data.append({
            'id':i.id,
            'cname':i.cname,
            'cdate':i.cdate,
            'stuNO':i.stuNO,
            'className':i.className,
            'rank':i.rank,
            'realname':i.realName,
            'newRating':i.newRating,
            'diff':diff,
            'solve':i.solve,
            'difftype':difftype,
            'type':i.ctype,
            'after':i.aftersolve,
        })
    return data

def saveCFstatu(stuNO,realname,cid,cname,time,tags,statu,index,subid):
    print(subid)
    t=0
    while True:
        try:
            t=t+1
            sc = CFContest.objects.filter(subid=subid)
            if len(sc)==0 or sc.code=='get error':
                code = bsdata.submitdetail(cid,subid)
                break
            else:
                code = sc[0].code
                break
        except:
            if t>5 :
                code='get error'
                break
    cdiv = cdiv = getDivByName(cname)
    try:
        CFContest.objects.create(stuNO=stuNO,realName=realname,cid=cid,cname=cname,subid=subid,index=index,
            cdiv = cdiv,code = code,tag = tags,statu = statu,ctime=time)
    except:
        CFContest.objects.create(stuNO=stuNO,realName=realname,cid=cid,cname=cname,subid=subid,index=index,
            cdiv = cdiv,code = 'get error',tag = tags,statu = statu,ctime=time)
    try:
        cfsolvereset(stuNO,cid)
    except:
        pass

def cfsolvereset(stuNO,cid):
    submits = CFContest.objects.filter(stuNO=stuNO,cid=cid)
    ok = []
    solve = 0
    for submit in submits:
        if submit.statu == 'OK' and ok.count(submit.index)==0:
            solve=solve+1
            ok.append(submit.index)
    contest = StudentContest.objects.get(stuNO=stuNO,cid=cid)
    contest.solve = str(solve)
    contest.save()
def cftimesreset():
    students = Student.objects.all()
    for stu in students:
        contests = StudentContest.objects.filter(ctype='cf',stuNO=stu.stuNO)
        stu.cfTimes = len(contests)
        stu.save()

def addforecastlist(starttime,cname,during,link,ctype,cid=0):
    if ctype == 'cf':
        sc = Contestforecast.objects.filter(cid=cid)
    else:
        sc = Contestforecast.objects.filter(cname=cname)
    if len(sc)==0:
        Contestforecast.objects.create(ctype=ctype,link=link,cname=cname,starttime=starttime,during=during,cid=cid)
    else:
        a=sc[0]
        a.ctype=ctype
        a.link=link
        a.cname=cname
        a.starttime=starttime
        a.during=during
        a.save()
    
def timestamptotime(ts):
    hour = ts/3600
    minute = (ts%3600)/60
    time = '%02d:%02d' % (hour,minute)
    return time

def cftimeStandard():
    cfcontest = Contest.objects.filter(ctype='cf')
    cflist=[]
    strs=''
    for contest in cfcontest:
        cflist.append(contest.cid)
    timelist = bsdata.getcftimestamp(cflist)
    for contest in timelist:
        strs += str(contest['cid']) +'  &  '
        con = Contest.objects.get(cid = contest['cid'])
        con.starttimestamp = contest['starttime']
        con.cdate = time.strftime("%Y-%m-%d %H:%M:%S",(time.localtime(int(contest['starttime']))))
        con.endtimestamp = contest['endtime']
        con.save()
    return strs

def setcontestsolve(cid):
    stucons = StudentContest.objects.filter(cid=cid)
    for stucon in stucons:
        submits = CFContest.objects.filter(cid=cid,stuNO=stucon.stuNO)
        contest = Contest.objects.get(cid=cid)
        solve = 0
        after = 0
        index = []
        for submit in submits:
            if submit.statu=='OK' and submit.index not in index :
                if submit.ctime > contest.endtimestamp:
                    after = after + 1
                else:
                    solve = solve + 1
                index.append(submit.index)
        stucon.solve = str(solve)
        stucon.aftersolve = str(after)
        stucon.save()

def setaftersolve(stu):
    allsub = 0
    correctsub = 0
    StuCFcontests = StudentContest.objects.filter(stuNO=stu.stuNO,ctype='cf')
    for con in StuCFcontests:
        cont = Contest.objects.get(cid = con.cid)
        submitlen = len(CFContest.objects.filter(cid=con.cid,stuNO=stu.stuNO,ctime__gt=cont.endtimestamp))
        allsub += int(submitlen)
        correctsub += int(con.aftersolve)
    stu.all_cf_aftersolve= allsub
    stu.correct_cf_aftersolve = correctsub
    stu.save()

def setcfdata():
    cfcontests = StudentContest.objects.filter(ctype='cf',stuNO=stuNO)
    data = []
    for contest in cfcontests:
        con = Contest.objects.get(cid=contest.cid)
        submits = CFContest.objects.filter(cid=contest.cid,stuNO=stuNO,ctime__gt=con.endtimestamp)
        for submit in submits:
            data.append({
                'stuNO':submit.stuNO,
                'realName':submit.realName,
                'contestname':con.cname,
                'subid':submit.subid,
                'index':submit.index,
                'tag':submit.tag,
                'statu':submit.statu,
                'time':time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(submit.ctime)),
            })
    context = {
        'name':Student.objects.get(stuNO=stuNO).realName,
        'list':data,
    }
    return render(request,"aftersubmit.html",context)

def setallaftersolve(request):
    students = Student.objects.all()
    strs = ''
    for stu in students:
        strs += stu.realName + ','
        datautils.setaftersolve(stu)
    context = {'str': strs }
    return render(request, 'spiderResults.html', context)

def addprizet(request):
    if request.method=="POST":
        formt = addprize(request.POST)
        if formt.is_valid():
            form = formt.clean()
            AddContestprize.objects.create(name = form['name'],className=form['classname'],stuyear=form['year'],
            stuNO=form['stuNO'],cname=form['contestname'],cyear=form['cyear'],clevel=form['level'],prize=form['prize'],exe=False)
            forms = addprize(initial={"name":form['name'],'classname':form['classname'],'year':form['year'],'stuNO':form['stuNO']})
            return render(request,'addprize.html',{'form': forms})
    else:
        formt = addprize()
    return render(request,'addprize.html',{'form': formt})


#color
def get_n_hls_colors(num):
    hls_colors = []
    i = 0
    step = 360.0 / num
    while i < 360:
        h = i
        s = 90 + random.random() * 10
        l = 50 + random.random() * 10
        _hlsc = [h / 360.0, l / 100.0, s / 100.0]
        hls_colors.append(_hlsc)
        i += step
 
    return hls_colors
 
def ncolors(num):
    rgb_colors = []
    if num < 1:
        return rgb_colors
    hls_colors = get_n_hls_colors(num)
    for hlsc in hls_colors:
        _r, _g, _b = colorsys.hls_to_rgb(hlsc[0], hlsc[1], hlsc[2])
        r, g, b = [int(x * 255.0) for x in (_r, _g, _b)]
        rgb_colors.append("rgba("+str(r)+','+str(g)+","+str(b))
    return rgb_colors
#colorend