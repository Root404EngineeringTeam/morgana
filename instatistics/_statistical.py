import os
import sys
import json
import shutil
import pandas
import logging
import operator

from jinja2 import Template

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
            'timeline': None,
            'top_followers': {},
            'username': username,
            'ff_percent': 0,
            'most_liked_post': None,
            'most_commented_post': None,
            'search': {
                'followers': [],
                'following': [],
                'posts': [],
                'likes': [],
                'comments': [],
                'query': None
            }
        }

        if not os.path.exists(self.username):
            logging.fatal("%s data folder doesn't exists" % self.username)
            sys.exit(1)

        os.chdir(self.username)

        for key in self.data_sources:
            file_name = "%s_%s" % (self.username, key)
            file_path = os.path.abspath(file_name)

            if not os.path.exists(file_path):
                logging.fatal("source file %s doesn't exists" % file_path)
                sys.exit(1)

            if ".csv" in key:
                self.data[key.replace(".csv", "")] = pandas.read_csv(file_path)

            else:
                with open(file_path) as json_file:
                    self.data[key.replace(".json", "")] = json.load(json_file)


class Basics:

    def __init__(self, data):
        self.data = data

        if type(self.data['top_followers']) is list:
            return

        for post in self.data['timeline']:
            for liker in post['likes']:
                if liker['username'] in self.data['top_followers'].keys():
                    self.data['top_followers'][liker['username']] += 1

                else:
                    self.data['top_followers'][liker['username']] = 1

        count = 0
        self.data['top_followers'] = sorted(self.data['top_followers'].items(), key=operator.itemgetter(1), reverse=True)

    def general(self):
        print("\n==========================")
        print("= GENERAL")
        print('--------------------------')
        print('Followers: %i' % len(self.data['followers']))
        print('Following: %i' % len(self.data['following']))
        print('Posts: %i' % len(self.data['timeline']))
        print('--------------------------')

    def following_followers_percent(self):
        count = 0

        print("\n==========================")
        print("= FOLLOWING FOLLOWERS")
        print('--------------------------')

        for index, follower in self.data['followers'].iterrows():
            if not (self.data['following'].loc[self.data['following']['username'] == follower['username']]).empty:
                count += 1

                #print("%s aka. %s" % (follower['full_name'], follower['username']))
        self.data['ff_percent'] = int((count / self.data['followers'].shape[0]) * 100)
        print("People who follows user and user follow them: %i" % count)
        print("That's %i%% of the %s followers" % (
            self.data['ff_percent'], self.data['followers'].shape[0]))
        print("==========================")

    def search_for_people(self, query):
        print("\n===========================")
        print("= Searching for: %s" % query)

        self.data['search']['query'] = query

        print('--------------------------')
        print('FOLLOWERS')
        print('--------------------------')

        for index, follower in self.data['followers'].iterrows():
            follower['full_name'] = str(follower['full_name'])
            if (query in follower['full_name'].lower()) or (query in follower['username'].lower()):
                print("%s aka. %s" % (follower['full_name'], follower['username']))
                self.data['search']['followers'].append((follower['full_name'], follower['username']))

        print('--------------------------')
        print('FOLLOWING')
        print('--------------------------')

        for index, follower in self.data['following'].iterrows():
            follower['full_name'] = str(follower['full_name'])
            if (query in follower['full_name'].lower()) or (query in follower['username'].lower()):
                print("%s aka. %s" % (follower['full_name'], follower['username']))
                self.data['search']['following'].append((follower['full_name'], follower['username']))

        print('--------------------------')

        print('--------------------------')
        print('TIMELINE POSTS CAPTIONS')
        print('--------------------------')

        for post in self.data['timeline']:
            for caption in post['captions']:
                if query in caption.lower():
                    print("https://www.instagram.com/p/%s" % post['shortcode'])
                    print(caption)
                    self.data['search']['posts'].append((post, caption))

        print('--------------------------')

        print('--------------------------')
        print('TIMELINE LIKES')
        print('--------------------------')

        for post in self.data['timeline']:

            for liker in post['likes']:
                liker['full_name'] = str(liker['full_name'])
                if (query in liker['username'].lower()) or (query in liker['full_name'].lower()):
                    posts_liked = 0

                    for username, likes_count in self.data['top_followers']:
                        if username == liker['username']:
                            posts_liked = likes_count

                    print("https://www.instagram.com/p/%s" % post['shortcode'])
                    print("%s aka. %s like this and other %s posts" %(liker['username'], liker['full_name'], posts_liked))

                    self.data['search']['likes'].append((post, liker))

        print('--------------------------')

        print('--------------------------')
        print('TIMELINE COMMENTS')
        print('--------------------------')

        for post in self.data['timeline']:

            for comment in post['comments']:
                if (query in comment['text'].lower()) or (query in comment['owner']['username']):
                    print("https://www.instagram.com/p/%s" % post['shortcode'])
                    print("%s commented '%s'" % (comment['owner']['username'], comment['text']))

                    self.data['search']['comments'].append((post, comment['owner']['username'], comment['text']))
        print('--------------------------')

    def top_followers(self):
        top_followers = {}

        print("\n==========================")
        print('TOP FOLLOWERS')
        print('--------------------------')

        count = 0

        for username, likes_count in self.data['top_followers']:
            print("%s liked %s posts" % (username, likes_count))

            count += 1

            if count == 10:
                break

        print('--------------------------')

    def most_popular_post(self):
        likes_count = 0
        most_liked = None

        print("\n==========================")
        print('MOST LIKED POST')
        print('--------------------------')

        for post in self.data['timeline']:
            if post['likes_count'] > likes_count:
                likes_count = post['likes_count']
                most_liked = post
                self.data['most_liked_post'] = post

        if most_liked:
            print("https://www.instagram.com/p/%s" % most_liked['shortcode'])

        else:
            print("No likes in any post :(")

        comments_count = 0
        most_commented = None

        print("\n==========================")
        print('MOST COMMENTED POST')
        print('--------------------------')

        for post in self.data['timeline']:
            if post['comments_count'] > comments_count:
                comments_count = post['comments_count']
                most_commented = post
                self.data['most_commented_post'] = post

        if most_commented:
            print("https://www.instagram.com/p/%s" % most_commented['shortcode'])

        else:
            print("No comments in any post :(")


class HTMLReporting(Basics):

    def __init__(self, data):
        super().__init__(data)

    def generate(self):
        path = os.path.dirname(os.path.realpath(__file__))

        print(" [ >] generating html report...")
        shutil.copyfile('%s/templates/bootstrap.scss' % path, 'theme.css')

        with open('%s/templates/report.jinja2' % path) as source:
            report = Template(source.read())

        output = report.render(data=self.data)

        with open('report.html', 'w') as output_file:
            output_file.write(output)

        print(" [ >] report saved to report.html")
