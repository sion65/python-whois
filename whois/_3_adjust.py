import re
import sys
import datetime
from .exceptions import UnknownDateFormat

from typing import Any, List, Dict, Optional

PYTHON_VERSION = sys.version_info[0]

# Define a function for
# for validating an Email
def check_email(email):

    # pass the regualar expression
    # and the string in search() method
    if "@" in email:
        return email

    else:
        return ''

def check_regid(regid):

    # pass the regualar expression
    # and the string in search() method
    if regid.isdigit():
        return regid

    else:
        return ''

class Domain:
    # make sure all fields actually exist allways
    name: str = None
    tld = None
    registrar = None
    reg_id = None
    reg_abuse = None
    registrant_country = None

    creation_date = None
    expiration_date = None
    last_updated = None

    status = None
    statuses: List = []

    dnssec = None
    name_servers = []
    owner = None
    abuse_contact = None
    reseller = None
    registrant = None
    admin = None

    def __init__(
        self,
        data: Dict[str, Any],
        verbose: bool = False,
    ):
        self.name = data["domain_name"][0].strip().lower()
        self.tld = data["tld"]

        self.registrar = data["registrar"][0].strip()
        self.reg_id = check_regid(data['reg_id'][0].strip())
        self.reg_abuse = check_email(data['reg_abuse'][0].strip())
        self.registrant_country = data["registrant_country"][0].strip()

        self.creation_date = str_to_date(data["creation_date"][0], self.tld.lower())
        self.expiration_date = str_to_date(data["expiration_date"][0], self.tld.lower())
        self.last_updated = str_to_date(data["updated_date"][0], self.tld.lower())

        self.status = data["status"][0].strip()
        self.statuses = list(set([s.strip() for s in data["status"]]))  # list(set(...))) to deduplicate

        self.dnssec = data["DNSSEC"]

        # ----------------------------
        # name_servers
        tmp = []
        for x in data["name_servers"]:
            if isinstance(x, str):
                tmp.append(x.strip().lower())
                continue
            # not a string but an array
            for y in x:
                tmp.append(y.strip().lower())

        if 0:
            if verbose:
                print(tmp, file=sys.stderr)

        self.name_servers = []
        for x in tmp:
            x = x.strip(" .")  # remove ant leading or trailing spaces and/or dots
            if x:
                if " " in x:
                    x, _ = x.split(" ", 1)
                    x = x.strip(" .")

                x = x.lower()
                if x not in self.name_servers:
                    self.name_servers.append(x)
        self.name_servers = sorted(self.name_servers)
        # ----------------------------

        if "owner" in data:
            self.owner = data["owner"][0].strip()

        if "abuse_contact" in data:
            self.abuse_contact = data["abuse_contact"][0].strip()

        if "reseller" in data:
            self.reseller = data["reseller"][0].strip()

        if "registrant" in data:
            self.registrant = data["registrant"][0].strip()

        if "admin" in data:
            self.admin = data["admin"][0].strip()


