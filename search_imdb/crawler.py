"""
This file defines crawler functions to get and parse IMDB top 1000 movies.
"""
import pickle
import re
import requests
import sys

from bs4 import BeautifulSoup
import const
import utils

HEADERS = {
    'User-Agent':
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36',
}

class IMDB1KCrawler:
    def __init__(self):
        self.DOMAIN = u'https://www.imdb.com'
        self.URL_BASE_TOP1K = self.DOMAIN + u'/search/title/?groups=top_1000&view=simple&sort=user_rating,desc&start={}&ref_=adv_nxt'
        self.NUM_MOVIES_PER_PAGE = 50
        self.TOTAL_NUM_OF_MOVIES = 1000

    def request_search_page(self):
        """
        Crawls IMDB top 1000 movie list page.
        Parses the content and write the result to a file with movie ids and movie links.
        """
        num_finished_page = 0
        with open(const.ID_TO_MOVIE_FILE_PATH, 'w') as f:
            while True:
                start_num = num_finished_page * self.NUM_MOVIES_PER_PAGE + 1
                utils.progress_bar(start_num, self.TOTAL_NUM_OF_MOVIES)
                if start_num > self.TOTAL_NUM_OF_MOVIES:
                    # Out of range
                    break
                url = self.URL_BASE_TOP1K.format(start_num)
                r = requests.get(url, headers=HEADERS)
                id_to_movie_link = self.parse_top1k_result(r.text)
                f.writelines(id_to_movie_link)
                num_finished_page += 1
            print(
                '\n{} pages parsed and results are written to file {}'.format(
                    num_finished_page, f.name))

    def parse_top1k_result(self, content):
        """
        Parses the top1000 result page to list of anchors pointing to movie page.
        Processes anchors to movie ids and movie links.
        :param content: html content
        :return: a list of string with the format of '<movie_id>,<movie_link>\n'
        """
        soup = BeautifulSoup(content, 'html.parser')
        list_of_anchors = soup.select(
            'div[class="lister-item mode-simple"] > .lister-item-content .col-title > .lister-item-header a[href]'
        )
        id_to_movie_link = []
        for anchor in list_of_anchors:
            href = anchor['href']
            movie_id = re.search('/title/(.*)/', href, flags=0).group(1)
            movie_link = self.DOMAIN + href
            id_to_movie_link.append('{},{}\n'.format(movie_id, movie_link))
        return id_to_movie_link

    def parse_cast_page(self, content):
        """
        Parses cast page and return a list of (actor name, character name).
        """
        soup = BeautifulSoup(content, 'html.parser')
        cast_tags = soup.select('table[class=cast_list] > tr')
        actor_to_charactor = []
        for tag in cast_tags:
            if tag.select('.castlist_label'):  # Remove castlist label rows
                continue
            actor_tag, character_tag = tag.select('[href*=name]'), tag.select(
                '[href*=character]')
            actor = actor_tag[1].string.strip() if len(actor_tag) > 1 else ''
            character = character_tag[0].string.strip(
            ) if len(character_tag) > 0 else ''
            if actor == '' and character == '':
                continue
            actor_to_charactor.append((actor, character))
        return actor_to_charactor

    def parse_movie_page(self, movie_content, cast_content):
        """
        Parses movie detail page and return a map of formatted data.
        """
        soup = BeautifulSoup(movie_content, 'html.parser')
        title_block = soup.select('.title_wrapper > h1')
        title_tag, year_tag = title_block[0].contents[0], title_block[
            0].contents[1].a
        title, year = title_tag.string.replace(u'\xa0', u''), year_tag.string
        director_tag = soup.select('.credit_summary_item')[0].select('a')
        directors = [tag.string for tag in director_tag]
        genre_tag = soup.select(
            '[class="see-more inline canwrap"] a[href*="genres"]')
        genres = [tag.string.strip() for tag in genre_tag]
        casts = self.parse_cast_page(cast_content)
        formatted_content = {
            'title': title,
            'year': year,
            'directors': directors,
            'genres': genres,
            'casts': casts
        }
        return formatted_content

    def request_movie_page(self):
        """
        Crawls single movie detail page. Returns a map of <movie_id, formatted data>.
        """
        with open(const.ID_TO_MOVIE_FILE_PATH, 'r') as input_f:
            lines = input_f.readlines()
            id_to_movie_link = [line[:-1].split(',') for line in lines]

        id_to_details = {}
        print('Successfully loaded {} movie ids and links.'.format(
            len(id_to_movie_link)))
        print('Starts to request and parse movie details.')
        for i in range(len(id_to_movie_link)):
            utils.progress_bar(i + 1, len(id_to_movie_link))
            (movie_id, movie_link) = id_to_movie_link[i]
            r_movie = requests.get(movie_link, headers=HEADERS)
            cast_link = '{}/title/{}/fullcredits?ref_=tt_cl_sm#cast'.format(
                self.DOMAIN, movie_id)
            r_cast = requests.get(cast_link, headers=HEADERS)
            formatted_content = self.parse_movie_page(r_movie.text,
                                                      r_cast.text)
            id_to_details[movie_id] = formatted_content
        print('Successfully parsed {} movie details.'.format(
            len(id_to_movie_link)))
        return id_to_details

    def run(self):
        self.request_search_page()
        id_to_details = self.request_movie_page()

        sys.setrecursionlimit(100000)
        # Dumps formatted results a pickle file.
        with open(const.ID_TO_DETAIL_FILE_PATH, 'wb') as output_f:
            pickle.dump(id_to_details, output_f)
        print('Movie data were dump to {}'.format(
            const.ID_TO_DETAIL_FILE_PATH))


if __name__ == '__main__':
    crawler = IMDB1KCrawler()
    crawler.run()
