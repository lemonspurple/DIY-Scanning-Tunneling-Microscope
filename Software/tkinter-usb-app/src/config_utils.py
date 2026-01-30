import configparser
import os
import sys

# Create a ConfigParser object
config = configparser.ConfigParser()

# Define the path to the config file
if hasattr(sys, "_MEIPASS"):
    # If running as a PyInstaller .exe, look for config.ini in the same directory as the .exe
    base_path = os.path.dirname(sys.executable)
else:
    # If running as a script, look for config.ini in the script's directory
    base_path = os.path.dirname(__file__)

config_file = os.path.join(base_path, "config.ini")
print(f"Config file path: {config_file}")


def get_config(section, option, fallback=None):
    """
    Get a configuration value.

    :param section: The section of the config file.
    :param option: The option within the section.
    :param fallback: The fallback value if the option is not found.
    :return: The value of the configuration option.
    """
    return config.get(section, option, fallback=fallback)


def set_config(section, option, value):
    """
    Set a configuration value and save it to the config file.

    :param section: The section of the config file.
    :param option: The option within the section.
    :param value: The value to set.
    """
    if not config.has_section(section):
        config.add_section(section)
    config.set(section, option, value)
    with open(config_file, "w") as configfile:
        config.write(configfile)


def create_default_config():
    """Create a default config.ini file if it doesn't exist"""
    default_config = configparser.ConfigParser()

    # USB section
    default_config.add_section("USB")
    default_config.set("USB", "port", "COM3")
    default_config.set("USB", "baudrate", "460800")

    # ADC_TO_NA section
    default_config.add_section("ADC_TO_NA")
    default_config.set("ADC_TO_NA", "adc_voltage_divider", "1000000.0")
    default_config.set("ADC_TO_NA", "adc_value_max", "65535.0")
    default_config.set("ADC_TO_NA", "adc_voltage_max", "3.3")

    # TUNNEL section
    default_config.add_section("TUNNEL")
    default_config.set("TUNNEL", "tunnelcounts", "100")

    # Write the config file
    with open(config_file, "w") as configfile:
        default_config.write(configfile)
    print(f"Created default config file: {config_file}")


# Create the config file if it does not exist
if not os.path.isfile(config_file):
    create_default_config()

# Read the config file
config.read(config_file)
