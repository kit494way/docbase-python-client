from collections import namedtuple, UserList
import base64
import re
import requests
import os


class Config(object):

    """Configuration to acess DocBase API.

    :type api_token: str
    :param api_token: The api token to access API.
    :type team: str
    :param team: The team name to access API.

    """

    def __init__(self, api_token=None, team=None):
        self.api_token = api_token
        self.team = team

    @property
    def base_url(self):
        """Base url of the DocBase API.
        :returns: base url

        """
        return 'https://api.docbase.io'

    def headers(self, method):
        if method in ['post', 'patch']:
            return {
                'X-DocBaseToken': self.api_token,
                'Content-Type': 'application/json',
            }
        elif method in ['get', 'delete']:
            return {'X-DocBaseToken': self.api_token}
        else:
            return {}


config = Config()


def create(post=None, title='', body='', draft=False, notice=True,
           scope='everyone', groups=None, tags=None):
    """Create a new post.

    When the post argument is passed, that's properties are used,
    and other arguments are ignored if passed.

    :type post: :py:class:`~docbase.Post`
    :param post: The post to create.
    :type title: str
    :param title: The title of the post.
    :type body: str
    :param body: The document string of the post.
    :type draft: bool
    :param draft: Whether to save as draft.
    :type notice: bool
    :param notice: Whether to notify.
    :type scope: str
    :param scope: The scope of disclosure.
        The scope arguments is one of the following, 'private', 'group' or
        'everyone'. Default is 'everyone'.
    :type groups: list of dict or list of :py:class:`~docbase.Group`
    :param groups: Groups which are allowed to access this post.
    :type tags: list of str
    :param tags: Tags.

    :rtype: :py:class:`~docbase.Post`
    :returns: The post created.

    :raises: requests.exceptions.HTTPError

    """
    url = _index_url('posts')
    if post is None:
        post = Post(title=title, body=body, draft=draft, notice=notice,
                    scope=scope, groups=groups, tags=tags)

    payload = _post_to_payload(post)
    res = requests.post(url, headers=config.headers('post'), json=payload)
    res.raise_for_status()
    return _response_to_post(res.json())


def update(post):
    """Update a post.

    :type post: :py:class:`~docbase.Post`
    :param post: The new post.

    :rtype: :py:class:`~docbase.Post`
    :returns: The post updated.

    :raises: requests.exceptions.HTTPError

    """
    url = _resource_url('posts', post.id)
    payload = _post_to_payload(post)
    res = requests.patch(url, headers=config.headers('patch'), json=payload)
    res.raise_for_status()
    return _response_to_post(res.json())


def delete(post):
    """Delete a post.

    :type post: :py:class:`~docbase.Post` or int
    :param post: The post or post id to delete.

    :raises: requests.exceptions.HTTPError

    """
    post_id = post if isinstance(post, int) else post.id
    url = _resource_url('posts', post_id)
    res = requests.delete(url, headers=config.headers('delete'))
    res.raise_for_status()
    return True


def comment(post, message=None, notice=True):
    """Comment to the post.

    :type post: :py:class:`~docbase.Post` or int
    :param post: The post or post id to comment.
    :type message: str
    :param message: Comment message.
    :type notice: bool
    :param notice: Whether to notify.

    :raises: requests.exceptions.HTTPError

    """
    post_id = post.id if isinstance(post, Post) else post
    url = _resource_url('posts', post_id) + '/comments'
    payload = {
        'body': message,
        'notice': notice,
    }
    res = requests.post(url, headers=config.headers('post'), json=payload)
    res.raise_for_status()
    res_json = res.json()
    res_json['user'] = User(**res_json['user'])
    return Comment(**res_json)


def delete_comment(comment):
    """Delete a comment.

    :type comment: :py:class:`~docbase.Comment` or int
    :param comment: The comment or comment id to delete.

    :raises: requests.exceptions.HTTPError

    """
    comment_id = comment.id if isinstance(comment, Comment) else comment
    url = _resource_url('comments', comment_id)
    res = requests.delete(url, headers=config.headers('delete'))
    res.raise_for_status()
    return True


