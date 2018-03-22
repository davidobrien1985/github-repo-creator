import datetime as date
import json
import os

import requests as r


def main(req):
    """main function being called
    
    Arguments:
        req {Azure Function input} -- input object from the Azure Function trigger
    """
    githubBaseUrl = "https://api.github.com"
    githubOwner = "davidobrien1985"
    createRepository(githubOwner, githubBaseUrl, os.environ['githubPAT'], "test123")
    configureGitHubBranch(githubOwner, githubBaseUrl, os.environ['githubPAT'], "test123", "master")

def createRepository(githubOwner, githubBaseUrl, githubPat, githubRepoName):
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
        'allow_rebase_merge': 'false'
        }

    headers = {
        'Authorization': 'token %s' % githubPat,
        "User-Agent": "githubmanage-python"
    }

    response = r.post(
        githubBaseUrl + "/user/repos",
        data=json.dumps(payload),
        json=None,
        headers=headers)

    jsonResponse = json.loads(response.content)
    print("Created repository {repoName} at {time}".format(repoName=jsonResponse['full_name'], time=date.datetime.now()))

def createGitHubBranch(githubOwner, githubBaseUrl, githubPat, githubBranchName):
    """create a GitHub branch
    
    Arguments:
        githubPat {string} -- GitHub Personal Access Token
        githubRepoName {string} -- GitHub repository name
        githubBranch {string} -- GitHub branch to configure
        githubBaseUrl {string} -- base Url to the GitHub API
    """


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
