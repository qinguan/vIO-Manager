#!/bin/bash

sudo kvm -hda /home/qinguan/exp/2/ubuntu_disk.img -net nic,model=virtio,macaddr=52:54:00:12:34:57  -net tap -m 512

