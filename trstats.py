import sys, os
import argparse
import json
import plotly.graph_objects as go
import plotly.io as pio
import time

# Author: Josh Messitte (811976008)
# CSCI 6760 Project 1: trstats.py
# Usage: python3 trstats.py -o OUTPUT [-n NUM_RUNS] [-t TARGET] [-m MAX_HOPS] [-d RUN_DELAY] [--test TEST_DIR]

# Main method
if __name__ == '__main__':

    # Set up argument parsing automation
    prog = 'python3 trstats.py'
    descr = 'Python Wrapper Script to Analyze Traceroute Performance'
    parser = argparse.ArgumentParser(prog=prog, description=descr)
    parser.add_argument('-o', '--output', type=str, default='output.json', required=True, help='Path and Name of outpt '
                                                                                               'JSON')
    parser.add_argument('-n', '--num_runs', type=int, default=10, help='Number of times traceroute will run')
    parser.add_argument('-d', '--run_delay', type=int, default=0, help='Number of seconds to wait between two '
                                                                       'condsectuive runs')
    parser.add_argument('-m', '--max_hops', type=int, default=100, help='Number of times traceroute will run')
    parser.add_argument('-t', '--target', type=str, default='www.yahoo.co.jp',
                        help='A target domain name or IP address')
    parser.add_argument('--test', '--test', type=str, default=None, help='Directory containing num_runs text files, '
                                                                         'each with traceroute output. If present, '
                                                                         'override and do not run traceroute.')

    # Parse the given arguments
    args = parser.parse_args()

    if args.test != None:
        # A directiory of text files was provided // this conditional branch executes // DON'T run traceroute
        dir_path = args.test
        file_list = []
        for folder, subfolder, files in os.walk(dir_path):
            for f in files:
                complete_path = os.path.join(folder, f)
                file_list.append(complete_path)

        hosts_by_hop = []
        times_by_hop = []
        hops_seen = []

        for item in file_list:
            # Iterate over all files
            txt_f = open(item, 'r')
            count = 0
            while True:
                # File for each line of a txt file
                curr = txt_f.readline()

                if len(curr) < 1:
                    break

                if count > 0:
                    # Past first line
                    if count < 10:
                        curr_hop = int(curr[1:curr.find('  ')])
                    else:
                        curr_hop = int(curr[0:curr.find('  ')])

                    if curr_hop > args.max_hops:
                        break

                    hops_seen.append(curr_hop)
                    curr = curr[4:]
                    total_parsets = curr.count('(')

                    # If traceroute yields statistics, we will observe the 'ms' unit measurement
                    hosts = []
                    times = []

                    # Pull first host-time matchup
                    if total_parsets > 0:

                        double_sp = curr.find('  ')
                        msloc = curr.find(' ms')

                        hosts.append(curr[0:double_sp])
                        if curr[double_sp + 2:msloc] != '*':
                            times.append(float(curr[double_sp + 2:msloc]))
                        curr = curr[msloc + 1:]
                    total_parsets = curr.count('(')

                    if total_parsets == 0:
                        # Form: domain_(ip)__x_ms__x_ms__x_ms
                        msloc = curr.find(' ms')

                        if msloc != -1 and curr[4:msloc] != '*':
                            times.append(float(curr[4:msloc]))
                        curr = curr[msloc + 1:]
                        msloc = curr.find(' ms')
                        if msloc != -1 and curr[4:msloc] != '*':
                            times.append(float(curr[4:msloc]))

                    elif total_parsets == 1:
                        # Two total hosts for this single hop
                        if curr.find('(') < curr.find('  '):
                            # Form: domain_(ip)__x_ms_domain_(ip)__x_ms__x_ms
                            double_sp = curr.find('  ')
                            hosts.append(curr[3:double_sp])
                            curr = curr[double_sp + 2:]
                            msloc = curr.find(' ms')
                            if msloc != -1 and curr[0:msloc] != '*':
                                times.append(float(curr[0:msloc]))
                            curr = curr[msloc + 1:]
                            msloc = curr.find(' ms')
                            if msloc != -1 and curr[4:msloc] != '*':
                                times.append(float(curr[4:msloc]))
                        elif curr.find('(') > curr.find('  '):
                            # Form: domain_ip__x_ms__x_ms_domain_(ip)__x_ms
                            msloc = curr.find(' ms')
                            if msloc != -1 and curr[4:msloc] != '*':
                                times.append(float(curr[4:msloc]))
                            curr = curr[msloc + 1:]
                            double_sp = curr.find('  ')
                            hosts.append(curr[3:double_sp])
                            curr = curr[double_sp + 2:]
                            msloc = curr.find(' ms')
                            if msloc != -1 and curr[0:msloc] != '*':
                                times.append(float(curr[0:msloc]))

                    elif total_parsets == 2:
                        # Form: domain_(ip)__x_ms_domain_(ip)__x_ms_domain_(ip)__x_ms
                        double_sp = curr.find('  ')
                        hosts.append(curr[3:double_sp])
                        curr = curr[double_sp + 2:]
                        msloc = curr.find(' ms')

                        if msloc != -1 and curr[0:msloc] != '*':
                            times.append(float(curr[0:msloc]))
                        curr = curr[msloc + 1:]
                        double_sp = curr.find('  ')
                        hosts.append(curr[3:double_sp])
                        curr = curr[double_sp + 2:]
                        msloc = curr.find(' ms')
                        if msloc != 0 and curr[0:msloc] != '*':
                            times.append(float(curr[0:msloc]))

                    # Update hosts
                    if len(hosts_by_hop) < curr_hop:
                        hosts_by_hop.append(hosts)
                    else:
                        hosts_by_hop[curr_hop - 1].extend(hosts)

                    # Update times
                    if len(times_by_hop) < curr_hop:
                        times_by_hop.append(times)
                    else:
                        times_by_hop[curr_hop - 1].extend(times)
                count += 1

        # Start calculations
        hop_avgs = []
        hop_hosts = []
        hop_maxs = []
        hop_mins = []
        hop_meds = []

        for hop in hosts_by_hop:
            # Remove duplicate host
            host_list = "[("
            for host in hop:
                domain = host[0:host.find(' ')]
                if host_list.find(domain) != -1:
                    hop.remove(host)
                else:
                    host_list += "'" + host[0:host.find(' ')] + "', '" + host[host.find(' ') + 1:] + "',"
            host_list = host_list[0:len(host_list) - 1]
            host_list += ')]'
            if host_list == '[)]':
                host_list = 'No traceroute-detectable hosts'
            hop_hosts.append(host_list)

        for hop in times_by_hop:
            # Sort times array for easier math
            hop.sort()

        for hop in times_by_hop:
            # Compile statistics
            hop_total = 0
            for time in hop:
                hop_total += time
            if len(hop) != 0:
                hop_avgs.append(hop_total / len(hop))
                hop_maxs.append(hop[len(hop) - 1])
                hop_mins.append(hop[0])
                if len(hop) % 2 == 0:
                    hop_meds.append(hop[int(len(hop) / 2)])
                elif len(hop) % 2 == 1:
                    hop_meds.append(hop[int(len(hop) / 2)])
            else:
                hop_avgs.append(0)
                hop_maxs.append(0)
                hop_mins.append(0)
                hop_meds.append(0)

        data_frame = []

        if len(times_by_hop) == len(hosts_by_hop):
            hop_tracer = 0
            json_obj = []
            already_added = []

            for hop in hosts_by_hop:

                if hop_hosts[hop_tracer] != 'No traceroute-detectable hosts' and hops_seen[hop_tracer] not in already_added:
                    already_added.append(hops_seen[hop_tracer])
                    hop = 'hop '
                    trace = go.Box(
                        y=times_by_hop[hop_tracer],
                        name=hop + str(hop_tracer + 1)
                    )
                    data_frame.append(trace)
                    # Start formatting json file
                    json_obj.append({
                        'avg': hop_avgs[hop_tracer],
                        'hop': hops_seen[hop_tracer],
                        'hosts': hop_hosts[hop_tracer],
                        'max': hop_maxs[hop_tracer],
                        'med': hop_meds[hop_tracer],
                        'min': hop_mins[hop_tracer]
                    })
                    hop_tracer += 1
                else:
                    hop_tracer += 1

        else:
            print('For some reason, the two tracker arrays have different lengths')

        outputf = args.output + '.json'
        outputpic = args.output + '.pdf'
        with open(outputf, 'w') as jsonFile:
            json.dump(json_obj, jsonFile, indent=2)
        layout = go.Layout(title='Distribution of Traceroute Latency')
        
        fig = go.Figure(data=data_frame, layout=layout)
        fig.write_image(outputpic, engine='kaleido')



    else:
        # NO test directory provided // RUN traceroute
        print('Running traceroute and measuring latency...')
        target = args.target
        traceroute_counter = 1

        # Will end up being 2-dim matrices for collecting data
        hosts_by_hop = []
        times_by_hop = []
        hops_seen = []

        while traceroute_counter <= args.num_runs:
            # Outer TR loop
            # if traceroute_counter > 1:
            time.sleep(args.run_delay)

            tr_cmd = 'traceroute ' + target + ' > tr_output.txt'
            tr_out = ''
            os.system(tr_cmd)

            # txt_f will open the file and pull all needed data
            txt_f = open('tr_output.txt', 'r')
            count = 0

            while True:
                # File for each line of a txt file
                curr = txt_f.readline()

                if len(curr) < 1:
                    break

                if count > 0:
                    # Past first line
                    if count < 10:
                        curr_hop = int(curr[1:curr.find('  ')])
                    else:
                        curr_hop = int(curr[0:curr.find('  ')])

                    if curr_hop > args.max_hops:
                        break

                    hops_seen.append(curr_hop)
                    curr = curr[4:]
                    total_parsets = curr.count('(')

                    # If traceroute yields statistics, we will observe the 'ms' unit measurement
                    hosts = []
                    times = []

                    # Pull first host-time matchup
                    if total_parsets > 0:

                        double_sp = curr.find('  ')
                        msloc = curr.find(' ms')

                        hosts.append(curr[0:double_sp])
                        if curr[double_sp + 2:msloc] != '*':
                            times.append(float(curr[double_sp + 2:msloc]))
                        curr = curr[msloc + 1:]
                    total_parsets = curr.count('(')

                    if total_parsets == 0:
                        # Form: domain_(ip)__x_ms__x_ms__x_ms
                        msloc = curr.find(' ms')

                        if msloc != -1 and curr[4:msloc] != '*':
                            times.append(float(curr[4:msloc]))
                        curr = curr[msloc + 1:]
                        msloc = curr.find(' ms')
                        if msloc != -1 and curr[4:msloc] != '*':
                            times.append(float(curr[4:msloc]))

                    elif total_parsets == 1:
                        # Two total hosts for this single hop
                        if curr.find('(') < curr.find('  '):
                            # Form: domain_(ip)__x_ms_domain_(ip)__x_ms__x_ms
                            double_sp = curr.find('  ')
                            hosts.append(curr[3:double_sp])
                            curr = curr[double_sp + 2:]
                            msloc = curr.find(' ms')
                            if msloc != -1 and curr[0:msloc] != '*':
                                times.append(float(curr[0:msloc]))
                            curr = curr[msloc + 1:]
                            msloc = curr.find(' ms')
                            if msloc != -1 and curr[4:msloc] != '*':
                                times.append(float(curr[4:msloc]))
                        elif curr.find('(') > curr.find('  '):
                            # Form: domain_ip__x_ms__x_ms_domain_(ip)__x_ms
                            msloc = curr.find(' ms')
                            if msloc != -1 and curr[4:msloc] != '*':
                                times.append(float(curr[4:msloc]))
                            curr = curr[msloc + 1:]
                            double_sp = curr.find('  ')
                            hosts.append(curr[3:double_sp])
                            curr = curr[double_sp + 2:]
                            msloc = curr.find(' ms')
                            if msloc != -1 and curr[0:msloc] != '*':
                                times.append(float(curr[0:msloc]))

                    elif total_parsets == 2:
                        # Form: domain_(ip)__x_ms_domain_(ip)__x_ms_domain_(ip)__x_ms
                        double_sp = curr.find('  ')
                        hosts.append(curr[3:double_sp])
                        curr = curr[double_sp + 2:]
                        msloc = curr.find(' ms')

                        if msloc != -1 and curr[0:msloc] != '*':
                            times.append(float(curr[0:msloc]))
                        curr = curr[msloc + 1:]
                        double_sp = curr.find('  ')
                        hosts.append(curr[3:double_sp])
                        curr = curr[double_sp + 2:]
                        msloc = curr.find(' ms')
                        if msloc != 0 and curr[0:msloc] != '*':
                            times.append(float(curr[0:msloc]))

                    # Update hosts
                    if len(hosts_by_hop) < curr_hop:
                        hosts_by_hop.append(hosts)
                    else:
                        hosts_by_hop[curr_hop - 1].extend(hosts)

                    # Update times
                    if len(times_by_hop) < curr_hop:
                        times_by_hop.append(times)
                    else:
                        times_by_hop[curr_hop - 1].extend(times)
                count += 1
            traceroute_counter += 1

        # Start calculations
        hop_avgs = []
        hop_hosts = []
        hop_maxs = []
        hop_mins = []
        hop_meds = []

        for hop in hosts_by_hop:
            # Remove duplicate host
            host_list = "[("
            for host in hop:
                domain = host[0:host.find(' ')]
                if host_list.find(domain) != -1:
                    host_list = host_list
                else:
                    host_list += "'" + host[0:host.find(' ')] + "', '" + host[host.find(' ') + 1:] + "',"
            host_list = host_list[0:len(host_list) - 1]
            host_list += ')]'
            if host_list == '[)]':
                host_list = 'No traceroute-detectable hosts'
            hop_hosts.append(host_list)

        for hop in times_by_hop:
            # Sort times array for easier math
            hop.sort()

        for hop in times_by_hop:
            # Compile statistics
            hop_total = 0
            for time in hop:
                hop_total += time
            if len(hop) != 0:
                hop_avgs.append(hop_total / len(hop))
                hop_maxs.append(hop[len(hop) - 1])
                hop_mins.append(hop[0])
                if len(hop) % 2 == 0:
                    hop_meds.append(hop[int(len(hop) / 2)])
                elif len(hop) % 2 == 1:
                    hop_meds.append(hop[int(len(hop) / 2)])
            else:
                hop_avgs.append(0)
                hop_maxs.append(0)
                hop_mins.append(0)
                hop_meds.append(0)

        data_frame = []

        if len(times_by_hop) == len(hosts_by_hop):
            hop_tracer = 0
            json_obj = []
            already_seen = []

            for hop in hosts_by_hop:

                if hop_hosts[hop_tracer] != 'No traceroute-detectable hosts' and hops_seen[hop_tracer] not in already_seen:
                    already_seen.append(hops_seen[hop_tracer])
                    hop = 'hop '
                    trace = go.Box(
                        y=times_by_hop[hop_tracer],
                        name=hop + str(hop_tracer + 1)
                    )
                    data_frame.append(trace)
                    # Start formatting json file
                    json_obj.append({
                        'avg': hop_avgs[hop_tracer],
                        'hop': hops_seen[hop_tracer],
                        'hosts': hop_hosts[hop_tracer],
                        'max': hop_maxs[hop_tracer],
                        'med': hop_meds[hop_tracer],
                        'min': hop_mins[hop_tracer]
                    })
                    hop_tracer += 1
                else:
                    # Undetecetable hop
                    hop_tracer += 1

        else:
            print('For some reason, the two tracker arrays have different lengths')

        outputf = args.output + '.json'
        outputpic = args.output + '.pdf'
        with open(outputf, 'w') as jsonFile:
            json.dump(json_obj, jsonFile, indent=2)

        layout = go.Layout(title='Distribution of Traceroute Latency')
        fig = go.Figure(data=data_frame, layout=layout)
        fig.write_image(outputpic, engine='kaleido')

        os.system('rm tr_output.txt')
