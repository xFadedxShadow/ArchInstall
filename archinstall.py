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
        print(e.output)

# Runs a normal command.
def command(command):
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(e.output)


# Update timezone information.
def update_timezone(timezone):
    command(f'sudo timedatectl set-timezone {timezone}')
    command('sudo timedatectl set-ntp true')
    command('sudo hwclock --systohc')

# Update pacman mirrors & conf.
def update_mirrors():
    command('sudo pacman -Syy && sudo pacman -S reflector rsync curl')
    command('sudo reflector --latest 50 --fastest 8 --age 8 --sort rate --country "United States" --save /etc/pacman.d/mirrorlist')
    command('sudo pacman -Syy')

# Update pacman.conf
def update_pacman_conf():
    data = str(read_file('/etc/pacman.conf'))
    data = data.replace('#[multilib]\n#Include = /etc/pacman.d/mirrorlist', '[multilib]\nInclude = /etc/pacman.d/mirrorlist')
    data = data.replace('#ParallelDownloads = 5', 'ParallelDownloads = 4')
    data = data.replace('#Color', 'Color')
    write_file('/etc/pacman.conf', data)


if __name__ == '__main__':
    # Defines arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument('root_partition', help='select root partition.')
    parser.add_argument('--config', help='select a custom configuration.')
    parser.add_argument('--post_install', help='post installation process', default=False, action=argparse.BooleanOptionalAction)
    args = parser.parse_args()


    # Default Configuration.
    default_config = {
        "base": ["base", "base-devel", "linux", "linux-headers", "linux-firmware", "xdg-user-dirs"],
        "network-manager": ["networkmanager"],
        "timezone": "US/Eastern",
        "locale": "en_US.UTF-8",
        "hostname": "archlinux",
        "bootloader": ["grub", "efibootmgr"],
        "network-manager-services": ["NetworkManager"],
        "drivers": [],
        "driver_cfg": "",
        "audio_subsystem": [],
        "users": [],
        "additional_packages": [],
        "services": [],
    }


    # Loads either default or custom config.
    if (args.config) == None:
        write_config('config.ini', default_config)
        config = load_config('config.ini')
        print('Loaded "config.ini" configuration.')
    else:
        config = load_config(args.config)
        print(f'Loaded "{args.config}" configuration.')


    if (args.post_install) == False:

        # 1. Update system clock for live enviorment - from ['timezone']
        update_timezone(config['timezone'])


        # 2. Partition Disks and Format them.


        # 3. Update pacman.conf & mirrors in live enviorment.
        update_pacman_conf()
        update_mirrors()


        # 4. Pacstrap packages - from ["base"]
        for package in config['base']:
            command(f'sudo pacstrap -K {args.root_partition} {package}')
        

        # 5. Update pacman.conf & mirrors for install.
        command(f'sudo cp /etc/pacman.conf {args.root_partition}/etc/pacman.conf')
        command(f'sudo cp /etc/pacman.d/mirrorlist {args.root_partition}/etc/pacman.d/mirrorlist')
        

        # 6. Install network-manager - from ['network-manager']
        for package in config['network-manager']:
            command(f'sudo pacstrap -K {args.root_partition} {package}')
        

        # 7. Generate fstab
        command(f'sudo genfstab -U {args.root_partition} >> {args.root_partition}/etc/fstab')


        # 8. Install bootloader - from ['bootloader']
        for package in config['bootloader']:
            chroot_command(args.root_partition, f'sudo pacman -S {package}')
        
        chroot_command(args.root_partition, 'sudo grub-install --target=x86_64-efi --efi-directory=/boot/efi --bootloader-id=GRUB')


        # 9. Configure root account.
        print('Enter "root" account passwd. (Do not mess up.)')
        chroot_command(args.root_partition, 'sudo passwd')


        # 10. Enable system network-manager service. - from ['network-manager-services']
        for service in config['network-manager-services']:
            chroot_command(args.root_partition, f'sudo systemctl enable {service}')


        # 11. Generate mkinitramfs & bootloader config
        chroot_command(args.root_partition, 'sudo mkinitcpio -P')
        chroot_command(args.root_partition, 'sudo grub-mkconfig -o /boot/grub/grub.cfg')
    
    else:

        # 12. Configure timezone & hwclock - from ['timezone']
        update_timezone(config['timezone'])


        # 13. Configure locales & hostname - from ['locale'] & ['hostname']
        command(f'sudo echo -e "{config["locale"]} UTF-8" > /etc/locale.gen')
        command(f'sudo echo -e "LANG={config["locale"]}" > /etc/locale.conf')
        command('sudo locale-gen')
        command(f'sudo echo -e "{config["hostname"]}" >> /etc/hostname')

        command('sudo pacman -Syy')
        command('sudo pacman -Syu')


        # 14. Install audio subsystem - from ['audio_subsystem']
        if 'audio_subsystem' in config and len(config['audio_subsystem']) > 0:
            for package in config['audio_subsystem']:
                command(f'sudo pacman -S {package}')


        # 15. Install Drivers if there are any - from ['drivers']
        if 'drivers' in config and len(config['drivers']) > 0:
            for package in config['drivers']:
                command(f'sudo pacman -S {package}')
            
            # 15.1. Configure system to use new driver - from ['driver_cfg']
            if 'driver_cfg' in config and len(config['driver_cfg']) > 0:
                if config['driver_cfg'] == 'nvidia':
                    command('sudo cp configs/mkinitcpio/nvidia /etc/mkinitcpio.conf')
                    command('sudo cp configs/grub/nvidia.cfg /etc/default/grub')
                    command('sudo mkdir /etc/pacman.d/hooks')
                    command('sudo cp configs/hooks/nvidia.hook /etc/pacman.d/hooks/nvidia.hook')
        

        # 16. Configure users - from ['users']
        if 'users' in config and len(config['users']) > 0:
            for user in config['users']:
                command(f'sudo useradd -m -g users -G wheel,storage,power -s /bin/bash {user}')
                print(f'Enter password for user: {user}')
                command(f'sudo passwd {user}')


        # 17. Install additional packages - from ['additional_packages']
        if 'additional_packages' in config and len(config['additional_packages']) > 0:
            for package in config['additional_packages']:
                command(f'sudo pacman -S {package}')
        

        # 18. Enable system services - from ['services']
        if 'services' in config and len(config['services']) > 0:
            for service in config['services']:
                command(f'sudo systemctl enable {service}')
        

        # 19. Regenerate initramfs & bootloader config.
        command('sudo mkinitcpio -P')
        command('sudo grub-mkconfig -o /boot/grub/grub.cfg')