import pickle

filepath = './pickled_cookies/1310107654071838_post-accept_www_gov_uk.pkl'

cookies = pickle.load(open(filepath, "rb"))
for cookie in cookies:
    print(cookie)

### Too tired to finish this, will be done for tomorrow... Sorry :( ###