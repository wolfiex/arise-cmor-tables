#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 16 15:00:00 2020

This script cleans up existing repo tags following discussions in
https://github.com/PCMDI/cmip6-cmor-tables/issues/207

Based on the script:
https://github.com/WCRP-CMIP/CMIP6_CVs/blob/master/src/cleanupTags.py

Using the method described in this Stack Overflow post:
https://stackoverflow.com/questions/21738647/change-date-of-git-tag-or-github-release-based-on-it
"""

import os
import subprocess


def delete_tags(tags):
    """
    Delete existing tags in the repository.

    Args:
        tags (list): List of tags to delete.

    Returns:
        None
    """
    for tag in tags:
        print('Tag:', tag)
        subprocess.call(['git', 'tag', '-d', tag])  # Git delete existing tag
        subprocess.call(['git', 'push', 'origin', ':refs/tags/' + tag])  # Push deletion to remote


def create_tags(tag_list):
    """
    Create new tags in the repository.

    Args:
        tag_list (dict): Dictionary containing tag information.

    Returns:
        None
    """
    for tag, info in tag_list.items():
        print('Tag:', tag)
        print('Comment:', info['Comment'])
        print('MD5:', info['MD5'])

        subprocess.call(['git', 'checkout', info['MD5']])  # Git checkout tag hash

        # Get timestamp of hash
        cmd = 'git show --format=%aD|head -1'
        ps = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
        timestamp = ps.communicate()[0].rstrip().decode("utf-8")
        print('Timestamp:', timestamp)

        # Generate composite command and execute
        cmd = 'GIT_COMMITTER_DATE="%s" git tag -a %s -m "%s"' % (timestamp, tag, info['Comment'])
        print('Command:', cmd)
        subprocess.call(cmd, shell=True)  # Shell=True required for string

    # Push all new tags to remote
    subprocess.call(['git', 'push', '--tags'])


def main():
    # Create cleanup list
    tag_clean = ['6.2.10.0', '6.2.11.2', '6.2.15.0', '6.2.8.23', '6.5.29', '6.6.30', '6.7.31', '6.8.31', '6.9.32']

    # Create target dictionary
    tag_list = {
        '6.2.24': {
            'Comment': 'CMIP6_CVs-6.2.8.23/DREQ-01.00.24/CMOR-3.3.3',
            'MD5': '8eb3f1227afa76ae9db69d2affd1742c480c2031'
        },
        '6.3.27': {
            'Comment': 'CMIP6_CVs-6.2.10.0/DREQ-01.00.27/CMOR-3.3.3',
            'MD5': '26b4f2489c0448ed32c94d408f06cc380d640f89'
        },
        '6.3.27-fixed': {
            'Comment': 'CMIP6_CVs-6.2.11.2/DREQ-01.00.27(modified)/CMOR-3.3.3',
            'MD5': 'b427077cbca2c28b2948752c63e4d3f68449fc1f'
        },
        '6.4.28': {
            'Comment': 'CMIP6_CVs-6.2.15.0/DREQ-01.00.28/CMOR-3.3.3',
            'MD5': '96cd03b09264e07b1d1f5ab912eed085e23e30c2'
        },
        '6.5.29': {
            'Comment': 'CMIP6_CVs-6.2.15.0/DREQ-01.00.29/CMOR-3.4.0',
            'MD5': '0a4445523f2d2964ef37aaf2423691b218a00bee'
        },
        '6.6.30': {
            'Comment': 'CMIP6_CVs-6.2.20.1/DREQ-01.00.30/CMOR-3.4.0',
            'MD5': 'ea2a2f73ee859706c58b34f83df1d52b0b6c1798'
        },
        '6.7.31': {
            'Comment': 'CMIP6_CVs-6.2.35.0/DREQ-01.00.31/CMOR-3.4.0',
            'MD5': '02c87565bcac3c3fc916cd1e0f5242a68b588158'
        },
        '6.8.31': {
            'Comment': 'CMIP6_CVs-6.2.35.3/DREQ-01.00.31/CMOR-3.5.0',
            'MD5': '9f0ed59b7575331c0c25320cfa8bb7f0b722a2d6'
        },
        '6.9.32': {
            'Comment': 'CMIP6_CVs-6.2.53.0/DREQ-01.00.32/CMOR-3.6.0',
            'MD5': 'b73ef115532e5d177dd03f8f662fd262c8b688ba'
        }
    }

    # ensure we have not forgotten a historic tag
    assert len(set(tag_clean) - set(tag_list)) == 0 

    # Delete existing tags
    delete_tags(tag_clean)

    # Create new tags in their place
    create_tags(tag_list)


if __name__ == '__main__':
    main()
