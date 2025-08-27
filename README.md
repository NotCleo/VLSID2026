# VLSID2026

Most visited URLS are 

    https://chatgpt.com/share/68a9d839-f9f0-8013-bfcf-3cb1bb41fc4f - Shravan's GPT context
    
    
    https://www.microchip.com/en-us/development-tool/mpfs-icicle-kit-es
    https://github.com/Microchip-Vectorblox/VectorBlox-SDK/blob/master/tutorials/onnx/yolov7/yolov7.sh
    https://github.com/polarfire-soc/icicle-kit-reference-design?tab=readme-ov-file
    https://github.com/Microchip-Vectorblox/VectorBlox-Video-Kit-Demo?tab=readme-ov-file
    https://web.pa.msu.edu/people/edmunds/Disco_Kraken/PolarFire_SoC_Register_Map/PF_SoC_RegMap/pfsoc_regmap.htm

---------------------------------------------------------------------------------------------------------------------------------------------

Here's the manual diagram to ensure we dont mess up UART/MSS-Config/FlashPro ports

![image](https://github.com/NotCleo/VLSID2026/blob/main/image.png?raw=true)


---------------------------------------------------------------------------------------------------------------------------------------------


The event registration is here - https://vlsid.org/design-contest/


1) We're flashing the board with a SSD, which will be loaded with the Ubuntu(RV variant) - ubuntu-24.04.3-preinstalled-server-riscv64+icicle.img.xz

2) We needed a SSD card and it's reader to do so....

3) How to check my laptop's MAC/IP and what ports are active, and what's my ethernet port and is it active or not? How do I check if the Icicle Kit to which I have SSH access into is communicating with my laptop or not via the ethernet? How do I check the same things for the board too?

4) Refer the BootProcess.png for why to switch between eMMC and the SSD, but how?

5) Always take the MAC binded to the Ethernet for the Silver Microchip Licence

6) When doing a UART debug between the SOC and host laptop via PuTTY client, select to Serial connection type, adjust the Baud=115200, and then perform the console, but only after flashing the board (via the JTAG DEBUGGER!?) with a program to transmit via the USART something?! Not sure...., need to verify this part...., but also idk about how to check which USB port is the board connected to, like the /dev/ttyS0 or some /dev/ttyUSB*, like how?! 

7) How to see UART using minicom between mcu and laptop over serial to usb port? - I think I saw a yt video for that - https://www.youtube.com/watch?v=dEQwSl8mCFs

8) https://www.microchip.com/en-us/products/fpgas-and-plds/fpga-and-soc-design-tools/fpga/libero-software-later-versions - Use this to download the Libero SDK after having recieved the license.dat on my mail from Microchip regarding the Libero Silver 1Yr Floating License for Linux Server (LIB-SLV-F-1YR), it can be found here - https://www.microchipdirect.com/fpga-software-products?_ga=2.35074785.1714206911.1658467220-1049315983.1658467219, anyhow the mail contents are below,



---------------------------------------------------------------------------------------------------------------------------------------------

The attached license enables operation of Libero software per the terms of the license agreement you accepted during your software installation.
 
Refer the below Libero Software Download 
https://www.microchip.com/en-us/products/fpgas-and-plds/fpga-and-soc-design-tools/fpga/libero-software-later-versions

License Installation Quick Start Guide
https://coredocs.s3.amazonaws.com/Libero/2023_1/Tool/libero_download_license_quickstart.pdf
 
Libero Software Installation and Licensing Guide
https://coredocs.s3.amazonaws.com/Libero/2023_1/Tool/Libero_Installation_Licensing_Setup_User_Guide.pdf

NOTE:
    Starting with Libero SoC v2024.2, the latest 64-bit license daemons with FlexLM v11.19 are required for all floating license users. 
License daemon download links are included below. Please refer to release notes for more details.
https://www.microchip.com/en-us/products/fpgas-and-plds/fpga-and-soc-design-tools/fpga/libero-software-later-versions

Linux license daemon bundle: 
    https://ww1.microchip.com/downloads/secure/aemDocuments/documents/FPGA/media-content/FPGA/daemons/Linux_Licensing_Daemon_11.19.6.0_64-bit.tar.gz
Windows license daemon bundle:
    https://ww1.microchip.com/downloads/secure/aemDocuments/documents/FPGA/media-content/FPGA/daemons/Windows_Licensing_Daemon_11.19.6.0_64-bit.zip


And i have uploaded the license.dat too

---------------------------------------------------------------------------------------------------------------------------------------------


# Steps to Download, Install, and Launch Libero SoC 2025.1 on Ubuntu 24.04 LTS

