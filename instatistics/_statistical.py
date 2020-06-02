import os
import pandas
import logging


class DataSources:

    def __init__(self):
        self.data_sources = {
            'followers': None,
            'following': None,
            'timeline': None
        }

        self.data = {
            'followers': None,
            'following': None,
            'timeline': None
        }

    def load_data(self):
        os.chdir('..')

        for key in self.data_sources:
            if self.data_sources[key]:
                file_path = os.path.abspath(self.data_sources[key])

                if not os.path.exists(file_path):
                    logging.fatal("source file %s doesn't exists" % file_path)
                    sys.exit(1)

                self.data[key] = pandas.read_csv(file_path)


# meto pruebas aqui pa no mover el main
if __name__ == "__main__":
    dispersion = DataSources()

    dispersion.data_sources['followers'] = input('followers path: ')
    dispersion.data_sources['following'] = input('following path: ')

    dispersion.load_data()
