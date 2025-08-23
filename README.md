# VLSID2026

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

17) Mobuxterminal ko use karke we can see the boot console, log files as it boots.

18) 


