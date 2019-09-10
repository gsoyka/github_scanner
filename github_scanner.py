#!/usr/bin/env python3
import base64
import json
import re
import subprocess
import os, sys
import argparse
from time import gmtime, strftime
from github import Github


def print_nice_json(content):
    """
    Helper function for easier debugging
    """
    print(json.dumps(content, indent=2, sort_keys=True))


def get_repo_names(github, scan_private, org=None):
    """
    Get all repos visible to the specified user, or alternatively get
    all repos in the specified organization
    """
    if org is not None:
        repos = github.get_organization(org).get_repos()
    else:
        repos = github.get_user().get_repos()
    repo_list =[]

    for repo in repos:
        # This is a bit cludgy, but there is reason to the madness
        # Github imposes a limit on how many ssh clones you can perform
        # If you exceed the timeout, you will get connection reset by peer errors
        # To enable scanning private repos, we will add only the private ones with ssh
        # clone links, and add public ones as https.
        if scan_private is True:
            if repo.private == True:
                repo_list.append(repo.ssh_url)
            else:
                repo_list.append(repo.clone_url)
        # If scan_private is unset, just add public repos using https
        elif repo.private == False:
            repo_list.append(repo.clone_url)
    # Alphabetize our list to make it easier to follow
    return sorted(repo_list, key=str.lower)


def write_to_file(output, repo_name):
    global datestamp
    # Define the directory to write to as a folder named templates in the current dir
    dir = os.path.abspath(os.path.join(os.path.dirname( __file__ ),'reports'))

    # Create the directory if it does not exist
    if not os.path.exists(dir):
        os.makedirs(dir)

        # Define filename
        filename = re.sub('\.py$','', sys.argv[0])
        file = os.path.join(dir,filename)

        # Format our output
        output = output.decode('utf-8')
        output = re.sub('\[92m', '', output)
        output = re.sub('\[93m', '', output)
        output = re.sub('\[0m', '', output)

        # Write the stdout to txt file
        target = open(file + "-" + datestamp + '.txt', 'a')
        target.truncate()
        target.write(repo_name + "\n")
        target.write(output)
        target.write("\n")
        target.close()


def scan_repos(repos):
    problem_repos = []

    print(f"\033[1;32;93m Preparing to check {len(repos)} repositories")

    # Run trufflehog over all the repos
    for repo_name in repos:
        print("\033[1;32;40m \n Checking: " + repo_name)
        cmd = "trufflehog --regex --entropy=False " + repo_name
        try:
            output = subprocess.check_output(
                f"trufflehog --regex --entropy=False {repo_name}",
                shell=True,
                stderr=subprocess.STDOUT,
                universal_newlines=True
            )
            # If the output is not empty, trufflehog found a problem, so
            # add the repo name to our list of problem repos, and write the
            # output to our report file
            if len(output) != 0:
                print("\033[1;31;40m Problems found in: " + repo_name)
                problem_repos.append(repo_name)
                write_to_file(output, repo_name)

        except subprocess.CalledProcessError as e:
            print("\033[1;31;40m Problems found in repo: " + repo_name)
            print(e.output)
        except Exception as e:
            print("\033[1;31;40m Problem checking repo: " + repo_name)

        # Report on our findings
        if len(problem_repos) != 0:
            print("\n")
            print("\033[1;31;40m Problems detected in " + str(len(problem_repos)) + " repository(s) which are listed below")
            print("\033[1;31;40m Please review the generated report for additional detail")
            for repo in problem_repos:
                print("\033[1;31;40m" + repo)


######################## MAIN BEGINS HERE ###############################
def main(argv):
    # Get options, if any
    parser = argparse.ArgumentParser()
    parser.add_argument('-t','--token', help='Github API key', required=False)
    parser.add_argument('-u','--user', help='Github Username', required=False)
    parser.add_argument('-p','--password', help='Github Password', required=False)
    parser.add_argument('-o','--org', help='Github Organization to Limit to', required=False)
    parser.add_argument('-a','--scan_private', help='Use to scan private repositories', action='store_true', required=False)
    args = parser.parse_args()

    # Set our timestamp for writing to the output file
    global datestamp
    datestamp = strftime('%Y-%m-%d-%H:%M:%S')

    if args.token:
        g = Github(args.token)
    elif args.user and args.password:
        g = Github(args.user, args.password)
    else:
        print("You must specify either a Github access token or a username and password")
        exit(1)

    # Get a list of repos to check
    print("\033[1;32;93m Fetching list of repositories to check")
    repos = get_repo_names(Github(args.token), args.scan_private, args.org)

    # Run trufflehog over repos
    scan_repos(repos)

if __name__ == "__main__":
    main(sys.argv[1:])
