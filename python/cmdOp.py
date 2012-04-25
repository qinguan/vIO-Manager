from hwDetect import *
from nicInfoHand import *
from createVF import *
from threading import Timer
import thread
import time

#import pdb
#pdb.set_trace()



# connect the database
# input: path: "mysql://root@127.0.0.1/xu_test" default,
#        table: "xgj_nics" default
# return: db@(engine,usedTable)
#db = connect(path="mysql://root@127.0.0.1/xu_test",table="xgj_nics")

#--------------------------------------------------------------------------------#
#detect the hardware in the machine
#--------------------------------------------------------------------------------#
# input  :db@(engine,usedTable)
# output :pf_nic_bsf_address:[]@(bus:slot.function,name,type)
#         sriov_nic_info:the nic whether support sr-iov
def hw_detect(db):
    #delete all infomation in db first
    db[1].delete().execute()
    
    # detect the cpu whether support vt
    # return :True if support
    is_vt_support = cpuDetect()
    
    # count the num of nic
    # output:the number of nics
    nic_num = nicDetect()
    
    # detect the nic whether support sr-iov
    # output:{}@"sriov82576Num":num/"sriov82599Num":num
    sriov_nic_info = nicSriovDetect()
    
    # get the nic pci address
    # return PFNicBsfAddress:[]@(bus:slot.function,name,type)
    pf_nic_bsf_address = getPFNicBsfAddress()
    
    # get bus:slot.function && mac address
    # input:cmd:"ls /sys/class/net" default
    # output:bsf_mac_address:[]@(bus:slot.function,macaddress)
    bsf_mac_address = getBsfMacAddress()
        
    # insert the PF 
    # input:usedTable@db[1],
    #       nic_bsf_address:[] @(bus:slot.function,name,nictype,used)
    # PF
    nicBsfNameNictypeUsedInsert(db[1],pf_nic_bsf_address)
    
    # insert the PF's macaddress
    # input :db@(engine,usedTable),
    #        bsf_mac_address:[]@(bus:slot.function,macaddress)
    macAddressInsert(db,bsf_mac_address)
    
    return pf_nic_bsf_address,sriov_nic_info
#test:
#q = hw_detect(db)    


#--------------------------------------------------------------------------------#
#create VF by the supported nic:82576 0r 82599
#--------------------------------------------------------------------------------#
# input: db@(engine,usedTable),
#        pf_nic_bsf_address,
#        sriov_nic_info,param=1,
#        param=1,0 create by 82576,1 create by 82599 , 2 create by 82576 and 82599
#        igb_max_vfs=4,
#        ixgbe_max_vfs=4
def virtIO(db,pf_nic_bsf_address,sriov_nic_info,param=1,igb_max_vfs=4,ixgbe_max_vfs=4):   
    # create the VF function to support sriov and set the corresponding PF:used=1
    # input:PFNicBsfAddress:[]@(bus:slot.function,name/82576 or 82599,nictype),
    #       sriovNicInfo:{}@"sriov82576Num":num/"sriov82599Num":num,
    #       param: 0 create by 82576,1 create by 82599 , 2 create by 82576 and 82599
    #       igb_max_vfs:1 default , 1~7 available,
    #       ixgbe_max_vfs:1 default ,1-63 available ,
    pfbsfused = createNicVirtualFunction(pf_nic_bsf_address,sriov_nic_info,param,igb_max_vfs,ixgbe_max_vfs)
    
    # set the corresponding PF creating VFs : used=1
    # input:db:@(engine,usedTable)
    #       pfbsfused:[]@bus:slot.function
    setPFNicUsed(db,pfbsfused)
    
    pfbsfnotused = getPFSupportNotUsed(pfbsfused)
    setPFNicNotUsed(db,pfbsfnotused)
    
    # get the VF info after create VirtualFunction
    # return:VFNicBsfAddress:[]@(bus:slot.function,name/82576 or 82599,nictype)
    vf_nic_bsf_address = getVFNicBsfAddress()
    
    # insert the VF 
    # input:usedTable@db[1],
    #       nic_bsf_address:[] @(bus:slot.function,name,nictype,used)
    # VF
    nicBsfNameNictypeUsedInsert(db[1],vf_nic_bsf_address)
    
    # get the relationship PF & VF,namely, VFs <== PF
    # input : pfbsfused:@(bus:slot.function)
    # return :pf_owned_vfs:[]@(domain:bus:slot.function)
    pf_owned_vfs = getPFOwnVFs(pfbsfused)
    
    # set the relationships between PF & VF in db
    # input : db :@connect(path,table)
    #         pf_owned_vfs:[]@[pf@"bus:slot.function":vfs@["bus:slot.function",,,],,,]
    setPFandVFRelation(db,pf_owned_vfs)
    
    
