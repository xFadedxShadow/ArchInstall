#!/usr/bin/env python

import os
import json
import platform
import subprocess


class CommandManager:
    def chroot_command(root_point = None, command = None):
        if type(root_point) != str or type(root_point) == None:
            raise TypeError(f"Root Mount Point: '{root_point}' argument must be type of str.")

        elif os.path.exists(root_point) == False:
            raise Exception(f"Root Mount Point: '{root_point}' directory does not exist.")
        
        print(f"Mount point")

        subprocess.run(f"sudo arch-chroot {root_point} {command}")


class PackageManager:
    def install(packages = None):

        if type(packages) != list or type(packages) == None:
            raise TypeError("'Packages' argument must be type of list.")
        

        for package in packages:
            print(f"\nAttempting to install '{package}' package.\n")

            output = subprocess.run(f"sudo pacman -S {package}", shell=True)

            if (output.returncode == 1):
                raise ChildProcessError(f"Package '{package}' was either not found, or unable to install.")
        

    def uninstall(packages = None):

        if type(packages) != list or type(packages) == None:
            raise TypeError("'Packages' argument must be type of list.")
        

        for package in packages:
            print(f"\nAttempting to uninstall '{package}' package.\n")

            output = subprocess.run(f"sudo pacman -Rns {package}", shell=True)
            
            if (output.returncode == 1):
                raise ChildProcessError(f"Package: '{package}' was either not found, or unable to uninstall.")


    def pacstrap_install(root_point = None, packages = None):

        if type(packages) != list or type(packages) == None:
            raise TypeError(f"Packages: '{packages}' argument must be type of list.")
        
        if type(root_point) != str or type(root_point) == None:
            raise TypeError(f"Root Mount Point: '{root_point}' argument must be type of str.")

        elif os.path.exists(root_point) == False:
            raise Exception(f"Root Mount Point: '{root_point}' directory does not exist.")
        

        for package in packages:
            print(f"\nAttempting to install '{package}' package.\n")

            output = subprocess.run(f"sudo pacstrap -K {root_point} {package}", shell=True)

            if (output.returncode == 1):
                raise ChildProcessError(f"Package: '{package}' was either not found, or unable to install.")


    def chroot_install(root_point = None, packages = None):

        if type(packages) != list or type(packages) == None:
            raise TypeError(f"Packages: '{packages}' argument must be type of list.")

        if type(root_point) != str or type(root_point) == None:
            raise TypeError(f"Root Mount Point: '{root_point}' argument must be type of str.")

        elif os.path.exists(root_point) == False:
            raise Exception(f"Root Mount Point: '{root_point}' directory does not exist.")


        for package in packages:
            print(f"\nAttempting to install '{package}' package.\n")

            output = subprocess.run(f"sudo arch-chroot {root_point} sudo pacman -S {package}", shell=True)
            
            if (output.returncode == 1):
                raise ChildProcessError(f"Package: '{package}' was either not found, or unable to install.")


    def chroot_uninstall(root_point = None, packages = None):

        if type(packages) != list or type(packages) == None:
            raise TypeError(f"Packages: '{packages}' argument must be type of list.")

        if type(root_point) != str or type(root_point) == None:
            raise TypeError(f"Root Mount Point: '{root_point}' argument must be type of str.")

        elif os.path.exists(root_point) == False:
            raise Exception(f"Root Mount Point: '{root_point}' directory does not exist.")


        for package in packages:
            print(f"\nAttempting to uninstall '{package}' package.\n")

            output = subprocess.run(f"sudo arch-chroot {root_point} sudo pacman -Rns {package}", shell=True)
            
            if (output.returncode == 1):
                raise ChildProcessError(f"Package: '{package}' was either not found, or unable to uninstall.")



# Configure timezone | Locales | Hostname | Services | GRUB | Users | Files | live enviorment
class SystemConfig:
    def read_file(_file):
        with open(_file, 'r') as f : return f.read()

    
    def write_file(_file, _data):
        with open(_file, 'w') as f : return f.write(_data)


    def config_timezone(root_point = None, timezone = None):
        if type(root_point) != str or type(root_point) == None:
            raise TypeError(f"Root Mount Point: '{root_point}' argument must be type of str.")


        CommandManager.chroot_command(root_point, f"sudo timedatectl set-timezone {timezone}")
        CommandManager.chroot_command(root_point, "sudo timedatectl set-ntp true")
        CommandManager.chroot_command(root_point, f"sudo hwclock --systohc")
    

    def config_locales(root_point = None, locale = None):
        if type(locale) != str or type(locale) == None:
            raise TypeError(f"Locale: '{locale}' argument must be of type str.")


        CommandManager.chroot_command(root_point, f"sudo echo -e '{locale} UTF-8' > /etc/locale.gen")
        CommandManager.chroot_command(root_point, f"sudo echo -e 'LANG={locale}' > /etc/locale.conf")
        CommandManager.chroot_command(root_point, "sudo locale-gen")


    def config_hostname(root_point = None, hostname = None):
        if type(hostname) != str or type(hostname) == None:
            raise TypeError(f"Hostname: '{hostname}' must be of type str.")
        

        CommandManager.chroot_command(root_point, f"sudo echo -e '{hostname}' >> /etc/hostname")


    def config_users(root_point = None ,users = None):
        if type(users) != list or type(users) == None:
            raise TypeError(f"Users: '{users}' must be of type list.")
        

        for user in users:
            CommandManager.chroot_command(root_point, f"sudo useradd -m -g users -G wheel,storage,power -s /bin/bash {user}")
            print(f"{user} Password")
            CommandManager.chroot_command(root_point, f"sudo passwd {user}")
        

        print("Root Password.")
        CommandManager.chroot_command(root_point, "sudo passwd")


    def enable_services(root_point = None, services = None):
        if type(services) != list or type(services) == None:
            raise TypeError(f"Services: '{services}' argument must be type of list.")
        

        for service in services:
            CommandManager.chroot_command(root_point, f"sudo systemctl enable {service}")
    

    def config_grub(root_point = None ,efi_mount_point = None):
        if type(efi_mount_point) != str or type(efi_mount_point) == None:
            raise TypeError(f"EFI Boot Mount Point: '{efi_mount_point}' argument must be type of str.")

        elif os.path.exists(root_point) == False:
            raise Exception(f"EFI Boot Mount Point: '{efi_mount_point}' directory does not exist.")
        

        CommandManager.chroot_command(root_point ,f"sudo grub-install --target=x86_64-efi --efi-directory={efi_mount_point} --bootloader-id=GRUB")
        CommandManager.chroot_command(root_point ,"sudo grub-mkconfig -o /boot/grub/grub.cfg")


class ConfigManager:
    def load_config(config = None):
        # Select a configuration from 'configs' directory | If none are selected or found use default config | return the config.
        if type(config) != str or type(config) == None:
            raise TypeError(f"Config: '{config}' must be of type str.")
        
        elif os.path.exists(config) == False:
            raise Exception(f"Configuration: '{config}' file does not exist.")

        
        return json.loads(SystemConfig.read_file(config))