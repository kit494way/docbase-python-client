# from unittest import TestCase
import unittest
from unittest.mock import MagicMock, patch

import copy
import json
import os

import docbase

THIS_DIR = os.path.dirname(os.path.abspath(__file__))


class TestDocBase(unittest.TestCase):

    def setUp(self):
        with open(os.path.join(THIS_DIR, 'post.json')) as fin:
            self.posts_id_json = json.load(fin)

        with open(os.path.join(THIS_DIR, 'posts.json')) as fin:
            self.posts_json = json.load(fin)

        with open(os.path.join(THIS_DIR, 'comment.json')) as fin:
            self.comment_json = json.load(fin)

        docbase.config.team = 'kray'
        docbase.config.api_token = 'api_token'

    @patch('requests.get')
    def test_posts_id(self, requests_get):
        get_return = MagicMock()
        get_return.json.return_value = self.posts_id_json
        requests_get.return_value = get_return

        post = docbase.posts(1)
        self.assertEqual(post.id, self.posts_id_json['id'])
        self.assertEqual(post.title, self.posts_id_json['title'])
        self.assertEqual(post.body, self.posts_id_json['body'])
        self.assertEqual(post.url, self.posts_id_json['url'])
        self.assertEqual(post.scope, self.posts_id_json['scope'])
        self.assertEqual(post.draft, self.posts_id_json['draft'])

        self.assertEqual(post.user.name, self.posts_id_json['user']['name'])
        self.assertEqual(
            post.user.profile_image_url,
            self.posts_id_json['user']['profile_image_url'])

        self.assertIn(self.posts_id_json['tags'][0]['name'], post.tags)

    @patch('requests.get')
    def test_posts(self, requests_get):
        post_return = MagicMock()
        post_return.json.return_value = self.posts_json
        requests_get.return_value = post_return

        posts = docbase.posts()

        self.assertEqual(posts.total, self.posts_json['meta']['total'])
        self.assertEqual(
            posts.previous_page,
            self.posts_json['meta']['previous_page'])
        self.assertEqual(
            posts.next_page,
            self.posts_json['meta']['next_page'])

        posts.next()

        requests_get.assert_called_with(
            self.posts_json['meta']['next_page'],
            headers={'X-DocBaseToken': docbase.config.api_token},
            params=None)

    @patch('requests.post')
    def test_comment(self, requests_post):
        post_return = MagicMock()
        post_return.json.return_value = copy.copy(self.comment_json)
        requests_post.return_value = post_return

        post_id = 1
        message = 'hello world'
        comment = docbase.comment(post_id, message=message)

        requests_post.assert_called_with(
            'https://api.docbase.io/teams/{}/posts/{}/comments'.format(
                docbase.config.team,
                post_id),
            headers={'X-DocBaseToken': docbase.config.api_token,
                     'Content-Type': 'application/json'},
            json={'body': message, 'notice': True})
        self.assertEqual(comment.body, self.comment_json['body'])
        self.assertEqual(comment.user.name, self.comment_json['user']['name'])


if __name__ == "__main__":
    unittest.main()
