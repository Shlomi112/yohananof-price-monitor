"""Minimal client for the Cerberus price-transparency FTPS portal.

Deliberately implemented with stdlib ftplib only (no third-party scraper
package): the community `il-supermarket-scraper` package depends on `fcntl`
(Unix-only) and pulls in Playwright/MongoDB, none of which are needed for
this chain - Yohananof's files are served over plain FTPS.
"""

import fnmatch
import gzip
import io
from ftplib import FTP_TLS

from . import config


def _connect(ftp_username):
    ftp = FTP_TLS(config.FTP_HOST, ftp_username, "", timeout=30)
    ftp.trust_server_pasv_ipv4_address = True
    ftp.cwd("/")
    return ftp


def list_files(chain, pattern=None):
    """List file names on the portal, optionally filtered by a glob pattern."""
    ftp_username = config.CHAINS[chain]["ftp_username"]
    ftp = _connect(ftp_username)
    try:
        names = [name for name, facts in ftp.mlsd() if facts.get("type") == "file"]
    finally:
        ftp.quit()
    if pattern:
        names = [n for n in names if fnmatch.fnmatch(n.lower(), pattern.lower())]
    return names


def download(chain, file_name):
    """Download a file by name, gunzip-ing it if it's a .gz, return raw bytes."""
    ftp_username = config.CHAINS[chain]["ftp_username"]
    ftp = _connect(ftp_username)
    try:
        buf = io.BytesIO()
        ftp.retrbinary("RETR " + file_name, buf.write)
    finally:
        ftp.quit()
    data = buf.getvalue()
    if file_name.endswith(".gz"):
        data = gzip.decompress(data)
    return data


def latest_full_file(chain, file_type, store_id):
    """Find the most recent *Full* dump (PriceFull/PromoFull) for a store.

    Full dumps are complete snapshots (not deltas), which is what we want
    to diff against the previous run. Falls back to the newest match if no
    "Full" variant is found.
    """
    pattern = f"*{file_type}*-{store_id}-*"
    names = list_files(chain, pattern)
    full_names = [n for n in names if n.startswith(f"{file_type}Full")]
    candidates = full_names or names
    if not candidates:
        return None
    # File names end with -YYYYMMDD-HHMMSS[.gz|.xml], so lexical sort = chronological.
    return sorted(candidates)[-1]
