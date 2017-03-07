import json
import time
import datetime
import os
import sys
import getpass
from os.path import expanduser
from subprocess import Popen, PIPE, STDOUT
import subprocess as sb
import stat
import tempfile
import pwd

import git
import bit
import owncloud
import rsync

structure="\n\
/file_system_a\n\
    |\n\
    '- data\n\
        |\n\
        '- projects\n\
            |\n\
            |- Company_A\n\
            |   |\n\
            |   |- CA_project_y\n\
            |   |\n\
            |   '- CA_project_x\n\
            |       |\n\
            |       |- results\n\
            |       |- models\n\
            |       |- scripts\n\
            |       |- tmp\n\
            |       |- slurm_logs\n\
            |       '- wiki\n\
            |\n\
            '- Company_B\n\
                |\n\
                '- CB_project_n\n\n\
absolute path to projects =  /file_system_a/data/projects/"

def get_owncloud_address():
    owncloud_address=str(raw_input("Please give in your ownCloud address (eg. http://domain.tld/owncloud): ")) or None
    return owncloud_address

def get_owncloud_upload_folder():
    owncloud_upload_folder=str(raw_input("Please give in the folder in your ownCloud that will be used to deliver data to users.\nYou can share this folder with your colleagues so that everybody delivers data through the same folder. (default: DELIVERY_SERVICE):")) or "DELIVERY_SERVICE"
    return owncloud_upload_folder

def get_owncloud_download_folder():
    owncloud_download_folder=str(raw_input("Please give in the folder in your ownCloud that will be used to retrieve data from users.\nYou can share this folder with your colleagues so that everybody retrieves data through the same folder. (default: DROPBOX):")) or "DROPBOX"
    return owncloud_download_folder

def get_owncloud_user(config_file=None):
    if config_file:
        owncloud_user=str(raw_input("Please give in your ownCloud user name or press Enter if you do not want to save this information on the config file: ")) or None
    else:
        owncloud_user=str(raw_input("Please give in your ownCloud user name: ")) or None
    return owncloud_user

def get_owncloud_pass(config_file=None):
    if config_file:
        owncloud_pass=str(getpass.getpass(prompt="Please give in your ownCloud password or press Enter if you do not want to save this information on the config file: ")) or None
    else:
        owncloud_pass=str(getpass.getpass(prompt="Please give in your ownCloud password: ")) or None
    return owncloud_pass

def get_github_address():
    github_address=str(raw_input("Github server address (default: https://github.com): ") or "https://github.com")
    return github_address

def get_github_organization():
    github_organization=str(raw_input("Your GitHub organization name (eg. mpg-age-bioinformatics for https://github.com/mpg-age-bioinformatics): ")) or None
    return github_organization

def get_github_user(config_file=None,gitssh=None):
    if not gitssh:
        if config_file:
            github_user=str(raw_input("Please give in your user name for your github server or press Enter if you do not want to save this information on the config file: ")) or None
        else:
            github_user=str(raw_input("Please give in your user name for your github server: ")) or None
    else:
        github_user=None
    return github_user

def get_github_pass(config_file=None,gitssh=None):
    if not gitssh:
        if config_file:
            github_pass=str(getpass.getpass(prompt="Please give in your password for your github server or press Enter if you do not want to save this information on the config file: ")) or None
        else:
            github_pass=str(getpass.getpass(prompt="Please give in your password for your github server: ")) or None
    else:
        github_pass=None
    return github_pass

def get_local_path(structure=structure):
    local_path=str(raw_input("The bermuda information triangle works on the basis that all your projects are located in the same path and have a parent subpath in your local machine ie. %s\n" %structure ) ) or None
    return local_path

def get_user_group():
    user_group=str(raw_input("If you are using ACLs to give your group members access to this project please give in the users that will have read write access to every projects top folders. eg. userA,userB,userC -- DO NOT forger to give in your own user name: ")) or None
    if user_group:
        user_group=user_group.split(",")
	return user_group

def get_github_api(github_address):
    if "github.com" in github_address:
        github_api="https://api.github.com/orgs/"
    else:
        github_api=github_address+"/api/v3/orgs/"
    return github_api

def make_bitconfig(require_func=requirements,special_reqs=special_reqs):
    configdic={}
    configdic=bit.check_reqs(require_func,configdic,config_file=True, gitssh=None)
    uhome=expanduser("~")+"/"
    configfile=open(uhome+".bit_config","w+")
    with open(uhome+".bit_config", 'w') as configfile:
        json.dump(configdic, configfile)
    os.chmod(uhome+".bit_config", stat.S_IRWXU )
    print "Your bit config file as been generated:"
    for c in configdic:
        if "pass" not in c:
            print c, configdic.get(c)
            sys.stdout.flush()
        elif configdic.get(c) == None:
            print c, configdic.get(c)
            sys.stdout.flush()
        else:
            print c, "*"
            sys.stdout.flush()

def read_bitconfig(showit=None,bit_config=".bit_config"):
    uhome=expanduser("~")+"/"
    with open(uhome+bit_config, 'r') as configfile:
        configdic=json.load(configfile)
    if showit:
        for c in configdic:
            if "pass" not in c:
                print c, configdic.get(c)
                sys.stdout.flush()
            elif configdic.get(c) == None:
                print c, configdic.get(c)
                sys.stdout.flush()
            else:
                print c, "*"
                sys.stdout.flush()
    return configdic
