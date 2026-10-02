import logging
import re


# Split into sections based on either dashes or underscores
# (to collect possible errors)
def section_split(input: str) -> list[str]:
    return re.split("[-_]", input)


def split_into_elements(pv: str):
    try:
        [domain_group, technical_area, component, identifier] = section_split(
            pv.split(":")[0]
        )
    except ValueError:
        logging.error("Not enough values to unpack")
        raise

    # Split domain and subdomain
    if len(domain_group) > 2:
        domain = domain_group[:2]
        subdomain: str | None = domain_group[2:]
    else:
        domain = domain_group
        subdomain = None

    return [domain, subdomain, technical_area, component, identifier]
