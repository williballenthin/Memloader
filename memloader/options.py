"""Headless options passed to the loaders via IDA's ``-O`` command line switch."""

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

PLUGIN_OPTIONS_NAME = "memloader"
DEFAULT_PASSWORD = "infected"
DEFAULT_SHELLCODE_BITNESS = 32


class OptionsError(ValueError):
    pass


@dataclass(frozen=True)
class LoadOptions:
    """Options that replace the interactive prompts when IDA runs in batch mode.

    Passed as ``-Omemloader:key=value;key=value`` on the IDA command line.
    Entries are separated by ``;`` so that values may contain ``:`` (for example URLs).
    """

    member: str | None = None
    password: str = DEFAULT_PASSWORD
    url: str | None = None
    bitness: int = DEFAULT_SHELLCODE_BITNESS

    @classmethod
    def from_plugin_options(cls, text: str) -> "LoadOptions":
        """Parse the string that IDA returns from ``get_plugin_options("memloader")``.

        Raises:
            OptionsError: an entry is not ``key=value``, the key is unknown, or bitness is not 32 or 64.
        """
        values: dict[str, str] = {}
        for entry in filter(None, text.split(";")):
            key, sep, value = entry.partition("=")
            if not sep:
                raise OptionsError(f"expected key=value, got {entry!r}")
            values[key] = value

        unknown = set(values) - {"member", "password", "url", "bitness"}
        if unknown:
            raise OptionsError(f"unknown option(s): {', '.join(sorted(unknown))}")

        bitness = DEFAULT_SHELLCODE_BITNESS
        if "bitness" in values:
            if values["bitness"] not in ("32", "64"):
                raise OptionsError(f"bitness must be 32 or 64, got {values['bitness']!r}")
            bitness = int(values["bitness"])

        return cls(
            member=values.get("member"),
            password=values.get("password", DEFAULT_PASSWORD),
            url=values.get("url"),
            bitness=bitness,
        )
