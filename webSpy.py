import argparse
import os
import socket
import subprocess
import time
from ipaddress import ip_network
from urllib.parse import urlparse
from selenium import webdriver


def ping_sweep(targets):
    """
    Perform a ping sweep on the specified targets and return a list of
    reachable IP addresses.
    """
    print(f"Performing ping sweep on {targets}...")
    ping_args = ["ping", "-c", "1", "-w", "1"]
    reachable_hosts = []
    for ip in targets:
        if subprocess.call(ping_args + [ip], stdout=subprocess.DEVNULL) == 0:
            reachable_hosts.append(ip)
    return reachable_hosts


def check_ports(ip, ports):
    """
    Check if the specified ports are open on the specified IP address.
    Return a list of open ports.
    """
    print(f"Checking ports on {ip}...")
    open_ports = []
    for port in ports:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.1)
        result = s.connect_ex((ip, port))
        if result == 0:
            open_ports.append(port)
        s.close()
    return open_ports


def get_hostname(ip):
    """
    Get the hostname for the specified IP address using nslookup.
    """
    print(f"Performing nslookup on {ip}...")
    try:
        hostname = socket.gethostbyaddr(ip)[0]
    except socket.herror:
        hostname = ""
    return hostname


def take_screenshot(url, output_dir):
    """
    Take a screenshot of the specified URL and save it to the specified
    output directory.
    """
    print(f"Taking screenshot of {url}...")
    options = webdriver.ChromeOptions()
    options.add_argument("headless")
    options.add_argument("disable-gpu")
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    time.sleep(1)
    driver.save_screenshot(os.path.join(output_dir, f"{urlparse(url).hostname}.png"))
    driver.quit()


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--range", help="IP range with CIDR notation")
    parser.add_argument("-f", "--file", help="text file with target list")
    parser.add_argument("-s", "--rate", type=float, default=1.0, help="rate limit in seconds")
    args = parser.parse_args()

    # Check if IP range or target file is specified
    if not args.range and not args.file:
        print("Please specify an IP range or target file.")
        return

    # Define ports to check
    ports = [80, 443]

    # Get list of targets
    if args.range:
        targets = [str(ip) for ip in ip_network(args.range).hosts()]
    elif args.file:
        with open(args.file) as f:
            targets = f.read().splitlines()

    # Perform ping sweep on targets
    reachable_hosts = ping_sweep(targets)

    # Check open ports and perform nslookup
    for ip in reachable_hosts:
        open_ports = check_ports(ip, ports)
        if open_ports:
            hostname = get_hostname(ip)
            if hostname:
                url = f"http://{ip}"
                take_screenshot(url, "screenshots")


if __name__ == "__main__":
    main()
