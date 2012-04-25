import os
import commands
import time
import re 
"""
import pdb
pdb.set_trace()
"""

def exe_command(command):
    pipe=os.popen(command,"r")
    result=pipe.readlines()
    pipe.close()
    return result

def print_info(str):
    os.system('echo '+ str + ' >> /var/rails/DB_Reader_IOvirt/log/IOvirt.log')
    
# add the fixed mac and ip to the image
# input : file_path:@/mnt/etc/init.d/rc.local
#         mac_address:@AA:BB:CC:DD:EE:FF
#         ip_address:@192.168.1.187
def addIPMacAddressToImage(file_path,mac_address,ip_address):
    if not os.path.exists(file_path):
        #print file_path + " not exist . "
        print_info(file_path + " not exist . ")
        return
    
    eth0_down = commands.getstatusoutput("echo 'sudo ifconfig eth0 down' >> " + file_path)
    hw_ether = commands.getstatusoutput("echo 'sudo ifconfig eth0 hw ether "+mac_address+" ' >> "+file_path)       
    ip_add = commands.getstatusoutput("echo 'sudo ifconfig eth0 "+ip_address +" '>>"+file_path)        
    eth0_up = commands.getstatusoutput("echo 'sudo ifconfig eth0 up'>>"+file_path)
    
    result = int(eth0_down[0]) + int(hw_ether[0]) + int(ip_add[0]) + int(eth0_up[0])
    if not result:
        #print "echo 'sudo ifconfig eth0 down' >> " + file_path
        print_info("echo 'sudo ifconfig eth0 down' >> " + file_path)
        #print "echo 'sudo ifconfig eth0 hw ether "+mac_address+" ' >> "+file_path        
        print_info("echo 'sudo ifconfig eth0 hw ether "+mac_address+" ' >> "+file_path)
        #print "echo 'sudo ifconfig eth0 "+ip_address +" '>>"+file_path       
        print_info("echo 'sudo ifconfig eth0 "+ip_address +" '>>"+file_path)
        #print "echo 'sudo ifconfig eth0 up'>>"+file_path
        print_info("echo 'sudo ifconfig eth0 up'>>"+file_path)
        #print "add ip and mac address to the image successfully ."
        print_info("add ip and mac address to the image successfully .")
    else:
        #print "add the fixed mac and ip to the image failed ." 
        print_info("add the fixed mac and ip to the image failed ." )
    #os.system("tail -10 "+ file_path)
    os.system("tail -10 "+ file_path + " >> /var/rails/DB_Reader_IOvirt/log/IOvirt.log ")

        
#test:
#addIPMacAddress("/home/qinguan/temp","11:22:33:44:55:66","192.168.1.198")


# if use VT-d,make the ethX to eth0 in order to configure ip and mac
# if use sr-iov ,eth ethX appears as eth0 and shouldn't modify
def makeEthxToEth0(udev_rules_path,mac_address):
    cmd = "ls "+udev_rules_path
    #print cmd
    result = exe_command(cmd)
    for elem in result:
        if re.findall("-net.rules$",elem):            
            # if exist the net rules file , make it unable
            rm_cmd = "rm "+udev_rules_path + elem.rstrip()
            if commands.getstatusoutput(rm_cmd)[0] == 0:
                #print rm_cmd + " successfully ."
                print_info(rm_cmd + " successfully .")
            else:
                #print  rm_cmd + " failed . "                    
                print_info(rm_cmd + " failed . ")
    
    # create new net rules by create a new file 70-net-new.rules under /etc/udev/rules.d/
    if os.path.exists(udev_rules_path+"70-net-new.rules"):
        os.system("rm "+ udev_rules_path + "70-net-new.rules")
        #print "rm the old file "+ udev_rules_path + "70-net-new.rules"
        print_info("rm the old file "+ udev_rules_path + "70-net-new.rules")
"""
    create_cmd = "touch "+ udev_rules_path+"70-net-new.rules"
    if commands.getstatusoutput(create_cmd)[0] == 0:
        print create_cmd + " successfully ."
    else:    
        print "create new file 70-net-new.rules failed . "

    # the rule make fixd mac_address bind to the 'eth0'
    udev_rule = "SUBSYSTEM=='net', ACTION=='add', DRIVERS=='?*',ATTR{address}=='"+mac_address+"',KERNEL=='eth*',NAME='eth0'"

    # the command that wirte the rule into the rules file
    add_udev_rule_cmd = "echo \""+udev_rule+"\" >> " +udev_rules_path + "70-net-new.rules"

    # add the new rule to the rules.d directory
    #commands.getstatusoutput(add_udev_rule_cmd)
    print add_udev_rule_cmd + " successfully ." 
    print "make fixd mac_address bind to the 'eth0' failed ."
"""    
#test:
#makeEthXToeth0("/etc/udev/rules.d/","11:22:33:44:55:66")
    