1. **Found MAC ID and hostname**
   /sbin/ifconfig -a | grep ether
   hostname

2. **Got license from Microchip**
   # Downloaded License.dat from Microchip and placed into ~/Downloads

3. **Created license directory and extracted license daemons**
   sudo mkdir -p /opt/microchip/license
   sudo tar -xvzf ~/Downloads/Linux_Licensing_Daemon_11.19.6.0_64-bit.tar.gz -C /opt/microchip/license

4. **Copied License.dat into license folder**
   sudo cp ~/Downloads/License.dat /opt/microchip/license/

5. **Started license server with log file**
   cd /opt/microchip/license
   sudo /opt/microchip/license/lmgrd -c /opt/microchip/license/License.dat -l /opt/microchip/license/license.log

6. **Fixed FlexLM missing temp directory error**
   sudo mkdir -p /usr/tmp/.flexlm
   sudo chmod 777 /usr/tmp/.flexlm

7. **Set license environment variable**
   export LM_LICENSE_FILE=1702@Maverick

8. **Unzipped Libero 2025.1 web installer**
   unzip ~/Downloads/libero_soc_2025.1_online_lin.zip -d ~/Downloads/libero2025_installer
   cd ~/Downloads/libero2025_installer/Libero_SoC_2025.1_online_lin
   chmod +x Libero_SoC_2025.1_online_lin.bin

9. **Fixed missing dependency (libxcb-cursor)**
   sudo apt update
   sudo apt install libxcb-cursor0

10. **Fixed missing dependency (libpng15) by building from source**
    cd ~/Downloads
    wget https://sourceforge.net/projects/libpng/files/libpng15/older-releases/1.5.15/libpng-1.5.15.tar.gz
    tar -xzf libpng-1.5.15.tar.gz
    cd libpng-1.5.15
    ./configure --prefix=/usr/local
    make
    sudo make install
    sudo ldconfig

    # Optional if needed
    export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH

11. **Ran the Libero installer**
    cd ~/Downloads/libero2025_installer/Libero_SoC_2025.1_online_lin
    ./Libero_SoC_2025.1_online_lin.bin

12. **Installed additional required packages for FP6 / Designer tools**
    sudo /home/amrut/microchip/Libero_SoC_2025.1/req_to_install.sh
    sudo /home/amrut/microchip/Libero_SoC_2025.1/Libero_SoC/Designer/bin/fp6_env_install

13. **Fixed GLIBCXX mismatch by using system libstdc++ instead of bundled one**
    mv /home/amrut/microchip/Libero_SoC_2025.1/Libero_SoC/Designer/lib64/rhel/libstdc++.so.6 \
       /home/amrut/microchip/Libero_SoC_2025.1/Libero_SoC/Designer/lib64/rhel/libstdc++.so.6.bak

14. **Launched Libero successfully**
    /home/amrut/microchip/Libero_SoC_2025.1/Libero_SoC/Designer/bin/libero 

15. **(Optional) Create alias for convenience**
    echo 'alias libero="/home/amrut/microchip/Libero_SoC_2025.1/Libero_SoC/Designer/bin/libero"' >> ~/.bashrc
    source ~/.bashrc

---------------------------------------------------------------------------------------------------------------------------------------------



11) Then comes the part of how do I switch between the eMMC and the SSD in that MUX, is it via the Libero?! How? Since i'm planning to boot as discussed in step (1), because package manager issue or something with the linux that the board booted with, we couldn't do anything around that, so this is what we came up with....

12) run /home/amrut/microchip/Libero_SoC_2025.1/Libero_SoC/Designer/bin/libero everytime i have to open Libero

13) see this demo - https://www.youtube.com/watch?v=_4nW-BgvGoU

14) Prof wants us to use a Robot?! - https://clearpathrobotics.com/turtlebot-4/

15) If you face issues regarding the license validity, perform these debug statements,
    in the sense if "/home/amrut/microchip/Libero_SoC_2025.1/Libero_SoC/Designer/bin/libero" does not work

run these, 

     ps -ef | grep lmgrd
     tail -n 100 /opt/microchip/license/license.log
     echo $LM_LICENSE_FILE
     export LM_LICENSE_FILE=1702@Maverick
     echo 'export LM_LICENSE_FILE=1702@Maverick' >> ~/.bashrc
     verify using echo $LM_LICENSE_FILE again
     /opt/microchip/license/lmutil lmstat -a -c 1702@Maverick
     cd /opt/microchip/license/
     do a list all to verify license.dat's presence
     sudo ./lmgrd -c /opt/microchip/license/License.dat -l /opt/microchip/license/license.log
     ps aux | grep lmgrd
     /opt/microchip/license/lmutil lmstat -a -c 1702@Maverick -> veriy if you get the Actel_BASESoC
     now run -> /home/amrut/microchip/Libero_SoC_2025.1/Libero_SoC/Designer/bin/libero


