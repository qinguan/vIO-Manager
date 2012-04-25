import os
from cmdOp import *
from vmImageNetworkModify import *
from makeXml import *

#import pdb
#pdb.set_trace()

class manager(): 
    def __init__(self):
        self.image_file_path = ""
        self.xml_file_path = "/home/qinguan/xml/"
        
    def pre(self):
        #--------------------------------------------------------------------------------#
        #detect the hardware in the machine
        #--------------------------------------------------------------------------------#
        # input  :db@(engine,usedTable)
        # output :pf_nic_bsf_address:[]@(bus:slot.function,name,type)
        #         sriov_nic_info:the nic whether support sr-iov
        pf_nic_bsf_address ,sriov_nic_info = hw_detect(db)

        #--------------------------------------------------------------------------------#
        #create VF by the supported nic:82576 0r 82599
        #--------------------------------------------------------------------------------#
        # input: db@(engine,usedTable),
        #        pf_nic_bsf_address,
        #        sriov_nic_info,
        #        param=1,0 create by 82576,1 create by 82599 , 2 create by 82576 and 82599
        #        igb_max_vfs=4,
        #        ixgbe_max_vfs=4
        virtIO(db,pf_nic_bsf_address,sriov_nic_info,param=1,igb_max_vfs=4,ixgbe_max_vfs=4)
        
    def startVM(self,hostname,mac_address,ip_address,image_file_path,network=2):
        if image_file_path:
            self.image_file_path = image_file_path
        #if network = 2 ,flag = 1 ->vt-d;network = 1 ,flag = 0 -> sriov
        vm_xml = makeVMConfigureXML(hostname,self.image_file_path,network,memory=524288,passwd="")
        saveXmlToFile(vm_xml,self.xml_file_path,hostname) 
        
        # modify the image
        if network ==0 :
            res = modifyImage(self.image_file_path,1,mac_address,ip_address)#virtio
        elif network == 1:
            res = modifyImage(self.image_file_path,0,mac_address,ip_address)#sriov
        else:
            res = modifyImage(self.image_file_path,1,mac_address,ip_address)#vt-d
        #print "res : " + str(res)
        print_info("res : " + str(res))
        
        if res == 1:
            if commands.getstatusoutput("virsh create " + self.xml_file_path+hostname+".xml")[0] == 0:
                #print "virsh create " + self.xml_file_path+hostname+".xml  ......\n"
                print_info("virsh create " + self.xml_file_path+hostname+".xml  ......\n")
                #os.system("virt-viewer -c qemu:///system "+ hostname)
            else:
                #print "virsh create " + self.xml_file_path+hostname+".xml  failed ."
                print_info("virsh create " + self.xml_file_path+hostname+".xml  failed .")
        else:
            #print "start vm " + hostname + " failed ."
            print_info("start vm " + hostname + " failed .")

    def destroyVM(self,hostname):
        cmd = "virsh destroy "+ hostname
        if commands.getstatusoutput("virsh destroy "+ hostname)[0] == 0:
            print cmd + " successfully ."
            print_info(cmd + " successfully .")
        else:
            print cmd + " failed ."
            print_info(cmd + " failed .")
    
    def suspendVM(self,hostname):
        
        cmd = "virsh suspend "+ hostname
        if commands.getstatusoutput("virsh suspend "+ hostname)[0] == 0:
            print cmd + "successfully ."
            print_info(cmd + "successfully .")
        else:
            print cmd + " failed ."
            print_info(cmd + " failed .")
    
    def resumeVM(self,hostname):
        
        cmd = "virsh resume "+ hostname
        if commands.getstatusoutput("virsh resume "+ hostname)[0] == 0:
            print cmd + "successfully ."
            print_info(cmd + "successfully .")
        else:
            print cmd + " failed ."
            print_info(cmd + " failed .")
    
    def rebootVM(self,hostname):
        cmd = "virsh reboot "+ hostname
        if commands.getstatusoutput("virsh destroy" + hostname)[0]==0:
            if commands.getstatusoutput("virsh create /home/qinguan/xml/"+hostname+".xml")[0]==0:
                print cmd + "successfully ."
                print_info(cmd + "successfully .")
        else:
            print cmd + " failed ."
            print_info(cmd + " failed .")
            
    def do_monitor(self):
        result = exe_command("ps x | grep   monitor.py | grep Sl | awk   '{print   $1} '")
        #print result
        if len(result) > 1:
            #print "monitor is already running background ."
            print_info("monitor is already running background .")
            #print "the pid is "+result[0].rstrip()
            print_info("the pid is "+result[0].rstrip())
        else:
            pwd = os.getcwd()+"/monitor.py"
            bg_monitor_cmd = 'python ' + pwd+"&"
            os.system(bg_monitor_cmd)
            #print "monitor is running background now."      
            print_info("monitor is running background now.")

#test:
#manager().pre()
#manager().do_monitor()
#print "start vm xu_test1...\n"
#manager().startVM("xu_test1",mac_address="a7:cc:55:44:55:88",ip_address="10.100.0.31",image_file_path ="/home/qinguan/exp/kvm_img/ubuntu_1.img")
#print "start vm xu_test2...\n"
#manager().startVM("xu_test2",mac_address="b7:22:aa:44:55:66",ip_address="10.100.0.41",image_file_path ="/home/qinguan/exp/kvm_img/ubuntu_2.img")
#print "start vm xu_test3...\n"
#manager().startVM("xu_test3",mac_address="c7:22:aa:44:55:66",ip_address="10.100.0.52",image_file_path ="/home/qinguan/exp/kvm_img/ubuntu_3.img")
#print "start vm xu_test4...\n"
#manager().startVM("xu_test4",mac_address="d7:22:aa:44:55:66",ip_address="10.100.0.53",image_file_path ="/home/qinguan/exp/kvm_img/ubuntu_4.img")
