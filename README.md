# MAC-trace_code

## DEVICETYPE
* cisco_ios
* arista_eos
* dell_force10 (default)

## MAC
* 1234.5678.9ABC
* 12:34:56:78:9A:BC
* 123456789ABC

## Device
* X.X.X.X
* HOSTNAME 
    * dns should be able to resolve to IP

## SEARCH_MASK
* x.x.x.
    * mgmt subnet mask
* HOSTNAME
    * hostname_mask (if swi01,swi02.... , then swi)
* Regex Format
    * (x.x.x.|swi)

## Source of information
* arguments
* files
    * devices_list.txt
    * mac_list.txt
    * info.env

=============================
## Usage
* find_mac_v2.py [-h] [-s SEARCH_MASK] [-u USERNAME] [-p PASSWORD] [-m MAC] [-t DEVICETYPE] [-d DEVICE]

    * options:
        * -h, --help        show this help message and exit
        * -s SEARCH_MASK, --search_mask SEARCH_MASK
            * lldp neighbor search mask
        * -u USERNAME, --username USERNAME
            * username
        * -p PASSWORD, --password PASSWORD
            * Password
        * -m MAC, --mac MAC
            * Mac address
        * -t DEVICETYPE, --devicetype DEVICETYPE
            * Device type: 'cisco_ios','dell_force10','arista_eos'
        * -d DEVICE, --device DEVICE
            * Device

## Run with Arguments
```
python find_mac_v2.py -u USERNAME -p "PASSWORD" -m MAC -d IP|NAME -t DEVICETYPE -s SEARCH_MASK
```

## Run with Environment Variables
```
export UUU=USERNAME
export PPP=PASSWORD
export LLDP_SEARCH_MASK=SEARCH_MASK
python find_mac_v2.py -m MAC -d IP|NAME -t DEVICETYPE
```
## Run using info.env file
```
    cat <<"EOF" > ./info.env
    uu=USERNAME
    pp=PASSWORD
    lldp_search_mask=SEARCH_MASK
    EOF

```