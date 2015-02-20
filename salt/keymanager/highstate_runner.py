#!/usr/bin/env python
"""Usage: highstate_runner.py MINION_ID

Run a highstate on one minion if it has not been run on the minion previously, and a highstate
is not currently running.  Also, ensure that no other salt masters should run the highstate.

Arguments:
  MINION_ID

Options:
  -h --help

"""
from docopt import docopt
import salt.client
import socket


def check_if_first_highstate_ever(minion_id):
  '''Check if a highstate has ever been run on the minion'''
  # initial highstate creates a file  --> /root/most_recent_salt_highstate_run.txt
  client = salt.client.LocalClient()
  # file.path_exists_glob /root/most_recent_salt_highstate_run.txt
  mypath = ["/root/most_recent_salt_highstate_run.txt"]
  results_by_minion = client.cmd(tgt=minion_id, fun='file.path_exists_glob', arg=mypath)   # sync call
  return results_by_minion[minion_id]

def check_if_highstate_running(minion_id):
  '''Check if a highstate is currently running on a minion'''
  client = salt.client.LocalClient()
  #  salt ip-10-0-0-113.ec2.internal saltutil.is_running state.highstate
  running_function = ["state.highstate"]
  results_by_minion = client.cmd(tgt=minion_id, fun='saltutil.is_running', arg=running_function)   # sync call
  minion_results = results_by_minion.get(minion_id, [])
  if not minion_results:
    return False
  else:
    return True

def write_highstate_runner_claim(minion_id):
  '''Write our saltmaster's id into a file on the minion, designating which saltmaster gets to run the
     highstate on it.  First in wins.
     /tmp/highstate_runner'''
  client = salt.client.LocalClient()
  path = "/tmp/highstate_runner"
  hostname = socket.gethostname()
  results = client.cmd(tgt=minion_id, fun='file.touch', arg=[path])   # sync call
  results_by_minion = client.cmd(tgt=minion_id, fun='file.append', arg=[path, hostname])   # sync call
  print results_by_minion
  return

def should_run_highstate(minion_id):
  '''Determine if we should run the highstate by checking the first line in /tmp/highstate_runner
     for our hostname'''
  client = salt.client.LocalClient()
  path = "/tmp/highstate_runner"
  hostname = socket.gethostname()
  results_by_minion = client.cmd(tgt=minion_id, fun='cmd.run', arg=["cat /tmp/highstate_runner"])   # sync call
  contents = results_by_minion.get(minion_id, '')
  lines = contents.split("\n")
  first_line = lines[0].strip()
  if first_line == hostname:
    return True
  else:
    return False
# salt ip-10-0-0-113.ec2.internal cmd.run "cat /tmp/highstate_runner"

def call_highstate(minion_id):
  '''execute an async salt call to a minion to run state.highstate asynchronously'''
  client = salt.client.LocalClient()
  minions = client.cmd_async(tgt=minion_id, fun='state.highstate', arg=[], timeout=1, expr_form='compound')
  return 

if __name__ == '__main__':
  arguments = docopt(__doc__)
  # print(arguments)
  minion_id = arguments['MINION_ID']
  print
  print "minion_id: %s" % minion_id
  print
  print "Highstate has been run previously: %s" % check_if_first_highstate_ever(minion_id)
  print 
  print "Highstate is currently running: %s" % check_if_highstate_running(minion_id)
  print 
  print "Attempting to set this salmaster as the highstate runner"
  print write_highstate_runner_claim(minion_id)
  print "Should we run the highstate?"
  print should_run_highstate(minion_id)
  print "Running highstate"
  call_highstate(minion_id)


  # run a highstate

