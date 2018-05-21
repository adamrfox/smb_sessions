#!/usr/bin/python

import papi
import getpass
import json
import sys
import getopt

def get_openfiles (node, user, password):
  path = "/platform/1/protocols/smb/openfiles"
  (status, reason, resp) = papi.call (node, '8080', 'GET', path, '', 'any', 'application/json', user, password)
  if status != 200:
    err_string = "ERROR: Bad Status: " + status
    sys.stderr.write (err_string)
    exit (status)
  return (json.loads(resp))

def dprint (message):
  if DEBUG:
    print "DEBUG: " + message + "\n"

def usage ():
  sys.stderr.write ("Usage: smb_openfiles[.py]\n")
  sys.stderr.write ("	List Files (default mode):\n")
  sys.stderr.write ("		[{-C | --cluster}] : Specify a cluster from the config file\n")
  sys.stderr.write ("		[{-f | --file}] : Specify an alternative config file\n")
  sys.stderr.write ("	Close File Mode:\n")
  sys.stderr.write ("		[{-c | --close}] : Close file(s) Selects Close File Mode\n")
  sys.stderr.write ("		[{-n | --node]} : Specifies a node where the file is open\n")
  sys.stderr.write ("		[{-i | id}] : Specify a comma-separated list of IDs\n")
  sys.stderr.write ("	[-h | --help] : display usage syntax\n\n")
  exit (0)



cluster = ''
cluster_list = []
node_list = []
user = ""
password = ""
conf_file = "nodes.conf"
MODE = "view"
node = ""
id_list = []
user_name = ""
addr_list = []
node_num_s = ""
DEBUG = 0
ALL = 1

optlist, args = getopt.getopt (sys.argv[1:], 'DC:f:cn:i:h', ["cluster=", "file=", "close", "node=", "id=", "help"])
for opt, a in optlist:
  if opt == '-D':
    DEBUG = 1
  if opt in ('-C', "--cluster"):
    ALL = 0
    cluster = a
  if opt in ('-f', "--file"):
    conf_file = a
  if opt in ('-c', "--close"):
    MODE = "close"
  if opt in ('-n', "--node"):
    node_num_s = a
  if opt in ('-i', "--id"):
    ids = a.split(',')
    for i in ids:
      id_list.append(i)
  if opt in ('-h' , "--help"):
    usage()

for node in open (conf_file):
  node_s = node.rstrip ('\r\n')
  nl = node_s.split (':')
  if ALL == 0 and nl[0] != cluster:
    continue
  cluster_list.append (nl[0])
  node_list.append (nl[1])
  addr_list.append (nl[2])
if (len(addr_list) == 0):
  print "No Clusters Found."
  exit (0)
if MODE == "view":
  user = raw_input ("User: ")
  password = getpass.getpass ("Password: :")
  for i, node in enumerate (addr_list):
    ofiles = get_openfiles (node, user, password)
    node_name = cluster_list[i] + "-" + node_list[i] + ":"
    print "--------------------------------------"
    if ofiles['total'] == 0:
      print node_name, "No Open Files"
    else:
      print node_name
      print "ID: File:                                    User:            #Locks:"

      print "--------------------------------------"
      for file_inst in ofiles['openfiles']:
        print "{0:3d} {1:40s} {2:15s} {3:2d}".format(file_inst['id'],file_inst['file'],file_inst['user'],file_inst['locks'])  
    print ""
else:
  if node_num_s == "" or len(id_list) == 0:
    sys.stderr.write ("To close a file the node and ID must be specificed.\n")
    usage()
    exit (2)
  nnf = node_num_s.split ('-')
  node_name = nnf[0]
  node_num = nnf[1]
  for i,n in enumerate (node_list):
    if cluster_list[i] == node_name and node_list[i] == node_num:
      index = i
      break
  user = raw_input ("User: ")
  password = getpass.getpass ("Password: ")
  for id in id_list:
    path = "/platform/1/protocols/smb/openfiles/" + id
    dprint (path)
    dprint (addr_list[index])
    (status, resp, reason) = papi.call (addr_list[index], '8080', 'DELETE', path, 'any', '', 'application/json', user, password)
    if status != 204:
      err_string = "Bad Status: " + `status` + "\n"
      sys.stderr.write (err_string)
      err = json.loads (reason)
      sys.stderr.write (err['errors'][0]['message'])
      sys.stderr.write ("\n")
      exit (status)
    print "ID " + id + " Closed."

