#!/usr/bin/python

"""
verifier.py - v.01 2015-10-24 Mario Blazevic

This module provides a few classes to easily find Verification Records
and appropriate results directories.
"""

__version__ = '0.3'
__date__    = '2015-10-24'
__author__  = 'Mario Blazevic'

#--- CHANGES -----------------------------------------------------------

# 2015-10-24 v0.01: - First version


#-----------------------------------------------------------------------
#TODO:
# - nice printout from the shell
# - process VRec
#       - print pass rate - there can be multiple VRec inside one file
# - check if there are any failed test cases
# - process failed test cases
# - GUI


# --- IMPORTS ----------------------------------------------------------
import os
import csv
import inspect
import sys
import logging
import time
from HTMLParser import HTMLParser



#--- CONSTANTS ---------------------------------------------------------
WCDMA_DIR = "/home/mario/CV_work/examples/test_results_verifier/test1/WCDMA"
MSR_DIR   = "/home/mario/CV_work/examples/test_results_verifier/test1/MSR"
FORMAT    = "%(asctime)s %(levelname)s:%(message)s"


#--- GLOBALS ---------------------------------------------------------

found_pass_tested = False
pass_tested       = ""


loglevel          = "DEBUG"
logging_enabled   = True
logging_num_level = getattr(logging, loglevel.upper(), None)
log_to_file       = False
logging_file      = "/home/mario/CV_work/example.log"
#logger            = logging.getLogger('mylog')
if (logging_enabled is True):
    logging.basicConfig(level=logging_num_level, filename=logging_file, format=FORMAT)

#=== LOGGING ===========================================================
def configure_logging(loggin_to_file, loglevel):
    logging_num_level = getattr(logging, loglevel.upper(), None)
    if (loggin_to_file is True):
        logging.basicConfig(level=logging_num_level, filename=logging_file, 
                            format=FORMAT)
    else:
        logging.basicConfig(level=logging_num_level, format=FORMAT)


#=== CLASSES ===========================================================


class Task():
    """
    A class that represents a single task
    """
    def __init__(self, software, rat, project, radio, position):
        self._software = str(software.split("_")[0])
        
        self._rat, self._rattag     = determine_rat(rat)
        if (self._rat == "WCDMA" and project[0] == "M"):
            self._project = "W" + project[1:]
        else:
            self._project  = project
        
        self._radio    = radio
        self._position = position
        self._vrec     = "No path"
        self._resultdir= "No path"
        self._pass_rate = ""
        
    def __str__(self):
        return "SW: " + self._software + ", RAT: " + self._rat + \
               " " + self._project + " " + self._radio + " " + \
               self._position + "\n" + "VRec: " + self._vrec + "\n" + \
               "Result dir: " + self._resultdir + "\n" + self._pass_rate
    
    def get_software(self):
        return self._software
    
    def get_rat(self):
        return self._rat
        
    def get_project(self):
        return self._project
        
    def get_position(self):
        return self._position
        
    def get_radio(self):
        return self._radio
        
    def get_vrec(self):
        return self._vrec
        
    def get_resultdir(self):
        return self._resultdir
        
    def get_rattag(self):
        return self._rattag
        
    def set_vrec(self, vrec):
        self._vrec = vrec
        
    def set_resultdir(self, resultdir):
        self._resultdir = resultdir
        
    def set_rattag(self, rattag):
        self._rattag = rattag
        
    def process_vrec(self):
        global pass_tested
        if (self._vrec is not "No path"):
            fin = open(self._vrec, "r")
            parser = MyHTMLParser()
            parser.feed(fin.read())
            fin.close()
            self._pass_rate = pass_tested
            pass_tested = ""
        
        

#-----------------------------------------------------------------------

class MyHTMLParser(HTMLParser):
#    def handle_starttag(self, tag, attrs):
#        print "Encountered a start tag:", tag
#    def handle_endtag(self, tag):
#        print "Encountered an end tag :", tag
    def handle_data(self, data):
        #print "Encountered some data  :", data
        parsing(data)

