"""
This is the server to run search api.
"""
import pickle
import re

from os import path

import const
import crawler
import index_builder

QUERY_TEXT_RE_EXTRACTOR = re.compile(r'(".*?"|[^" ]+)')


class MovieSearch:
    def __init__(self):
        """
        Loads movie and index data.
        Initializes data if we don't have the data yet.
        """
        if not path.exists(const.TOKEN_TO_INDEX_FILE_PATH):
            if not path.exists(const.ID_TO_DETAIL_FILE_PATH):
                print('Initializing system. Starts crawling movies...')
                c = crawler.IMDB1KCrawler()
                c.run()
            print('Initializing system. Starts building index...')
            ib = index_builder.IndexBuilder()
            ib.run(const.ID_TO_DETAIL_FILE_PATH,
                   const.TOKEN_TO_INDEX_FILE_PATH)

        with open(const.TOKEN_TO_INDEX_FILE_PATH, 'rb') as token_to_index_f:
            self.index = pickle.load(token_to_index_f)

    def search_movies(self, query_text):
        """
        Processes query text and finds results.
        """
        query_text = query_text.lower()
        keywords = self.parse_query(query_text)
        list_of_movies = set()
        for keyword in keywords:
            if keyword in self.index:
                if len(list_of_movies) == 0:
                    list_of_movies.update(self.index[keyword])
                else:
                    list_of_movies = list_of_movies.intersection(
                        self.index[keyword])
        res = [item[1] for item in list_of_movies]
        return res

    def parse_query(self, query_text):
        """
        Parses the query text to list of single words and exact match words.
        """
        keywords = [
            token.replace('"', '')
            for token in QUERY_TEXT_RE_EXTRACTOR.findall(query_text)
        ]
        return keywords


if __name__ == '__main__':
    # Entry.
    print('Server starts.')
    movie_search = MovieSearch()
    while (True):
        print('Please type your search. Press enter to get results.')
        print('Press Q to quit.')
        query_text = input()
        if query_text == 'Q':
            break
        res = movie_search.search_movies(query_text)
        print('Search result of \'{}\''.format(query_text))
        print(res)