def posts(id=None, *, query=None, page=1, per_page=20, url=None):
    """Search posts.

    When id is passed and the post is found, returns :py:class:`~docbase.Post`.
    In this case, other arguments are ignored.
    When id is not passed, returns the list of :py:class:`~docbase.Post`.

    :type id: int
    :param id: ID of the post to find.
    :type query: str
    :param query: Search query.
    :type page: int
    :param page: Page number to get.
    :type per_page: int
    :param per_page: Number of posts to get per page.

    :rtype: :py:class:`~docbase.PostSearchResult`
    :returns: Found posts.

    """
    if id is not None:
        return _response_to_post(_get(_resource_url('posts', id)))

    if url is not None:
        return _posts_from_url(url)

    params = {}

    if page > 1:
        params['page'] = page

    if not per_page == 20:
        params['per_page'] = per_page

    if query is not None:
        params['q'] = query

    return PostSearchResult.from_response(_get(_index_url('posts'), params))


def groups():
    """Get groups belong to.

    :rtype: list of :py:class:`~docbase.Group`
    :returns: Groups.

    """
    return [Group(id=g['id'], name=g['name'])
            for g in _get(_index_url('groups'))]


def tags():
    """Get tags.

    :rtype: list of str
    :returns: Tags.

    """
    return [tag['name'] for tag in _get(_index_url('tags'))]


def teams():
    """Get teams.

    :rtype: list of dict
    :returns: Teams belongs to.

    """
    return _get(_index_url('teams'))


def file_upload(file_path):
    """Upload a file and get the url.

    :type file_path: str
    :param file_path: The file path to upload.
    :rtype: :py:class:`~docbase.Attachment`
    :returns: The informaion of the uploaded file.

    """
    with open(file_path, mode='rb') as fin:
        payload = {
            'name': os.path.basename(file_path),
            'content': base64.b64encode(fin.read()).decode('ascii'),
        }
    res = requests.post(_index_url('attachments'),
                        headers=config.headers('post'), json=payload)
    res.raise_for_status()
    return Attachment(**res.json())


class Post(object):

    """A post to DocBase.

    :type title: str
    :param title: Title.
    :type body: str
    :param body: The contents of the post.
    :type notice: bool
    :param notice: Whether to notify when create or update.
    :type comments: list of :py:class:`~docbase.Comment`
    :param comments: The comments to the post.
    :type user: :py:class:`~docbase.User`
    :param user: The author of the post.

    """

    def __init__(self, title='', body='', draft=False, notice=True,
                 scope='everyone', groups=None, tags=None, id=None):
        self.title = title
        self.body = body
        self.draft = draft
        self.notice = notice
        self._scope = scope

        if tags is None:
            self._tags = set()
        else:
            self.tags = tags

        self._groups = set()
        if groups is not None:
            self.groups.append(groups)

        self.id = id
        self.comments = []
        self.user = None
        self.url = None

    @property
    def groups(self):
        """Groups which are allowed to access this post.

        :rtype: set of :py:class:`~docbase.Group`
        :returns: Groups which can read this post.

        """
        if not self.scope == 'group':
            raise GroupScopeError

        return self._groups

    @groups.setter
    def groups(self, groups):
        if not self.scope == 'group':
            raise GroupScopeError

        def _to_group(x):
            if isinstance(x, Group):
                return x

            return Group(id=x['id'], name=x['name'])

        self._groups = [_to_group(g) for g in groups]

    @property
    def scope(self):
        """Scope of disclosure.

        Scope is one of the following, 'private', 'group' or 'everyone'.
        Default 'everyone'.

        :returns: Scope of disclosure.
        :rtype: string

        """
        return self._scope

    @scope.setter
    def scope(self, scope):
        if scope not in ['everyone', 'group', 'private']:
            raise InvalidScopeError(str(scope))

        if not scope == 'group':
            self._groups.clear()

        self._scope = scope

    @property
    def tags(self):
        """Tags of this post.

        :rtype: set of str
        :returns: Tags.

        """
        return self._tags

    @tags.setter
    def tags(self, tags):
        self._tags = set([str(tag) for tag in tags])


