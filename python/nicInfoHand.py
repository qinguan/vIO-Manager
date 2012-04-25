from sqlalchemy import *
from virshTool import *
from sqlalchemy.engine import *

        
def print_info(str):
    os.system('echo '+ str + ' >> /var/rails/DB_Reader_IOvirt/log/IOvirt.log')
    
# connect the database
# input: path: "mysql://root@127.0.0.1/xu_test" default,
#        table: "xgj_nics" default
# return: db@(engine,usedTable)
def connect(path="mysql://root@127.0.0.1/iovirt",table="nics"):
    try:
        engine = create_engine(path)
        #print "connect the database successfully. "
    except:        
        print "failed to connect the database."
        print_info("failed to connect the database.")
    meta = MetaData(engine)
    try:
        usedTable = Table(table,meta,autoload=True)     
        #print "table :"+ table +" loaded successfully."
        return engine,usedTable
    except:
        print "failed to load the table '" + table + "' ."
        print_info("failed to load the table '" + table + "' .")
db = connect(path="mysql://root@127.0.0.1/iovirt",table="nics")
db_virtio = connect(path="mysql://root@127.0.0.1/iovirt",table="virtios")
#test:        
#t = connect()
#print t[0],t[1]

# insert the PF & VF 
# nicBsfAddress:[] @(bus:slot.function,name,nictype,used)
def nicBsfNameNictypeUsedInsert(usedTable,nicBsfAddress):
    try:
        i = usedTable.insert()
        for element in nicBsfAddress:    
            i.execute(bsf_address = element[0],name = element[1],nic_type = element[2],used = 0,virtual_machine_instance_id = -1)  
            #print "insert the nic "+ element[0]+" successfully ."
            print_info("insert the nic "+ element[0]+" successfully .")
        #print "insert the nic_address@(bus:slot.function,name,nictype,used) successfully . "
    except:
        #print "failed insert the nicaddress ."
        print_info("failed insert the nicaddress .")
        

#test:
#nicBsfNameNictypeUsedInsert(t[1],hd.VFNicBsfAddress)

# set the corresponding PF creating VFs : used=1
# input:db:@(engine,usedTable)
#       pfbsfused:[]@bus:slot.function
def setPFNicUsed(db,pfbsfused):
    #print pfbsfused
    # set the PF used=1 in the database
    if len(pfbsfused):
        for elem in pfbsfused:
            #print elem
            try:
                upd = db[1].update().where(db[1].c.bsf_address == elem).values({db[1].c.used : 1})
                db[0].execute(upd)
                #print "set " + elem + " used to 1"
                print_info("set " + elem + " used to 1")
            except:
                #print "failed to set the PF used to 1"
                print_info("failed to set the PF used to 1")
                
# consider the case "modprobe igb_max_vfs=3,0"
# need set some multiple NIC port's used=0
# 
def setPFNicNotUsed(db,pfbsfnotused):
    if len(pfbsfnotused):
        for elem in pfbsfnotused:
            try:
                upd = db[1].update().where(db[1].c.bsf_address == elem).values({db[1].c.used : 0})
                db[0].execute(upd)
                #print "set " + elem + " used to 0"
                print_info("set " + elem + " used to 0")
            except:
                #print "failed to set the PF used to 0"
                print_info("failed to set the PF used to 0")
                
# when assign a nic to vm ,just set the used=1 ,and virtual_machine_instance_id may be update by the function update()
# input : db@
#         bsf_address@
def setNicUsedByVM(db,bsf_address):
    if bsf_address:
        try:
            upd = db[1].update().where(db[1].c.bsf_address == bsf_address).values({db[1].c.used : 1})
            db[0].execute(upd)
            #print "set " + bsf_address + " used to 1 ."
            print_info("set " + bsf_address + " used to 1 .")
        except:
            #print "failed to set the Nic used to 1 ."
            print_info("failed to set the Nic used to 1 .")
            
                
