from domain import *
from nicInfoHand import *

"""
import pdb
pdb.set_trace()
"""
# make the vm configure xml file
# input : hostname:@ the vm name showed in virsh list
#         sourcefile:@the image file location ->/home/qinguan/ubuntu.img
#         network:@ 0->virtio , 1->vt_d, 2-> sriov
#         memory:@ the VM's memory
#         passwd:
# output: a xml file define a VM
def makeVMConfigureXML(hostname,sourcefile,network=0,memory=524288,passwd=""):
    try:
        #<input type='mouse' bus='ps2'/>
        inputDevice = InputDevice()

        #<disk type='file' device='disk'>
        #      <source file='/var/civic/vmc/vmi/kvm/developer.img'/>
        #      <target dev='hda' bus='virtio'/>
        #</disk>
        diskDevice = DiskXml("file","disk")
        diskDevice.setTarget('vda','virtio')
        diskDevice.setSource(sourcefile)

        #<emulator>/usr/bin/kvm</emulator>
        emulator = EmulatorXml("/usr/bin/kvm")        

        #print "kkk1"
        #<graphics type='vnc' port='-1' listen='127.0.0.1'/>
        graphicalFramebuffer = GraphicalFramebuffer("vnc")
        graphicalFramebuffer.setPort("-1")
        graphicalFramebuffer.setListen("0.0.0.0")
        graphicalFramebuffer.setPassword(passwd)

        #<hostdev mode='subsystem' type='pci' managed='yes'>
        #	<source>
        #		<address bus='0x2' slot='0x10' function='0x1'/>
        #	</source>
        #</hostdev>
        #print "kkk1.5"
        hostdevPciXml = HostdevNicXml()
        #print "kkk1.6"
        #network =0 ->virtio,1->vf,2->vt-d 	or not give the network
        if network == 0:
             #print "kkk1.7"
            networkInterface = NetworkInterfaceXml()
            devices = [inputDevice,diskDevice,emulator,graphicalFramebuffer,networkInterface]
            #read the PF bsf for virtio,all VM start with virtio append to the firsh PF
            #pf_available = queryAllNicNotUsed(db[1],1)
            #bsf = pf_available[0][1]
            #appentVirtioVMtoPF(db,bsf)
        elif network == 1:
             #vf@01:00.0  <- query from db
            vf_available = queryAllNicNotUsed(db[1],0)
            if len(vf_available) :
                vf_bsf = vf_available[0][1]
                setNicUsedByVM(db,vf_bsf)
                hostdevPciXml.setSource(vf_bsf.split(":")[0],vf_bsf.split(":")[1].split(".")[0],vf_bsf.split(".")[1])
                devices = [inputDevice,diskDevice,emulator,graphicalFramebuffer,hostdevPciXml]
                print "assign a VF to the Virtual Machine ..."
                print_info("assign a VF to the Virtual Machine ...")
            else:
                print "no available VF can be assigned ."
                print_info("no available VF can be assigned .")
                networkInterface = NetworkInterfaceXml()
                devices = [inputDevice,diskDevice,emulator,graphicalFramebuffer,networkInterface]
                print "assign a virtio Nic to the Virtual Machine ."
                print_info("assign a virtio Nic to the Virtual Machine .")
        else:
            #pf@0:19.0   <-query from db
            pf_available = queryAllNicNotUsed(db[1],1)
            if len(pf_available) > 1 :
#            if len(pf_available) :
                pf_bsf = pf_available[1][1] # select the second PF to assign to VM 
                setNicUsedByVM(db,pf_bsf)
                hostdevPciXml.setSource(pf_bsf.split(":")[0],pf_bsf.split(":")[1].split(".")[0],pf_bsf.split(".")[1])         
                devices = [inputDevice,diskDevice,emulator,graphicalFramebuffer,hostdevPciXml]
                print "assign a PF to the Virtual Machine ..."
                print_info("assign a PF to the Virtual Machine ...")
            else:
                print "no available PF can be assigned ."
                print_info("no available PF can be assigned .")
                #vf@01:00.0  <- query from db
                vf_available = queryAllNicNotUsed(db[1],0)
                if len(vf_available) :
                    vf_bsf = vf_available[0][1]
                    setNicUsedByVM(db,vf_bsf)
                    hostdevPciXml.setSource(vf_bsf.split(":")[0],vf_bsf.split(":")[1].split(".")[0],vf_bsf.split(".")[1])
                    devices = [inputDevice,diskDevice,emulator,graphicalFramebuffer,hostdevPciXml]
                    print "assign a VF to the Virtual Machine ..."
                    print_info("assign a VF to the Virtual Machine ...")
                else:
                    #print "no available VF can be assigned ."
                    print_info("no available VF can be assigned .")
                    networkInterface = NetworkInterfaceXml()
                    devices = [inputDevice,diskDevice,emulator,graphicalFramebuffer,networkInterface]
                    #print "assign a virtio Nic to the Virtual Machine ..."
                    print_info("assign a virtio Nic to the Virtual Machine ...")
        
        #print "kkk2"
        domain = DomainXml("kvm",hostname)

        #<memory>524288</memory>
        #<currentMemory>524288</currentMemory>
        domain.setBasicResources(memory,memory)    

        #setLifecycleControl (self,on_poweroff,on_reboot,on_crash)
        #<on_poweroff>destroy</on_poweroff>
        #<on_reboot>restart</on_reboot>
        #<on_crash>destroy</on_crash>
        domain.setLifecycleControl("destroy","restart","destroy")

        #<features><pae/><acpi/><apic/></features>
        #domain.setFeatures();

        #set clock
        #<clock offset='utc'/>
        domain.setClock("utc")       

        #print "kkk3"
        domain.setDevices(devices)    
        #print "kkk4"

        #domain xml for vm
        domainXML = domain.toXml()
        return domainXML
    except Exception,e:
        print_info("make libvirt XML failed.")
        return "make libvirt XML failed."
    
#test:
#print makeVMConfigureXML("xu","/home/qinguan/exp/kvm/ubuntu_1.img",0)


def saveXmlToFile(xml,path,filename):
    '''write xml information to a file'''
    try:
        if not os.path.exists(path):
            os.mkdir(path)
        if not os.path.exists(path+filename+".xml"):
            os.system("touch "+path+filename+".xml")
        file = open(path+filename+".xml","w")
        file.write(xml)
        file.close()
    except OSError,e:
        print "create file or make directory error . "
        print_info("create file or make directory error . ")
        file.close()
        return -1
    except IOError,e:
        print "create file or make directory error ."
        print_info("create file or make directory error . ")
        file.close()
        return -2
    return 0