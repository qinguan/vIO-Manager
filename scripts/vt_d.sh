#!/bin/bash
modprobe pci_stub
echo "8086 10de" > /sys/bus/pci/drivers/pci-stub/new_id
echo 0000:00:19.0 > /sys/bus/pci/devices/0000:00:19.0/driver/unbind
echo 0000:00:19.0 > /sys/bus/pci/drivers/pci-stub/bind
modprobe kvm
modprobe kvm-intel
sudo kvm -m 512 -boot c -net none -hda /home/qinguan/exp/3/ubuntu_disk.img  -device pci-assign,host=00:19.0

