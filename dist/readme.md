# Overview
rasynvoice.exe is a python application compiled into a windows executable.  The application can be used to help demonstrate the Avnet RASynBoard Out of Box application at trade shows or customer events.

## Usage

Usage: rasynvoice.exe [-h] [-p PWRSRC] [-n BLENAME] [-c COMPORT]

### ```-p <serial | ble>``` or ```--pwrSrc <serial | ble>```

Defines how the application will attempt to collect power measurement data from a TC66C power monitor dongle.  

**If this option is not provided, the application will default to serial.**  

### ```-p <comX>```

Defines which windows com port the application will attempt to open to collect power measurement data from the TC66C power monitor dongle.  Note this setting is only used when ```--pwrSrc serial``` is used

**If this option is not provided, the application will default to com5**

### ```-n <New_BLE_Name>``` or ```--bleName <New_BLE_Name>```

Defines the BLE broadcast name that the application will look for when connecting to the RASynBoard DA16600 over BLE.  This name can be set on the Avnet RASynBoard Out of Box application (v1.3.0 and greater) by setting ```[BLE Mode]-> BLE_Name=<New_BLE_Name>``` in the config.ini file on the microSD card.  

**If this option is not provided, the application will default to ```DA16600-```, the default BLE name sent by the RASynBoard's DA16600.**

