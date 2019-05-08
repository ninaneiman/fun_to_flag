import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm
import os, sys


class flag_out(object):
    def __init__(self, ant1, ant2, spw, chan, scan):
        self.ant1=np.array(ant1, int)
        self.ant2=np.array(ant2, int)
        self.spw=np.array(spw, int)
        self.chan=np.array(chan, int)
        self.scan=np.array(scan, int)
        self.ants=np.concatenate((np.array(ant1, int),np.array(ant2, int)),axis=0)

    def __repr__(self):
        return "<All output in sequrnce: %s, size: %d>" % (len(self.ant1))



def read_output(myfile):
    
    h = open("%s"%myfile,'r')                                                                                                                                                           
                                                                                                                                                                                        
    ant1=[]                                                                                                                                                                             
    ant2=[]                                                                                                                                                                             
    spw=[]                                                                                                                                                                              
    chan=[]                                                                                                                                                                             
    scan=[]                                                                                                                                                                             
                                                                                                                                                                                        
    lines=[]
    all_lines=[]
    
    for line in h:
        if ('locate+' in line) and ('Scan' in line):
            tail=line.split('INFO')[1]
            all_lines.append(line)
            if tail in lines:                                                                                                                                                           
                do=0                                                                                                                                                                    
            else:                                                                                                                                                                       
                lines.append(tail)                                                                                                                                                      
                ant_line=line.split('BL=ea')
                scan_line=ant_line[0].split('Scan=')
                scan.append(scan_line[1].split(' ')[0])
                ant1.append(ant_line[1].split('@')[0])
                ant2_l=ant_line[1].split(' ea')[1]
                ant2.append(ant2_l.split('@')[0])
                spw_l=ant_line[1].split('Spw=')[1]
                spw.append(spw_l.split(' ')[0])
                chan_l=spw_l.split('Chan=')[1]
                chan.append(chan_l.split(' ')[0])
    
    flags=flag_out(ant1, ant2, spw, chan, scan)
    print 'ALL LINES:', len(all_lines), 'NO REPEATERS', len(lines)
    return flags


def out_plot(flags):
    fig = plt.figure()

    x1=0.03
    y1=0.1
    gap=0.07
    l1=0.45
    h1=0.4

    rect1 = [x1, y1+h1+gap, l1, h1]
    rect2 = [x1+l1+gap, y1+h1+gap, l1, h1]
    rect3 = [x1, y1, l1, h1]
    rect4 = [x1+l1+gap, y1, l1, h1]

    ax11 = fig.add_axes(rect1)
    ax21 = fig.add_axes(rect2)
    ax31 = fig.add_axes(rect3) 
    ax41 = fig.add_axes(rect4)

    nums1=ax11.hist(flags.spw, bins=27, color='g')
    ax11.set_title('Spectral windows')

    nums2=ax21.hist(flags.ants, bins=27, color='r')
    ax21.set_title('Antennas')

    nums4=ax31.hist(flags.scan, bins=100, color='y')
    ax31.set_title('Scans')

    nums3=ax41.hist(flags.chan, bins=30, color='b')
    ax41.set_title('Channels')

    plt.gcf().set_size_inches(9, 7)
    plt.plot()
    return

##Calculating which are the most frequent object(thing)
def fr_calc(array, num_object, percents=1., outfile=None):
    size=[]
    for i in range(1,num_object):
        calc=array[(array == i)]
        size.append([i,len(calc)])

    den=100./percents
    threshold=len(array)/den
    #print 'threshold=', threshold
    size_a=np.array(size, int)
    size_new=size_a[(size_a[:,1] > threshold)]
    size_new.view('i8,i8').sort(order=['f1'], axis=0)
    
    for k in range(1,len(size_new)+1):
        #print size_new[len(size_new)-k]
        if outfile != None:
            outfile.write('%s \n'%size_new[len(size_new)-k])
            
    new_size=np.array(list(reversed(size_new)))
    print 'lim:', threshold,'total # to flag:', np.shape(new_size)[0], 'max:', np.amax(new_size[:,1]), 'min:', np.amin(new_size[:,1])
    return new_size

def freq_time_ant(flags, ant_num):
    
    chan_ant1=flags.chan[(flags.ant1 == ant_num)]
    chan_ant2=flags.chan[(flags.ant2 == ant_num)]

    chan_ant=np.concatenate((chan_ant1, chan_ant2), axis=0)
    
    scan_ant1=flags.scan[(flags.ant1 == ant_num)]
    scan_ant2=flags.scan[(flags.ant2 == ant_num)]

    scan_ant=np.concatenate((scan_ant1, scan_ant2), axis=0)
    
    return chan_ant, scan_ant


