import argparse
import socket
import threading


def tcp_connect(ip, port, timeout):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.settimeout(timeout)

    try:
        s.connect((ip, port_number))
        port_status = 'Listening'
    except:
        port_status = ''

    return port_status


def main():
    data = []
    for addr in addrs:
        print("[*] Checking host {}".format(addr))
        host_data = []
        if args.verbose:
            print("[*] Checking for SMI...")
        smi_status = tcp_connect(addr, 4786)
        if smi_status:
            print("[+] SMI Detected on {}! Try using the SIET tool.".format(addr))
        else:
            if args.verbose:
                print("[-] SMI not detected")
        host_data.extend((addr, smi_status))

        data.append(host_data)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    parser.add_argument("-csv", "--csv", nargs='?', const='results.csv', help="specify the name of a csv file to write to. If the file already exists it will be appended")
    parser.add_argument("-ip", "--ip_address", help="specify a target IP address")
    parser.add_argument("-ipf", "--ip_address_file", help="specify a file containing IP addresses one per line.")
    parser.add_argument("-t", "--threads", nargs="?", type=int, default=1, help="specify number of threads (default=1)")
    parser.add_argument("-to", "--timeout", nargs="?", type=int, default=1, help="specify socket timeout (default=1)")
    args = parser.parse_args()

    if not(args.ip_address and args.ip_address_file):
        parser.print_help()
        print('\n[-] Please specify an IP address (-ip) or file containing IP addresses (-ipf)\n')
        exit()

    if args.ip_address:
        addrs = [args.ip_address]

    if args.ip_address_file:
        if not os.path.exists(args.ip_address_file):
            parser.print_help()
            print("\n[-]  The file cannot be found or you do not have permission to open the file. Please check the path and try again\n")
            exit()
        addrs = open(args.ip_address_file).read().splitlines() 


    main()