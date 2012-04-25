class CreateNics < ActiveRecord::Migration
  def self.up
    create_table :nics do |t|
      t.column :bsf_address, :string
      t.column :name, :string
      t.column :nic_type, :string
      t.column :used, :integer
      t.column :vf_belongto_pf, :string
      t.column :virtual_machine_instance_id, :integer
      t.column :mac_address, :string
      t.column :netmask, :string
      t.column :gateway, :string
    end
  end

  def self.down
    drop_table :nics
  end
end
