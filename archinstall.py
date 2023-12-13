#!/usr/bin/env python

import os
import json
import argparse
import subprocess

from core.base import PackageManager, ConfigManager, SystemConfig, CommandManager


# Define arguments
def define_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', help='Select a customized configuration.')
    parser.add_argument('--post_install', help='post installation process', default=False, action=argparse.BooleanOptionalAction)
    return parser.parse_args()



if __name__ == '__main__':

    args = define_arguments()

    if (args.config) == None:
        config = ConfigManager.load_config('configs/default.json')
        print('Loaded "configs/default.json" configuration.')
    else:
        config = ConfigManager.load_config(args.config)
        print(f'Loaded "{args.config}" configuration.')


    if (args.post_install) == False:
        PackageManager.pacstrap_install('/mnt', config['base']) # Install base arch system

        CommandManager.run("sudo genfstab -U /mnt >> /mnt/etc/fstab") # Generate fstab

        SystemConfig.config_users('/mnt', config['users']) # Configures Users

        PackageManager.install(config['additional_packages']) # Install additional packages on top of base system

        SystemConfig.config_grub('/mnt', '/boot/efi') # Installs GRUB

        SystemConfig.enable_services('/mnt', config['services']) # Configure services while booted into OS


    else:
        SystemConfig.config_timezone(config['timezone']) # Configure timezone

        SystemConfig.config_locales(config['locale']) # Configure locales

        SystemConfig.config_hostname(config['hostname']) # Configure hostname