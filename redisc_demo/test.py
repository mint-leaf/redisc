from redis import Redis
from redisc import Rkeys, Rstring


conn = Redis()
rkeys = Rkeys(conn)


def test_funs():
    return "hello test"

class test_test():
    def __init__(self):
        self.message = "hello test"


def test_string():
    # normal
    rstring = Rstring(rkeys, key="key-test", value="value-test")
    # different type
    print(rstring[1:-2])
    print(rstring.getbit())
    try:
        rstring1 = Rstring(rkeys, key="key-error1", value=test_funs)
        print(rstring1.get_value())
    except Exception as e1:
        print(e1)
    try:
        rstring2 = Rstring(rkeys, key="key-error2", value=test_test)
        print(rstring2.get_value())
    except Exception as e2:
        print(e2)
    try:
        rstring = Rstring(rkeys, key=None, value=None)
    except Exception as e3:
        print(e3)
    # test get_values
    values_aim = rkeys.get_values(*rkeys.keys())
    print(values_aim)
    # test set_values
    params = {
        'key1': 'value1',
        'key2': 'value2',
        'key3': 'value3'
    }
    result = rkeys.set_values(**params)
    print(result)


def main():
    test_string()
    print([x for x in rkeys.keys()])
    print(rkeys.get_all())
    print(rkeys.keys())
    print(rkeys.delete(all=True))
    print(rkeys.Rstring_keys)


if __name__ == "__main__":
    main()
