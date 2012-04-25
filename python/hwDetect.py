import os
import re 
from nicInfoHand import *

"""
import pdb
pdb.set_trace()
"""
def exe_command(command):
    pipe=os.popen(command,"r")
    result=pipe.readlines()
    pipe.close()
    return result
    
# detect the cpu whether support vt
# return :True if support
def cpuDetect():
    isVtSupport = False
    result=exe_command("egrep '(vmx|svm)' /proc/cpuinfo")       
    if len(result) != 0:
        isVtSupport = True     
        #print "the machine supports VT-d ."
        print_info("the machine supports VT-d .")
    return isVtSupport
        
# count the num of nic
# output:the number of nics
def nicDetect():
    result = exe_command("lspci | grep Ethernet | grep Connection")
    nicNum = len(result)     
    #print str(nicNum) + " Ethernet totally in this machine ."
    print_info(str(nicNum) + " Ethernet totally in this machine .")
    return nicNum

# detect the nic whether support sr-iov
# output:{}@"sriov82576Num":num/"sriov82599Num":num
def nicSriovDetect():
    sriovNicInfo = {}
#    isSriovSupport = False
    result = exe_command("lspci | grep Ethernet | egrep '(82576|82599)'")
    if len(result) != 0:
#        isSriovSupport = True
        sriov82576Num = 0
        sriov82599Num = 0
        try:
            for eachLine in result:
                if re.findall('82576',eachLine):
                    sriov82576Num = sriov82576Num +1
                else:
                    sriov82599Num = sriov82599Num +1    
        except:
            #print "no available 82576 or 82599 Ethernet ."
            print_info("no available 82576 or 82599 Ethernet .")
        sriovNicInfo['sriov82576Num'] = sriov82576Num
        sriovNicInfo['sriov82599Num'] = sriov82599Num
        if sriov82576Num !=0 :
            #print str(sriov82576Num) + " 82576 nic totally in this machine ."
            print_info(str(sriov82576Num) + " 82576 nic totally in this machine .")
        elif sriov82599Num !=0:
            #print str(sriov82599Num) + " 82599 nic totally in this machine . "
            print_info(str(sriov82599Num) + " 82599 nic totally in this machine . ")
    return sriovNicInfo

# get the nic pci address
# return PFNicBsfAddress:[]@(bus:slot.function,name,type)
def getPFNicBsfAddress():
    PFNicBsfAddress = []
    result = exe_command("lspci | grep Ethernet | grep Network")
    try:     
        for eachline in result:
            if re.findall('82576',eachline):
                PFNicBsfAddress.append((eachline.split()[0],82576,'PF'))
            elif re.findall('82599',eachline):
                PFNicBsfAddress.append((eachline.split()[0],82599,'PF'))
            else:# only intel Corporation 
                PFNicBsfAddress.append((eachline.split()[0],eachline.split("Corporation ")[1].split()[0],'PF'))
    except:
        #print "no available Ethernet Controlle."
        print_info("no available Ethernet Controlle.")
    return PFNicBsfAddress
            
# get the VF info after create VirtualFunction
# return:VFNicBsfAddress:[]@(bus:slot.function,name/82576 or 82599,nictype)
def getVFNicBsfAddress():
    VFNicBsfAddress = []
    result = exe_command("lspci | grep Ethernet | egrep '(82576|82599)' | grep 'Virtual Function'")
    try:
        for eachline in result:
            if re.findall('82576',eachline):
                VFNicBsfAddress.append((eachline.split()[0],82576,'VF'))
            elif re.findall('82599',eachline):
                VFNicBsfAddress.append((eachline.split()[0],82599,'VF'))
            else:# only intel Corporation 
                VFNicBsfAddress.append((eachline.split()[0],eachline.split("Corporation ")[1].split()[0],'VF'))
    except:
        #print "no available Virtual Function."            
        print_info("no available Virtual Function.")
    return VFNicBsfAddress
        
# get bus:slot.function && mac address
# input:cmd:"ls /sys/class/net" default
# output:bsfMacAddress:[]@(bus:slot.function,macaddress)
def getBsfMacAddress(cmd = "ls /sys/class/net"):
    bsfMacAddress = []
    result = exe_command(cmd)
    
    for r in result:
        if re.findall('eth',r):
            ethx_bsf = "udevadm info -a -p /sys/class/net/" + r.rstrip()+"| grep 'net/eth'"
            bsf_str = exe_command(ethx_bsf)
            try:
                #enable ethX up
                #print "/sbin/ifconfig "+ r.rstrip() + " up"
                os.system("/sbin/ifconfig "+ r.rstrip() + " up")
                
                #dbsf=domain:bus:slot.function
                dbsf = bsf_str[0].split("/net/eth")[0].split("/")[-1] 
                #bsf=bus:slot.function
                bsfAddress = dbsf.split(":")[1]+":"+dbsf.split(":")[-1]
            except:
                #print "failed to get ethX"
                print_info("failed to get ethX")
            
            ethx_mac = "udevadm info -a -p /sys/class/net/" + r.rstrip()+"| grep 'ATTR{address}'"
            mac_str = exe_command(ethx_mac)
            try:
                macAddress = mac_str[0].split('"')[1]
                bsfMacAddress.append((bsfAddress,macAddress))    
            except:
                #print "failed to get the mac address"
                print_info("failed to get the mac address")
    return bsfMacAddress

#test:
#bsfMacAddress = getBsfMacAddress();
#print bsfMacAddress