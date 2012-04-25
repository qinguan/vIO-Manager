class DomainXml:
    def __init__(self,type="kvm",name=""):
        self.type =type
        self.name = name
        self.description = self.name
        self.memory = 524288
        self.currentMemory = 524288
        self.on_poweroff = "destroy"
        self.on_reboot = "restart"
        self.on_crash = "destroy"      
        self.clock = "utc"
        self.devices = []

    def setName(self,name):
        self.name = name

    def nameToXml(self):
        xml = ""
        xml += "<name>"+self.name+"</name>"
        return xml

    def setDescription(self,description):
        self.description = description

    def descriptionToXml(self):
        xml = ""
        if self.description != "":
            xml += "<description>"+self.description+"</description>"
        return xml

    def osToxml(self):
        xml = ""
        xml += "<os>"
        xml += "\n\t\t<type>hvm</type>"
        xml += "\n\t\t<boot dev='hd'/>"
        xml += "\n\t</os>"
        return xml

    def setBasicResources(self,memory,currentMemory):
        self.memory = memory
        self.currentMemory = currentMemory 	

    def basicResourcesToXml(self):
        xml = ""
        if self.memory != -1:
            xml += "<memory>"+str(self.memory)+"</memory>\n"
        if self.currentMemory != -1:
            xml += "\t<currentMemory>"+str(self.currentMemory)+"</currentMemory>"
        return xml

    def  setLifecycleControl (self,on_poweroff="destroy",on_reboot="restart",on_crash="destroy"):
        self.on_poweroff = on_poweroff
        self.on_reboot = on_reboot
        self.on_crash = on_crash

    def lifecycleControlToXml(self):
        xml = ""
        if self.on_poweroff!="":
            xml += "\n\t<on_poweroff>"+self.on_poweroff+"</on_poweroff>"
        if self.on_reboot != "":
            xml += "\n\t<on_reboot>"+self.on_reboot+"</on_reboot>"
        if self.on_crash != "":
            xml += "\n\t<on_crash>"+self.on_crash+"</on_crash>"
        return xml

    def setDevices(self,devices):
        self.devices = devices

    def featuresToXml(self):
        return "<features><pae/><acpi/><apic/></features>"

    def setClock(self,time ):
        self.clock = time

    def cloctToXml(self):
        return "<clock offset='"+self.clock+"'/>"

    def toXml(self):
        xml = ""
        xml += "<domain type='"+self.type+"'>"
        xml += "\n\t"+self.nameToXml()        
        xml += "\n\t"+self.descriptionToXml()     
        xml += "\n\t"+self.osToxml()
        xml += "\n\t"+self.basicResourcesToXml()        
        xml += "\n\t"+self.lifecycleControlToXml()        
        xml += "\n\t"+self.featuresToXml()              
        xml += "\n\t"+self.cloctToXml()
        xml += "\n\t<devices>"
        for i in range(len(self.devices)):
            xml += "\n\t\t"+self.devices[i].toXml()
        xml += "\n\t</devices>"
        xml += "\n</domain>"
        return xml

class InputDevice:
    def __init__(self,type="mouse",bus="usb"):
        self.type = type
        self.bus = bus
    def toXml(self):
        if self.bus == "":
            return "<input type='"+self.type+"' />"
        else:
            return "<input type='"+self.type+"' bus='"+self.bus+"'/>"

class DiskXml:
    def __init__(self, type="file",device="disk"):
        self.type = type
        self.source = ""
        self.target = {"dev":"hda","bus":"virtio"}
        self.device = device

    def setSource(self,file):
        self.source = file

    def sourceToXml(self):
        try:
            return "<source file='"+self.source+"'/>"
        except KeyError:
            return ""

    def setTarget(self,dev,bus):
        self.target['dev'] = dev
        self.target['bus'] = bus

    def targetToXml(self):
        try:    
            return "<target dev='"+self.target['dev']+"' bus='"+self.target['bus']+"'/>"
        except KeyError:
            return ""

    def toXml(self):
        xml = ""
        xml = "<disk type='"+self.type+"' "+"device='"+self.device+"'>"
        xml += "\n\t\t\t"+self.sourceToXml()
        xml += "\n\t\t\t"+self.targetToXml()
        xml += "\n\t\t</disk>"
        return xml
