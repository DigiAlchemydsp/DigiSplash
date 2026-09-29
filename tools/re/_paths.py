"""Locate the sibling checkouts the tools here import.

Each tool needs a digiemu or elekloader checkout. Set DIGIEMU_DIR /
ELEKLOADER_DIR to it, or keep the checkout next to this repo (the defaults
look upward for a directory with that name).
"""
import os


def find(env, name, *bases):
    v = os.environ.get(env)
    if v:
        if os.path.isdir(v):
            return os.path.abspath(v)
        raise SystemExit('%s is not a directory: %s' % (env, v))
    here = os.path.dirname(os.path.abspath(__file__))
    for b in bases:
        p = os.path.normpath(os.path.join(here, b, name))
        if os.path.isdir(p):
            return p
    raise SystemExit(
        'cannot find the %s checkout: set %s to it, or place %s where the '
        'defaults look (%s).' % (name, env, name, ', '.join(bases)))
