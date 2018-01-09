import argparse
from collections import Counter
from collections import OrderedDict

def read_bro_file(filename):
    ''' Reads in a file and puts each line into a list. Returns
    the list.
    '''
    log_list = open(filename).read().splitlines()[1:]
    return log_list
        

def sort_byte_count(data):
    sorted_orig_bytes_dict = OrderedDict(sorted(data.items(), key=lambda i: i[1]['orig_bytes'], reverse=True))
    sorted_resp_bytes_dict = OrderedDict(sorted(data.items(), key=lambda i: i[1]['resp_bytes'], reverse=True))
    return sorted_orig_bytes_dict, sorted_resp_bytes_dict


def count_interval(data):
    ip_counter = Counter()
    for i in data:
        ip_counter.update(data[i])

    return ip_counter


def get_common_intersection(data_dict):
    ''' Not implemented
    '''
    keys = []
    for i in data_dict:
        keys.append(data_dict[i])
    print(keys[0])
    common = set(data_dict[0])

    for alist in data_dict.values():
        common.intersection_update(set(alist))


def get_unique_dict(data_dict):
    ''' Takes the dictionary full of timing intervals and IP
    addresses and builds a new dictionary with the same keys but
    with only unique IP addresses. Returns the new dictionary with
    unique IP addreses.
    '''
    print(" [+]  Creating a new dictionary with unique IP addresses.\n")
    new_dict = {}
    for i in data_dict:
        new_dict[i] = list(set(data_dict[i]))
    return new_dict


def count_dest_ips(data, n):
    ''' Counts the destination IP addresses and returns the n most
    visited addresses
    '''
    print("\n [+]  Counting destination IP addresses.\n")
    ip_counter = Counter()
    for item in data:
        ip = item[1]
        ip_counter.update([ip])

    return ip_counter.most_common(n) 


def count_bytes(data):
    ''' Maps the bytes to each IP and adds them up.
    '''
    print("\n [+]  Adding the transferred bytes for all hosts. \n")
    new_dict = {}
    for item in data:
        try:
            orig_bytes = int(item[0])
            resp_bytes = int(item[1])
            dest_ip = item[2]
        except:
            continue
        if dest_ip not in new_dict:
            new_dict[dest_ip] = {"orig_bytes": [orig_bytes], 
                                 "resp_bytes": [resp_bytes]}
        else: 
            new_dict[dest_ip]['orig_bytes'].append(orig_bytes)
            new_dict[dest_ip]['resp_bytes'].append(resp_bytes)

    for item in new_dict:
        new_dict[item]['orig_bytes'] = sum(new_dict[item]['orig_bytes'])
        new_dict[item]['resp_bytes'] = sum(new_dict[item]['resp_bytes'])

    return new_dict


def get_interval_minutes(interval, data):
    ''' Creates a dictionary with keys corresponding to the 
    hour (1-24) and specified minute interval. The log timestamp
    is read and the corresponding IP address is added to the 
    appropriate key. Returns the dictionary consisting of
    intervals and IP addresses
    '''
    time_intervals = {}
    keys = []
    for i in range(1,25):
        for timeframe in range(0, 60, interval):
            time_intervals[str(i).zfill(2) + '-' + str(timeframe)] = []
            keys.append(str(i).zfill(2) + '-' + str(timeframe))

    print("\n [+]  Creating a dictionary with {} keys.\n".format(len(keys)))

    for item in data:
        timestamp = item[0]
        hour = int(timestamp[11:13])
        minutes = int(timestamp[14:16])
        
        ip = item[1] 

        for i in range(len(keys)):
            try:
                t1 = int(keys[i].split('-')[1])
                t2 = int(keys[i + 1].split('-')[1]) 
                if t1 < minutes < t2:
                    time_intervals[keys[i]].append(ip)
            except IndexError:
                if t1 < minutes < 61:
                    time_intervals[keys[i]].append(ip)

    return time_intervals


def main():
    contents = read_bro_file(filename)
    time_data = []
    bytes_data = []
    ip_list = []
    suspects = []

    for line in contents:
        time_dest_data = []
        host_bytes_data = []
        timestamp = line.split(',')[0].strip('"')
        orig_bytes = line.split(',')[-4].strip('"')
        resp_bytes = line.split(',')[-3].strip('"')

        dest_ip = line.split(',')[3].strip('"')
        ip_list.append(dest_ip)
        time_dest_data.extend((timestamp, dest_ip))
        host_bytes_data.extend((orig_bytes, resp_bytes, dest_ip))
        time_data.append(time_dest_data)
        bytes_data.append((orig_bytes, resp_bytes, dest_ip))   

    if args.most_common:
        ip_counts = count_dest_ips(time_data, args.most_common)
        for item in ip_counts:
            print(item)

    if args.most_bytes:
        byte_count = count_bytes(bytes_data)
        sorted_orig_byte_count, sorted_resp_byte_count = sort_byte_count(byte_count)
        
        print(" [+]  Hosts ordered by ORIG_IP_BYTES\n")
        counter = 0
        while counter < args.most_bytes:
            for item in sorted_orig_byte_count:
                print(item, sorted_orig_byte_count[item])
                counter += 1
                if counter == args.most_bytes:
                    break

        print("\n [+]  Hosts ordered by RESP_IP_BYTES\n")
        counter = 0
        while counter < args.most_bytes:
            for item in sorted_resp_byte_count:
                print(item, sorted_resp_byte_count[item])
                counter += 1
                if counter == args.most_bytes:
                    break
        
    if args.analyze_intervals:
        interval_ips_dict = get_interval_minutes(minutes_interval, time_data)
        unique_dict = get_unique_dict(interval_ips_dict)
        counted_intervals = count_interval(unique_dict)
        print("IP ADDRESS  COUNT")
        for item in counted_intervals.most_common(100):
            addr = item[0]
            occurence = item[1]
            print(addr, occurence)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    parser.add_argument("-mc", "--most_common", type=int, help="displays the n most visited destination ip addresses")
    parser.add_argument("-mb", "--most_bytes", type=int, help="displays the n most ip addresses with most data transferred")
    parser.add_argument("-m", "--minutes", type=int, choices=range(1,61), metavar="[1-60]", help="specify the minute interval to check between 1 and 60")
    parser.add_argument("-f", "--filename", help="specify a bro log file.")
    parser.add_argument("-ai", "--analyze_intervals", help="perform analysis on timing intervals", action="store_true")
    args = parser.parse_args()

    if not args.filename:
        parser.print_help()
        print("\n [-]  Please specify the filename to analyze.\n")
        exit()

    if args.minutes and not args.analyze_intervals:
        parser.print_help()
        print("\n [-]  The minutes argument needs to be used with the -ai switch.\n")
        exit()

    if args.analyze_intervals and not args.minutes:
        parser.print_help()
        print("\n [-]  The -ai argument also requires a time interval (-m 5).\n")
        exit()

    filename = args.filename
    minutes_interval = args.minutes
    main()