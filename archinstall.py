#!/usr/bin/env python

import json
import argparse
import subprocess


# Read a file.
def read_file(_):
    with open(_, 'r') as f : return f.read()

# Write a file.
def write_file(_, data):
    with open(_, 'w') as f : return f.write(data)


# Writes configuration file.
def write_config(config_file, config_data):
    write_file(config_file, json.dumps(config_data, indent=4))

# Loads configuration file.
def load_config(config_file):
    return json.loads(read_file(config_file))


# Runs a chrooted command.
def chroot_command(partition, command):
    try:
        subprocess.run(f'sudo arch-chroot {partition} {command}', shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(e.output.decode())

# Runs a normal command.
def command(command):
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(e.output.decode())


if __name__ == '__main__':
    # Defines arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument('root_partition', help='select root partition.')
    parser.add_argument('--config', help='select a custom configuration.')
    parser.add_argument('--post_install', help='post installation process', default=False, action=argparse.BooleanOptionalAction)
    args = parser.parse_args()


    # Default Configuration.
    default_config = {
        "base": ["base", "base-devel", "linux", "linux-headers", "linux-firmware"],
        "network-manager": ["networkmanager"],
        "timezone": "US/Eastern",
        "locales": "en_US.UTF-8",
        "hostname": "archlinux",
        "bootloader": ["grub", "efibootmgr"]
    }

    write_config('config.ini', default_config)

    # Loads either default or custom config.
    if (args.config) == None:
        config = load_config('config.ini')
    else:
        config = load_config(args.config)


    if (args.post_install) == False:

        # 1. Update system clock for live enviorment.
        command(f'sudo timedatectl set-timezone {config["timezone"]}')
        command('sudo timedatectl set-ntp true')
        command('sudo hwclock --systohc')

        # 2. Update pacman.conf & mirrors in live enviorment.
        data = str(read_file('/etc/pacman.conf'))
        data.replace('#[multilib]', '[multilib]')
        data.replace('#Include = /etc/pacman.d/mirrorlist', 'Include = /etc/pacman.d/mirrorlist')
        data.replace('#ParallelDownloads = 5', 'ParallelDownloads = 4')
        data.replace('#Color', 'Color')
        write_file('/etc/pacman.conf', data)
        command('sudo pacman -Syy && yes | sudo pacman -S reflector rsync curl')
        command('sudo reflector --latest 50 --fastest 8 --age 8 --sort rate --country "United States" --save /etc/pacman.d/mirrorlist')
        command('sudo pacman -Syy')

        # 3. Partition Disks and Format them.

        # 4. Pacstrap minimum packages
        for package in config['base']:
            command(f'sudo pacstrap -K {args.root_partition} {package}')
        
        # 5. Install network-manager
        for package in config['network-manager']:
            command(f'sudo pacstrap -K {args.root_partition} {package}')
        
        # 6. Generate fstab
        command(f'sudo genfstab -U {args.root_partition} >> {args.root_partition}/etc/fstab')

        # 7. Install bootloader
        for package in config['bootloader']:
            chroot_command(args.root_partition, f'sudo pacman -S {package}')
        
        chroot_command(args.root_partition, 'sudo grub-install --target=x86_64-efi --efi-directory=/boot/efi --bootloader-id=GRUB')

        # 8. Configure root account.
        print('Enter "root" account passwd. (Do not mess up.)')
        chroot_command(args.root_partition, 'sudo passwd')

        # 9. Generate mkinitramfs & bootloader config
        chroot_command(args.root_partition, 'sudo mkinitcpio -P')
        chroot_command(args.root_partition, 'sudo grub-mkconfig -o /boot/grub/grub.cfg')
    
    else:
        print("Post Installation Process.")





    # How to check if any driver packages exist in config file.
    #if 'drivers' in config and len(config['drivers']) > 0:
    #    print(f'Driver Packages Loaded. | {len(config["drivers"])}')
    #else:
    #    print("No driver packages!")d