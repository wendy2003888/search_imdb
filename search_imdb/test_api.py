import server

if __name__ == '__main__':
    queries = [
        'spielberg', 'spielberg hanks', '"Morgan Freeman"',
        '"Morgan Freeman" shawshank', '1994', 'City "Good will" dreAm', 'void'
    ]
    movie_search = server.MovieSearch()
    for q in queries:
        res = movie_search.search_movies(q)
        print('Search result of \'{}\''.format(q))
        print(res)
