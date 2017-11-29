===========
Get Started
===========

Install
-------

.. code:: sh

  pip install docbase


Usage
-----

First. import this libaray.

.. code:: python

  import docbase


Config
~~~~~~

You must set the team and the api token to access DocBase API.
See `here <https://help.docbase.io/posts/45703#アクセストークン>`_, to get the access token.

.. code:: python

  docbase.config.team = 'your_team_domain'
  docbase.config.api_token = 'your_api_token'


Get posts
~~~~~~~~~

Get the post by id.

.. code:: python

  post_id = 12345
  post = docbase.posts(post_id)

Get posts.

.. code:: python

  posts = docbase.posts()

Get posts with query.

.. code:: python

  posts = docbase.posts(query='keyword search')
  posts = docbase.posts(query='tag:test')

Paginate.

.. code:: python

  posts = docbase.posts()
  next_posts = posts.next()
  prev_posts = next_posts.prev()


Create posts
~~~~~~~~~~~~

Use ``docbase.create()`` to create a new post.
``docbase.create()`` receive attributes of the post or ``docbase.Post`` object.

.. code:: python

  post = docbase.Post(title='test', body='this is a test')
  new_post = docbase.create(post)

or

.. code:: python

  new_post = docbase.create(title='test', body='this is a test')


Update posts
~~~~~~~~~~~~

.. code:: python

  post = docbase.posts(12345)
  post.body = 'modified body'
  docbase.update(post)


Delete posts
~~~~~~~~~~~~

``docbase.delete()`` receive the id or ``docbase.Post`` object.

.. code:: python

  docbase.delete(12345)

or

.. code:: python

  post = docbase.posts(12345)
  docbase.delete(post)
