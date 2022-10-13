#!/usr/bin/python3 

import base64
import json
import os
import praw
import sys
import sqlite3
import time
from shutil import copyfile

#  ____
# |  _ \ _ __ ___ _ __
# | |_) | '__/ _ \ '_ \
# |  __/| | |  __/ |_) |
# |_|   |_|  \___| .__/
#                |_|

scriptBasename = os.path.basename(__file__).split('.')[0]


confLocation= scriptBasename + ".ini"
if os.path.isfile(confLocation) is False:
  copyfile(confLocation + '.default', confLocation)
  sys.exit(confLocation + ' is missing and cannot be. Creating from default and exiting.')

with open(confLocation,'r') as file:
  confJson = json.loads(file.read())

class DB():
  def __init__(self):
    self.con = sqlite3.connect(scriptBasename + ".db")
    self.cur = self.con.cursor()
    self.cur.execute("CREATE TABLE IF NOT EXISTS " + scriptBasename + "(sourceSub, submissionSourceId, sourceScore, destSub, submissionDestId, dateProcessed)")

  def checkPost(self, submission):
    result = self.cur.execute(
      "SELECT submissionSourceId,dateProcessed from %s where submissionSourceId = '"'%s'"' " % (scriptBasename, submission.id)
      )
    data=self.cur.fetchone()
    if data is None:
      return False
    else:
      return True

  def trackPost(self, submission):
    result = self.cur.execute(
      "INSERT into %s(sourceSub, submissionSourceId, sourceScore, destSub) values('"'%s'"', '"'%s'"', '"'%s'"', '"'%s'"')" % (scriptBasename, submission.subreddit.display_name, submission.id, submission.score, confJson['global']['subreddit_dest'])
      )
    if self.con.commit():
      print('\tTracked post.')

  def markXpostComplete(self, submission, result):
    now = time.time()
    result = self.cur.execute(
            "UPDATE %s SET submissionDestId = '"'%s'"', dateProcessed = '"'%s'"' where sourceSub = '"'%s'"' and submissionSourceId = '"'%s'"' and destSub = '"'%s'"'" % (scriptBasename, result.id, now, submission.subreddit.display_name, submission.id, confJson['global']['subreddit_dest'] )
      )
    if self.con.commit():
      print('\tMarked post complete.')

class CROSSPOSTER():
  def __init__(self):
    self.reddit = praw.Reddit(
      client_id       = confJson['reddit']['client_id'],
      client_secret   = confJson['reddit']['client_secret'],
      username        = confJson['reddit']['username'],
      password        = confJson['reddit']['password'],
      user_agent      = confJson['global']['user_agent']
    )

    self.db = DB()

  def crosspost(self):
    for submission in self.reddit.subreddit(confJson['global']['subreddit_source']).hot(limit=15):
     if not self.db.checkPost(submission):
        print('Seen untracked submission: ' + submission.id)

        if not submission.score > confJson['global']['source_post_min_score']:
          print('\tSubmission score of ' + str(submission.score) + ' not at minimum: ' + str(confJson['global']['source_post_min_score']) + '. Processing skipped for now.' )
          continue
        if bool(confJson['global']['do_trackpost']):
          self.db.trackPost(submission)
        else:
          print('\tTracking crossposts in db disabled in config')

        if bool(confJson['global']['do_crosspost']):
          try:
            result = submission.crosspost(confJson['global']['subreddit_dest'], title="[" + submission.title + "]", send_replies=True)
            #breakpoint()
            self.db.markXpostComplete(submission, result)
          except Exception as e:
            print('\tFailed to crosspost: ' + submission.id )
            print(e)
        else:
          print('\tCrossposting disabled in config')



#  __  __       _
# |  \/  | __ _(_)_ __
# | |\/| |/ _` | | '_ \
# | |  | | (_| | | | | |
# |_|  |_|\__,_|_|_| |_|
#

def main():

  crossposter = CROSSPOSTER()
  crossposter.crosspost()

if __name__ == '__main__':
  main()
