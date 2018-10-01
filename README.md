# GitHub Scanner

## Overview

This is a CLI wrapper around Trufflehog, designed to scan Github repos for potentially sensitive information.

## Requirements
* Github API Token
* Trufflehog: https://github.com/dxa4481/truffleHog

## How to Use

At a minimum, you must specify a Github Username and Token.  By default, we will scan all public repos
owned by a given user, along with any public repos in any organizations that user belongs to.

### Configuration Options

* `-t`, `--token`: Github API Key
* `-u`, `--user`: Github Username
* `-o`, `--org`: Limit scan to a given organization
* `-p`, `--scan_private`: Scan private repositories

## Results

Results will be printed to the console, and saved to a file in the `reports/` directory.
