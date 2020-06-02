import argparse
from instatistics import core

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='get some instagram statistics')

    parser.add_argument('--cookies', type=str, required=True)
    parser.add_argument('--user', type=str, required=True)
    parser.add_argument('--scrap', action='store_true', required=False)
    # TODO (@Algoru):
    # --output (especifíca donde se van a escribir los resultados)
    # --scrap (scrap información)
    # --stat (genera estadísticas deseadas)
    #    [all, followers, following, likes, publicaciones en un periodo de tiempo, comentarios, etc]

    args = parser.parse_args()

    scrapper = core.Instadistics(user_name=args.user, cookies=args.cookies)

    if args.scrap:
        scrapper.scrap_user_info()

        scrapper.fetch_followers()
        scrapper.fetch_following()
        scrapper.fetch_timeline()

        print(" [ >] hf!")
