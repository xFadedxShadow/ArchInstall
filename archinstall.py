#!/usr/bin/env python

import os
import json
import argparse
import subprocess

from core.base import PackageManager, ConfigManager, SystemConfig


# Define arguments
def define_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', help='Select a customized configuration.')
    return parser.parse_args()



if __name__ == '__main__':

    args = define_arguments()

    if (args.config) == None:
        config = ConfigManager.load_config('configs/default.json')
        print('Loaded "configs/default.json" configuration.')
    else:
        config = ConfigManager.load_config(args.config)
        print(f'Loaded "{args.config}" configuration.')


    PackageManager.pacstrap_install('/', config['base']) # Install base arch system

    PackageManager.chroot_install('/', config['additional_packages']) # Install additional packages on top of base system

    # PackageManager.chroot_uninstall() | Uninstall packages from base system

    SystemConfig.config_timezone('/', config['timezone']) # Configure timezone

    SystemConfig.config_locales('/', config['locale']) # Configure locales

    SystemConfig.config_hostname('/', config['hostname']) # Configure hostname

    SystemConfig.config_users('/', config['users']) # Configures Users

    SystemConfig.config_grub('/', '/boot/efi') # Installs GRUB

    SystemConfig.enable_services('/', config['services']) # Configure services while booted into OS

    # PackageManager.install() | Install packages while booted into OS

    # PackageManager.uninstall() | Uninstall packages while booted into OS