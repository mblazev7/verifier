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
import sys
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
        self._position = ""
        self._pass_rate   = ""
        self._failed_list = []
        self._known_list  = []
        self._untested    = []
        self._radio       = ""
        self._serial      = ""
        self._krc         = ""
        self._revision    = ""
        self._prod_date   = ""
    
    def __str__(self):
        return ("Radio: " + str(self._radio) + "\n" +
                "Position: " + str(self._description) + "\nPass rate: " + str(self._pass_rate) + 
                "\nFailed:\n" + self._nice_failed() + "\nKnown issues:\n" + self._nice_known())
        
    def set_pass_rate(self, pass_rate):
        self._pass_rate = str(pass_rate)
        
    def set_position(self, description):
        self._description = description
        
    def update_failed(self, test):
        self._failed_list.append(test)
        
    def update_known(self, test):
        self._known_list.append(test)
        
    def update_untested(self, test):
        self._untested.append(test)
        
    def get_position(self):
        return self._description
        
    def set_radio(self, radio):
        self._radio = radio
        
    def get_radio(self):
        return self._radio
        
    def set_serial(self, serial):
        self._serial = serial
        
    def get_serial(self):
        return self._serial
        
    def set_krc(self, krc):
        self._krc = krc
        
    def get_krc(self):
        return self._krc
        
    def set_revision(self, revision):
        self._revision = revision
        
    def get_revision(self):
        return self._revision
        
    def set_date(self, date):
        self._prod_date = date
        
    def get_date(self):
        return self._prod_date
        
    def _nice_known(self):
        printout = ""
        for failed in self._known_list:
            printout += str(failed[0]) + " - " + str(failed[1]) + "\n"
        return printout
        
    def _nice_failed(self):
        printout = ""
        for failed in self._failed_list:
            printout += str(failed[0])
            if (len(str(failed[1] >= 2))):
                printout += " - " + str(failed[1])
            printout += "\n"
        return printout


#=== FUNCTIONS =========================================================


def get_comments(mhweb, descr):
    """
    Input : list of links to the mhweb
            list of descriptions in the entry
    Return: string with matching 
    """
    temp_descr = []
    for elem in descr:
        # eliminate empty entries
        if (elem.string is not None):
            temp_descr.append(elem)
    descr = temp_descr
    comment_str = ""
    tr_idx = 0
    have_trs = False
    if (len(mhweb) == len(descr)):
        have_trs = True
    for entry in descr:
        if (entry.string is not None):
            comment_str += str(entry.string)
            if (have_trs is True):
                comment_str += (" " + str(mhweb[tr_idx].string) + " " +
                                str(mhweb[tr_idx]['href']))
                tr_idx += 1
            comment_str += ";"
    return comment_str


