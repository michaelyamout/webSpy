To use this script, you can specify the IP range or target file using the -r or -f option, respectively.


For example, to specify an IP range of 192.168.1.0/24 and a rate limit of 2 seconds per request, you can run the script as follows:
```
./ping_sweep.sh -r 192.168.1.0/24 -s 2
```

To specify a target file with a list of targets, you can run the script as follows:
```
./ping_sweep.sh -f targets.txt -s 2
```

The target file should contain one target per line, like this:
```
192.168.1.1
192.168.1.2
192.168.1.3
...
```