---------------------------------------------------------------------------------------------------------------------------------------------

# 1) Start the license server manually
cd /opt/microchip/license
sudo ./lmgrd -c /opt/microchip/license/License.dat -l /opt/microchip/license/license.log

# 2) Verify the license server is running
ps aux | grep lmgrd

# 3) Check license server status
/opt/microchip/license/lmutil lmstat -a -c 1702@Maverick

# 4) (Optional) Make the license server start automatically on boot
sudo nano /etc/systemd/system/microchip-license.service




16) I downloaded the SoftConsole as mentioned in the vectorblox and it gave the post installation guide here (dont judge it's only for my laptop) - file:///home/amrut/Microchip/SoftConsole-v2022.2-RISC-V-747/documentation/softconsole/using_softconsole/post_installation.html

17) Mobaxterminal ko use karke we can see the boot console, log files as it boots.
 
---------------------------------------------------------------------------------------------------------------------------------------------

18) # 1. Monitor which device appears when you plug in the Icicle Kit's SD card
inotifywait --event create --format "%w%f" /dev

# (you will see something like /dev/sdX or /dev/mmcblk0, not /dev/sg0)

# 2. Verify what was detected
lsblk -p

# Look for the correct device (example: /dev/sdb or /dev/mmcblk0) and its size (should match your SD card size).

# 3. Flash the image to that device
# Replace /dev/sdX with the correct one you found in lsblk
sudo dd if=ubuntu-24.04.3-preinstalled-server-riscv64+icicle.img \
        of=/dev/sdX \
        bs=16M status=progress conv=fsync

# 4. Once done, safely eject
sync
sudo eject /dev/sdX

Triple Check this otherwise DEATH!


reference - https://canonical-ubuntu-boards.readthedocs-hosted.com/en/latest/how-to/flash-images/
---------------------------------------------------------------------------------------------------------------------------------------------


19) We tried flashing with Ubuntu 24.04 but the QSPI was not supporting it and hence the image's header couldnt be read with correct offset, however the issue of the board detecting the boot from SD card was a relief as we do not need use any SoftConsole to get it to switch from eNVM to SD, but it happens on its own - "If SD is present, the kit usually prioritizes SD over eMMC"

But we now are facing the issue of QSPI compatibility issue as it's not detecting the HSS payload and apparently our image which we flahsed does not support it

So now we need to look for QSPI update or Image downgrade to match the bootloader to read the image's header correctly


20) I needed to get the desktop shortcut sorted out for the SoftConsole, or just run - /home/amrut/Microchip/SoftConsole-v2022.2-RISC-V-747/softconsole.sh everytime to launch the SoftConsole, btw i was told to read the post installation guide - file:////home/amrut/Microchip/SoftConsole-v2022.2-RISC-V-747/documentation/softconsole/using_softconsole/post_installation.html


21) (note to self, revise and figure out) what is rootfs, how does the bootloader work in linux, what is a bootloader, what is firmware, image? and what is this /dev, /usr, /bin, /proc, ... all these directories which are different from my /Downloads,/Desktop, .... and what is Uefi, GRUB, ....


BTW ubuntu distros for Microchip was from here - https://canonical-ubuntu-boards.readthedocs-hosted.com/en/latest/how-to/microchip-polarfire-icicle/


22) OUr HSS - v0.99.36 - 2023, so we tried Ubuntu 24 and 22, and in either cases the HSS payload isnt being detected (the Bootloader isnt able to find the "image's header offset")

23) Updating the QSPI wont fix it apparently, we will need to i think build the HSS payload using the raw ubuntu disk image, as raw ubuntu disk image has only the GPT partitions like rootfs, Uboot and the kernel so back to making the HSS payload fix.

here's the full explanation - "HSS is trying to boot a raw HSS payload from the MMC device (SD/eMMC). The “magic” values b007c0de / c08b8355 are for HSS-format payloads. Your Ubuntu media isn’t an HSS payload; it’s a normal disk image with GPT partitions (U-Boot, kernel, rootfs). So HSS looks for an HSS payload, doesn’t find one in the expected GPT partition, falls back to LBA0, reads garbage (from HSS’s perspective), and aborts. This is a configuration/flash-flow mismatch, not a QSPI problem
Do you need to “upgrade QSPI”?

