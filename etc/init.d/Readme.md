# Start up script
A single host can monitor multiple instances of batteries using apcupsd very easily.

Define a collection of files matching the expression apcupsd*.conf for each instance of a battery you want to monitor using apcupsd.

Keep in mind the purpose of apcaccess is to have it's NIS port open and only one instance of battery monitoring per port is possible. 
One could configure only using the daemon scripts of apcupsd and not use apcaccess to trigger a Nagios passive check when necessary.

Following items must be different for each configuration instance
* STATFILE /var/log/apcupsd.status
* EVENTSFILE /var/log/apcupsd.events
* NISPORT 3551 (if using apcaccess)


# Use udev rules
If connected via USB or other physical connection to the host running apcupsd, then setup some rules so you can count on 
references using DEVICE are static. I haven't quite figured it out but these did not acutally work for me, however it is the concept
that counts.

    KERNEL=="hiddev*", ATTRS{manufacturer}=="Amercian Power Conversion", ATTRS{serial}=="4B1720P29823  ", OWNER="root", SYMLINK+="usb/ups-bx1300gg"

    ACTION=="add", ATTRS{manufacturer}=="American Power Conversion", ATTRS{serial}=="8675309  ", OWNER="root", SYMLINK+="usb/ups-bx1300g"

