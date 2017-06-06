class Rkeys(object):
    def __init__(self, conn):
        self.conn = conn
        self.keys = self.conn.keys
        self.Rstring_keys = []
        self.Rlist_list = []
        self.Rset_keys = []
        self.Rhash_keys = []
        self.Rzset_keys = []

    def get_all(self):
        return self.keys()

    def delete(self, key=None, kind=None, all=False):
        if kind is not None:
            return self.conn.delete(*kind)
        if all:
            return self.conn.delete(*self.keys())
        if all is False and key is  None and kind is None:
            raise TypeError("'key' must be not none if 'all' is False")
        return self.conn.delete(key)

    def get_values(self, *args):
        result_list = self.conn.mget(*args)
        result = {key: value for key, value in zip(args, result_list)}
        return result

    def set_values(self, **kargs):
        self.Rstring_keys += [key for key in kargs]
        return self.conn.mset(**kargs)


class Rstring(object):
    """for redis-key type"""
    def __init__(self, rkeys, key, value=None):
        self.conn = rkeys.conn
        self.rkeys = rkeys
        self.key = key
        if value is None:
            value = ""
        try:
            self.conn.set(self.key, value)
            self.rkeys.Rstring_keys.append(self.key)
        except Exception as ex:
            raise ex

    def set_value(self, value="", timeout=None):
        """set value for self.key"""
        if timeout is not None:
            if not isinstance(timeout, 1):
                raise TypeError("timeout must be int type")
            pipline = self.conn.pipeline()
            pipline.set(self.key, value)
            pipline.expire(self.key, timeout)
            result = pipline.execute()
            return result[0] and result[1]
        try:
            result = self.conn.set(self.key, value)
        except Exception as ex:
            raise ex
        return result

    def get_value(self, ttl=False):
        """get the value of self.key"""
        if not ttl:
            return self.conn.get(self.key)

        else:
            pipline = self.conn.pipeline()
            pipline.get(self.key)
            pipline.ttl(self.key)
            result = pipline.execute()
            return result

    def append(self, value):
        """add value to the end of """
        result = self.conn.append(self.key, value)

    def join(self, *args):
        try:
            target = "".join(args)
        except TypeError as e:
            raise e
        self.conn.append(self.key, target)

    def incr(num=None):
        try:
            result = self.conn.incr(self.key, 1 if not num else abs(num))
        except Exception as ex:
            raise ex
        return result

    def decr(num=None):
        try:
            result = self.conn.incr(self.key, -1 if not num else -abs(num))
        except Exception as ex:
            raise ex
        return result

    def getrange(self, start, end):
        if not (isinstance(start, type(1)) or isinstance(end, type(1))):
            raise TypeError("start and end must be int type")
        return self.conn.getrange(self.key, start, end)

    def setrange(self, offset, value):
        if not isinstance(offset, type(1)):
            raise TypeError("offset must be int type")
        return self.conn.setrange(self.key, offset, value)

    def getbit(self, offset=None):
        if offset is None:
            result = "".join([bin(ord(str(c))).replace('0b', "")
                              for c in str(self.get_value())[1:]])
            return result
        else:
            if not isinstance(offset, type(1)):
                raise TypeError("offset must be int type")
            if offset >= 0:
                result = self.conn.getbit(self.key)
                return result
            elif offset < 0:
                result = self.getbit()
                return result[offset]

    def setbit(self, offset, element):
        if not (element in [0, 1] or element in [True, False]):
            raise TypeError("element must be boolean type")
        if not isinstance(offset, type(1)):
            raise TypeError("offset must be int type")
        if offset >= 0:
            return self.conn.setbit(self.key, offset, element)
        elif offset < 0:
            real_offset = len(self.getbit()) + offset
            return self.conn.setbit(self.key, real_offset, element)

    def bitcount(self, start=None, end=None):
        try:
            result  = self.conn.bitcount(self.key, start=start, end=end)
        except Exception as ex:
            raise ex
        return result

    def bitop(self, operation, dest_key, *args):
        try:
            result = self.conn.bitop(operation, dest_key, *args)
            self.rkeys.Rstring_keys.append(dest_key)
        except Exception as ex:
            raise ex
        return self.get_value(dest_key)

    def __getitem__(self, key):
        return self.get_value().__getitem__(key)

    def __str__(self):
        return str(self.key)


class Rlist(list):

    def __init__(self, rkeys, key, value=None):
        self.rkeys = rkeys
        self.conn = self.rkeys.conn
        self.key = key
        if value is None:
            _value = list()
        _value = value
        try:
            self.conn.set(self.key, _value)
            self.rkeys.Rlist_list.append(self.key)
        except Exception as ex:
            raise ex

    def push(self, left=True, value):
        # True is left,  False is right
        if not isinstance(left, bool):
            raise TypeError("must be bool type")
        if methods:
            result = self.conn.lpush(self.key, *value)
        else:
            result = self.conn.rpush(self.key, *value)
        return result

    def pop(self, left=True):
        if not isinstance(left, bool):
            raise TypeError("must be bool type")
        if methods:
            result = self.conn.lpop(self.key)
        else:
            result = self.conn.rpop(self.key)
        return result

    def cut(self, start, end):
        if not (isinstance(start, int) and isinstance(end, start)):
            raise TypeError("start and end must be int type")
        return self.conn.ltrim(self.key)

    def bpop(self, left=True, time_out=0, dest=None, num=1):
        if not (isinstance(time_out, int) and isinstance(left, bool)):
            raise TypeError("time_out must be int type")
        if left and not dest:
            return self.conn.blpop(self.key, time_out)
        elif not dest:
            return self.conn.brpop(self.key, time_out)
        elif dest:
            if not isinstance(dest, list):
                raise TypeError("dest type error")
            try:
                if dest.key in self.rkeys.Rlist:
                    return self.conn.brpoplpush(self.key, dest.key, time_out)
            except Exception:
                result = self.conn.rpop(self.key)
                return [result, ] + 