#-----------------------------------------------------------------------

#=== FUNCTIONS =========================================================

def PrintFrame():
    """ Returns __FILE__ __LINE__ and calling function """
    callerframerecord = inspect.stack()[1]    # 0 represents this line
                                              # 1 represents line at caller
    frame = callerframerecord[0]
    info = inspect.getframeinfo(frame)
    return "File:" + str(info.filename) + " line:" + str(info.lineno) + \
           " function: " + str(info.function)


def parsing(data):
    global found_pass_tested, pass_tested
    if (found_pass_tested is False):
        if (("Pass" in data) and ("Tested" in data)):
            found_pass_tested = True
        else:
            return
    else:
        if ("/" in str(data)):
            pass_tested = "Passed / Tested:\n" + str(data)
            found_pass_tested = False


def determine_rat(entry):
    """
    Determine which RAT was passed. Defaults to LTE-TDD if something
    unrecognized is passed to this function
    """
    if (entry == "W" or entry == "WCDMA"):
        rat = "WCDMA"
        tag = "w"
    elif (entry == "C" or entry == "CDMA"):
        rat = "CDMA"
        tag = "c"
    elif (entry == "G" or entry == "GSM"):
        rat = "GSM"
        tag = "g"
    elif (entry == "L" or entry == "LTE"):
        rat = "LTE"
        rat = "l"
    elif (entry == "MM L+L"):
        rat = "MM LL"
        tag = "mmll"
    elif (entry == "MM LC"):
        rat = "MM LC"
        tag = "mmlc"
    elif (entry == "MM L+G"):
        rat = "MM LG"
        tag = "mmlg"
    elif (entry == "MM L+W"):
        rat = "MM LW"
        tag = "mmlw"
    elif (entry == "MM W+G"):
        rat = "MM WG"
        tag = "mmwg"
    else:
        # assume LTE-TDD
        rat = "LTE-TDD"
        tag = "tdd"
    logging.debug("%s Entry: %s, determined rat: %s, tag: %s" %(PrintFrame(), str(entry), str(rat), str(tag)))
    return (rat, tag)
    
    
def insert_task(alist, task):
    found_place = False
    for idx in range(len(alist)):
        if (alist[idx].get_software() == task.get_software()):
            alist.insert(idx, task)
            found_place = True
            break
    if (found_place is False):
        alist.append(task)

def get_tasks_from_csv(file_in):
    wcdma_list = []
    msr_list   = []
    with (open(file_in, 'r')) as fin:
        idx = 0
        reader = csv.reader(fin)
        for row in reader:
            # table rows are:
            # software, rat, project, radio, position
            idx += 1
            # print "DEBUG::", row[0], row[1], row[2], row[3], row[4]
            logging.debug("Read from table--> sw: %s, rat: %s, project: %s, radio: %s, position: %s" 
                          %(str(row[0]), str(row[1]), str(row[2]), str(row[3]), 
                            str(row[4]) ) )
            task = Task(row[0], row[1], row[2], row[3], row[4])
            if (task.get_rat() == "WCDMA"):
                insert_task(wcdma_list, task)
            else:
                insert_task(msr_list, task)
            if (idx == 2):
                break
                
    return (wcdma_list, msr_list)
    
    
