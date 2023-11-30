#!/usr/bin/env python

import argparse
import itertools
import subprocess
from configparser import ConfigParser

# Still have to add disk configuration, partitioning, formatting.

config = ConfigParser()

# xFadedxShadows Configuration File.
config["xFadedxShadowsConfig"] = {
    'base': ["base', 'base-devel', 'linux-zen', 'linux-zen-headers', 'linux-firmware', 'sudo', 'nano', 'xdg-user-dirs', 'amd-ucode"],
    'audio_subsystem': ["pipewire', 'lib32-pipewire', 'pipewire-pulse', 'pipewire-audio', 'pipewire-alsa', 'pipewire-jack', 'lib32-pipewire-jack"],
    'network': ["networkmanager"],
    'bootloader': ["grub', 'efibootmgr"],
    'bootloader_cfg': 'configs/grub/nvidia',
    'drivers': ["nvidia-dkms', 'libglvnd', 'nvidia-utils', 'opencl-nvidia', 'lib32-libglvnd', 'lib32-nvidia-utils', 'lib32-opencl-nvidia', 'nvidia-settings"],
    'drivers_cfg': 'configs/mkinitcpio/nvidia.conf',
    'pacman_hooks': 'config/hooks/nvidia.hook',
    'post_packages': ["firefox', 'discord', 'steam', 'yuzu', 'p7zip', 'unrar', 'transmission-gtk', 'htop', 'neofetch"],
    'timezone': 'US/Eastern',
    'locale': 'en_US.UTF-8',
    'hostname': 'null-desktop',
    'users': ["xfadedxshadow"],
    'groups': ["wheel' ,'storage', 'power"],
    'system_services': ["NetworkManager', 'bluetooth"]
}


# Writes default configuration if not found.
def write_config():
    with open('config.cfg', 'w') as data:
        config.write(data)


# Reads a configuration
def read_config(configuration):
    config.read(configuration)


# Chroots into root enviorment and runs a command.
def command(command):
        try:
            subprocess.check_output(command, shell=True).rstrip()
        except subprocess.CalledProcessError as error:
            print(error.output).rstrip()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--root_partition")
    args = parser.parse_args()

    write_config()
    read_config('config.cfg')
    config_data = config["xFadedxShadowsConfig"]
    
    # Runs pacstrap for base packages.
    for package in config_data["base"]:
        command(f'sudo pacstrap -K {args.root_partition} {package}')
    
    # Generate fstab
    command(f'sudo genfstab -U {args.root_partition} >> {args.root_partition}/etc/fstab')
    
    # Installs audio subsystem
    for package in config_data["audio_subsystem"]:
        command(f'sudo arch-chroot {args.root_partition} sudo pacman -S {package}')
    
    # Installs networking
    for package in config_data["network"]:
        command(f'sudo arch-chroot {args.root_partition} sudo pacman -S {package}')
    
    # Installs bootloader
    for package in config_data["bootloader"]:
        command(f'sudo arch-chroot {args.root_partition} sudo pacman -S {package}')
    
    command(f'sudo arch-chroot {args.root_partition} sudo grub-install --target=x86_64-efi --efi-directory=/boot/efi --bootloader-id=GRUB')

    
    # Configure bootloader [Check if config is empty and decide to run]
    #command(f'sudo arch-chroot {args.root_partition} sudo cp {config_data["bootloader_cfg"]} >> /etc/default/grub')
    
    # Installs drivers
    #for package in config_data["drivers"]:
    #    command(f'sudo arch-chroot {args.root_partition} sudo pacman -S {package}')
    
    # Configure drivers [Check if config is empty and decide to run]
    #command(f'sudo arch-chroot {args.root_partition} sudo cp {config_data["drivers_cfg"]} >> /etc/mkinitcpio.conf')
    
    # Installs additional packages
    for package in config_data["post_packages"]:
        command(f'sudo arch-chroot {args.root_partition} sudo pacman -S {package}')
    
    # Configures pacman hooks. [Check if hooks is empty or not and is nvidia]
    #command(f'sudo arch-chroot {args.root_partition} sudo mkdir /etc/pacman.d/hooks')
    #command(f'sudo arch-chroot {args.root_partition} sudo cp {config_data["pacman_hooks"]} >> /etc/pacman.d/hooks/nvidia.hook')

    # Configure timezone
    command(f'sudo arch-chroot {args.root_partition} sudo timedatectl set-timezone {config_data["timezone"]}')
    command(f'sudo arch-chroot {args.root_partition} sudo ln -sf /usr/share/zoneinfo/{config_data["timezone"]} /etc/localtime')
    command(f'sudo arch-chroot {args.root_partition} sudo hwclock --systohc')

    # Configure locales
    command(f'sudo arch-chroot {args.root_partition} sudo echo "{config_data["locale"]}" >> /etc/locale.gen')
    command(f'sudo arch-chroot {args.root_partition} sudo echo "LANG={config[locale]}" >> /etc/locale.conf')
    command(f'sudo arch-chroot {args.root_partition} sudo locale-gen')

    # Configure hostname
    command(f'sudo arch-chroot {args.root_partition} sudo echo "{config_data["hostname"]}" >> /etc/hostname')

    # Configure users
    for user in config_data["users"]:
        command(f'sudo arch-chroot {args.root_partition} sudo usermod -m {user}')
        for group in config_data["groups"]:
            command(f'sudo arch-chroot {args.root_partition} sudo usermod -aG {group} {user}')
    
    # Enable system services
    for service in config_data["system_services"]:
        command(f'sudo arch-chroot {args.root_partition} sudo systemctl enable {service}')
    
    # Regenerate initramfs & grub configuration
    command(f'sudo arch-chroot {args.root_partition} sudo mkinitcpio -P')
    command(f'sudo arch-chroot {args.root_partition} sudo grub-mkconfig -o /boot/grub/grub.cfg')