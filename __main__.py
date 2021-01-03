import argparse
from site_checker import SiteChecker

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check sites text.")
    parser.add_argument("config", type=str, nargs=1, help="Path to config json file.")
    parser.add_argument(
        "-a",
        dest="apiKey",
        type=str,
        nargs=1,
        required=True,
        help="Pushbullet API key.",
    )
    parser.add_argument(
        "-m", dest="maxFailCount", type=int, nargs=1, help="Max fail count."
    )
    parser.add_argument(
        "-u", dest="updateCycle", type=int, nargs=1, help="Update cycle in second"
    )
    parser.add_argument(
        "-v", dest="isVerbose", action="store_true", help="Verbose mode."
    )
    parser.add_argument(
        "-q",
        dest="isQuiet",
        action="store_true",
        help="Quiet mode. Does not call pushbullet",
    )

    args = parser.parse_args()

    k = SiteChecker(
        args.config[0],
        args.apiKey[0],
        args.isQuiet,
        args.isVerbose,
        args.maxFailCount,
        args.updateCycle,
    )
    k.check()
