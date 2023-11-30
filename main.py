#!/usr/bin/env python

import itertools
import subprocess
from configparser import ConfigParser

# Still have to add disk configuration, partitioning, formatting.

config = ConfigParser()

# xFadedxShadows Configuration File.
config['xFadedxShadowsConfig'] = {
    'base': ['base', 'base-devel', 'linux-zen', 'linux-zen-headers', 'linux-firmware', 'sudo', 'nano', 'xdg-user-dirs', 'amd-ucode'],
    'audio_subsystem': ['pipewire', 'lib32-pipewire', 'pipewire-pulse', 'pipewire-audio', 'pipewire-alsa', 'pipewire-jack', 'lib32-pipewire-jack'],
    'network': ['networkmanager'],
    'bootloader': ['grub', 'efibootmgr'],
    'bootloader_cfg': "configs/grub/nvidia",
    'drivers': ['nvidia-dkms', 'libglvnd', 'nvidia-utils', 'opencl-nvidia', 'lib32-libglvnd', 'lib32-nvidia-utils', 'lib32-opencl-nvidia', 'nvidia-settings'],
    'drivers_cfg': "configs/mkinitcpio/nvidia.conf",
    'pacman_hooks': "config/hooks/nvidia.hook",
    'post_packages': ['firefox', 'discord', 'steam', 'yuzu', 'p7zip', 'unrar', 'transmission-gtk', 'htop', 'neofetch'],
    'timezone': 'US/Eastern',
    'locale': 'en_US.UTF-8',
    'hostname': 'null-desktop',
    'users': ['xfadedxshadow'],
    'groups': ['wheel' ,'storage', 'power'],
    'system_services': ['NetworkManager', 'bluetooth']
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
            subprocess.check_output(command)
        except subprocess.CalledProcessError as error:
            print(error.output)


if __name__ == '__main__':
    write_config()
    read_config("config.cfg")
    config_data = config["xFadedxShadowsConfig"]
    
    # Runs pacstrap for base packages.
    for package in config["base"]:
        command(f"sudo pacstrap -K {package}")
    
    # Generate fstab
    command(f"sudo genfstab -U /{root_parition} >> /{root_parition}/etc/fstab")
    
    # Installs audio subsystem
    for package in config["audio_subsystem"]:
        command(f"sudo arch-chroot /{root_parition} sudo pacman -S {package}")
    
    # Installs networking
    for package in config["network"]:
        command(f"sudo arch-chroot /{root_parition} sudo pacman -S {package}")
    
    # Installs bootloader
    for package in config["bootloader"]:
        command(f"sudo arch-chroot /{root_parition} sudo pacman -S {package}")
    
    # Configure bootloader [Check if config is empty and decide to run]
    #command(f"sudo arch-chroot /{root_parition} sudo cp {config["bootloader_cfg"]} >> /etc/default/grub")
    
    # Installs drivers
    #for package in config["drivers"]:
    #    command(f"sudo arch-chroot /{root_parition} sudo pacman -S {package}")
    
    # Configure drivers [Check if config is empty and decide to run]
    #command(f"sudo arch-chroot /{root_parition} sudo cp {config["drivers_cfg"]} >> /etc/mkinitcpio.conf")
    
    # Installs additional packages
    for package in config["post_packages"]:
        command(f"sudo arch-chroot /{root_parition} sudo pacman -S {package}")
    
    # Configures pacman hooks. [Check if hooks is empty or not and is nvidia]
    #command(f"sudo arch-chroot /{root_parition} sudo mkdir /etc/pacman.d/hooks")
    #command(f"sudo arch-chroot /{root_parition} sudo cp {config["pacman_hooks"]} >> /etc/pacman.d/hooks/nvidia.hook")

    # Configure timezone
    command(f"sudo arch-chroot /{root_parition} sudo timedatectl set-timezone {config["timezone"]}")
    command(f"sudo arch-chroot /{root_parition} sudo ln -sf /usr/share/zoneinfo/{config["timezone"]} /etc/localtime")
    command(f"sudo arch-chroot /{root_parition} sudo hwclock --systohc")

    # Configure locales
    command(f'sudo arch-chroot /{root_parition} sudo echo "{config["locale"]}" >> /etc/locale.gen')
    command(f'sudo arch-chroot /{root_parition} sudo echo "LANG={config[locale]}" >> /etc/locale.conf')
    command(f'sudo arch-chroot /{root_parition} sudo locale-gen')

    # Configure hostname
    command(f'sudo arch-chroot /{root_parition} sudo echo "{config["hostname"]}" >> /etc/hostname')

    # Configure users
    for user in config["users"]:
        command(f"sudo arch-chroot /{root_parition} sudo usermod -m {user}")
        for group in config["groups"]:
            command(f"sudo arch-chroot /{root_parition} sudo usermod -aG {group} {user}")
    
    # Enable system services
    for service in config["system_services"]:
        command(f"sudo arch-chroot /{root_parition} sudo systemctl enable {service}")
    
    # Regenerate initramfs & grub configuration
    command(f"sudo arch-chroot /{root_parition} sudo mkinitcpio -P")
    command(f"sudo arch-chroot /{root_parition} sudo grub-mkconfig -o /boot/grub/grub.cfg")