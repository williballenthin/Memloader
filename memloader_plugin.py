"""Memloader plugin entry point.

Runs at IDA startup and keeps the Memloader loader links in ``$IDAUSR/loaders/``
up to date, so that the ZIP and URL loaders appear in the "Load a new file" dialog.
"""

import logging
from pathlib import Path

import ida_diskio
import ida_idaapi

from memloader.install import install_loader_links

PLUGIN_ROOT = Path(__file__).resolve().parent

logger = logging.getLogger("memloader")


class MemloaderPlugmod(ida_idaapi.plugmod_t):
    def __init__(self):
        super().__init__()
        loaders_dir = Path(ida_diskio.get_user_idadir()) / "loaders"
        try:
            paths = install_loader_links(loaders_dir, PLUGIN_ROOT)
        except OSError as e:
            logger.warning("Memloader: cannot install loader links into %s: %s", loaders_dir, e)
        else:
            logger.debug("Memloader: loader links current in %s: %s", loaders_dir, [p.name for p in paths])

    def run(self, arg):
        return False


class MemloaderPlugin(ida_idaapi.plugin_t):
    flags = ida_idaapi.PLUGIN_FIX | ida_idaapi.PLUGIN_HIDE | ida_idaapi.PLUGIN_MULTI
    wanted_name = "Memloader"
    wanted_hotkey = ""
    comment = "Load files from ZIP archives or URLs without writing them to disk"
    help = ""

    def init(self):
        return MemloaderPlugmod()


def PLUGIN_ENTRY():
    return MemloaderPlugin()