def DeleteIpMacInFile(file_path):
    if commands.getstatusoutput("mv "+file_path+" "+ file_path+".blk")[0] == 0:
        #print "mv "+file_path+" "+ file_path+".blk successfully ." 
        print_info("mv "+file_path+" "+ file_path+".blk successfully ." )
    if commands.getstatusoutput("touch "+file_path)[0] ==  0:
        #print "touch "+file_path+" successfully ."
        print_info("touch "+file_path+" successfully .")
        fpout = open(file_path+".blk",'r')
        fpin = open(file_path,'w')
        res = fpout.readlines()
        for eachline in res:
            if re.match("^sudo ifconfig eth0",eachline):
                continue
            else:
                fpin.write(eachline)
        if commands.getstatusoutput("chmod +x "+ file_path)[0] != 0:
            #print "chmod +x "+ file_path+ " failed ."
            print_info("chmod +x "+ file_path+ " failed .")
        fpout.close()
        fpin.close()
    else:
        if commands.getstatusoutput("mv "+file_path+".blk"+" "+ file_path)[0] == 0:
            #print "mv "+file_path+".blk"+" "+ file_path
            print_info("mv "+file_path+".blk"+" "+ file_path)
#test:
#DeleteIpMacInFile("/home/qinguan/test")
                

# modify the Image's network configure/mac_address & ip_address
# input: image_file_path:@the absolute path of the image
#         flag = 1 use VT-d and 0 use SR-IOV
def modifyImage(image_file_path,flag,mac_address,ip_address):
    try:
        # make sure no process use the nbd  first or may result a fatal fault
        if (commands.getoutput("lsmod | grep nbd")):
            commands.getstatusoutput("rmmod nbd")
            #print "rmmod nbd successfully ."
            print_info("rmmod nbd successfully .")

        if commands.getstatusoutput("modprobe nbd max_part=4")[0] == 0:
            #print "modprobe nbd max_part=4 successfully . "
            print_info("modprobe nbd max_part=4 successfully . ")
        else:
            #print "modprobe nbd max_part=4 failed ."
            print_info("modprobe nbd max_part=4 failed .")
            return 0
          
        
        if commands.getstatusoutput("kvm-nbd --connect=/dev/nbd4 " + image_file_path)[0] == 0: 
            #print "kvm-nbd --connect=/dev/nbd4 " + image_file_path + " successfully ."
            print_info("kvm-nbd --connect=/dev/nbd4 " + image_file_path + " successfully .")
        else:
            #print "kvm-nbd --disconnect /dev/nbd4 "
            print_info("kvm-nbd --disconnect /dev/nbd4 ")
            return 0
        
        time.sleep(2)
        
        if commands.getstatusoutput("sudo mount /dev/nbd4p1 /mnt")[0] == 0:
            #print "mount /dev/nbd4p1 /mnt successfully ."
            print_info("mount /dev/nbd4p1 /mnt successfully .")
        else:
            #print "mount /dev/nbd4p1 /mnt failed ."
            print_info("mount /dev/nbd4p1 /mnt failed .")
            #print commands.getstatusoutput("umount /mnt")
            print_info(commands.getstatusoutput("umount /mnt"))
            return 0

        if flag == 1:
            #VT-d
            DeleteIpMacInFile("/mnt/etc/init.d/rc.local")
            addIPMacAddressToImage("/mnt/etc/init.d/rc.local",mac_address,ip_address)
            udev_rules_path = "/mnt/etc/udev/rules.d/"
            makeEthxToEth0(udev_rules_path,mac_address);
        else:
            #SR-IOV
            DeleteIpMacInFile("/mnt/etc/init.d/rc.local")
            addIPMacAddressToImage("/mnt/etc/init.d/rc.local",mac_address,ip_address)
            #udev_rules_path = "/mnt/etc/udev/rules.d/"
            #makeEthxToEth0(udev_rules_path,mac_address);
            
        if commands.getstatusoutput("umount /mnt")[0] == 0:
            #print "umount /mnt succesfully ."
            print_info("umount /mnt succesfully .")
        else:
            #print "umount /mnt failed . "
            print_info("umount /mnt failed . ")
            return 0
        
        if commands.getstatusoutput("kvm-nbd --disconnect /dev/nbd4 ")[0] == 0:
            #print "kvm-nbd --disconnect /dev/nbd4 successfully ."
            print_info("kvm-nbd --disconnect /dev/nbd4 successfully .")
            return 1
        else:
            #print "kvm-nbd --disconnect /dev/nbd4 failed ."
            print_info("kvm-nbd --disconnect /dev/nbd4 failed .")
            return 0
        #print "modify Image successfully ."
        print_info("modify Image successfully .")
    except:
        #print "modify Image failed ."
        print_info("modify Image failed .")
        return 0
    
#test:
#modifyImage("/home/qinguan/exp/kvm/ubuntu_1.img",0,"66:55:44:33:22:11","192.168.1.186")    


    
