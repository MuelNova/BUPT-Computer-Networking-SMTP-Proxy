from app import logger, Proxy

proxy = Proxy(lambda x, y, z: print(z), host='0.0.0.0')
proxy()