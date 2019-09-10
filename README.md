# GitHub Scanner

## Overview

This is a CLI wrapper around Trufflehog, designed to scan Github repos for potentially sensitive information.

## Requirements
* Github API Token
* Trufflehog: https://github.com/dxa4481/truffleHog
* PyGithub

## How to Use

At a minimum, you must specify either a Github Token or Username/Password combo.  By default, we will scan all public repos
owned by a given user, along with any public repos in any organizations that user belongs to.

`github_scanner.py --token my_api_token`

### Configuration Options

* `-t`, `--token`: Github API Key
* `-u`, `--user`: Github Username
* `-p`, `--password`: Github Password
* `-o`, `--org`: Limit scan to a given organization
* `-a`, `--scan_private`: Scan private repositories

## Results

Results will be printed to the console, and saved to a file in the `reports/` directory.
