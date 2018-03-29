import datetime as date
import json
import os
import requests as r
import logging
import time
import html


logger = logging.getLogger()
logger.setLevel(logging.INFO)

def main(event, context):
    """main function being called
    
    Arguments:
        
    """
    logger.info('got event %s' % (event))
    body = convert_body_to_json(event['body'])
    print(body)
    text = html.unescape(body['text'])
    repoName = text.split(' ')[1][:-1]
    print(repoName)
    githubBaseUrl = "https://api.github.com"
    githubOwner = os.environ['githubOwner']
    cloudops_team_github_id = os.environ['cloudopsTeamGithubId']
    branches = "master","develop"

    try:
        logger.info('Create repository {0}'.format(repoName))
        createRepository(githubOwner, githubBaseUrl, os.environ['githubPAT'], repoName, cloudops_team_github_id)
    except (RuntimeError, TypeError, NameError) as err:
        return respond(err,"{0}".format(err))

    try:
        logger.info('Create develop branch on {0}'.format(repoName))
        time.sleep(5)
        createGitHubBranch(githubOwner, repoName, githubBaseUrl, os.environ['githubPAT'], "develop")
    except (RuntimeError, TypeError, NameError) as err:
        return respond(err,"{0}".format(err))

    # configure both master and develop branch on new repo
    for branch in branches:
        try:
            logger.info('Configuring branch {0} on repo {1}'.format(branch, repoName))
            configureGitHubBranch(githubOwner, githubBaseUrl, os.environ['githubPAT'], repoName, branch)
        except (RuntimeError, TypeError, NameError) as err:
            return respond(err,"{0}".format(err))

    return respond(None,"Successfully created GitHub repo {0}".format(repoName))


def respond(err, res=None):
    return {
        'statusCode': '400' if err else '200',
        'body': res,
        'headers': {
            'Content-Type': 'application/json',
        },
    }

def convert_body_to_json(body):
    new_body = json.loads(body)
    return new_body

def createRepository(githubOwner, githubBaseUrl, githubPat, githubRepoName, cloudops_team_github_id):
    """create a GitHub repository

    Arguments:
        githubPat {string} -- Personal Access Token to auth against GitHub API
        githubRepoName {string} -- GitHub repository name
    """
    print("Starting process to create GitHub repository:", githubRepoName,
          "\n", "at", date.datetime.now())

    payload = {
        'name': githubRepoName,
        'auto_init': 'true',
        'allow_merge_commit': 'false',
        'allow_rebase_merge': 'false',
        'private': 'true',
        'team_id': cloudops_team_github_id
        }

    headers = {
        'Authorization': 'token %s' % githubPat,
        "User-Agent": "githubmanage-python"
    }

    response = r.post(
        githubBaseUrl + "/orgs/{0}/repos".format(githubOwner),
        data=json.dumps(payload),
        json=None,
        headers=headers)

    jsonResponse = json.loads(response.content)
    print("Created repository {repoName} at {time}".format(repoName=jsonResponse['full_name'], time=date.datetime.now()))

def createGitHubBranch(githubOwner, githubRepoName, githubBaseUrl, githubPat, githubBranchName):
    """create a GitHub branch
    
    Arguments:
        githubPat {string} -- GitHub Personal Access Token
        githubRepoName {string} -- GitHub repository name
        githubBranch {string} -- GitHub branch to configure
        githubBaseUrl {string} -- base Url to the GitHub API
    """

    headers = {
        'Authorization': 'token %s' % githubPat,
        "User-Agent": "githubmanage-python"
    }

    sha = r.get(
        githubBaseUrl + "/repos/{0}/{1}/git/refs/heads".format(githubOwner, githubRepoName),
        headers=headers
    )

    content = json.loads(sha.content)

    sha = content[0]["object"]["sha"]

    payload = {
        "ref": "refs/heads/{0}".format(githubBranchName),
        "sha": sha
    }

    response = r.post(
        githubBaseUrl + "/repos/{0}/{1}/git/refs".format(githubOwner, githubRepoName),
        data=json.dumps(payload),
        json=None,
        headers=headers)

    jsonResponse = json.loads(response.content)
    print(jsonResponse)


def configureGitHubBranch(githubOwner, githubBaseUrl, githubPat, githubRepoName, githubBranch):
    """configure GitHub branch merging policy
    
    Arguments:
        githubPat {string} -- GitHub Personal Access Token
        githubRepoName {string} -- GitHub repository name
        githubBranch {string} -- GitHub branch to configure
        githubBaseUrl {string} -- base Url to the GitHub API
    """

    print("Starting process to configure GitHub repository:", githubRepoName,
          "\n", "at", date.datetime.now())

    payload = {
        "required_status_checks": None,
        "enforce_admins": True,
        "required_pull_request_reviews": {
            "dismiss_stale_reviews": True,
            "require_code_owner_reviews": True
        },
        "restrictions": None
    }

    headers = {
        'Authorization': 'token %s' % githubPat,
        "User-Agent": "githubmanage-python"
    }
    
    response = r.put(
        githubBaseUrl + "/repos/{githubUser}/{githubRepoName}/branches/{githubBranch}/protection".format(githubUser=githubOwner, githubRepoName=githubRepoName, githubBranch=githubBranch),
        data=json.dumps(payload),
        json=None,
        headers=headers)

    jsonResponse = json.loads(response.content)
    print(jsonResponse)
