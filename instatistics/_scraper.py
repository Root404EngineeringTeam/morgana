import re
import json
import time
import pandas
import requests
import urllib.parse
import os


class Scraper:
    def __init__(self, user_name, cookies, output):
        self.graphql_url = "https://www.instagram.com/graphql/query"
        self.base_url = "https://www.instagram.com"

        self.followers_query_hash = ""
        self.following_query_hash = ""
        self.timelime_query_hash = ""
        self.likes_query_hash = ''
        self.cookie = cookies
        self.user_id = ""
        self.user_name = user_name
        self.output = user_name if not output else output

        if not os.path.exists(self.output) or not os.path.isdir(self.output):
            os.makedirs(self.output)

        with open("banner.txt", "r", encoding="utf8") as banner:
            print(banner.read())

    def set_query_hashes(self, followers, following):
        self.followers_query_hash = followers
        self.following_query_hash = following

    def set_cookie(self, cookie):
        self.cookie = cookie

    def compose_query(self, query_hash, variables):
        variables = str(variables).replace("True", "true").replace(
            "False", "false").replace("'", '"').replace(" ", "")
        variables = urllib.parse.quote(variables)
        query = "%s?query_hash=%s&variables=%s" % (
            self.graphql_url, query_hash, variables)

        time.sleep(1)
        return query

    def fetch_likes(self, shortcode, current, total):
        print("\r [ >] Fetching likes information for %s (%i%%)" %
              (shortcode, (current / total) * 100), end='')

        variables = {"shortcode": shortcode,
                     "include_reel": False, "first": 45}
        query = self.compose_query(self.likes_query_hash, variables)

        response = requests.get(query, headers={'Cookie': self.cookie})
        result = json.loads(response.text)

        try:
            edges = result['data']['shortcode_media']['edge_liked_by']

        except KeyError as e:
            print(result)
            return []

        has_next_page = edges['page_info']['has_next_page']
        next_page_cursor = edges['page_info']['end_cursor']

        likes = [edge['node'] for edge in edges['edges']]

        while has_next_page:
            variables = {"shortcode": shortcode, "include_reel": False,
                         "first": 45, "after": next_page_cursor}
            query = self.compose_query(self.likes_query_hash, variables)

            response = requests.get(query, headers={'Cookie': self.cookie})
            result = json.loads(response.text)

            try:
                edges = result['data']['shortcode_media']['edge_liked_by']

            except KeyError as e:
                print(result)
                return []

            has_next_page = edges['page_info']['has_next_page']
            next_page_cursor = edges['page_info']['end_cursor']

            likes += [edge['node'] for edge in edges['edges']]

        return likes

    def fetch_timeline(self):
        variables = {"id": self.user_id, "first": 45}
        query = self.compose_query(self.timelime_query_hash, variables)

        response = requests.get(query, headers={'Cookie': self.cookie})
        result = json.loads(response.text)

        timeline = result['data']['user']['edge_owner_to_timeline_media']

        timeline_size = timeline['count']
        has_next_page = timeline['page_info']['has_next_page']
        next_page_cursor = timeline['page_info']['end_cursor']

        edges = timeline['edges']

        while has_next_page:
            variables = {"id": self.user_id,
                         "first": 45, "after": next_page_cursor}
            query = self.compose_query(self.timelime_query_hash, variables)

            response = requests.get(query, headers={'Cookie': self.cookie})
            result = json.loads(response.text)

            timeline = result['data']['user']['edge_owner_to_timeline_media']
            has_next_page = timeline['page_info']['has_next_page']
            next_page_cursor = timeline['page_info']['end_cursor']

            edges += timeline['edges']

            print("\r [ >] Fetching %i posts in timeline (%i%%)" % (
                timeline_size, (len(edges) / timeline_size) * 100), end='')

        # TODO: (@edo0xff)
        #   comments tambien se pagina, hay que scrapear todos los comments
        posts = []
        i = 1
        for edge in edges:
            node = edge['node']
            posts.append({
                'type': node['__typename'],
                'id': node['id'],
                'dimensions': "%sx%s" % (node['dimensions']['width'], node['dimensions']['height']),
                'display_url': node['display_url'],
                'is_video': node['is_video'],
                'captions': [edge['node']['text'] for edge in node['edge_media_to_caption']['edges']],
                'shortcode': node['shortcode'],
                'comments_count': node['edge_media_to_comment']['count'],
                'comments': [edge['node'] for edge in node['edge_media_to_comment']['edges']],
                'timestamp': node['taken_at_timestamp'],
                'likes_count': node['edge_media_preview_like']['count'],
                'likes': self.fetch_likes(node['shortcode'], i, len(edges))
            })

            i += 1

            time.sleep(2)

        output = os.path.join(self.output, '%s_timeline.json' % self.user_name)
        with open(output, 'w') as outfile:
            json.dump(posts, outfile)

        print("\n [ >] Data saved to %s_timeline.json" % self.user_name)
        print(" [ >] Operation done (%i posts fetched)" % len(posts))

    def fetch_following(self):
        variables = {"id": self.user_id, "include_reel": True,
                     "fetch_mutual": True, "first": 45}
        query = self.compose_query(self.following_query_hash, variables)

        response = requests.get(query, headers={'Cookie': self.cookie})
        result = json.loads(response.text)

        user = result['data']['user']

        following_count = user['edge_follow']['count']
        has_next_page = user['edge_follow']['page_info']['has_next_page']
        next_page_cursor = user['edge_follow']['page_info']['end_cursor']

        followings = user['edge_follow']['edges']

        while has_next_page:
            time.sleep(1)

            variables = {"id": self.user_id, "include_reel": True,
                         "fetch_mutual": True, "first": 45, "after": next_page_cursor}
            query = self.compose_query(self.following_query_hash, variables)

            response = requests.get(query, headers={'Cookie': self.cookie})
            result = json.loads(response.text)

            user = result['data']['user']

            has_next_page = user['edge_follow']['page_info']['has_next_page']
            next_page_cursor = user['edge_follow']['page_info']['end_cursor']

            followings += user['edge_follow']['edges']

            print("\r [ >] Fetching data of %i users that %s follows (%i%%)" % (
                following_count, self.user_name, (len(followings) / following_count) * 100), end='')

        data_frame = pandas.DataFrame(
            [following['node'] for following in followings])

        output = os.path.join(self.output, '%s_following.csv' % self.user_name)
        data_frame.to_csv(output)

        print("\n [ >] Data saved to %s_following.csv" % self.user_name)
        print(" [ >] Operation done")

    def fetch_followers(self):
        variables = {"id": self.user_id, "include_reel": False,
                     "fetch_mutual": True, "first": 45}
        query = self.compose_query(self.followers_query_hash, variables)

        response = requests.get(query, headers={'Cookie': self.cookie})
        result = json.loads(response.text)

        user = result['data']['user']

        mutual_followed = user['edge_mutual_followed_by']['count']
        followers_count = user['edge_followed_by']['count']
        has_next_page = user['edge_followed_by']['page_info']['has_next_page']
        next_page_cursor = user['edge_followed_by']['page_info']['end_cursor']

        followers = user['edge_followed_by']['edges']

        while has_next_page:
            time.sleep(1)
            
            variables = {"id": self.user_id, "include_reel": False,
                         "fetch_mutual": True, "first": 45, "after": next_page_cursor}
            query = self.compose_query(self.followers_query_hash, variables)

            response = requests.get(query, headers={'Cookie': self.cookie})
            result = json.loads(response.text)

            user = result['data']['user']

            has_next_page = user['edge_followed_by']['page_info']['has_next_page']
            next_page_cursor = user['edge_followed_by']['page_info']['end_cursor']

            followers += user['edge_followed_by']['edges']
            print("\r [ >] Fetching %i users data that follows %s (%i%%)" % (
                followers_count, self.user_name, (len(followers) / followers_count) * 100), end='')

        data_frame = pandas.DataFrame(
            [follower['node'] for follower in followers])

        output = os.path.join(self.output, '%s_followers.csv' % self.user_name)
        data_frame.to_csv(output)

        print("\n [ >] Data saved to %s_followers.csv" % self.user_name)
        print(" [ >] Operation done")

    def scrap_user_info(self):
        print(" [ >] Fetching user profile information")
        response = requests.get(
            "%s/%s" % (self.base_url, self.user_name), headers={'Cookie': self.cookie})
        result = response.text

        user_id_regex = r'profilePage_([0-9]+)'
        user_id = re.search(user_id_regex, result)

        if user_id:
            self.user_id = user_id.group(1)
            print(" [ >] user_id: %s" % user_id.group(1))
        response = requests.get(
            "https://www.instagram.com/static/bundles/es6/Consumer.js/72f23d3ee788.js", headers={'cookie': self.cookie})
        result = response.text

        follow_query_hash_regex = r'const t="(\w+)",n="(\w+)",u=1,l='
        follow_query_hash = re.search(follow_query_hash_regex, result)

        if follow_query_hash:
            self.followers_query_hash = follow_query_hash.group(1)
            self.following_query_hash = follow_query_hash.group(2)

            print(" [ >] Followers query_hash: %s" % self.followers_query_hash)
            print(" [ >] Following query_hash: %s" % self.following_query_hash)

        response = requests.get(
            "https://www.instagram.com/static/bundles/es6/ProfilePageContainer.js/352b6034e548.js", headers={'Cookie': self.cookie})
        result = response.text

        timeline_query_hash_regex = r'void 0:l.pagination\},queryId:"(\w+)",queryParams\:t=>\(\{id\:t\}\)'
        timeline_query_hash = re.search(timeline_query_hash_regex, result)

        if timeline_query_hash:
            self.timelime_query_hash = timeline_query_hash.group(1)

            print(" [ >] Timeline query hash: %s" % self.timelime_query_hash)

        response = requests.get(
            "https://www.instagram.com/static/bundles/es6/ConsumerLibCommons.js/dd161cf434d6.js",  headers={'Cookie': self.cookie})
        result = response.text

        likes_query_hash_regex = r'const t="(\w+)",o=1,n=\(function\(\)\{const n=t;'
        likes_query_hash = re.search(likes_query_hash_regex, result)

        if likes_query_hash:
            self.likes_query_hash = likes_query_hash.group(1)

            print(" [ >] Likes query hash: %s" % self.likes_query_hash)