# http://docs.python.org/library/datetime.html#strftime-strptime-behavior
DATE_FORMATS = [
    "%d-%b-%Y",  # 02-jan-2000
    "%d-%m-%Y",  # 02-01-2000
    "%d.%m.%Y",  # 02.02.2000
    "%d/%m/%Y",  # 01/06/2011
    "%Y-%m-%d",  # 2000-01-02
    "%Y.%m.%d",  # 2000.01.02
    "%Y/%m/%d",  # 2005/05/30
    "before %b-%Y",  # before aug-1996
    "before %Y%m%d",  # before 19950101
    "%Y.%m.%d %H:%M:%S",  # 2002.09.19 13:00:00
    "%Y%m%d %H:%M:%S",  # 20110908 14:44:51
    "%Y-%m-%d %H:%M:%S",  # 2011-09-08 14:44:51
    "%Y-%m-%d %H:%M:%S%z",  # 2025-04-27 02:54:19+03:00
    "%Y-%m-%d %H:%M:%S %z",  # 2020-05-18 01:30:25 +0200
    "%Y-%m-%d %H:%M:%S CLST",  # 2011-09-08 14:44:51 CLST CL
    "%Y-%m-%d %H:%M:%S.%f",  # 2011-09-08 14:44:51 CLST CL
    "%d.%m.%Y  %H:%M:%S",  # 19.09.2002 13:00:00
    "%d-%b-%Y %H:%M:%S %Z",  # 24-Jul-2009 13:20:03 UTC
    "%Y/%m/%d %H:%M:%S (%z)",  # 2011/06/01 01:05:01 (+0900)
    "%Y/%m/%d %H:%M:%S",  # 2011/06/01 01:05:01
    "%a %b %d %H:%M:%S %Z %Y",  # Tue Jun 21 23:59:59 GMT 2011
    "%a %b %d %Y",  # Tue Dec 12 2000
    "%Y-%m-%dT%H:%M:%S",  # 2007-01-26T19:10:31
    "%Y-%m-%dT%H:%M:%SZ",  # 2007-01-26T19:10:31Z
    "%Y-%m-%dt%H:%M:%S.%fz",  # 2007-01-26t19:10:31.00z
    "%Y-%m-%dT%H:%M:%S%z",  # 2011-03-30T19:36:27+0200
    "%Y-%m-%dT%H:%M:%S.%f%z",  # 2011-09-08T14:44:51.622265+03:00
    "%Y-%m-%dt%H:%M:%S.%f",  # 2011-09-08t14:44:51.622265
    "%Y-%m-%dt%H:%M:%S",  # 2007-01-26T19:10:31
    "%Y-%m-%dt%H:%M:%SZ",  # 2007-01-26T19:10:31Z
    "%Y-%m-%dt%H:%M:%S.%fz",  # 2007-01-26t19:10:31.00z
    "%Y-%m-%dt%H:%M:%S%z",  # 2011-03-30T19:36:27+0200
    "%Y-%m-%dt%H:%M:%S.%f%z",  # 2011-09-08T14:44:51.622265+03:00
    "%Y%m%d",  # 20110908
    "%Y. %m. %d.",  # 2020. 01. 12.
    "before %b-%Y",  # before aug-1996
    "%a %d %b %Y",  # Tue 21 Jun 2011
    "%A %d %b %Y",  # Tuesday 21 Jun 2011
    "%a %d %B %Y",  # Tue 21 June 2011
    "%A %d %B %Y",  # Tuesday 21 June 2011
    "%Y-%m-%d %H:%M:%S (%Z+0:00)",  # 2007-12-24 10:24:32 (gmt+0:00)
    "%d-%m-%Y %H:%M:%S %Z+1",  # 19-04-2021 13:56:51 GMT+1
    "%B %d %Y",  # January 01 2000
    "%Y-%b-%d",  # 2021-Oct-18
    "%d/%m/%Y %H:%M:%S",  # 08/09/2011 14:44:51
    "%m/%d/%Y",  # 03/28/2013
    "%d %b %Y",  # 28 jan 2021
    "%d-%b-%Y %H:%M:%S",  # 30-nov-2009 17:00:58
    "%Y%m%d%H%M%S",  # 20071224102432 used in edu_ua
    "%Y-%m-%d %H:%M:%S (%Z%z)",  # .tw uses (UTC+8) but we need (UTC+0800) for %z match
]

CUSTOM_DATE_FORMATS = {
    "ml": "%m/%d/%Y",
}


def str_to_date(text: str, tld: Optional[str] = None) -> Optional[datetime.datetime]:
    text = text.strip().lower()

    noDate = [
        "not defined",
        "n/a",
        "none",
    ]
    if not text or text in noDate:
        return None

    # replace japan standard time to +0900 (%z format)
    text = text.replace("(jst)", "(+0900)")
    text = re.sub(r"(\+[0-9]{2}):([0-9]{2})", "\\1\\2", text)
    text = re.sub(r"(\+[0-9]{2})$", "\\1:00", text)

    # strip trailing space and comment
    text = re.sub(r"(\ #.*)", "", text)

    # tw uses UTC+8, but strptime needs UTC+0800), note we are now lower case
    r = r"\(utc([-+])(\d)\)"
    if re.search(r, text):
        text = re.sub(r, "(utc\\g<1>0\\g<2>00)", text)

    # hack for 1st 2nd 3rd 4th etc
    # better here https://stackoverflow.com/questions/1258199/python-datetime-strptime-wildcard
    text = re.sub(r"(\d+)(st|nd|rd|th) ", r"\1 ", text)

    if tld and tld in CUSTOM_DATE_FORMATS:
        return datetime.datetime.strptime(text, CUSTOM_DATE_FORMATS[tld]).astimezone().replace(tzinfo=None)

    for f in DATE_FORMATS:
        try:
            return datetime.datetime.strptime(text, f).astimezone().replace(tzinfo=None)
        except ValueError:
            pass

    raise UnknownDateFormat("Unknown date format: '%s'" % text)