No. On the Icicle Kit, HSS runs from eNVM, not QSPI; QSPI contents aren’t involved in this Ubuntu boot flow. Updating QSPI won’t fix this symptom."

24) Note to self - reset is SW4 and do have a look at the diagram above always

---------------------------------------------------------------------------------------------------------------------------------------------


25) 

Probably this is one starting point - https://github.com/polarfire-soc/hart-software-services

i ) hss payload generator to wrap up the raw ubuntu disk image that's flashed into the card 

side quests with this above task -> build up/verify on Shravan's CGPT context of the HSS versioning with Ubun22 - "we have a relatively new HSS version running 2023.6 which should support ubuntu"


confirm if (my doubt) (we think its the first way)

a) we need to have the sd card flashed with the raw ubuntu image and then generate the HSS payload (maybe via the Mobax/SoftConsole/Libero)

(or)

b) we need to have the sd card flashed with the raw ubuntu image already wrapped up in the HSS payload which we will generate in our host pc (maybe via the Mobax/SoftConsole/Libero)

ii ) We then need to verify if we flashed with/wo partition in the sdc, that's the issue we are primarily facing(regarding the partition of ubuntu)

if we manage to boot it successfully, we will then have to perform

    -> Check python --version/ python3 --version, ubun22 does come with python packages/manager so we are hoping it works
    -> Then we need to again verify our network configurations right? since we booted with a new kernel in the board
    -> Then we need to test further with whatever works, maybe try out the yolov7.vnnx-> yolov7.tflite and try it out once


iii) Meanwhile the posenet PTQ files, the "issue" was as shravan mentions there are different datasets and not a global dataset, unlike what we understood from the yolo's PTQ which (sorry to re iterate) was

    -> Had the coco2017's calibration dataset (as a bin file), and we would PTQ the yolo (actually the bash script is what's doing it automatically because it's preloaded), so we have not one but many such "calibration datasets" (hopefully as a bin file) for the POSENET (this is what i understood, please correct me), so this is how the quantization problem came up, we will need to figure this out

---------------------------------------------------------------------------------------------------------------------------------------------


26) For the SD card to boot reliably, the j34/j43 jumpers must be short pins 1 and 2 to set 1.8 volts, if we want to verify see the video on the polarfire kit's website. If the jumpers are shorted on pin 2 and 3, it will be set at 3.3volts (reference for pin 1 2 3 regarding how to read is, keep the power pin of the board facing left and then read the pins 123 from right to left), video is here btw - https://www.youtube.com/watch?v=wip-mpxsR8k&t=35s

27) mrut@Maverick:~$ arp -a
_gateway (172.16.111.1) at 00:09:0f:09:01:12 [ether] on wlp2s0
amrut@Maverick:~$ ip a
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
       valid_lft forever preferred_lft forever
    inet6 ::1/128 scope host noprefixroute 
       valid_lft forever preferred_lft forever
2: enp1s0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP group default qlen 1000
    link/ether c4:ef:bb:ab:db:5b brd ff:ff:ff:ff:ff:ff
3: wlp2s0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP group default qlen 1000
    link/ether 70:08:94:61:af:2b brd ff:ff:ff:ff:ff:ff
    inet 172.16.104.100/19 brd 172.16.127.255 scope global dynamic noprefixroute wlp2s0
       valid_lft 604392sec preferred_lft 604392sec
    inet6 fe80::a4a4:b01e:8729:ec6/64 scope link noprefixroute 
       valid_lft forever preferred_lft forever
4: lxcbr0: <NO-CARRIER,BROADCAST,MULTICAST,UP> mtu 1500 qdisc noqueue state DOWN group default qlen 1000
    link/ether 00:16:3e:00:00:00 brd ff:ff:ff:ff:ff:ff
    inet 10.0.3.1/24 brd 10.0.3.255 scope global lxcbr0
       valid_lft forever preferred_lft forever
amrut@Maverick:~$ ip route
default via 172.16.111.1 dev wlp2s0 proto dhcp src 172.16.104.100 metric 600 
10.0.3.0/24 dev lxcbr0 proto kernel scope link src 10.0.3.1 linkdown 
172.16.96.0/19 dev wlp2s0 proto kernel scope link src 172.16.104.100 metric 600 
amrut@Maverick:~$ sudo ip addr add 192.168.100.1/24 dev enp1s0
[sudo] password for amrut: 
amrut@Maverick:~$ sudo ip link set enp1s0 up
amrut@Maverick:~$ sudo sysctl -w net.ipv4.ip_forward=1
net.ipv4.ip_forward = 1
amrut@Maverick:~$ sudo iptables -t nat -A POSTROUTING -o wlp2s0 -j MASQUERADE




