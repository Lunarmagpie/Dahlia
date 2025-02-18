from __future__ import annotations

from enum import Enum
from os import system
from sys import platform
from typing import Any

from .constants import (
    BG_FORMAT_TEMPLATES,
    COLORS_3BIT,
    COLORS_4BIT,
    COLORS_8BIT,
    COLORS_24BIT,
    FORMAT_TEMPLATES,
    FORMATTERS,
    NO_COLOR,
)
from .utils import _find_codes, _with_marker, clean

if platform in ("win32", "cygwin"):
    system("")  # type: ignore


class Depth(Enum):
    """Specifies usable color depth levels."""

    TTY = 3
    """3-bit color (tty)"""
    LOW = 4
    """4-bit color"""
    MEDIUM = 8
    """8-bit color"""
    HIGH = 24
    """24-bit color (true color)"""


class Dahlia:
    __slots__ = ("__depth", "__no_reset", "__patterns", "__marker", "__reset")

    def __init__(
        self, *, depth: Depth = Depth.HIGH, no_reset: bool = False, marker: str = "&"
    ) -> None:
        self.__depth = depth.value
        self.__no_reset = no_reset
        self.__patterns = _with_marker(marker)
        self.__marker = marker
        self.__reset = marker + "r"

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Dahlia):
            return (self.depth, self.no_reset, self.marker) == (
                other.depth,
                other.no_reset,
                self.marker,
            )
        return NotImplemented

    def __hash__(self) -> int:
        return hash((self.depth, self.no_reset, self.marker))

    def __repr__(self) -> str:
        return f"Dahlia(depth={self.depth}, no_reset={self.no_reset}, marker={self.marker!r})"

    @property
    def depth(self) -> int:
        """Specifies what ANSI color set to use (in bits)."""
        return self.__depth

    @property
    def marker(self) -> str:
        """Specifies the prefix used by format codes ("&" by default)."""
        return self.__marker

    @property
    def no_reset(self) -> bool:
        """When True, doesn't add an "&r" at the end when converting strings."""
        return self.__no_reset

    def convert(self, string: str) -> str:
        """
        Formats a string using the format codes.

        Example
        -------

        .. code-block :: python

            dahlia = Dahlia()
            text = dahlia.convert("&aHello\\n&cWorld")
            print(text)


        Output would be:

        .. raw:: html

            <pre>
                <span class="&a">Hello</span>
                <span class="&c">World</span>
            </pre>

        For more see :ref:`dahlia usage <usage>`

        Parameters
        ----------
        string : str
            String containing text and format codes.

        Returns
        -------
        str
            A formatted string with the appropriate formatting applied.
        """
        if NO_COLOR:
            return clean(string)
        if not (string.endswith(self.__reset) or self.no_reset):
            string += self.__reset
        for code, bg, color in _find_codes(string, self.__patterns):
            string = string.replace(code, self.__get_ansi(color, bg))
        return string

    def input(self, prompt: str) -> str:
        """
        Wrapper over :func:`input`, calling the :func:`dahlia` function on the prompt.

        Example
        -------
        .. code-block :: python

            dahlia = Dahlia()
            text = dahlia.input("&bEnter text: ")


        Output would be:

        .. raw:: html

            <pre>
                <span class="&b">Enter text: </span>
            </pre>

        Parameters
        ----------
        prompt : str
            String containing text and format codes to prompt the user with.

        Returns
        -------
        str
            User input entered after the formatted prompt.
        """
        return input(self.convert(prompt))

    def print(self, *args: Any, **kwargs: Any) -> None:
        r"""
        Wrapper over :func:`print`, calling the :func:`dahlia` method for each argument.

        Example
        -------
        .. code-block :: python

            dahlia = Dahlia()
            text = dahlia.print("&bHello", "&5World", sep="\n")


        Output would be:

        .. raw:: html

            <pre>
                <span class="&b">Hello</span>
                <span class="&5">World</span>
            </pre>

        Parameters
        ----------
        \*args : str
            Objects to print.

        \*\*kwargs
            Keyword arguments to pass to :func:`print`.
        """
        print(*map(self.convert, map(str, args)), **kwargs)

    def reset(self) -> None:
        """Resets all modifiers."""
        self.print(self.__reset, end="")

    def test(self) -> None:
        """Prints all default format codes and their formatting."""
        self.print(
            "".join(f"{self.marker}{i}{i}" for i in "0123456789abcdefg")
            + "&r&ll&r&mm&r&nn&r&oo".replace("&", self.marker)
        )

    def __get_ansi(self, code: str, bg: bool) -> str:
        formats = BG_FORMAT_TEMPLATES if bg else FORMAT_TEMPLATES
        if len(code) == 6:
            r, g, b = (int(code[i : i + 2], 16) for i in range(0, 6, 2))
            return formats[24].format(r, g, b)
        if code in FORMATTERS:
            return formats[3].format(FORMATTERS[code])

        template = formats[self.__depth]
        if self.depth == 24:
            r, g, b = COLORS_24BIT[code]
            return template.format(r, g, b)

        color_map = [COLORS_3BIT, COLORS_4BIT, COLORS_8BIT][self.depth]
        value = color_map[code]
        if self.depth == 8 and bg:
            value += 10
        return template.format(value)