# insert the PF's macaddress
# input :db@(engine,usedTable),macaddress:[]@(bus:slot.function,macaddress)
def macAddressInsert(db,bsfMacAddress):
    try:
        for elem in bsfMacAddress:
            #print elem
            print_info(elem[0])
            print_info(elem[1])
            try:
                # update the macaddress value for PF
                upd = db[1].update().where(db[1].c.bsf_address == elem[0]).values({db[1].c.mac_address : elem[1]})
                db[0].execute(upd)    
                #print "insert the bsf:"+elem[0]+" corresponding mac address:"+elem[1]+" successfully ."
                print_info("insert the bsf:"+elem[0]+" corresponding mac address:"+elem[1]+" successfully .")
            except:
                #print "failed to update the macaddress"      
                print_info("failed to update the macaddress.")
    except:
        #print "no available mac address need insert . "
        print_info("no available mac address need insert . ")
        

#test:            
#macAddressInsert(t,hd.bsf_macAddress)

# insert the VMdomid corresponding the nic (PF & VF)
# input:db@(engine,usedTable),vmdomidbsf:[]@(domid,bus:slot.function)
def vmDomidBsfInsert(db,vmdomidbsf):
    for elem in vmdomidbsf:
        print elem
        try:
            upd = db[1].update().where(db[1].c.bsf_address == elem[1]).values({db[1].c.virtual_machine_instance_id : elem[0],db[1].c.used: 1}) 
            db[0].execute(upd)
            #print "vmdomid insert successfully . "
            print_info("vmdomid insert successfully . ")
        except:
            #print "failed to insert the virtual_machine_instance_id."
            print_info("failed to insert the virtual_machine_instance_id.")

#test:            
#vmdnsu = getVMDomidNameStatusUuid()
#print vmdnsu
#vmuuidbsf = getVMuuidBsf(vmdnsu)
#print vmuuidbsf
#vmdomidbsf = getDomidBsf(vmdnsu,vmuuidbsf)
#print vmdomidbsf


# update the record that the bsf's corresponding Domid after destory a VM or start a VM
# input:db@(engine,usedTable),vmdomidbsf:[]@(domid,bus:slot.function)
def vmDomidBsfupdate(db,vmdomidbsf):
    try:
        sel = db[1].select(db[1].c.virtual_machine_instance_id != -1)
        result = sel.execute()
        vminfo = result.fetchall()
        vmdomidbsf_db = [(str(e[6]),(e[1])) for e in vminfo]
        vmdomidbsf_intersection = list(set(vmdomidbsf_db).intersection(set(vmdomidbsf)))
        #test:
        """
        print "vmdomidbsf_db : ",vmdomidbsf_db
        print "vmdomidbsf : " ,vmdomidbsf
        print "vmdomidbsf_intersection : ",vmdomidbsf_intersection
        """
        for elem in vmdomidbsf_db:
            if elem not in vmdomidbsf_intersection:
                upd = db[1].update().where(db[1].c.bsf_address == elem[1]).values({db[1].c.virtual_machine_instance_id : -1,db[1].c.used:0})
                db[0].execute(upd)
                print_info("the nic bsf:"+ elem[1] +" rerclaim from domid:" +elem[0] + " successfully . ")
        
        for elem in vmdomidbsf:
            if elem not in vmdomidbsf_intersection:
                upd = db[1].update().where(db[1].c.bsf_address == elem[1]).values({db[1].c.virtual_machine_instance_id : elem[0],db[1].c.used:1})
                db[0].execute(upd)                
                print_info("the nic bsf:"+ elem[1] +" assign to the domid:" + elem[0] + " successfully . ")
    except:
        print_info("failed  to update the virtual_machine_instance_id")
       
#test: 
#vmDomidBsfupdate(t,vmdomidbsf)            