class PostSearchResult(UserList):

    """Search result of posts."""

    def __init__(self, lst=[], previous_page=None, next_page=None, total=0):
        super().__init__(lst)
        self._previous_page = previous_page
        self._next_page = next_page
        self._total = total

    @staticmethod
    def from_response(res):
        return PostSearchResult([_response_to_post(p) for p in res['posts']],
                                **res['meta'])

    @property
    def next_page(self):
        return self._next_page

    @property
    def previous_page(self):
        return self._previous_page

    @property
    def total(self):
        return self._total

    def next(self):
        """Get next page.

        """
        if self._next_page is None:
            return []

        return PostSearchResult.from_response(_get(self._next_page))

    def previous(self):
        """Get previous page.

        """
        if self._previous_page is None:
            return []

        return PostSearchResult.from_response(_get(self._previous_page))


class Group(namedtuple('Group', ['id', 'name'])):

    """Group of users.

    :type id: str
    :param id: The id of group.
    :type name: str
    :param name: The name of group.

    """

    __slots__ = ()

    def __eq__(self, other):
        if not isinstance(other, Group):
            return False

        return self.id == other.id

    def __hash__(self):
        return hash(self.id)


Comment = namedtuple('Comment', ['id', 'body', 'created_at', 'user'])
User = namedtuple('User', ['id', 'name', 'profile_image_url'])
Attachment = namedtuple('Attachment',
                        ['id', 'name', 'size', 'url', 'markdown',
                         'created_at'])


class Error(Exception):
    pass


class InvalidScopeError(Error):

    def __init__(self, scope):
        super().__init__(
            "Scope must be one of the following, 'private', "
            "'group' or 'everyone', but '{0}' was passed.".format(scope))


class GroupScopeError(Error):

    def __init__(self):
        super().__init__("To use Post.groups, Post.scope must be 'group'")


def _get(url, params=None):
    """Send a GET request.

    :type url: str
    :param url: The request url.
    :type params: dict
    :param params: The equest parameters.

    :raises: requests.exceptions.HTTPError

    """
    res = requests.get(url, headers=config.headers('get'), params=params)
    res.raise_for_status()
    return res.json()


def _index_url(name):
    if name == 'teams':
        return '{0}/teams'.format(config.base_url)
    else:
        return '{0}/teams/{1}/{2}'.format(config.base_url, config.team,
                                          name)


def _posts_from_url(url):
    if not url.startswith(_index_url('posts')):
        raise Error('Invalid URL')

    if re.match(_resource_url('posts', '[0-9]+'), url):
        return _response_to_post(_get(url))

    return PostSearchResult.from_response(_get(url))


def _resource_url(name, id):
    return '{0}/{1}'.format(_index_url(name), id)


def _response_to_post(response):
    """Create an instance of Post from response.

    :type response: dict
    :param response: The response body.

    :returns: The instance of Post created from response.

    """
    post = Post(title=response['title'], body=response['body'],
                draft=response['draft'], scope=response['scope'],
                tags=[tag['name'] for tag in response['tags']])

    post.id = response['id']

    if post.scope == 'group':
        post.groups = response['groups']

    def to_comment(x):
        y = x.copy()
        y['user'] = User(**y['user'])
        return Comment(**y)

    post.comments = [to_comment(c) for c in response['comments']]

    post.user = User(**response['user'])
    post.url = response['url']

    return post


def _post_to_payload(post):
    """Convert the instance of Post to data to create or update api call.

    :type post: Post
    :param post: The post to request.

    :rtype: dict
    :returns: The post data to send to DocBase API.

    """
    payload = {
        'title': post.title,
        'body': post.body,
        'draft': post.draft,
        'notice': post.notice,
        'tags': [tag for tag in post.tags],
        'scope': post.scope,
    }

    if post.scope == 'group':
        payload['groups'] = [g.id for g in post.groups]

    return payload
