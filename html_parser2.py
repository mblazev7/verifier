#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Sat Nov  14 11:12:56 2015 Mario Blazevic
This module provides a methods to extract informations from HTML based VRec's
"""

__version__ = '0.15'
__date__    = '2015-11-20'
__author__  = 'Mario Blazevic'

#--- CHANGES -----------------------------------------------------------

# 2015-11-14 v0.01: - First update - created
# 2015-11-19 v0.10: - Second update - changed:
#                        added filtering by RAT, project, tower.
# 2015-11-24 v0.15: - Third update - added filtering by unit
# 2015-11-26 v0.16: - Fourth upodate  - added checking for
#                        unfinished jobs in CV engine


#-----------------------------------------------------------------------
#TODO:
# - nice printout from the shell
# - process failed test cases
# - check if there are running tasks on specified release (that is tower)
# - GUI


# --- IMPORTS ----------------------------------------------------------
from BeautifulSoup import *
import os
import sys
import urllib2
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
        self._position    = ""
        self._pass_rate   = ""
        self._failed_list = []
        self._known_list  = []
        self._untested    = []
        self._radio       = ""
        self._serial      = ""
        self._krc         = ""
        self._revision    = ""
        self._prod_date   = ""
        self._dir         = ""

    def __str__(self):
        return ("Radio: " + str(self.get_radio()) +
                "\nPosition: " + str(self.get_position()) +
                "\nPass rate: " + str(self._pass_rate) +
                self._nice_failed() +
                self._nice_known() )

    def set_pass_rate(self, pass_rate):
        self._pass_rate = str(pass_rate)

    def set_position(self, position):
        self._position = position

    def update_failed(self, test):
        self._failed_list.append(test)

    def update_known(self, test):
        self._known_list.append(test)

    def update_untested(self, test):
        self._untested.append(test)

    def get_position(self):
        return self._position

    def set_radio(self, radio):
        self._radio = radio

    def get_radio(self):
        if (((self._radio == "None") or (self._radio == "")) and (len(self._dir) > 2)):
            splited = str(self._dir).split("/")
            last = splited[-1]
            last = last[3:]
            last = last.split("-")
            radio = last[0]
            self.set_radio(radio)
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

    def set_dir(self, path):
        self._dir = path

    def get_dir(self):
        return str(self._dir)

    def nice_get_dir_printout(self):
        if ((len(self._known_list) > 0) or (len(self._failed_list) > 0)):
            return "Source: \nsource " + self.get_dir() + "/terass.rc &\n\n"
        else:
            return ""

    def _nice_known(self):
        """
        Checks if we have known errors in VRec and returns string containing
        all testcases which failed as known errors and their comments
        """
        if (len(self._known_list) <= 0):
            return ""
        # else
        printout = "\n\n\nKnown issues:\n"
        for failed in self._known_list:
            printout += str(failed[0])
            if (len(str(failed[1])) >= 2):
                printout += " " + str(failed[1])
            printout += "\n"
        return printout

    def _nice_failed(self):
        """
        Checks if we have failed testcases in VRec and returns a string
        containing all TCs which have failed and their comments
        (if there are any comments)
        """
        if (len(self._failed_list) <= 0):
            return ""
        # else
        printout = "\n\n\nFailed:\n"
        for failed in self._failed_list:
            printout += str(failed[0])
            if (len(str(failed[1] >= 2))):
                printout += " - " + str(failed[1])
            printout += "\n"
        return printout

    def get_nice_position(self):
        """ Return nice position in form of node_n_rus"""
        temp_position = self._position.split("_")
        lenght = len(temp_position)
        node_n_rus = []
        for idx in range(lenght):
            if (len(temp_position[idx]) > 2):
                if ((temp_position[idx] not in node_n_rus)
                    and ("mm" not in str(temp_position[idx]))):
                    node_n_rus.append(temp_position[idx])

        position = str(node_n_rus[0]) + "_" + str(node_n_rus[1])
        print "DEBUG node_n_rus position:", position
        return position



#=== FUNCTIONS =========================================================



def get_souped_rows(link):
    response = urllib2.urlopen(link)
    html = response.read()
    page = ""
    for line in html:
        page += line.strip()

    souped = BeautifulSoup(page)
    tables = souped.findAll("table")
    if (len(tables) < 1):
        print "something went wrong"
        sys.exit()
    rows = tables[0].findAll("tr")
    return rows



def get_releases(sw_version):
    url = ""
    rows = get_souped_rows(url)

    if (len(rows) <= 1):
        print "len is:", len(rows)
        print "Exiting"
        sys.exit(2)

    idx = 2
    releases = []

    while (idx < (len(rows) - 1)):
        col = rows[idx].findAll("tdclass")
        if (col[0].string == sw_version):
            #print "Release type:", str(col[1].string)
            releases.append(str(col[1].string))
        idx += 1
    return releases


def check_pending_jobs(rows, sw_version, release, position, rat, radio, project):
    """
    Checks rows of the table for pending jobs
    """
#    print "\nDEBUG"
#    print "sw_version:", sw_version
#    print "release:", release
#    print "position:", position
#    print "rat:", rat
#    print "radio:", radio
#    print "project:", project
#    print "END DEBUG\n"
    result = False
    if (len(rows) <= 2):
        print "Table row count is:", len(rows)
        return False

    if (len(rows) == 3):
        if (str(rows[1].string) == "No rows can be found"):
            return False

    idx = 1
    # print "DEBUG: len rows:", len(rows)
    while (idx < (len(rows) - 1)):
        col = rows[idx].findAll("td")
        if (len(col) < 10):
            idx += 1
            continue
        if (position is not None):
            if (position not in str(col[7].string)):
                idx += 1
                continue
        if (rat is not None):
            if (rat not in str(col[9].string)):
                idx += 1
                continue
        if (radio is not None):
            if (radio not in str(col[10].string)):
                idx += 1
                continue
        if (sw_version not in str(col[6].string)):
            print "DEBUG:: This should not happen"
            print "SW version:", sw_version
            idx += 1
            continue
        if (project is not None):
            read_project = str(col[4].string)
            print "DEBUG: read project", read_project
            if ("WCDMA" == str(col[9].string)):
                if (project[0] == "W"):
                    read_project = "M" + read_project[1:]
            if (project not in read_project):
                idx += 1
                continue

        # if we have reached this point then we have something
        result = True
        break

    return result


def get_pending_jobs(sw_version, release, position, rat, radio, project):
    """
    Get links for queued, attempted and started links
    """
    queued_link = "" + str(sw_version) + "&build_type=" + str(release) + "&status=queued"
    rows = get_souped_rows(queued_link)
    # print "Queued link:", queued_link
    queued = check_pending_jobs(rows, sw_version, release, position, rat, radio, project)
    if (queued is True):
        return True

    attempted_link = "" + str(sw_version) + "&build_type=" + str(release) + "&status=attempted"
    rows = get_souped_rows(attempted_link)
    attempted = check_pending_jobs(rows, sw_version, release, position, rat, radio, project)
    if (attempted is True):
        return True

    started_link = "" + str(sw_version) + "&build_type=" + str(release) + "&status=started"
    rows = get_souped_rows(started_link)
    started = check_pending_jobs(rows, sw_version, release, position, rat, radio, project)
    if (started is True):
        return True

    return False




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
    startup_col = rows[stored_idx].findAll("td")
    logs_dir = None

    for row in rows[stored_idx:]:
        col = row.findAll("td")
        jdx = 1
        for vrec in vrec_list:
            link = col[jdx].find("a")
            if ("startup" in str(col[0].string)):
                # we found startup. now search for the directory with logs
                parts = str(col[jdx].a["href"]).split("/")
                sep = "/"
                dir_name = sep.join(parts[:-1])
                # path is containing html file at the end so we should remove it
                # this is guaranteed by previous checks so no need to verify it here
                split_path = path.split("/")
                root_path = sep.join(split_path[:-1])
                logs_dir = os.path.join(root_path, dir_name)
                if (os.path.exists(logs_dir) is True):
                    vrec.set_dir(logs_dir)
                else:
                    print ("Could not access path:", logs_dir)


            if (link is None):
                verdict = "UNTESTED"
            else:
                verdict = str(col[jdx].find("a").string)

            if ((verdict == "FAILED") or (verdict == "SYNTAX ERROR") or
                ("ABORTED" in verdict) or ("TESTING" in verdict) or ("RUNNING" in verdict)):
                mhweb = col[-1].findAll("a")
                descr = col[-1].findAll("tt")
                vrec.update_failed((str(col[0].string), get_comments(mhweb, descr)))
            elif (verdict == "PASSED"):
                pass
                # for now
            elif (verdict == "KNOWN ERROR"):
                # find all links and descriptions of the TRs/errors
                mhweb = col[-1].findAll("a")
                descr = col[-1].findAll("tt")
                vrec.update_known((str(col[0].string), get_comments(mhweb, descr)))

            elif (verdict == "UNTESTED"):
                vrec.update_untested(str(col[0].string))
            else:
                print ("\n*************************************************************")
                print ("Unknown testcase verdict:", verdict)
                print ("File:", path)
                print ("DEBUG: VRec:", vrec)
                print ("************************************************************\n\n")

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



def process_entries(rootdir, release, tower = None,
                    rat_tag = None, project = None, unit = None,
                    check_finish = False):
    """
    Main function which does the processing
    It takes:
        rootdir          - the directory containg logs
        release          - the SW release
        tower            - optional string defining tower
        rat_tag          - optional tupple defining rat
        project          - optional string defining project
        unit             - optional string defining RU
    """
    vrec_release_str = "VRec__app_" + str(release) + "__CV_"
    if (os.path.exists(rootdir) is False):
        print "Could not access path:", rootdir
        return
    if (rat_tag is not None):
        rat = rat_tag[0]
        tag = rat_tag[1]
    else:
        rat = None
        tag = None
    for element in os.listdir(rootdir):
        sw_path = os.path.join(rootdir, element)
        if (os.path.isfile(sw_path)):
            if ((vrec_release_str in element) and (".html" in element)):
                if (tower is not None):
                    if (tower.lower() not in str(element).lower()):
                        continue
                if (unit is not None):
                    if (unit.lower() not in str(element).lower()):
                        continue
                if (project is not None):
                    if (project.upper() not in str(element).upper()):
                        continue

                lista = parse_html(sw_path)
                for elem in lista:
                    if (rat is not None):
                        if ((tag not in elem.get_position()) or
                            (("mm" not in tag) and
                            ("mm" in elem.get_position()))):
                            continue

                    print ("___________________________________")
                    if (rat is not None):
                        print"RAT:", rat
                    if (project is not None):
                        print "Project:", project.upper()
                    print elem
                    print "-----------------------------------"
                    print
                    print "Vrec path:", sw_path
                    print
                    print (elem.nice_get_dir_printout())
                    if (check_finish is True):
                        build_types = get_releases(release)
                        for build_type in build_types:
                            pending = get_pending_jobs(release, build_type, elem.get_nice_position(), rat, unit, project)
                            if (pending is True):
                                print "\n\nThere are still pending jobs in CV engine waiting to finish!!!\n\n"
                                break
                    print ("\n######################################")



def determine_rat(entry):
    """
    Determine which RAT was passed. Defaults to LTE-TDD if something
    unrecognized is passed to this function
    """
    if (entry == "W" or entry == "WCDMA"):
        rat = "WCDMA"
        tag = "ruw"
    elif (entry == "C" or entry == "CDMA"):
        rat = "CDMA"
        tag = "ruc"
    elif (entry == "G" or entry == "GSM"):
        rat = "GSM"
        tag = "rug"
    elif (entry == "L" or entry == "LTE"):
        rat = "LTE"
        tag = "rul"
    elif ((entry == "MML+L") or (entry == "MMLL")):
        rat = "MMLL"
        tag = "mmll"
    elif ((entry == "MML+C") or (entry == "MMLC")):
        rat = "MMLC"
        tag = "mmlc"
    elif ((entry == "MML+G") or (entry == "MMLG")):
        rat = "MMLG"
        tag = "mmlg"
    elif ((entry == "MML+W") or (entry == "MMLW")):
        rat = "MMLW"
        tag = "mmlw"
    elif ((entry == "MMW+G") or (entry == "MMWG")):
        rat = "MMWG"
        tag = "mmwg"
    elif (entry == "WCDMA-MSI"):
        rat = "WCDMA-MSI"
        tag = "ruw"
    elif ("TDD" in entry):
        # assume LTE-TDD
        rat = "LTE-TDD"
        tag = "tdd"
    else:
        rat = None
        tag = None
    return (rat, tag)



def usage(coli):
    """ Print help """
    print str (coli) + " version: " + str(__version__)
    print "Usage:"
    print "   " + str(coli) + " <sw release> [[option1], [option2], ...]"
    print "   The options available:"
    print "       -h, --help     - prints this text"
    print "       -r, --rat      - defines RAT type to be searched for"
    print "                      - RAT should be chosen from the following:"
    print "                            G[SM], W[CDMA], L[TE], C[DMA], MMLG, MMLW, MMLC, MMWG, WCDMA-MSI"
    print "       -t, --tower    - defines tower to be searched for"
    print "       -p, --project  - defines project to be searched for"
    print "       -u, --unit     - defines RU to be searched for"
    print "\nThe software release is a required information."
    print "Multiple options can be combined to create desired filter"
    print "RAT, project, release and tower entries are not case sensitive"




if (__name__ == "__main__"):

    import getopt

    release = None
    tower   = None
    rat     = None
    project = None
    tag     = None
    unit    = None

    check_fin = False

    if (len(sys.argv) <= 1):
        print ("Must provide at least SW release")
        sys.exit(2)

    release = (str(sys.argv[1])).upper()
    if (("R6" not in release) or ("-" in release)):
        if ("-h" in sys.argv[1]):
            usage(sys.argv[0])
        else:
            print ("Bad SW release")
        sys.exit(2)

    try:
        opts, args = getopt.getopt(sys.argv[2:], "ht:r:p:u:f", ["help", "tower", "rat", "project", "unit", "finished"])
    except getopt.GetoptError as err:
        # print help information and exit:
        print str(err)
        usage(sys.argv[0])
        sys.exit(2)

    for opt, arg in opts:
        if (opt in ("-r", "--rat")):
            entry = str(arg).upper()
            rat, tag = determine_rat(entry.strip())
            if ((rat is None) or (tag is None)):
                print "Unknown RAT passed:", rat
                print "See help for list of supported RATs"
                sys.exit(2)
        elif (opt in ("-p", "--project")):
            project = arg
        elif (opt in ("-t", "--tower")):
            tower = arg
        elif (opt in ("-h", "--help")):
            usage(sys.argv[0])
            sys.exit()
        elif (opt in ("-u", "--unit")):
            unit = arg
        elif (opt in ("-f", "--finished")):
            check_fin = True
        else:
            assert False, "Unhandled option, should not happen"

    if ((rat is not None) and (rat != "WCDMA")):
        rootdir = "/proj/terass_func/TerassResult/MSR/app_" + release + "__WORK"
        print "Starting with MSR directory...\n"
        process_entries(rootdir, release, tower, (rat, tag), project, unit, check_fin)
        print "\nDone with MSR directory.\n"
    elif (rat == "WCDMA"):
        print "Starting with WCDMA...\n"
        rootdir = "/proj/terass_func/TerassResult/WCDMA/app_" + release + "__WORK"
        process_entries(rootdir, release, tower, (rat, tag), project, unit, check_fin)
        print "\nDone with WCDMA directory.\n"

    else:
        print "Starting with both MSR and WCDMA directories...\n"
        rootdir = "/proj/terass_func/TerassResult/MSR/app_" + release + "__WORK"
        process_entries(rootdir, release, tower, (rat, tag), project, unit, check_fin)
        print "Done with MSR directory.\n"
        rootdir = "/proj/terass_func/TerassResult/WCDMA/app_" + release + "__WORK"
        process_entries(rootdir, release, tower, (rat, tag), project, unit, check_fin)
        print "\nDone with WCDMA directory.\n"



