import os
import sys
import pandas
import logging


class Sources:

    def __init__(self, username):
        self.username = username

        self.data_sources = {
            'followers.csv': None,
            'following.csv': None,
            'timeline.json': None
        }

        self.data = {
            'followers': None,
            'following': None,
            'timeline': None
        }

        if not os.path.exists(self.username):
            logging.fatal("%s data folder doesn't exists" % self.username)
            sys.exit(1)

        os.chdir(self.username)

        for key in self.data_sources:
            if ".csv" in key:
                file_name = "%s_%s" % (self.username, key)
                file_path = os.path.abspath(file_name)

                if not os.path.exists(file_path):
                    logging.fatal("source file %s doesn't exists" % file_path)
                    sys.exit(1)

                self.data[key.replace(".csv", "")] = pandas.read_csv(file_path)


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
