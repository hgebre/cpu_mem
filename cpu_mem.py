#!/bin/env python
#***************************************************************************************************
# usage: python cpu_mem (optional outputfilename)
# Change Log
#
# Date     Person       Description
# -------- ------------ -----------------------------------------------------------------------------
# 04/25/14 Gebre-amlak   v1.0 This script generates cpu, memory and name of porcess
# 01/5/16  Gebre-amlak   v1.1 Update to modify the alert level
#
#***************************************************************************************************

import time
import string
import sys
import os
import subprocess
import platform
import commands
import psutil
import socket

#change directory 
os.chdir('/prod01/alert_central')
sys.path.append('/prod01/tools/mediation/')
sys.path.append('/prod01/bin/')
import AlertCentralLib

cfgdir = '/prod01/alert_central/tables/'
plat = platform.system()
scriptDir = sys.path[0]
pid = psutil.pids()

platform_file = sys.argv[1]

platforms = os.path.join(cfgdir, platform_file)
pDict = {}
ip = socket.gethostname()
cpu_file = 'cpu_alert.dat'
mem_file= 'mem_alert.dat'

cpu_temp = os.path.join(cfgdir, cpu_file)
mem_temp = os.path.join(cfgdir, mem_file)
def getPlatform(ip):
    """
    #***********************************************************************************************
    # This method will take platform file and load it to dictionary for platform use
    # The key/value pair is based on the config file
    #***********************************************************************************************
    """
    with open(platforms) as platform:
        pDict=dict((key, str(value)) for key, value in (line.split('=') for line in platform))
        print pDict
    if(pDict[ip] != ''):
        return pDict[ip]
    else:
        return "NA"


def get_cpumem(pid):
    """
    #***********************************************************************************************
    # This function takes in process ID (PID) and
    # it returns indexed values of PID as int, CPU as float, Memory as float and the process name 
    #***********************************************************************************************
    """

    d = [i for i in commands.getoutput("ps aux").split("\n")
        if i.split()[1] == str(pid)]

    return (int(d[0].split()[1]),float(d[0].split()[2]), float(d[0].split()[3]),d[0].split()[10]) if d else None


def get_hostname():
    """
    #***********************************************************************************************
    # This function gets the hostname 
    #
    #***********************************************************************************************
    """
    if socket.gethostname().find('.')>=0:
        name=socket.gethostname()
    else:
        name=socket.gethostbyaddr(socket.gethostname())[0]

    return name

print("PID\t%CPU\t%MEM\tNAME")
for line in pid:
    try:
        x = get_cpumem(line)
        if not x:
            exit(1)
        print("%i\t%.2f\t%.2f\t%s" % x)
        cpu =  x[1]
        mem =  x[2]
        cmd =  x[3]
        #print cmd ,"PID:",line

        if (cpu > 99.99):
            aID = 1006
            p = getPlatform(socket.gethostname())
            p = p.replace("\n", "")
            d={ 'AlertId': aID, 'Platform': p, 'Host': socket.gethostname()}
            AlertCentralLib.getAlertID(d)

            if('AlertText' in d and d['AlertText'] >''):
                aText = d['AlertText']
                aText =  aText + " Name: " + cmd + " PID: " + str(line)
                d['AlertText'] = aText
                print AlertCentralLib.postAlert(d)

        if (mem > 99.99):
            aID = 1009
            p = getPlatform(socket.gethostname())
            p = p.replace("\n", "")
            d={ 'AlertId': aID, 'Platform': p,  'Host': socket.gethostname()}
            AlertCentralLib.getAlertID(d)

            if('AlertText' in d and d['AlertText'] >''):
                aText = d['AlertText']
                aText =  aText + " Name: " + cmd + " PID: " + str(line)
                d['AlertText'] = aText
                print AlertCentralLib.postAlert(d)

    except KeyboardInterrupt:
        print
        exit(0)

