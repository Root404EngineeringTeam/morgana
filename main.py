import argparse
import sys
import logging
from os import path
from instatistics import *


def read_cookies_file(src):
    cookies = None

    with open(src, 'r', encoding='utf-8') as cookies_file:
        cookies = cookies_file.read()

    return cookies.replace("\n", "")


def scrap(args):
    cookies = None
    if args.cookies:
        cookies = args.cookies
    elif args.cookies_from:
        if not path.exists(args.cookies_from):
            logging.fatal(
                'can\'t find the file \'%s\' because it doesn\'t exist' % args.cookies_from)
            sys.exit(1)
        else:
            cookies = read_cookies_file(args.cookies_from)
    else:
        if not path.exists('cookies.txt'):
            logging.fatal(
                'cookies were not specified by any means. Use --help to know how to enter your access cookies')
            sys.exit(1)
        else:
            cookies = read_cookies_file('cookies.txt')

    scrapper = Scraper(
        user_name=args.user, cookies=cookies, output=args.output)

    scrapper.scrap_user_info()

    scrapper.fetch_followers()
    scrapper.fetch_following()
    scrapper.fetch_timeline()

    print(" [ >] hf!")


def statistics(args):
    sources = Sources(args.user)
    basics = Basics(sources.data)

    basics.general()
    basics.following_followers_percent()
    basics.most_popular_post()
    basics.top_followers()

    if args.search:
        basics.search_for_people(args.search)

    if args.html:
        html_reporting = HTMLReporting(sources.data)
        html_reporting.generate()


if __name__ == '__main__':
    with open("banner", "r", encoding="utf8") as banner:
        print(banner.read())

    parser = argparse.ArgumentParser(
        description='get some instagram statistics')

    parser.add_argument('-c', '--cookies', type=str, dest='cookies')
    parser.add_argument('--cookies-from', type=str, dest='cookies_from')
    parser.add_argument('-u', '--user', type=str, dest='user', required=True)
    parser.add_argument('--scrap', action='store_true',
                        dest='scrap', required=False)
    parser.add_argument('--statistics', action='store_true',
                        dest='statistics', required=False)
    parser.add_argument('--search', type=str,
                        dest='search', required=False)
    parser.add_argument('--html', action='store_true',
                        dest='html', required=False)
    parser.add_argument('--output', type=str)
    # TODO (@Algoru):
    # --stat (genera estadísticas deseadas)
    #    [all, followers, following, likes, publicaciones en un periodo de tiempo, comentarios, etc]

    args = parser.parse_args()

    if args.scrap:
        scrap(args)

    elif args.statistics:
        statistics(args)

    else:
        print(" [ >] use --help")
