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
        SystemConfig.pacman_conf() # Configures pacman.conf

        SystemConfig.update_mirrors() # Updates arch mirrors.

        PackageManager.pacstrap_install('/mnt', config['base']) # Install base arch system

        CommandManager.run("sudo genfstab -U /mnt >> /mnt/etc/fstab") # Generate fstab

        SystemConfig.config_users('/mnt', config['users']) # Configures Users

        CommandManager.run("sudo cp /etc/pacman.conf /mnt/etc/pacman.conf") # Copies pacman.conf to new install

        CommandManager.run("sudo cp /etc/pacman.d/mirrorlist /mnt/etc/pacman.d/mirrorlist") # Copies mirrorslist to new install

        PackageManager.chroot_install('/mnt', config['additional_packages']) # Install additional packages on top of base system

        SystemConfig.config_grub('/mnt', '/boot/efi') # Installs GRUB

        SystemConfig.enable_services('/mnt', config['services']) # Configure services while booted into OS

        CommandManager.run('cp -r "~/ArchInstall" /mnt/ArchInstall') # Copies script files to root partition for post installation


    else:
        SystemConfig.config_timezone(config['timezone']) # Configure timezone

        SystemConfig.config_locales(config['locale']) # Configure locales

        SystemConfig.config_hostname(config['hostname']) # Configure hostname