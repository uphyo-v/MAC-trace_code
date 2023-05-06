# MAC-trace_code

## DEVICETYPE
* cisco_ios
* arista_eos
* dell_force10

## MAC
* xxxx.yyyy.zzzz
* xx:xx:yy:yy:zz:zz

## Device
* X.X.X.X
* HOSTNAME 
    * dns should be able to resolve to IP

## SEARCH_MASK
* x.x.x.
    * mgmt subnet mask
* HOSTNAME
    * hostname mask (if swi01,swi02.... , then swi)
* Regex Format
    * (x.x.x.|swi)

=============================
# Usage
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
echo 'uu=USERNAME
pp=PASSWORD
lldp_search_mask=SEARCH_MASK
'
```