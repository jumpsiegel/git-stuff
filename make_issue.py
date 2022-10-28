import sys
import pwd
from github import Github
from github import GithubObject
import os
import os.path
import urllib3
import subprocess

# Create your token: https://github.com/settings/tokens
# Put your token to ~/.github/raw_token

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def print_usage():
  print ("usage: ")
  print ("  list   - list issues assigned to me")
  print ("  create - create a new issue")
  sys.exit(-1)

me = pwd.getpwuid(os.getuid())[0]
try:
  with open(os.path.join(os.environ["HOME"], '.github/me'), 'r') as me_file:
    me = me_file.readline().strip()
except FileNotFoundError:
    pass

tok = None
try:
  with open(os.path.join(os.environ["HOME"], '.github/raw_token'), 'r') as tok_file:
    tok = tok_file.readline().strip()
except FileNotFoundError:
  print('Create your Github access token at https://github.com/settings/tokens and put it to ~/.github/raw_token')
  if len(sys.argv) < 2:
    print_usage()
  sys.exit(-1)

git = Github(tok)
org = git.get_organization('wormhole-foundation')
repo = org.get_repo('wormhole')

if len(sys.argv) < 2:
  print_usage()

if sys.argv[1] == "list":
#  issues=repo.get_issues(assignee=git.get_user(me))
  issues=repo.get_issues(state="open")
  for i in issues:
    print (i)
  sys.exit(0)

if sys.argv[1] == "topic":
  try:
    issue=repo.get_issue(int(sys.argv[2]))
    print (issue.title)
  except:
    print ("unknown")
  sys.exit(0)

if sys.argv[1] == "view":
  issue=repo.get_issue(int(sys.argv[2]))
  print ("Number: "+str(issue.number))
  print ("Title: "+issue.title)
  print ("assignees: "+str(issue.assignees))
  print ("Body:\n"+issue.body+"\n")
  for i in issue.get_comments():
    print (str(i.user) + ":" + i.body)
  sys.exit(0)

if sys.argv[1] == "create":
    t = ""
    if len(sys.argv) < 3:
      print ("what is the topic?")
      sys.exit(-1)
    for r in range(2, len(sys.argv)):
        if r == 2:
            t = sys.argv[r]
        else:
            t = t + " " + sys.argv[r]
    print (t)
    print (repo.create_issue(t, t, git.get_user(me), GithubObject.NotSet, GithubObject.NotSet, GithubObject.NotSet))
    sys.exit(0)

if sys.argv[1] == "new":
    t = ""
    if len(sys.argv) < 3:
      print ("what is the topic?")
      sys.exit(-1)
    for r in range(2, len(sys.argv)):
        if r == 2:
            t = sys.argv[r]
        else:
            t = t + " " + sys.argv[r]
    issue=repo.create_issue(t, t, git.get_user(me), GithubObject.NotSet, GithubObject.NotSet, GithubObject.NotSet)
    sb = repo.get_branch("dev.v2");
    ref=repo.create_git_ref(ref='refs/heads/' + 'WH-' + str(issue.number), sha=sb.commit.sha) 
    # It is unclear exactly how I avoid calling out to the shell...
    subprocess.run("git fetch", shell=True, check=True)
    subprocess.run("git checkout WH-" + str(issue.number), shell=True, check=True)
    subprocess.run("git config branch.WH-" + str(issue.number) + ".description \""+t+"\"", shell=True, check=True)

if sys.argv[1] == "pulls":
    for pull in repo.get_pulls(state="open"):
        print (pull)

if sys.argv[1] == "team":
    teams = org.get_teams()
    team = [t for t in teams if t.name == 'teamillini']
    for x in team[0].get_members():
        print (x)

if sys.argv[1] == "pr":
    if len(sys.argv) != 4:
        print ("git issue pr <issueNumber> <reviewer>")

        teams = org.get_teams()
        team = [t for t in teams if t.name == 'teamillini']
        mems=[]
        for x in team[0].get_members():
            mems.append(x.login)
        print ("valid users", mems)
    
        sys.exit(1)
    print (len(sys.argv))
    try:
      issue=repo.get_issue(int(sys.argv[2]))
    except:
      print ("Cannot find requested issue")
      sys.exit(-1)
    pull = repo.create_pull(body=issue.title, title=issue.title, base="master", head="WH-"+sys.argv[2])
    pull.create_review_request(reviewers=[sys.argv[3]])
    print (pull)
