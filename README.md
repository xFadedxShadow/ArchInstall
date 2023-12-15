# ArchInstall
Script that installs archlinux based on a json configuration file!

Major customization options will be included soon.

# Tasks
- [ ] Add support for disk partition & formatting.
- So far disk partition and formatting is not included in this script so you will have to partition manually before you run the script.

- [ ] Add pre-defined configurations for desktop enviorments.
- So far this script does not include any configuration presets for desktop enviorments.

## Requirements
Requirements for this project are listed [here](https://github.com/xFadedxShadow/ArchInstall/wiki#requirements) in the wiki.

## Usage
```python
python archinstall.py --config {config_location}
```

## Post Installation Usage
Run this under 'su' while booted into OS
```python
python archinstall.py --config {config_location} --post_install
```

## Default Config
```json
{
    "base": [
        "base",
        "base-devel",
        "linux",
        "linux-headers",
        "linux-firmware",
        "xdg-user-dirs",
        "dosfstools",
        "e2fsprogs",
        "exfatprogs",
        "btrfs-progs",
        "networkmanager",
        "python",
        "nano",
        "bash-completion",
        "grub",
        "efibootmgr"
    ],
    "users": [
        "username"
    ],
    "additional_packages": [
        "xorg-server",
        "plasma-desktop",
        "plasma-meta",
        "dolphin",
        "konsole",
        "pipewire",
        "lib32-pipewire",
        "pipewire-audio",
        "pipewire-alsa",
        "pipewire-pulse",
        "pipewire-jack",
        "firefox",
        "neofetch"
    ],
    "services": [
        "NetworkManager.service",
        "bluetooth.service",
        "sddm.service"
    ],
    "timezone": "US/Eastern",
    "locale": "en_US.UTF-8",
    "hostname": "archlinux"
}
```

- Learn more about creating a customized configuration file [here](https://github.com/xFadedxShadow/ArchInstall/wiki#creating-a-custom-configuration-insights) in the wiki.
