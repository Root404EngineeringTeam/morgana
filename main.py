import argparse
import sys
import logging
from os import path
from instatistics import core


def read_cookies_file(src):
    cookies = None
    with open(src, 'r', encoding='utf-8') as cookies_file:
        cookies = cookies_file.read()
    return cookies


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='get some instagram statistics')

    parser.add_argument('-c', '--cookies', type=str, dest='cookies')
    parser.add_argument('--cookies-from', type=str, dest='cookies_from')
    parser.add_argument('-u', '--user', type=str, dest='user', required=True)
    parser.add_argument('--scrap', action='store_true',
                        dest='scrap', required=False)
    parser.add_argument('--output', type=str)
    # TODO (@Algoru):
    # --output (especifíca donde se van a escribir los resultados)
    # --scrap (scrap información)
    # --stat (genera estadísticas deseadas)
    #    [all, followers, following, likes, publicaciones en un periodo de tiempo, comentarios, etc]

    args = parser.parse_args()

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

    scrapper = core.Instadistics(
        user_name=args.user, cookies=cookies, output=args.output)

    if args.scrap:
        scrapper.scrap_user_info()

        scrapper.fetch_followers()
        scrapper.fetch_following()
        scrapper.fetch_timeline()

        print(" [ >] hf!")
