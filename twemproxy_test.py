#!/usr/bin/python
import redis

if __name__ == '__main__':
    r = redis.StrictRedis(host = '127.0.0.1', port = 6379, db = 3)
