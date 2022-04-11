"""mkbfgroup.py -- CLI tool to create automatic groups in custom sites"""
import argparse
import getpass
import requests

import urllib3

print("mkbfgroup version 0.1")

# We assume unsigned API certificate
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# End of warning supression

parser = argparse.ArgumentParser()


parser.add_argument(
    "-s",
    "--bfserver",
    type=str,
    help="BigFix REST Server name/IP address",
    required=True,
)
parser.add_argument(
    "-p", "--bfport", type=int, help="BigFix Port number (default 52311)", default=52311
)
parser.add_argument(
    "-U", "--bfuser", type=str, help="BigFix Console/REST User name", required=True
)
parser.add_argument(
    "-P",
    "--bfpass",
    type=str,
    help="BigFix Console/REST Password (will prompt if omitted)",
)
parser.add_argument(
    "-r",
    "--relevance",
    type=str,
    help="Relevance that defines the group",
    required=True,
)
parser.add_argument(
    "-c", "--customsite", type=str, help="Custom site name", required=True
)
parser.add_argument("-t", "--title", type=str, required=True)

conf = parser.parse_args()

if conf.bfpass is None:
    ## TODO: Modify to prompt until 2 consecutive matching passwords
    passwd = getpass.getpass(prompt="Enter REST API password:")
else:
    passwd = conf.bfpass

postXml = f"""\
<BES xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="BES.xsd">
<ComputerGroup>
<Title>{conf.title}</Title>
<Domain>BESC</Domain>
<JoinByIntersection>true</JoinByIntersection>
<SearchComponentRelevance Comparison="IsTrue">
<Relevance>{conf.relevance}</Relevance>
</SearchComponentRelevance>
</ComputerGroup>
</BES>
""".strip()

session = requests.Session()
session.auth = (conf.bfuser, passwd)

qheader = {"Content-Type": "application/x-www-form-urlencoded"}

sitename = requests.utils.quote(conf.customsite)

req = requests.Request(
    "POST",
    f"https://{conf.bfserver}:{conf.bfport}/api/computergroups/custom/{sitename}",
    headers=qheader,
    data=postXml,
)

prepped = session.prepare_request(req)

result = session.send(prepped, verify=False)

if result.ok:
    print("\n\n**** Success ****")
    print(result.text)
else:
    print(f"\n\nREST API call failed with status {result.status_code}")
    print(f"Reason: {result.text}")
