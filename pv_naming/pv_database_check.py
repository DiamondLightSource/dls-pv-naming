import logging
import re
from typing import List

from pv_naming.fetch_info import fetch_information

# Empty version of database expected by pv_database_check
empty_database = {
    "domain": {},
    "subdomain": {},
    "domain_pair": {},
    "subdomain_pair": {},
    "technical_area": {},
    "component": {},
}


def pv_database_check(pv: str, database_info: dict = empty_database) -> bool:
    """
    Check that the values of the PV match database records
    
    :param: 
    """
    try:
        [domainGroup, technical_area, component, identifier] = re.split(
            "[-_]", pv.split(":")[0]
        )
    except ValueError:
        logging.error("Not enough values to unpack")
        return False

    # Split domain and subdomain
    if len(domainGroup) > 2:
        domain = domainGroup[:2]
        subdomain = domainGroup[2:]
    else:
        domain = domainGroup
        subdomain = None

    ### Perform checks on elements

    # Check domain is found in database
    logging.debug(f"Domain: {domain}")
    if domain[:2] not in database_info["domain"]:
        return False

    # Check subdomain exists and is paired with the correct domain
    if subdomain:
        logging.debug(f"Subdomain: {subdomain}")
        if subdomain not in database_info["subdomain"]:
            return False
        if subdomain not in database_info["domain_pair"][domain]:
            return False

    # Check technical area found in database
    logging.debug(f"Tech Area: {technical_area}")
    if technical_area not in database_info["technical_area"]:
        return False

    # Check component found in database
    logging.debug(f"Component: {component}")
    if component not in database_info["component"]:
        return False

    # Check identifier is just two numbers
    # Should be caught by a format check but included here for completeness
    if not re.match("^[0-9]{2}$", identifier):
        return False

    # If all of these tests passed, return True
    return True


def pv_database_report(pv: str, database_info: dict = empty_database) -> List[str]:
    """
    Return found issues
    
    :param: 
    """
    errors = []

    try:
        [domainGroup, technical_area, component, identifier] = re.split(
            "[-_]", pv.split(":")[0]
        )
    except ValueError:
        logging.error("Not enough values to unpack")
        errors.append(
            "Device name must contain 4 elements separated by hyphens: Domain-TechnicalArea-Component-Identifier"
        )
        return errors

    # Split domain and subdomain
    if len(domainGroup) > 2:
        domain = domainGroup[:2]
        subdomain = domainGroup[2:]
    else:
        domain = domainGroup
        subdomain = None

    ### Perform checks on elements

    # Check domain is found in database
    logging.debug(f"Domain: {domain}")
    if domain[:2] not in database_info["domain"]:
        errors.append(f"Domain of {domain} not found in database")
    # Check subdomain exists and is paired with the correct domain
    elif subdomain:
        logging.debug(f"Subdomain: {subdomain}")
        if subdomain not in database_info["subdomain"]:
            errors.append(f"Subdomain of {subdomain} not found in database")
        if domain not in database_info["domain_pair"]:
            errors.append(
                f"Domain of {domain} does not have any subdomains recorded in database"
            )
        elif subdomain not in database_info["domain_pair"][domain]:
            errors.append(f"Pair of {domain} and {subdomain} not found in database")

    # Check technical area found in database
    logging.debug(f"Tech Area: {technical_area}")
    if technical_area not in database_info["technical_area"]:
        errors.append(f"Technical Area of {technical_area} not found in database")

    # Check component found in database
    logging.debug(f"Component: {component}")
    if component not in database_info["component"]:
        errors.append(f"Component of {component} not found in database")

    # Check identifier is just two numbers
    # Should be caught by a format check but included here for completeness
    if not re.match("^[0-9]{2}$", identifier):
        errors.append(f"Identifier of {identifier} must contain only 2 numbers")
        if "O" in identifier:
            errors.append("Found capital letter O in identifier, expected number zero")

    return errors


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    database_info = fetch_information()
    # Some tests
    print(pv_database_check("BL16I-EA-IOC-02:MOTOR:TIM"))
    print(pv_database_check("BL16I-EA-IOC-02:MOTOR:TIM", database_info=database_info))
    print(pv_database_check("ME16I-EA-IOC-02:MOTOR:TIM", database_info=database_info))
    print(pv_database_report("ME16I-EA-IOC-02:MOTOR:TIM", database_info=database_info))
    print(pv_database_report("LI16I-EA-IOC-02:MOTOR:TIM", database_info=database_info))
