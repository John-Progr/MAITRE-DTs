# Node Provisioning & Network Configuration Script

<p><strong>This is the most important file in this project.</strong></p>

<p>
This script must run before everything else as it is the foundation of our testbed.
</p>

<p>
This script is a Node provisioning and Network Configuration script. It is designed to configure a Raspberry Pi (or similar device running Linux) to act as a dual-homed bridge between an Ad-hoc network (The data Network) and a standard Wifi network (The control network)
</p>

---

## 1. Internet gateway initialization

<p>
The script starts by forcing an IP address assignment on the Ethernet interface (<code>eth0</code>) using <code>dhclient</code>. You need an ethernet wire for this in order to connect it to a router. Also headless won't work . So you need a monitor with hdmi and keyboard, and a mouse something that it is proivided with the raspberry pi toolkit.
</p>

<p>
This provides the node with temporary internet access. This is a critical dependency for step 3 , where the script must download external drivers from Github to make the secondary Wi-fi work. We use a dongle .
</p>

---

## 2. Ad hoc Data plane set up

<p>
It kills any existing network managers and manually overwirtes /etc/network/interfaces to configure the oboard NIC (wlan0).
</p>

<p>
it sets a static IP ( 192.168.2.$1), fixes the frequency to Channel 50 (5.2GHz) and enables Ad-hoc mode. ( We picked channel 40 by default, you can pick whatever you want )
</p>

---

## 3. Control plane Driver and Connection

<p>
The script handles a secondary USB wi-fi adapter (wlan1) (The dongle)
</p>

<p>
It downloads, compiles, and installs the rtl8812au kernel module from source. This is necessary because many high-gain usb adapters aren't supported by default Linux kernels. (This one plugged doesn't work). (On my Dekstop running ubuntu 24.04 it runs without doing anything btw).
</p>

<p>
it uses wpa_passphrase to generate a secure configuration for the control network using the credentials we passed as arguments ($2 and $3)
</p>

---

## 4. Persistence and automation injection

<p>
Script modifies /etc/rc.local, which is the file Debian ( more specificall Raspbian) executes at the very end of the boot process.
</p>

<p>
it strips existing exit 0, injects commands to restart the wireless interfaces, and most importantly, triggers the client_control.sh script on the Desktop.
</p>

<p>
This makes stuff a little bit more automated as each time a raspberry pi comes to life , it becomes accessible so it can join whichever experiment we desire.
</p>

---

## 5. Remote management Activation

<p>
The final step enables and starts the SSH service
</p>

<p>
This is the headless part we talked about earlier. Since these nodes are often headless (no monitor), this allows us to log in remotely over the Control network and execut commands, debug, see if an error occured and of course without this headless approach the experiment is not feasible.
</p>

---

## Final Notes

<p>
This is everything as far as the script is concerned.
</p>

<p>
But there is a highlight we need to discuss. Not every driver "plays" on the default OS and kernel of raspberry pi. We had difficult time picking the correct configurations. Sometimes the control network worked but ad hoc failed for some reason. Driver randomness also gets picked up by the MAB algorithm which is fascinating even when data rates are on the table.
</p>
