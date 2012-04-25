class MonitorController < ApplicationController
    require "soap/rpc/driver"
    require 'builder'  
    require "rexml/document"  
    require "yaml"
    
=begin
          <nicinfo>
            <pf>
              <bsf>00:19.0</bsf>
              <vf_num>0</vf_num>
              <vmdomid>2</vmdomid>
            </pf>
            <pf>
              <bsf>01:00.0</bsf>
              <vf_num>4</vf_num>
              <vf><bsf>02:00.0</bsf><vmdomid>11</vmdomid></vf>
              <vf><bsf>02:00.2</bsf><vmdomid>12</vmdomid></vf>
              <vf><bsf>02:00.4</bsf><vmdomid>13</vmdomid></vf>
              <vf><bsf>02:00.6</bsf><vmdomid>14</vmdomid></vf>
            </pf>
            <pf>
              <bsf>01:00.1</bsf>
              <vf_num>4</vf_num>
              <vf><bsf>02:00.1</bsf><vmdomid>21</vmdomid></vf>
              <vf><bsf>02:00.3</bsf><vmdomid>22</vmdomid></vf>
              <vf><bsf>02:00.5</bsf><vmdomid>23</vmdomid></vf>
              <vf><bsf>02:00.7</bsf><vmdomid>24</vmdomid></vf>
            </pf>
          </nicinfo>
=end

    def read_pf_vf_info
      begin
        doc = REXML::Document.new "<nicinfo/>"
        @nic_pfs = Nic.find(:all,:conditions => ["nic_type = ?","PF"])
        pfs_count = Nic.find(:all,:conditions => ["nic_type = ?","PF"]).size       
        #pf_num = doc.root.add_element "pf_num"
        #pf_num.text = pfs_count
        @nic_pfs.each do |pf|
          pf_node = doc.root.add_element "pf"
          
          #<bsf>00:19.0</bsf>
          pf_bsf_node = pf_node.root.add_element "bsf"
          pf_bsf_node.text = pf.bsf_address
          pf_node.add pf_bsf_node
          
          #<vf_num>0</vf_num>
          @nic_vfs = Nic.find(:all,:conditions => ["nic_type = ? and vf_belongto_pf = ? ","VF",pf.bsf_address])
          vfs_count = @nic_vfs.size
          vf_num_node = pf_node.root.add_element "vf_num"
          vf_num_node.text = vfs_count
          pf_node.add vf_num_node
          
          if vfs_count == 0
            #<vmdomid>3</vmdomid>
            @vm = Nic.find(:first,:conditions => ["bsf_address = ? and virtual_machine_instance_id != -1 ",pf.bsf_address])
            if @vm
              vmdomid_node = pf_node.root.add_element "vmdomid"
              vmdomid_node.text = @vm.virtual_machine_instance_id
              pf_node.add vmdomid_node
            end      
            #doc.add pf_node
          else
            @nic_vfs.each do |vf|
              #<vf>
              vf_node = pf_node.root.add_element "vf"
              #<bsf>02:10.3</bsf>
              vf_bsf_node = vf_node.root.add_element "bsf"
              vf_bsf_node.text = vf.bsf_address
              vf_node.add vf_bsf_node
              #<vmdomid>3</vmdomid>
              @vm = Nic.find(:first,:conditions => ["bsf_address = ? and virtual_machine_instance_id != -1",vf.bsf_address])
              if @vm
                vmdomid_node = vf_node.root.add_element "vmdomid"
                vmdomid_node.text = @vm.virtual_machine_instance_id
                vf_node.add vmdomid_node
              end
            pf_node.add vf_node
            end
            #doc.add pf_node
          end
        end
        #puts doc.to_s
        render :inline => doc.to_s
      rescue Exception => e
          puts "kkk" 
      end
   end

=begin
  <virtio_vms>
    <vm_num>2</vm_num>
    <virtio_vm>
        <vmdomid>1</vmdomid>
    </virtio_vm>
  </virtio_vms>
=end
    def read_virtio
      begin
        @virtios = Virtio.find(:all)
        doc = REXML::Document.new "<virtio_vms/>"
        
        #<vm_num>2</vm_num>
	vm_num_node = doc.root.add_element "vm_num"
	vm_count = @virtios.size
	vm_num_node.text =vm_count
	
	#<virtio_vm>
	#  <vmdomid>1</vmdomid>
	#</virtio_vm>
	@virtios.each do |virtio|
	  virtio_node = doc.root.add_element "virtio_vm"
	  vmdomid_node = virtio_node.root.add_element "vmdomid"
	  vmdomid_node.text = virtio.domid
	  virtio_node.add vmdomid_node
	end
        render :inline =>doc.to_s
      rescue Exception => e
        puts "kkk2"
      end
   end

   def show
        
   end
end

