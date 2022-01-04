## Description
Batteryconservation is a small python script wich creates an appindicator for ubuntu which can be used to enable / disable battery conservation mode.
It's also using notifications to let you know when the mode changes and it will update every 30 seconds automatically.
Its limited to stop charging at 60%, 80% or 90% and disabled (charging normally), but you can easially expand those functions if you wish to.
Please add the needed requirements.
Make sure your user has write access to /sys/bus/platform/drivers/ideapad_acpi/VPC2004:00/conservation_mode else the application won't work

Application was tested with a Lenovo Yoga 7 14ACN6.

## Setup
Run these commands to install the missing packages
```bash
sudo apt install gir1.2-appindicator3-0.1
```

## Screenshots:
![image](https://user-images.githubusercontent.com/32970397/147856340-29529bf8-2493-411e-a5e4-9b594d5879b6.png)

![image](https://user-images.githubusercontent.com/32970397/147856361-6067d346-123b-46a2-aab9-88b4ff842724.png)

![image](https://user-images.githubusercontent.com/32970397/147856368-cc33cfe2-6f8b-4ab7-9903-3232dac7cf68.png)
