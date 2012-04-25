# This file is auto-generated from the current state of the database. Instead of editing this file, 
# please use the migrations feature of Active Record to incrementally modify your database, and
# then regenerate this schema definition.
#
# Note that this schema.rb definition is the authoritative source for your database schema. If you need
# to create the application database on another system, you should be using db:schema:load, not running
# all the migrations from scratch. The latter is a flawed and unsustainable approach (the more migrations
# you'll amass, the slower it'll run and the greater likelihood for issues).
#
# It's strongly recommended to check this file into your version control system.

ActiveRecord::Schema.define(:version => 20110605061459) do

  create_table "nics", :force => true do |t|
    t.string  "bsf_address"
    t.string  "name"
    t.string  "nic_type"
    t.integer "used"
    t.string  "vf_belongto_pf"
    t.integer "virtual_machine_instance_id"
    t.string  "mac_address"
    t.string  "netmask"
    t.string  "gateway"
  end

  create_table "virtios", :force => true do |t|
    t.integer "domid"
    t.string  "name"
    t.string  "ip_address"
    t.string  "mac_address"
  end

end