def print_tilda(array_x, spw, sep=',', ar_chan=False):
    if (sep==';') or (ar_chan is False):
        spw=''
    else:
        spw=str(spw)+':'
    my_array=array_x[:,0]
    array=sorted(my_array)
    array_line=''
    if len(array) > 1:
        if array[0]+1==array[1]:
            if len(array)>2:
                if array[0]+2!=array[2]:
                    array_line='%s~'%array[0]
                else:
                    array_line='%s'%array[0]
        else:
            array_line='%s%s%s'%(array[0],sep,spw)

    for i in range(1,len(array)-1):
        if (array[i]-1==array[i-1]) and (array[i]+1==array[i+1]):
            if array_line[len(array_line)-1]=='~':
                do=0
            else:
                array_line=array_line+'~'
        else:
            if (array[i]+1==array[i+1]) and (array[i]-1!=array[i-1]):
                array_line=array_line+'%s~'%array[i]
            else:
                array_line=array_line+'%s%s%s'%(array[i],sep,spw)

    array_l=array_line+'%s'%array[len(array)-1]
    return array_l



def print_output(spw,ant,chan_a,scan_a, sep=',', print_scan=True):
    if ant < 10:
        mode_ant='mode=\'manual\' antenna=\'ea0%s\''%(ant)
    else:
        mode_ant='mode=\'manual\' antenna=\'ea%s\''%(ant)
    
    chan_l=print_tilda(chan_a,sep=sep,spw=spw,ar_chan=True)
    scan_l=print_tilda(scan_a,sep=sep,spw=spw)
        
    if print_scan is True:
        command=mode_ant+' spw=\'%s:%s\''%(spw,chan_l)+' scan=\'%s\'\n'%scan_l
    else:
        command=mode_ant+' spw=\'%s:%s\''%(spw,chan_l)+'\n'
    print command
    return command
    #outfile.write('%s'%command)
    
    
def make_command(namefile, casalogname=False, sep=',', print_scan=True):
    
    flags_in=read_output(namefile)
    out_plot(flags_in)
    plt.show()
   
    spw=[]
    for j in flags_in.spw:
        if j in spw:
            kk=2
        else:
            spw.append(j)
            
    if casalogname == True:
        headd='casa'
        outdate=namefile.split('-')[1]
        outnum=outdate[2].split('.')[0]
    else:
        os.system('date \"+%Y-%m-%d %H%M%S\" > mytime')
        kk=open("mytime",'r')
        mytime=kk.read()
        outdate=mytime.split(' ')[0]
        outnum=mytime.split(' ')[1]
        headd=namefile.split('.')[0]
        
        

    g = open("cmd_%s-%s-%s.txt"%(headd,outdate,outnum),'w+')
    
    for spw_num in spw:
        
        print 'Spectral window:', spw_num
        ant1=flags_in.ant1[(flags_in.spw==spw_num)]
        ant2=flags_in.ant2[(flags_in.spw==spw_num)]
        chans=flags_in.chan[(flags_in.spw==spw_num)]
        scans=flags_in.scan[(flags_in.spw==spw_num)]
        spws=flags_in.spw[(flags_in.spw==spw_num)]
        
        flags=flag_out(ant1, ant2, spws, chans, scans)
        out_plot(flags)

        print 'antennas:'
        ants_list=fr_calc(flags.ants, 29, percents=1)

        for i in ants_list[:,0]:
            chan_ant, scan_ant=freq_time_ant(flags, i)

            plt.hist(chan_ant, bins=30, color='b')
            plt.title('ANT %s: Channels'%i)
            plt.show()
            plt.hist(scan_ant, bins=30, color='y')
            plt.title('ANT %s: Scans'%i)
            plt.show()

            print 'ANTENNA %s'%i
            print 'cols:', ants_list[(ants_list[:,0]==i)]
            print 'Channels:'
            chan_list=fr_calc(chan_ant, 62, percents=0.5)
            print 'scans:'
            scan_list=fr_calc(scan_ant, 172,percents=0.5)

            command=print_output(spw_num,i,chan_list,scan_list,sep=sep, print_scan=print_scan)

            g.write(command)
    g.close()