"""test:    
q = DiskXml()
q.setSource("/home/qinguan/exp/kvm_sriov/ubuntu_2.img")
q.setTarget()
print q.toXml()
""" 

class HostdevNicXml:
    def __init__(self,mode="subsystem",type="pci",managed = "yes"):
        self.mode = mode
        self.type = type
        self.managed = managed
        self.source = {}

    def setSource(self,bus,slot,function):
        self.source['bus'] = bus
        self.source['slot'] = slot
        self.source['function'] = function

    def sourceToXml(self):
        try:
            xml = ""
            xml = "<source>"
            xml += "\n\t\t\t\t<address bus = '0x" + self.source['bus']+"' slot = '0x"+ self.source['slot']+"' function = '0x" + self.source['function']+"' />"
            xml += "\n\t\t\t</source>"
            return xml
        except KeyError:
            return ""

    def toXml(self):
        xml = ""
        xml += "\n\t\t<hostdev mode='"+self.mode+"' type='"+self.type+"'"+" managed='"+"yes' >"
        xml += "\n\t\t\t"+ self.sourceToXml()
        xml += "\n\t\t</hostdev>"
        return xml

class NetworkInterfaceXml:
    def __init__(self,type="network",source="default",model="virtio"):
        self.type = type
        self.source = source
        self.model = model

    def setSource(self,network="default"):
        self.source['network'] = network

    def sourceToXml(self):
        type = self.type
        return  "<source network='"+self.source+"'/>"

    def setModel(self,type="virtio"):
        self.model['type']=type

    def modelToXml(self):
        return "<model type='"+self.model+"'/>"

    def toXml(self):
        xml = ""
        xml = "<interface type='"+self.type+"'>"
        xml += "\n\t\t\t" + self.sourceToXml()
        xml += "\n\t\t\t" + self.modelToXml()		
        xml += "\n\t\t</interface>"
        return xml
#test:
#q = NetworkInterfaceXml()
#print q.toXml()

class EmulatorXml:
    def __init__(self,path="/usr/bin/kvm"):
        self.path = path
    def toXml(self):
        xml = ""
        xml = "<emulator>"+self.path+"</emulator>"
        return xml
"""test
q = EmulatorXml()
print q.toXml()
"""    
class GraphicalFramebuffer:
    def __init__(self,type="vnc"):
        self.type = type
        self.autoport = 0
        self.port = "-1"
        self.listen = "0.0.0.0"
        self.password = ""
    def setAutoport(self):
        self.autoport = 1
    def setPort(self,port="-1"):
        self.port = port
    def setListen(self,listen="0.0.0.0"):
        self.listen = listen
    def setPassword(self,password):
        self.password = password

    def toXml(self):
        xml = ""
        xml = "<graphics type='"+self.type+"' "
        if self.autoport == 1:
            xml += " autoport "
        elif self.port != "" :
            xml += " port='"+self.port+"' "
        if self.listen != "":
            xml += " listen='"+self.listen+"' "
        if self.password != "":
            xml += " passwd='"+self.password+"' "
        xml += " />"
        return xml
"""test:    
q = GraphicalFramebuffer()
print q.toXml()
"""

class DevicesXml:
    def __init__(self):
        self.devices = []
    def addDevice(self,device):
        self.devices.append(device)
    def toXml(self):
        xml = ""
        for i in range (len(self.devices)):
            xml += self.devices[i].toXml()+"\n"
        return xml

"""
q= DomainXml(name="xu")
a = DevicesXml()
b = InputDevice()
c = DiskXml()
c.setSource("C:/xu")
d = EmulatorXml()
e = GraphicalFramebuffer()
f = HostdevNicXml()
f.setSource("00","19","0")
#print c.toXml()
#print d.toXml()
#print e.toXml()
q.setDevices([b,c,d,e,f])
print q.toXml()
"""