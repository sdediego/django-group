from django.core.cache import cache

# Create your caches here.

CACHE_KEYS = {
    'user_keys': {
        # user primary key (pk = user.pk)
        'groups': 'grp_g-{pk}',
        'requests': 'grp_r-{pk}',
        'sent_requests': 'grp_sr-{pk}',
        'viewed_requests': 'grp_vr-{pk}',
        'unviewed_requests': 'grp_uvr-{pk}',
        'rejected_requests': 'grp_rr-{pk}',
        'unrejected_requests': 'grp_urr-{pk}',
        },
    'group_keys': {
        # group primary key (pk = post.pk)
        'memberships': 'grp_ms-{pk}',
        'members': 'grp_mb-{pk}',
    },
}

CACHE_BUST = {
    'groups': [
        'groups',
    ],
    'memberships': [
        'memberships',
        'members',
    ],
    'requests': [
        'requests',
        'viewed_requests',
        'unviewed_requests',
        'rejected_requests',
        'unrejected_requests',
    ],
    'sent_requests': [
        'sent_requests',
    ],
}


def cache_bust(cache_types):
    """
    Bust the cache for a given type.
    The 'cache_types' parameters is a list
    of tuples (key_type, pk).
    """
    for key_type, pk in cache_types:
        bust_types = CACHE_BUST.get(key_type, None)
        keys = [make_key(to_bust, pk) for to_bust in bust_types]
        cache.delete_many(keys)


def make_key(key_type, pk):
    """
    Build the cache key for a particular type of cached value.
    """
    key = CACHE_KEYS['user_keys'].get(key_type, None)
    if key is None:
        key = CACHE_KEYS['group_keys'].get(key_type)
    key.format(pk=pk)
    return key


def make_key_many(cache_types):
    """
    Build the cache key for several cache values.
    """
    keys = {}
    for key_type, pk in cache_types:
        key = make_key(key_type, pk)
        keys.update({key_type: key})
    return keys
