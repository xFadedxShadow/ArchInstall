#!/usr/bin/env python

import os
import json
import argparse
import itertools


# xFadedxShadows Configuration File.
config = {
    "base": [
        "base",
        "base-devel",
        "linux-zen",
        "linux-zen-headers",
        "linux-firmware",
        "sudo",
        "nano",
        "xdg-user-dirs",
        "amd-ucode"
    ],
    "audio_subsystem": [
        "pipewire",
        "pipewire-pulse",
        "pipewire-audio",
        "pipewire-alsa",
        "pipewire-jack"
    ],
    "network": [
        "networkmanager"
    ],
    "bootloader": [
        "grub",
        "efibootmgr"
    ],
    "drivers": [
        "default"
    ],
    "bootloader_cfg": "default",
    "drivers_cfg": "default",
    "pacman_hooks": [
    ],
    "post_packages": [
        "firefox",
        "discord",
        "steam",
        "yuzu",
        "p7zip",
        "unrar",
        "transmission-gtk",
        "htop",
        "neofetch"
    ],
    "timezone": "US/Eastern",
    "locale": "en_US.UTF-8",
    "hostname": "null-desktop",
    "users": [
        "xfadedxshadow"
    ],
    "groups": [
        "wheel",
        "storage",
        "power"
    ],
    "system_services": [
        "NetworkManager"
    ]
}


# Writes default configuration if not found.
def write_config():
    with open('config.cfg', 'w') as f:
        f.write(json.dumps(config, indent=4))


# Reads a configuration
def read_config(configuration):
    with open('config.cfg', 'r') as f:
        return json.load(f)


# Chroots into root enviorment and runs a command.
def command(command):
    os.system(f'/bin/bash -c {command}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--root_partition")
    args = parser.parse_args()

    write_config()
    config_data = read_config("config.cfg")
    
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
    
    # Configure bootloader [Check if config is empty and decide to run] > tries to install a default config which cannot be found?
    print(f"Error Test: {config_data["bootloader_cfg"]}")
    if config_data["bootloader_cfg"] != "default":
        command(f'sudo arch-chroot {args.root_partition} sudo cp configs/grub/{config_data["bootloader_cfg"]} >> /etc/default/grub')
    
    # Installs drivers
    if config_data["drivers"] != "default":
        for package in config_data["drivers"]:
            command(f'sudo arch-chroot {args.root_partition} sudo pacman -S {package}')
    
    # Configure drivers [Check if config is empty and decide to run]
    if config_data["drivers_cfg"] != "default":
        command(f'sudo arch-chroot {args.root_partition} sudo cp configs/mkinitcpio/{config_data["drivers_cfg"]} >> /etc/mkinitcpio.conf')
    
    # Installs additional packages
    for package in config_data["post_packages"]:
        command(f'sudo arch-chroot {args.root_partition} sudo pacman -S {package}')
    
    # Configures pacman hooks. [Check if hooks is empty or not and is nvidia]
    if len(config_data["pacman_hooks"]) == 0:
        command(f'sudo arch-chroot {args.root_partition} sudo mkdir /etc/pacman.d/hooks')
        for hook in config_data["pacman_hooks"]:
            command(f'sudo arch-chroot {args.root_partition} sudo cp configs/hooks/{hook} >> /etc/pacman.d/hooks/{hook}')

    # Configure timezone
    command(f'sudo arch-chroot {args.root_partition} sudo timedatectl set-timezone {config_data["timezone"]}')
    command(f'sudo arch-chroot {args.root_partition} sudo ln -sf /usr/share/zoneinfo/{config_data["timezone"]} /etc/localtime')
    command(f'sudo arch-chroot {args.root_partition} sudo hwclock --systohc')

    # Configure locales
    command(f'sudo arch-chroot {args.root_partition} sudo echo -e "{config_data["locale"]} UTF-8" >> /etc/locale.gen') # Not echoing into file.
    command(f'sudo arch-chroot {args.root_partition} sudo touch /etc/locale.conf')
    command(f'sudo arch-chroot {args.root_partition} sudo echo -e LANG="{config["locale"]}" >> /etc/locale.conf') # Not echoing into file.
    command(f'sudo arch-chroot {args.root_partition} sudo locale-gen')

    # Configure hostname || Did not configure hostname
    command(f'sudo arch-chroot {args.root_partition} sudo touch /etc/hostname')
    command(f'sudo arch-chroot {args.root_partition} sudo echo -e "{config_data["hostname"]}" >> /etc/hostname') # Not echoing into file.

    # Configure users
    for user in config_data["users"]:
        command(f'sudo arch-chroot {args.root_partition} sudo useradd -m -g users -G wheel,storage,power -s /bin/bash {user}')
        print(f'Enter a passwd for {user}.')
        command(f'sudo arch-chroot {args.root_partition} sudo passwd {user}')
    
    # Root passwd
    print('Enter a passwd for root.')
    command(f'sudo arch-chroot {args.root_partition} sudo passwd')
    
    # Enable system services
    for service in config_data["system_services"]:
        command(f'sudo arch-chroot {args.root_partition} sudo systemctl enable {service}')
    
    # Regenerate initramfs & grub configuration
    command(f'sudo arch-chroot {args.root_partition} sudo mkinitcpio -P')
    command(f'sudo arch-chroot {args.root_partition} sudo grub-mkconfig -o /boot/grub/grub.cfg')