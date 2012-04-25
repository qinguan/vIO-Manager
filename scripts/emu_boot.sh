#!/bin/bash

sudo kvm -m 512 -hda /home/qinguan/exp/1/ubuntu_disk.img -net nic,macaddr=52:54:00:12:34:59 -net tap
