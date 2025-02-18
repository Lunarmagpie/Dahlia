from __future__ import annotations

from argparse import ArgumentParser

from .dahlia import Dahlia, Depth, clean


def main() -> None:
    UNSET = object()
    parser = ArgumentParser()
    parser.add_argument(
        "-d",
        "--depth",
        help="set the color depth",
        type=int,
        choices={3, 8, 24},
        default=24,
    )
    parser.add_argument("-t", "--test", help="test the colors", action="store_true")
    parser.add_argument(
        "-v", "--version", help="print the version", action="store_true"
    )
    parser.add_argument("-c", "--clean", help="clean codes", action="store_true")
    parser.add_argument("string", nargs="?", help="the string to color", default=UNSET)
    args = parser.parse_args()

    d = Dahlia(depth=Depth(args.depth))
    string = args.string

    if string is UNSET:
        if args.test:
            d.test()
        elif args.version:
            print("Dahlia 2.1.1")
        exit()
    if args.clean:
        print(clean(string))
    else:
        d.print(string)


if __name__ == "__main__":
    main()
