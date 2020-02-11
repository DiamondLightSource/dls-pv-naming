import logging
import re
from typing import List, Optional


# Split into sections based on either dashes or underscores
# (to collect possible errors)
def section_split(input: str) -> List[str]:
    return re.split("[-_]", input)


def split_into_elements(pv: str):
    try:
        [domainGroup, technical_area, component, identifier] = section_split(
            pv.split(":")[0]
        )
    except ValueError:
        logging.error("Not enough values to unpack")
        raise

    # Split domain and subdomain
    if len(domainGroup) > 2:
        domain = domainGroup[:2]
        subdomain: Optional[str] = domainGroup[2:]
    else:
        domain = domainGroup
        subdomain = None

    return [domain, subdomain, technical_area, component, identifier]