def parse_html(path, rat = None):
    """
    Input : Takes path to VRec and desired RAT.
            Optional: Specified RAT
    Output: Extracts all relevant data (pass rate, list of files which failed) for specified RAT
            and returns it in a dictionary
            If no RAT specified returns entire list of VRec's found in the file
            If specified RAT is found returns data only for that RAT
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
            new_vrec.set_position(header[1 + idx].string)
            vrec_list.append(new_vrec)
    else:
        # debug inof
        print "Danger, danger, danger..."
        return None
    
    idx = 0
    rows = table.findAll("tr")
    product_name       = ""
    product_number     = ""
    product_revision   = ""
    serial_number      = ""
    production_date    = ""
    while (idx < len(rows)):
        if ("Pass / Tested" in str(rows[idx])):
            break
        elif ("productName" in str(rows[idx])):
            product_name = str(rows[idx].findAll("td")[1].string)
        elif ("productNumber" in str(rows[idx])):
            product_number = str(rows[idx].findAll("td")[1].string)
        elif ("productRevision" in str(rows[idx])):
            product_revision = str(rows[idx].findAll("td")[1].string)
        elif ("serialNumber" in str(rows[idx])):
            serial_number = str(rows[idx].findAll("td")[1].string)
        elif ("productionDate" in str(rows[idx])):
            production_date = str(rows[idx].findAll("td")[1].string)
        idx += 1
    # debug info
    stored_idx = idx
    if (stored_idx >= len(rows)):
        print "Danger"
        return None
    
    jdx = 1
    col = rows[stored_idx].findAll("td")
    for vrec in vrec_list:
        #print col[jdx].string
        vrec.set_pass_rate(col[jdx].string)
        vrec.set_radio(product_name)
        vrec.set_krc(product_number)
        vrec.set_revision(product_revision)
        vrec.set_serial(serial_number)
        vrec.set_date(production_date)
        jdx += 1        
    
    stored_idx += 1
    for row in rows[stored_idx:]:
        col = row.findAll("td")
        jdx = 1
        for vrec in vrec_list:
            link = col[jdx].find("a")
            if (link is None):
                verdict = "UNTESTED"
            else:
                verdict = str(col[jdx].find("a").string)
            
            if ((verdict == "FAILED") or (verdict == "SYNTAX ERROR") or (verdict == "ABORTED")):
                mhweb = col[-1].findAll("a")
                descr = col[-1].findAll("tt")                
                vrec.update_failed((str(col[0].string), get_comments(mhweb, descr)))
            elif (verdict == "PASSED"):
                pass # for now
            elif (verdict == "KNOWN ERROR"):
                # find all links and descriptions of the TRs/errors
                mhweb = col[-1].findAll("a")
                descr = col[-1].findAll("tt")
                vrec.update_known((str(col[0].string), get_comments(mhweb, descr)))

            elif (verdict == "UNTESTED"):
                vrec.update_untested(str(col[0].string))
            else:
                print "Unknown testcase verdict:", verdict
            
            jdx += 1

        
        
    # determine rat
    if (type(rat) == type("")):
        #rat = rat.lower()
        vrec_idx = -1
        idx = 0
        for vrec in vrec_list:
            if (rat in vrec.get_position()):
                vrec_indx = idx
            if ((rat in vrec.get_position()) and ("air" in vrec.get_position())):
                vrec_idx = idx
            idx += 1
        if (vrec_idx != -1):
            return vrec_list[vrec_idx]
        else:
            print "Could not find this rat", rat
            
    else:
        return vrec_list


if (__name__ == "__main__"):
    
    release = ""
    tower   = ""
    if (len(sys.argv) <= 1):
        print ("Must provide at least SW release")
        sys.exit(2)
    else:
        release = (str(sys.argv[1])).upper()
        if ("R6" not in release):
            print ("Bad SW release")
            sys.exit(2)
        if (len(sys.argv) > 2):
            tower = sys.argv[2]
        
    rootdir = "/home/mario/CV_work/examples/test_results_verifier/test1/MSR/app_" + release + "__WORK"
    
    print "\nStarting...\n"
    #rootdir = "/home/mario/CV_work/examples/test_results_verifier/test1/MSR/app_R61BL__WORK/"
    for element in os.listdir(rootdir):
        sw_path = os.path.join(rootdir, element)
        if (os.path.isfile(sw_path)):
            if (("VRec__app_R61BL__CV_" in element) and (".html" in element)):
                if (tower != ""):
                    if (tower not in element):
                        continue
                lista = parse_html(sw_path)
                for elem in lista:
                    print "___________________________________"
                    print elem
                    print "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
                    print
                
    #lista = parse_html("/home/mario/CV_work/examples/test_results_verifier/test1/MSR/app_R61BL__WORK/VRec__app_R61BL__CV_RUS01B2_2-RUL-Maxwell1_rus3a_M16B__rul.html")
#    lista = parse_html("/home/mario/CV_work/examples/test_results_verifier/test1/MSR/app_R61BL__WORK/Vrec__app_R61BL__CV_RRUS0YB8-RUL-Faraday2_rus3a_M16B__rul_kopija.html")
#    print "×××××××××××××××××××××××××××××××××××"
#    for element in lista:
#        print element
