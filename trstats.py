import sys, os
import argparse
import json


# Author: Josh Messitte (811976008)
# CSCI 6760 Project 1: Traceroute

# Main method
if __name__ == '__main__':


    # Set up argument parsing automation
    prog = 'python3 trstats.py'
    descr = 'Python Wrapper Script to Analyze Traceroute Performance'
    parser = argparse.ArgumentParser(prog = prog, description = descr)
    parser.add_argument('-o','--output',type = str, default = 'output.json', required = True, help = 'Path and Name of outpt JSON')
    parser.add_argument('-n','--num_runs',type = int, default = 10, help = 'Number of times traceroute will run')
    parser.add_argument('-d','--run_delay',type = int, default = 0, help = 'Number of seconds to wait between two condsectuive runs')
    parser.add_argument('-m','--max_hops',type = int, default = 100, help = 'Number of times traceroute will run')
    parser.add_argument('-t','--target',type = str, default = 'www.yahoo.co.jp', help = 'A target domain name or IP address')
    parser.add_argument('--test', '--test', type = str, default = None, help = 'Directory containing num_runs text files, each with traceroute output. If present, override and do not run traceroute.')

    # Parse the given arguments
    args = parser.parse_args()
        
    # A directiory of text files was provided // this conditional branch executes // DON'T run traceroute
    if args.test != None:
        print ('Test directory was provided')

    # NO test directory provided // RUN traceroute
    else:
        print('Running traceroute and measuring latency...')
        target = args.target
        traceroute_counter = 1

        # Will end up being 2-dim matrices for collecting data
        hosts_by_hop = []
        times_by_hop = []
        
        # Overall traceroute loop
        while traceroute_counter < args.num_runs:

            #print("traceroute run #:", traceroute_counter)
            tr_cmd = 'traceroute ' + target + ' > tr_output.txt'
            tr_out = ''
            os.system(tr_cmd)

            # txt_f will open the file and pull all needed data
            txt_f = open('tr_output.txt','r')
            count = 0
            
            # Iterate over file line by line
            while True:
            
                curr = txt_f.readline()

                # End of traceroute output
                if len(curr) < 1:
                    break
                
                # If past the first line
                if count > 0:
                    curr_hop = int(curr[0:2])
                    curr = curr[3:]
                    double_space = curr.find('  ')
                    millisecond = curr.find(' ms')
                    open_par_index = curr.find('(')
                
                    # If traceroute yields statistics, we will observe the 'ms' unit measurement
                    hosts = []
                    times = []
                    # Pull first host-time matchup
                    if ( millisecond != -1 )or( open_par_index != -1 ):

                        if open_par_index != -1:
                            hosts.append(curr[0:double_space])
                        if millisecond != -1:
                            times.append(curr[double_space+2:millisecond])
                            curr = curr[millisecond+1]

                    close_par_index = curr.find(')')
                    
                    # There is a different host within THIS hop
                    if close_par_index != -1:
                        hosts.append(curr[4:close+par_index+1])
                        millisecond = curr.find(' ms')
                        if millisecond != -1:
                            times.append(curr[close_par_index+3:millisecond])
                            curr = curr[millisecon+1]

                    # The rest are ms time readings
                    else:
                        
                        

                    # Update hosts
                    if len(hosts_by_hop) < curr_hop:
                        hosts_by_hop.append(hosts)
                    else:
                        hosts_by_hop[curr_hop-1].extend(hosts)

                    # Store each hop time in ms
                    
                    i = 0
                    #print("curr:", curr, "hop: ", curr_hop)
                    while i < 3:
                        index_of_ms = curr.find('ms')
                        if(index_of_ms == -1):
                            break
                        next_time = float(curr[3:index_of_ms-1])
                        curr = curr[index_of_ms+1:]
                        times.append(next_time)
                        i += 1

                    # Update times
                    if len(times_by_hop) < curr_hop:
                        times_by_hop.append(times)
                    else:
                        times_by_hop[curr_hop-1].extend(times)

                count += 1
                
            traceroute_counter += 1
            
        print('end of both loops')

        for hop in hosts_by_hop:
            for host in hop:
                print("Host:",host)

        for hop in times_by_hop:
            for time in hop:
                print("Time:",time)
                
        