def get_results_for_same_sw(task_list,
                            first = 0,
                            last = -1):
    """
    Fetch results for same SW build. Exploits the fact that list is sorted
    """
    if (last < 0):
        last = len(task_list) - 1
    if (last < first):
        logging.info("List is empty")
        return
    
    logging.debug("%s First index of the list: %d Last index: %d " %(PrintFrame(), first, last))
    rootdir = ""
    if (task_list[first].get_rat() == "WCDMA"):
        rootdir = WCDMA_DIR
    else :
        rootdir = MSR_DIR
        
    # find the correct dir and store it
    path_found = False
    sw = task_list[first].get_software()
    logging.debug("%s Searching for %s software" %(PrintFrame(), str(sw)))
    directory_name = "app_" + str(sw)+ "__WORK"
    for element in os.listdir(rootdir):
        if (element == directory_name):
            sw_path = os.path.join(rootdir, element)
            if (os.path.isdir(sw_path)):
                path_found = True
                logging.debug("%s Path found: %s" %(PrintFrame(), str(sw_path)))
                break
            else:
                logging.debug("%s Interesting - found not dir matching searching criteria: %s" 
                              %(PrintFrame(), str(sw_path)))
    
    idx = first
    if (path_found is True):
        # read from the disk once
        contents = os.listdir(sw_path)
        while (idx <= last):
            # loop for all tasks having same SW
            radio    = task_list[idx].get_radio()
            project  = task_list[idx].get_project()
            position = task_list[idx].get_position()
            rat      = task_list[idx].get_rattag()
            tdd = False
            if ("mm" in rat):
                rattag = rat
            elif ("tdd" in rat):
                rattag = "rul"
                tdd = True
            else:
                rattag = "ru" + str(rat)
            logging.debug("%s radio: %s, project: %s, position: %s, rat: %s" 
                          %(PrintFrame(), str(radio), str(project), str(position), str(rat)))
            for entry in contents:
                # search the contents of the SW directory
                lowered = str(entry).lower()
                if ((radio in entry) and (project in entry) and (position in entry)):
                    # radio, project and position (node_n_rus) MUST be in directory element
                    if (tdd is True):
                        # we have TDD so tdd should be there
                        if ("tdd" not in lower):
                            logging.debug("%s Matching rat, radio, sw, position - but its not TDD?" %(PrintFrame()))
                            continue
                    # else we do not have TDD radio or tdd tag is present so carry on...
                    radio_path = os.path.join(sw_path, entry)
                    if (os.path.isdir(radio_path)):
                        if (rattag in entry):
                            # result directory MUST have rat tag
                            task_list[idx].set_resultdir(radio_path)
                            logging.debug("%s Adding path: %s to the result dir" %(PrintFrame(), str(radio_path)))
                    elif (os.path.isfile(radio_path)):
                        # there could be multiple VRec's inside one file, so we cannot search
                        # for rat here... It is sufficient to search by radio, project and position
                        # as no other option is viable
                        if (("vrec" in lowered) and ("html" in lowered)):
                            task_list[idx].set_vrec(radio_path)
                            logging.debug("%s Adding path: %s to the VRec" 
                                         %(PrintFrame(), str(radio_path)))
                    else:
                        logging.critical("%s Not a file nor dir: %s" 
                                         %(PrintFrame(), str(radio_path)))
                elif(False):
                    pass
                else:
                    pass
                # end of for loop     
            idx += 1
    else:
        logging.debug("%s No path found for: %s build" %(PrintFrame(), str(sw)))
    return
    

def fetch_logs_by_sw(taks_list):
    idx_first = 0
    idx_last = len(taks_list)
    if (idx_last > 0):
        idx = 0
        curr_sw = taks_list[idx].get_software()
        temp_last = 0
        while (idx < (idx_last - 1)):
            if (curr_sw == taks_list[idx + 1].get_software()):
                temp_last = idx + 1
            else:
                get_results_for_same_sw(taks_list, idx_first, temp_last)
                idx_first = idx + 1
                curr_sw = taks_list[idx + 1].get_software()
            idx += 1
        get_results_for_same_sw(taks_list, idx_first, idx)
    return


if __name__ == "__main__":
    print ""
    for elem in sys.argv:
        print elem
    print "\n\n"
    file_in = "/home/mario/CV_work/examples/example_R61_hansoft_tasks__test1.csv"
    wcdma_list, msr_list = get_tasks_from_csv(file_in)
        
    # determine which SW builds we have
    fetch_logs_by_sw(wcdma_list)
    fetch_logs_by_sw(msr_list)
    
    print "\n\n###############################################"
    print "$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$"
    print "WCDMA list"
    for task in wcdma_list:
        task.process_vrec()
        print task
    
    print "\n"
    print "###############"
    print "MSR list"
    for task in msr_list:
        task.process_vrec()
        print task
        print ""












