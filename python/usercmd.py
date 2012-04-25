from vmManager import  *
import time

#import pdb
#pdb.set_trace()

def start_test_1():
    destory_test()
    print "start vm xu_test1..."
    manager().startVM("xu_test1",mac_address="a7:cc:55:44:55:88",ip_address="10.100.0.31",image_file_path ="/home/qinguan/exp/kvm_img/ubuntu_1.img" ,network=2)
    print "start vm xu_test2..."
    manager().startVM("xu_test2",mac_address="b7:22:aa:44:55:66",ip_address="10.100.0.41",image_file_path ="/home/qinguan/exp/kvm_img/ubuntu_2.img" ,network=1)
    print "start vm xu_test3..."
    manager().startVM("xu_test3",mac_address="c7:22:aa:44:55:66",ip_address="10.100.0.52",image_file_path ="/home/qinguan/exp/kvm_img/ubuntu_3.img" ,network=0)
    print "start vm xu_test4..."
    manager().startVM("xu_test4",mac_address="d7:22:aa:44:55:66",ip_address="10.100.0.53",image_file_path ="/home/qinguan/exp/kvm_img/ubuntu_4.img" ,network=0)

def start_test_2():
    destory_test()
    print "start vm xu_test1..."
    manager().startVM("xu_test1",mac_address="a7:cc:55:44:55:88",ip_address="10.100.0.51",image_file_path ="/home/qinguan/exp/kvm_img/ubuntu_1.img" ,network=2)
    print "start vm xu_test2..."
    manager().startVM("xu_test2",mac_address="b7:22:aa:44:55:66",ip_address="10.100.0.61",image_file_path ="/home/qinguan/exp/kvm_img/ubuntu_2.img" ,network=1)
    print "start vm xu_test3..."
    manager().startVM("xu_test3",mac_address="c7:22:aa:44:55:66",ip_address="10.100.0.71",image_file_path ="/home/qinguan/exp/kvm_img/ubuntu_3.img" ,network=1)
    print "start vm xu_test4..."
    manager().startVM("xu_test4",mac_address="d7:22:aa:44:55:66",ip_address="10.100.0.72",image_file_path ="/home/qinguan/exp/kvm_img/ubuntu_4.img" ,network=1)

def start_test_3():
    destory_test()
    print "start vm xu_test1..."
    manager().startVM("xu_test1",mac_address="a7:cc:55:44:55:88",ip_address="10.100.0.61",image_file_path ="/home/qinguan/exp/kvm_img/ubuntu_1.img" ,network=1)
    print "start vm xu_test2..."
    manager().startVM("xu_test2",mac_address="b7:22:aa:44:55:66",ip_address="10.100.0.62",image_file_path ="/home/qinguan/exp/kvm_img/ubuntu_2.img" ,network=1)
    print "start vm xu_test3..."
    manager().startVM("xu_test3",mac_address="c7:22:aa:44:55:66",ip_address="10.100.0.52",image_file_path ="/home/qinguan/exp/kvm_img/ubuntu_3.img" ,network=0)
    print "start vm xu_test4..."
    manager().startVM("xu_test4",mac_address="d7:22:aa:44:55:66",ip_address="10.100.0.53",image_file_path ="/home/qinguan/exp/kvm_img/ubuntu_4.img" ,network=0)
    
def destory_test():
    vms = exe_command("virsh list")
    if len(vms)>3:
        os.system("virsh destroy xu_test1")
        os.system("virsh destroy xu_test2")
        os.system("virsh destroy xu_test3")
        os.system("virsh destroy xu_test4")
        time.sleep(5)
    else:
        pass
    
#start_test()
destory_test()

def exe_command(command):
    pipe=os.popen(command,"r")
    result=pipe.readlines()
    pipe.close()
    return result

def cmd_list():
    print "cmd list:"
    print "1->list Virtual machine"
    print "2->start Virtual machine"
    print "3->destroy Virtual machine"
    print "4->suspend Virtual machine"
    print "5->resume Virtual machine"
    #print "6->reboot Virtual machine"
    print "7->boot 4 VMs with 1 VT-d ,1 SR-IOV and 2 Virtio."
    print "8->boot 4 VMs with 1 VT-d and 3 SR-IOV."
    print "9->boot 4 VMs with 2 SR-IOV and 2 Virtio."
    print "0->quit the system"
    print "please input the number!!!"
    
def start_vm():
    vm_name = raw_input("please input the Virtual machine's name:").strip()
    ip_address = raw_input("please input the Virtual machine's IP:").strip()
    mac_address = raw_input("please input the Virtual machine's MAC:").strip()
    image_file_path = raw_input("please input the Virtual machine's image file path:").strip()
    print "please input the Virtual machine's network:"
    network= int(raw_input("2->VT-d,1->SR-IOV,0->virtio:").strip())
    if network== 2:
        #network = 2
        print "you choose the VT-d way to boot the VM and the VM's name is %s,VM's ip is %s" % (vm_name , ip_address)
    elif network== 1:
        print "you choose the SR-IOV way to boot the VM and the VM's name is %s,VM's ip is %s" % (vm_name , ip_address)
    else:
        print "you choose the virtio way to boot the VM and the VM's name is %s,VM's ip is %s" % (vm_name , ip_address)
    manager().startVM(vm_name,mac_address,ip_address,image_file_path,network)
    
def list_vm():
    vm_s = exe_command("virsh list")
    if len(vm_s):
        for vm in vm_s:
            print vm
    else:
        print "no virtual machine is running ."    

def print_(num):
    print num

def destroy_exit():
    destory_test()
    return()
    
def cmd_deal(parma):        
    if parma in [3,4,5,6]:
        vm_name = raw_input("please input the Virtual machine's name:").strip()
    {
        1 :lambda : list_vm(),
        2 :lambda : start_vm(),
        3 :lambda : manager().destroyVM(vm_name),
        4 :lambda : manager().suspendVM(vm_name),
        5 :lambda : manager().resumeVM(vm_name),
        6 :lambda : manager().rebootVM(vm_name),
        7 :lambda : start_test_1(),
        8 :lambda : start_test_2(),
        9 :lambda : start_test_3(),
        #0 :lambda : destroy_exit()
    }[parma]()

def user_cmd():
    manager().pre()
    manager().do_monitor()
    print "*********************************************"
    print "      iovirt-managerment system"
    print "*********************************************"
    cmd_list()
    while True:
        cmd = raw_input(">>>")
        try:
            if isinstance(int(cmd),int) and int(cmd) < 10:
                if int(cmd) == 0:
                    return
                else:
                    cmd_deal(int(cmd))
            else:
                print "please input the num listed..."
                cmd_list()
        except:
                print "please input the num listed..."
                cmd_list()
    
user_cmd()    
