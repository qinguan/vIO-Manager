import os
import commands
from xml.dom import minidom


#import pdb
#pdb.set_trace()

def exe_command(command):
    pipe=os.popen(command,"r")
    result=pipe.readlines()
    pipe.close()
    return result

def print_info(str):
    os.system('echo '+ str + ' >> /var/rails/DB_Reader_IOvirt/log/IOvirt.log')
    
# get the VM information 
# return vmdnsu: [] @(domid:name:status:uuid)
def getVMDomidNameStatusUuid():
    vmdnsu = []
    #get the VM in list
    vminfo = exe_command("virsh list")
    for elem in vminfo[2:-1]:
        vmdns = elem.split("\n")[0].split()
        getuuidcmd = "virsh domuuid " + vmdns[0]
        vmuuid = exe_command(getuuidcmd)[0].rstrip()
        vmdnsu.append((vmdns[0],vmdns[1],vmdns[2],vmuuid))
#test:        
#        print vmdns        
#        print getuuidcmd
#        print vmuuid
    #print vmdnsu 
    return vmdnsu
#getVMDomidNameStatusUuid()

#test:
#getVMInfo()

# get uuid && bsf
# input vmdnsu:[] @(domid,name,status,uuid)
# output uuidbsf :[] @(bus:slot.function,uuid,(bus,slot,function))
#        virtio :[] @domid
def getVMuuidBsf(vmdnsu):
    uuidbsf=[]
    virtio=[]
    for vm in vmdnsu:
        try:
            getxml = commands.getoutput("virsh dumpxml "+ vm[0])
            xmlstr = minidom.parseString(getxml)
            if xmlstr.getElementsByTagName("hostdev"):
                #vt-d or sriov
                hostdev = xmlstr.getElementsByTagName("hostdev")[0].childNodes[1]
                source = hostdev.childNodes[1]
                #get the bus:slot.function
                address = (source.getAttribute('bus'),source.getAttribute('slot'),source.getAttribute('function'))
                bsfTostr = address[0].split("0x")[-1]+":"+address[1].split("0x")[-1]+"."+address[2].split("0x")[-1]
                #add the (bsfTostr,uuid,(bus,slot,function)) to uuidbsf
                uuidbsf.append((bsfTostr,vm[3],address))
                #print bsfTostr
            else:
                #virtio
                interface = xmlstr.getElementsByTagName("interface")[0]
                interfacexml = minidom.parseString(interface.toxml())
                model = interfacexml.getElementsByTagName('model')
                #print model[0].getAttribute('type')
                virtio.append(vm[0])
        except:
            #print "getVMuuidBsf failed ."
            print_info("getVMuuidBsf failed .")
            
    #print uuidbsf,virtio
    return uuidbsf,virtio 
#test:    
#getVMuuidBsf(getVMDomidNameStatusUuid())
#getVMuuidBsf([('1','virtio','running','a8ac03dc-0310-de3b-4709-307fa146ab33')])

# get domid && bsf
# input:vmdnsu []@(domid:name:status:uuid),uuidbsf []@(bus:slot.function,uuid,(bus,slot,function))
# output: domidbsf:[]@(domid,bus:slot.function)
def getDomidBsf(vmdnsu,uuidbsf):
    domidbsf = []
    for elem1 in vmdnsu:
        for elem2 in uuidbsf:
            if elem1[3] == elem2[1]:
                domidbsf.append((elem1[0],elem2[0]))
    return domidbsf


# get the relationship PF & VF,namely, VFs <== PF
# input : pfbsfused:@(bus:slot.function)
# return :pf_owned_vfs:[]@(domain:bus:slot.function)
def getPFOwnVFs(pfbsfused):
    pf_owned_vfs = []
    for pf in pfbsfused:
        bus = pf.split(":")[0]
        slot = pf.split(":")[1].split(".")[0]
        function = pf.split(":")[1].split(".")[1]
        getxml = commands.getoutput("virsh nodedev-dumpxml pci_0000_"+bus+"_"+slot+"_"+function)
#        print getxml
        xmlstr = minidom.parseString(getxml)
        #dbsf_address = <address domain='0x0000' bus='0x02' slot='0x10' function='0x1'/>
        dbsf_address = xmlstr.getElementsByTagName("address")
        vfs = []        
        for elem in dbsf_address:
            # vf=(domain,bus,slot,function)
            vf = (elem.getAttribute("domain"),elem.getAttribute("bus"),elem.getAttribute("slot"),elem.getAttribute("function"))
            #vf_to_str1 = (domain:bus:slot.function)            
            #vf_to_str = vf[0].split("0x")[1]+":"+vf[1].split("0x")[1]+":"+vf[2].split("0x")[1]+"."+vf[3].split("0x")[1]      
            #vf_to_str1 = (bus:slot.function)                   
            vf_to_str = vf[1].split("0x")[1]+":"+vf[2].split("0x")[1]+"."+vf[3].split("0x")[1]      
            vfs.append(vf_to_str)
#        print vfs
        pf_owned_vfs.append((pf,vfs))
#    print pf_owned_vfs
    return pf_owned_vfs
#test:
#pfbsfuesd = ["01:00.0","01:00.1"]
#getPFOwnVFs(pfbsfuesd)

# input : pfbsfused:@(bus:slot.function)
# output : pfbsfnotused:@(bus:slot.function)
def getPFSupportNotUsed(pfbsfused):
    pfbsfnotused = []
    for elem in pfbsfused:
        bus = elem.split(":")[0]
        slot = elem.split(":")[1].split(".")[0]
        function = elem.split(":")[1].split(".")[1]
        try:
            getxml = commands.getoutput("virsh nodedev-dumpxml pci_0000_"+ bus+"_"+slot+"_"+function)
            xmlstr = minidom.parseString(getxml)
            if xmlstr.getElementsByTagName("address"):
                continue
            else:
                pfbsfnotused.append(elem)
        except:
            #print "get FP support not used failed."
            print_info("get FP support not used failed.")
    return pfbsfnotused
#test:    
#pfbsfused = ["01:00.0","01:00.1"]
#a = getPFSupportNotUsed(pfbsfused)
#print a 

        
        
        
        
        