class CreateVirtios < ActiveRecord::Migration
  def self.up
    create_table :virtios do |t|
      t.column :domid, :integer
      t.column :name, :string
      t.column :ip_address, :string
      t.column :mac_address,:string
    end
  end

  def self.down
    drop_table :virtios
  end
end
