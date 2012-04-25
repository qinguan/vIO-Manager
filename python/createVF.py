import os 
import re

def exe_command(command):
    pipe=os.popen(command,"r")
    result=pipe.readlines()
    pipe.close()
    return result

def print_info(str):
    os.system('echo '+ str + ' >> /var/rails/DB_Reader_IOvirt/log/IOvirt.log')
    
# default 2 port
def createVFBy82576Nic(igb_max_vfs):
    try:
        if igb_max_vfs >0 and igb_max_vfs <8 :
            os.system("rmmod igb")
            #print "rmmod igb successfully ."
            print_info("rmmod igb successfully .")
#            cmd = "modprobe igb max_vfs="+str(igb_max_vfs)+","+str(igb_max_vfs)
            cmd = "modprobe igb max_vfs="+str(0)+","+str(igb_max_vfs)
            os.system(cmd)
            #print cmd+" successfully ."
            print_info(cmd+" successfully .")
            #print "VF created by 82576 Nic . "
            print_info("VF created by 82576 Nic . ")
        else:
            #print "the igb_max_vfs param is not valid."
            print_info("the igb_max_vfs param is not valid.")
    except:
        os.system("modprobe igb") 
        #print "the 82576 Nic creates VF failed ."
        print_info("the 82576 Nic creates VF failed .")
        
# default 2 port
def createVFBy82599Nic(ixgbe_max_vfs):
    try:
        if ixgbe_max_vfs >0 and ixgbe_max_vfs <64:
            os.system("rmmod ixgbe")
            #print "rmmod ixgbe successfully ."
            print_info("rmmod ixgbe successfully .")
            cmd = "modprobe ixgbe max_vfs="+str(ixgbe_max_vfs)+","+str(ixgbe_max_vfs)
            os.system(cmd)
            #print cmd + " successfully."
            print_info(cmd + " successfully.")
            #print "VF created by 82599 Nic . "
            print_info("VF created by 82599 Nic . ")
        else:
            #print "the ixgbe_max_vfs param is not valid."
            print_info("the ixgbe_max_vfs param is not valid.")
    except:
        os.system("modprobe ixgbe")
        #print "the 82599 Nic creates VF failed ."
        print_info("the 82599 Nic creates VF failed .")
        
        
# create the VF function to support sriov 
# input:PFNicBsfAddress:[]@(bus:slot.function,name/82576 or 82599,nictype),
#       sriovNicInfo:{}@"sriov82576Num":num/"sriov82599Num":num,
#       param: 0 create by 82576,1 create by 82599 , 2 create by 82576 and 82599
#       igb_max_vfs:0 default , 1~7 available,
#       ixgbe_max_vfs:0 default ,1-63 available ,
# output:pfbsfused :[]@(bus:slot.function)
def createNicVirtualFunction(PFNicBsfAddress,sriovNicInfo,param,igb_max_vfs=0,ixgbe_max_vfs=0):
    pfbsfused = []
    vf82576 = 0
    vf82599 = 0
    if len(PFNicBsfAddress) > len(sriovNicInfo) and len(sriovNicInfo) != 0:
        if param == 1:
            for elem in PFNicBsfAddress:
                if elem[1] == 82576 and vf82576 == 0:
                    createVFBy82576Nic(igb_max_vfs)
                    vf82576 = 1
                    pfbsfused.append(elem[0])
                elif elem[1] == 82576:
                    pfbsfused.append(elem[0])
        if param == 2:
            for elem in PFNicBsfAddress:
                if elem[1] == 82599 and vf82599 == 0:
                    createVFBy82576Nic(igb_max_vfs)
                    vf82599 = 1
                    pfbsfused.append(elem[0])
                elif elem[1] == 82599:
                    pfbsfused.append(elem[0])
        if param == 3:             
            for elem in PFNicBsfAddress:
                if elem[1] == 82576 and vf82576 == 0 :
                    createVFBy82576Nic(igb_max_vfs)
                    vf82576 = 1
                    pfbsfused.append(elem[0])
                elif elem[1] == 82576 :
                    pfbsfused.append(elem[0])
                elif elem[1] == 82599 and vf82599 == 0: 
                    createVFBy82599Nic(ixgbe_max_vfs)
                    vf82599 = 1
                    pfbsfused.append(elem[0])
                elif elem[1] == 82599 :
                    pfbsfused.append(elem[0])
                else:
                    pass
    #if len(PFNicBsfAddress) != 0 and len(sriovNicInfo) != 0:
        #for elem in PFNicBsfAddress:
            #if elem[1] == 82576 and vf82576 == 0 :
                #createVFBy82576Nic(igb_max_vfs)
                #vf82576 = 1
                #pfbsfused.append(elem[0])
            #elif elem[1] == 82576 :
                #pfbsfused.append(elem[0])
            #elif elem[1] == 82599 and vf82599 == 0: 
                #createVFBy82599Nic(ixgbe_max_vfs)
                #vf82599 = 1
                #pfbsfused.append(elem[0])
            #elif elem[1] == 82599 :
                #pfbsfused.append(elem[0])
            #else:
                #pass
        # enable ethX up after creating the VFs
        cmd = "ls /sys/class/net"
        result = exe_command(cmd)
        for r in result:
            if re.findall('eth',r):
                try:
                    os.system("/sbin/ifconfig " + r.rstrip() + " up")
                    #print "/sbin/ifconfig " + r.rstrip() + " up ."
                    print_info("/sbin/ifconfig " + r.rstrip() + " up .")
                except:
                    #print "up the " + r.rstrip() + " failed ." 
                    print_info("up the " + r.rstrip() + " failed ." )
    else:
        #print "no NIC virtual Function is created."               
        print_info("no NIC virtual Function is created.")
    return pfbsfused        