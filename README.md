# ArchInstall
Script that installs archlinux based on a json configuration file!

Major customization options will be included soon.

## Requirements
Requirements for this project are listed [here](https://github.com/xFadedxShadow/ArchInstall/wiki#requirements) in the wiki.

## Usage
- Pre-Installation.
```python archinstall.py {root_partition}```

- Post-Installation
```python archinstall.py {root_partition} --post_install```

### Optional Arguments
- Load a configuration file for Pre-Installation.
```python archinstall.py {root_partition} --config {config_file}```

- Load a configuration file for Post-Installation.
```python archinstall.py {root_partition} --config {config_file} --post_install```