#update the table virtio
def vmVirtioVMupdate(db_virtio,virtio_domid):
    try:
        sel = db_virtio[1].select()
        result = sel.execute()
        vmvirtio = result.fetchall()
        vmdomid_db = [str(e[1]) for e in vmvirtio]
        vmdomid_intersection = list(set(vmdomid_db).intersection(set(virtio_domid)))
        
        for elem in vmdomid_db:
            if elem not in vmdomid_intersection:
                upd = db_virtio[1].delete().where(db_virtio[1].c.domid == elem)
                db_virtio[0].execute(upd)
                #print "the VM:"+ elem +" using virtio has been destroyed successfully . "
                print_info("the VM:"+ elem +" using virtio has been destroyed successfully . ")
        for elem in virtio_domid:
            i = db_virtio[1].insert()
            if elem not in vmdomid_intersection:
                i.execute(domid = elem)          
                #print "the VM:"+ elem +" using virtio start successfully . "
                print_info("the VM:"+ elem +" using virtio start successfully . ")
    except:
        print_info("failed  to update the virtual_machine using virtio")

# query  all nic
# input:usedTable/connect(path,table)[1]
# return:[]@(id,bsfaddress,name,nictype,used,vswitch_id,virtual_machine_instance_id,macaddress,netmask,gateway)
def queryNicInfoAll(usedTable):
    sel = usedTable.select()
    res = sel.execute()
    return res.fetchall()
#test:
#for ele in queryNicInfoAll(db[1]):
#    print ele

# query all Nics are used now
# input:usedTable/connect(path,table)[1]
# output:[]@(id,bsfaddress,name,nictype,used,vswitch_id,virtual_machine_instance_id,macaddress,netmask,gateway)
def queryAllNicUsed(usedTable):
    sel = usedTable.select(usedTable.c.used == 1)
    res = sel.execute()
    return res.fetchall()
#test:
#for ele in queryAllNicUsed(db[1]):
#    print ele

# query the nic by bsfAdresss:@bus:slot.function
# input:usedTable/connect(path,table)[1],bsfAddress@bus:slot.function
# output:@(id,bsfaddress,name,nictype,used,vswitch_id,virtual_machine_instance_id,macaddress,netmask,gateway)
def queryNicInfoByBsf(usedTable,bsfAddress):
    sel = usedTable.select(usedTable.c.bsf_address == bsfAddress)
    res = sel.execute()
    return res.fetchone()

#test:
#print queryNicInfoByBsf(t[1],hd.bsf_macAddress[0][0])

# query all the nic NIC can be assigned
# input :usedTable/connect(path,table)[1]
#        param: 0 get VFs ;1 get PFs
# output:[]@(id,bsfaddress,name,nictype,used,vswitch_id,virtual_machine_instance_id,macaddress,netmask,gateway)
def queryAllNicNotUsed(usedTable,param):
    sel = {
        0:lambda : usedTable.select(and_(usedTable.c.nic_type == "VF" , usedTable.c.used == 0,usedTable.c.virtual_machine_instance_id == -1)),
        1:lambda : usedTable.select(and_(usedTable.c.nic_type == "PF" , usedTable.c.used == 0,usedTable.c.virtual_machine_instance_id == -1))
    }[param]()
    res = sel.execute()    
    return res.fetchall()

#test:
#db = connect(path="mysql://root@127.0.0.1/xu_test",table="xgj_nics")
#for ele in queryAllNicNotUsed(db[1],0):
#    print ele

# set the relationships between PF & VF in db
# input : db :@connect(path,table)
#         pf_owned_vfs:[]@[pf@"bus:slot.function":vfs@["bus:slot.function",,,],,,]
def setPFandVFRelation(db,pf_owned_vfs):
    for elem in pf_owned_vfs:
        try:
            for vf in elem[1]:
                #print vf
                upd = db[1].update().where(db[1].c.bsf_address == vf).values({db[1].c.vf_belongto_pf : elem[0]})
                db[0].execute(upd)
                #print "VF: "+vf + " belongs to the PF: "+elem[0]
                print_info("VF: "+vf + " belongs to the PF: "+elem[0])
        except:
            #print "failed to set the relationship between PF & VF . "
            print_info("failed to set the relationship between PF & VF . ")
#test:
#db = connect(path="mysql://root@127.0.0.1/xu_test",table="xgj_nics")
#pfbsfused = ["01:00.0","01:00.1"]
#pf_owned_vfs = getPFOwnVFs(pfbsfused)
#print pf_owned_vfs
#setPFandVFRelation(db,pf_owned_vfs)
  