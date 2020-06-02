import os
import pandas
import logging


class Sources:

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


class Basics:

    def __init__(self, data):
        self.data = data

    def following_followers_percent(self):
        count = 0

        print("\n==========================")
        print("= FOLLOWING FOLLOWERS")
        print('--------------------------')

        for idnex, follower in self.data['followers'].iterrows():
            if not (self.data['following'].loc[self.data['following']['username'] == follower['username']]).empty:
                count += 1

                print("%s aka. %s" % (follower['full_name'], follower['username']))

        print('--------------------------')
        print("People who follows user and user follow them: %i" % count)
        print("That's %i%% of the %s followers" % (
            (count / self.data['followers'].shape[0]) * 100, self.data['followers'].shape[0]))
        print("==========================")

# meto pruebas aqui pa no mover el main
if __name__ == "__main__":
    sources = Sources()

    sources.data_sources['followers'] = input('followers path: ')
    sources.data_sources['following'] = input('following path: ')

    sources.load_data()

    basics = Basics(sources.data)

    basics.following_followers_percent()
