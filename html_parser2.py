# -*- coding: utf-8 -*-
"""
Created on Sat Nov  7 11:12:56 2015 Mario Blazevic

This module provides a methods to extract informations from HTML based VRec's
"""

__version__ = '0.1'
__date__    = '2015-11-07'
__author__  = 'Mario Blazevic'

#--- CHANGES -----------------------------------------------------------

# 2015-11-07 v0.01: - First version


#-----------------------------------------------------------------------
#TODO:
# - nice printout from the shell
# - process VRec
#       - print pass rate - there can be multiple VRec inside one file
# - check if there are any failed test cases
# - process failed test cases
# - GUI


# --- IMPORTS ----------------------------------------------------------
from BeautifulSoup import *
import os
#-----------------------------------------------------------------------


#--- CONSTANTS ---------------------------------------------------------
#-----------------------------------------------------------------------

#--- GLOBALS -----------------------------------------------------------
#-----------------------------------------------------------------------

#=== CLASSES ===========================================================

class MyVRecEntry():
    """
    A class that represents single RAT in VRec - that is single column
    """
    def __init__ (self):
        self._description = ""
        self._pass_rate   = ""
        self._failed_list = []
        self._known_list  = []
        self._untested    = []
        self._radio       = ""
        self._serial      = ""
    
    def __str__(self):
        return ("Description:" + str(self._description) + "\nPass rate:" + str(self._pass_rate) + 
                "\nFailed:\n" + repr(self._failed_list) + "\nKnown issues:\n" + repr(self._known_list))
        
    def set_pass_rate(self, pass_rate):
        self._pass_rate = str(pass_rate)
        
    def set_description(self, description):
        self._description = description
        
    def update_failed(self, test):
        self._failed_list.append(test)
        
    def update_known(self, test):
        self._known_list.append(test)
        
    def update_untested(self, test):
        self._untested.append(test)
        
    def get_description(self):
        return self._description


#=== FUNCTIONS =========================================================
    

def parse_html(path, rat = None):
    """
    Input : Takes path to VRec and desired RAT.
            If no RAT is specified takes the first found entry in the VRec.
    Output: Extracts all relevant data (pass rate, list of files which failed) for specified RAT
            and returns it in a dictionary
            If no file found or no RAT found or specified RAT is not found returns None.
    """
    vrec_list = []
    read_text = ""
    try:
        fin = open(path)
        for line in fin:
            read_text += line.strip()
        fin.close()
    except IOError:
        print ("IOError on given file:", path)
        
    soup = BeautifulSoup(read_text)
    tables = soup.findAll("table")
        
    table = None
    for tab in tables:
        # only table with testcases has 'caption'
        for row in tab.findAll("caption"):
            if ("Verification Record" in str(row)):
                table = tab
            break
        if (table != None):
            break
    
    header = table.findAll("th")
    vrec_no = 0

    # determine number of columns
    # first column is testcase and last is comments
    if (len(header) >= 3):
        vrec_no = len(header) - 2
        for idx in range(vrec_no):
            new_vrec = MyVRecEntry()
            new_vrec.set_description(header[1 + idx].string)
            vrec_list.append(new_vrec)
    else:
        # debug inof
        return
        pass
    
    idx = 0
    rows = table.findAll("tr")
    while (idx < len(rows)):
        if ("Pass / Tested" in str(rows[idx])):
            # idx += 1
            break
        idx += 1
    # debug info
    if (idx >= len(rows)):
        print "Danger"
        return
    limit = 0
    
    jdx = 1
    col = rows[idx].findAll("td")
    for vrec in vrec_list:
        #print col[jdx].string
        vrec.set_pass_rate(col[jdx].string)
        jdx += 1        
    
    idx += 1
    for row in rows[idx:]:
        col = row.findAll("td")
        jdx = 1
        for vrec in vrec_list:
#            print "col[jdx]"
#            print col[jdx]
#            print
#            print "col[jdx].fin"
#            print col[jdx].find("a")
#            print
            link = col[jdx].find("a")
            if (link is None):
                verdict = "UNTESTED"
            else:
                verdict = col[jdx].find("a").string
            if (verdict == "FAILED"):
                vrec.update_failed(str(col[0].string))
                #print col[jdx].a['href']
            elif (verdict == "PASSED"):
                pass # for now
            elif (verdict == "KNOWN ERROR"):
                vrec.update_known((str(col[0].string), str(col[-1].string)))
                #print col[jdx].a['href']
            elif (verdict == "UNTESTED"):
                vrec.update_untested(str(col[0].string))
            else:
                print "Unknown testcase verdict:", verdict
            
            jdx += 1

        #limit += 1
        if (limit > 2):
            break
        
        
    # determine rat
    if (type(rat) == type("")):
        #rat = rat.lower()
        vrec_idx = -1
        idx = 0
        for vrec in vrec_list:
            if (rat in vrec.get_description()):
                vrec_indx = idx
            if ((rat in vrec.get_description()) and ("air" in vrec.get_description())):
                vrec_idx = idx
            idx += 1
        if (vrec_idx != -1):
            return vrec_list[vrec_idx]
        else:
            print "Could not find this rat", rat
            
    else:
        return vrec_list


if (__name__ == "__main__"):
    lista = parse_html("/home/mario/CV_work/examples/test_results_verifier/test1/MSR/app_R61BL__WORK/VRec__app_R61BL__CV_RUS01B2_2-RUL-Maxwell1_rus3a_M16B__rul.html")
    #lista = parse_html("/home/mario/CV_work/examples/TerassVR2.html", "rug")
    print "×××××××××××××××××××××××××××××××××××"
    for element in lista:
        print element