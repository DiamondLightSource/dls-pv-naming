import logging
import re
from typing import List


def pv_format_check(word: str) -> bool:
    """Check the PV against the format of a PV"""
    if re.match(
        "[A-Z]{2}(?:[0-9][A-Z0-9][A-Z]){0,1}-[A-Z]{2}-[A-Z][A-Z0-9]{0,4}-[0-9]{2}(?::[a-zA-Z0-9_.-]+)*$",
        word,
    ):
        return True
    else:
        return False


def get_device_name(pv: str) -> str:
    """Get the device name, allowing for cases where the pv is incorrect because of a missing colon"""

    # Default assignment
    device = pv

    # Return front end of multiple colon problems (keep as much common as possible)
    if re.search(":{2,}", pv):
        # Look for multiple colons and take first matching group
        # Include the colons to separate from similar device names
        device = re.match("((.*):{2,})", pv).group(0)
    elif len(re.split("[-_]", device)) >= 4:
        # Get the first group
        if ":" in pv:
            device = pv.split(":")[0]
        elements = re.split("[-_]", device)
        # Just the identifier
        initial_element = elements[3]
        shortened_element = elements[3][:2]
        potential_device = re.sub(
            f"(?<=[-_]){initial_element}(.*)", shortened_element, device
        )
        if pv_format_check(potential_device):
            device = potential_device

    return device


def pv_format_report(pv: str) -> List[str]:
    """Produce a dictionary detailing errors with the pv format"""
    errors = []

    if re.search(":{2,}", pv):
        errors.append("Only use single colons to separate device and subdevices")

    # Get the device name
    if (
        len(re.split("[-_]", pv)) > 4
        and ":" not in pv
        and len(re.split("[-_]", pv)[3]) > 2
    ) or (get_device_name(pv) != pv.split(":")[0]):
        # Don't add an unnecessary error here
        # If the report has already added an error based on 2 colons, it doesn't need another
        # one saying you are missing colons
        if len(errors) == 0:
            errors.append("Missing a colon after the device name")
        # Do still strip the name down though
        device = get_device_name(pv)
    else:
        device = pv.split(":")[0]

    logging.debug(f"Device: {device}")

    # Check uppercase
    if device.upper() != device:
        errors.append("PV device name must not contain lowercase characters")

    # Check underscores
    if "_" in device:
        errors.append("PV must not contain underscores in device name")

    # Check there are enough elements to test
    if (len(re.split("[-_]", device)) != 4) or not all(
        [element != "" for element in re.split("[-_]", device)]
    ):
        errors.append(
            "Device name must contain 4 elements separated by hyphens: Domain-TechnicalArea-Component-Identifier"
        )
    else:
        # Detailed inspection of device name elements
        [domain, technical_area, component, identifier] = re.split("[-_]", device)
        logging.debug(f"Domain: {domain}")
        if not re.match("^[A-Z]{2}", domain):
            errors.append(
                f"Domain in {domain} should be composed of two capital letters"
            )
        if len(domain) > 2:
            if not re.match("^[0-9][A-Z0-9][A-Z]$", domain[2:]):
                errors.append(
                    f"Subdomain in {domain} should be composed of a number, alphanumeric, and a letter"
                )

        logging.debug(f"Tech Area: {technical_area}")
        if not re.match("^[A-Z]{2}$", technical_area):
            errors.append(f"Technical Area of {technical_area} must contain 2 letters")

        logging.debug(f"Component: {component}")
        if not re.match("^[A-Z][A-Z0-9]{0,4}$", component):
            errors.append(
                f"Component of {component} must contain up to five alphanumeric characters, first character must be letter"
            )

        logging.debug(f"Identifier: {identifier}")
        # Make an exception for extra colons which will have been reported further up
        if not re.match("^[0-9]{2}$", identifier.split(":")[0]):
            errors.append(f"Identifier of {identifier} must contain only 2 numbers")
            if "O" in identifier:
                errors.append(
                    "Found capital letter O in identifier, expected number zero"
                )

    logging.debug(f"Errors: {errors}")
    return errors


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    get_device_name("BL18I-EA-IOC_03B")

    print(pv_format_check("BL16I-Ea_IO01-:MOTOR:Y"))
    pv_format_report("BL16I-Ea_IO01-:MOTOR:Y")
    print(pv_format_check("B1I6I-EAA-IOCSADSSD-O1:MOTOR:Y"))
    pv_format_report("B1I6I-EAA-IOCSADSSD-O1:MOTOR:Y")
    print(pv_format_check("BL16I-EA-IOC-01"))
    pv_format_report("BL16I-EA-IOC-01")
    pv_format_report("BL02I-EA-IOC-04SR_0_Time")
    pv_format_report("BL02I-EA-IOC-04SR_deadIfZero")
