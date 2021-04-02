from urllib.parse import quote

import moviesearch

# This is to search movie either in a name or a list of names on either websites.
def input_name():
    obj_raw = input("Input a name or a list of name (use ',' to seperate): ")
    obj_in = obj_raw.split(",")
    return obj_in


if __name__ == '__main__':
    while True:
        source = input("Input a source (Douban, IMDb, Q (for quit)): ").lower()

        if source == 'q':
            print("Quit.")
            break
        elif source == "douban":
            searcher = moviesearch.DoubanInfo()
        elif source == 'imdb':
            searcher = moviesearch.IMDbInfo()
        else:
            print("Wrong source.")

        if searcher:
            for name in input_name():
                searcher.search(quote(name))
            break