#test:
#virtIO(db,q[3],q[2])

#--------------------------------------------------------------------------------#
#update the info in db about VM corresponding nic:(domid,bsf)
#--------------------------------------------------------------------------------#
# input: db@(engine,usedTable)-->global var in nicInfoHand.py file
def vmdb_update():
    # get the VM information 
    # return vmdnsu: [] @(domid:name:status:uuid)
    vmdnsu = getVMDomidNameStatusUuid()
    
    # get uuid && bsf
    # input vmdnsu:[] @(domid:name:status:uuid)
    # output uuidbsf :[] @(bus:slot.function,uuid,(bus,slot,function))
    #        virtio:[]domid
    uuid_bsf,virtio_vmdomid = getVMuuidBsf(vmdnsu)
    
    # get domid && bsf
    # input:vmdnsu []@(domid:name:status:uuid),uuidbsf []@(bus:slot.function,uuid,(bus,slot,function))
    # output: vmdomidbsf:[]@(domid,bus:slot.function)
    vmdomidbsf = getDomidBsf(vmdnsu,uuid_bsf)
        
    # update the record that the bsf's corresponding Domid after destory a VM or start a VM
    # input:db@(engine,usedTable),vmdomidbsf:[]@(bus:slot.function)
    vmDomidBsfupdate(db,vmdomidbsf)
    #print vmdnsu,uuid_bsf,vmdomidbsf
    
    vmVirtioVMupdate(db_virtio,virtio_vmdomid)
    #print virtio_vmdomid
 
#test:
#vmdb_update()

#--------------------------------------------------------------------------------#
# queryNIc
#--------------------------------------------------------------------------------#
# query  all nic :param=1
# input:usedTable/connect(path,table)[1]
# return:[]@(id,bsfaddress,name,nictype,used,vswitch_id,virtual_machine_instance_id,macaddress,netmask,gateway)
#queryNicInfoAll(db[1])

# query all Nics are used now :param=2
# input:usedTable/connect(path,table)[1]
# output:[]@(id,bsfaddress,name,nictype,used,vswitch_id,virtual_machine_instance_id,macaddress,netmask,gateway)
#queryAllNicUsed(db[1])

# query the nic by bsfAdresss:@bus:slot.function :param=3
# input:usedTable/connect(path,table)[1],bsfAddress@bus:slot.function
# output:@(id,bsfaddress,name,nictype,used,vswitch_id,virtual_machine_instance_id,macaddress,netmask,gateway)
#queryNicInfoByBsf(db[1],bsfAddress)

# query all the nic Nic can be assigned: param=4 
# input :usedTable/connect(path,table)[1]
#        vf_or_pf: 0 get VFs ;1 get PFs
# output:[]@(id,bsfaddress,name,nictype,used,vswitch_id,virtual_machine_instance_id,macaddress,netmask,gateway)
#queryAllNicNotUsed(db[1],vf_or_pf)

def queryNic(parma,vf_or_pf=0,bsfAddress=None):
    result = {
        1 :lambda : queryNicInfoAll(db[1]),
        2 :lambda : queryAllNicUsed(db[1]),
        3 :lambda : queryNicInfoByBsf(db[1],bsfAddress),
        4 :lambda : queryAllNicNotUsed(db[1],vf_or_pf)
    }[parma]()
    print result

#test:
#queryNic(4,0)

def monitor():
    while(1):
        Timer(5,vmdb_update,()).start()
        time.sleep(5)


