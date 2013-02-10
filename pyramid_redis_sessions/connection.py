"""
Defines common methods for obtaining a redis connection.

To use a custom connect function, create a callable with parameters:

  ``request``
  The current pyramid request object

  ``**redis_options``
  Additional keyword arguments accepted by redis-py's StrictRedis class


The callable must return an instance of StrictRedis or must implement the same
interface.

To use your custom connection function, you can pass it in directly as the
``custom_connect`` argument to ``pyramid_redis_sessions.RedisSessionFactory``
or ``pyramid_redis_sessions.session_factory_from_settings``, or in your config
file you can specify a dotted python path as a string.


Example configuration in python::

    from my_cool_app import my_redis_connection_getter
    from pyramid_redis_sessions import session_factory_from_settings

    def main(global_config, **settings):
        config = Configurator(**settings)
        settings['custom_connect'] = my_redis_connection_getter
        session_factory = session_factory_from_settings(settings)
        config.set_session_factory(session_factory)


Example configuration from an ini file::

    redis.sessions.secret = mysecret
    redis.sessions.custom_connect = my_cool_app.my_redis_connection_getter


This option is available so that developers can define their own redis
instances as needed, but most users should not need to customize how they
connect.
"""

from redis import StrictRedis

def get_default_connection(request, url=None, **redis_options):
    """
    Default redis connection handler. Once a connection is established it is
    saved in `request.registry`.

    Parameters:

    ``request``
    The current pyramid request object

    ``url``
    An optional connection string that will be passed straight to
    `StrictRedis.from_url`. The connection string should be in the form:
        redis://username:password@localhost:6379/0

    ``settings``
    A dict of keyword args to be passed straight to `StrictRedis`

    Returns:

    An instance of `StrictRedis`
    """
    # attempt to get an existing connection from the registry
    redis = getattr(request.registry, '_redis_sessions', None)

    # if we found an active connection, return it
    if redis is not None:
        return redis

    # otherwise create a new connection
    if url is not None:
        redis = StrictRedis.from_url(url, **redis_options)
    else:
        redis = StrictRedis(**redis_options)

    # save the new connection in the registry
    setattr(request.registry, '_redis_sessions', redis)

    return redis
