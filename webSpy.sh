#!/bin/bash

# Set default values
ip_range=""
rate_limit=1

# Parse command line arguments
while getopts "r:f:s:" opt; do
  case $opt in
    r)
      ip_range=$OPTARG
      ;;
    f)
      target_file=$OPTARG
      ;;
    s)
      rate_limit=$OPTARG
      ;;
    \?)
      echo "Invalid option: -$OPTARG" >&2
      exit 1
      ;;
    :)
      echo "Option -$OPTARG requires an argument." >&2
      exit 1
      ;;
  esac
done

# Check if IP range or target file is specified
if [ -z "$ip_range" ] && [ -z "$target_file" ]; then
  echo "Please specify an IP range or target file."
  exit 1
fi

# Define ports to check
ports=(80 443)

# Loop through targets
if [ ! -z "$ip_range" ]; then
  # IP range specified
  targets=$(nmap -sL $ip_range | grep "Nmap scan report for" | awk '{print $NF}')
elif [ ! -z "$target_file" ]; then
  # Target file specified
  targets=$(cat $target_file)
fi

for target in $targets; do
  # Check for open ports
  for port in "${ports[@]}"; do
    (echo >/dev/tcp/$target/$port) >/dev/null 2>&1 && {
      # Perform nslookup on IP address
      hostname=$(nslookup $target | awk '/name = / {print $4}')
      if [ ! -z "$hostname" ]; then
        # Perform curl request
        curl --silent --max-time 10 --limit-rate $rate_limit "http://$target" -o /dev/null -w "%{http_code}" | grep -q "200" && {
          # Take screenshot
          mkdir -p screenshots
          chromium-browser --headless --disable-gpu --screenshot="screenshots/$hostname.png" "http://$target"
        }
      }
    }
  done
done > nslookup_results.txt
