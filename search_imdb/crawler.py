"""
This file defines crawler functions to get and parse IMDB top 1000 movies.
"""
import aiohttp
import asyncio
import math
import pickle
import re
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
        self.NUM_REQUEST_PER_BATCH = 5

    async def request_list_page(self, url):
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(
                verify_ssl=False)) as session:
            async with session.get(url) as resp:
                body = await resp.text()
                res = self.parse_top1k_result(body)
                return res

    async def request_list_pages(self):
        """
        Crawls IMDB top 1000 movie list page.
        Parses the content and write the result to a file with movie ids and movie links.
        """
        print('Starts to handle top 1000 movie list.')
        num_pages = math.ceil(self.TOTAL_NUM_OF_MOVIES /
                              self.NUM_MOVIES_PER_PAGE)
        urls = [
            self.URL_BASE_TOP1K.format(page * self.NUM_MOVIES_PER_PAGE + 1)
            for page in range(num_pages)
        ]
        batches = math.ceil(len(urls) / self.NUM_REQUEST_PER_BATCH)
        id_to_movie_link = []
        for batch in range(batches):
            st = batch * self.NUM_REQUEST_PER_BATCH
            ed = min(len(urls), (batch + 1) * self.NUM_REQUEST_PER_BATCH)
            sub_results = await asyncio.gather(
                *[self.request_list_page(u) for u in urls[st:ed]])
            for res in sub_results:
                id_to_movie_link.extend(res)
                utils.progress_bar(len(id_to_movie_link),
                                   self.TOTAL_NUM_OF_MOVIES)
        print('\n{} movie links parsed.'.format(len(id_to_movie_link)))
        return id_to_movie_link

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
            id_to_movie_link.append((movie_id, movie_link))
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

    def parse_movie_page(self, content):
        """
        Parses movie detail page and return a map of formatted data.
        """
        soup = BeautifulSoup(content, 'html.parser')
        title_block = soup.select('.title_wrapper > h1')
        title_tag, year_tag = title_block[0].contents[0], title_block[
            0].contents[1].a
        title, year = title_tag.string.replace(u'\xa0', u''), year_tag.string
        director_tag = soup.select('.credit_summary_item')[0].select('a')
        directors = [tag.string for tag in director_tag]
        genre_tag = soup.select(
            '[class="see-more inline canwrap"] a[href*="genres"]')
        genres = [tag.string.strip() for tag in genre_tag]
        formatted_content = {
            'title': title,
            'year': year,
            'directors': directors,
            'genres': genres,
        }
        return formatted_content

    async def request_movie_and_cast_page(self, movie_id, movie_link,
                                          cast_link):
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(
                verify_ssl=False)) as session:
            async with session.get(movie_link) as movie_resp:
                movie_body = await movie_resp.text()
                formatted_content = self.parse_movie_page(movie_body)
            async with session.get(cast_link) as cast_resp:
                cast_body = await cast_resp.text()
                casts = self.parse_cast_page(cast_body)
            formatted_content['casts'] = casts
            return {movie_id: formatted_content}

    async def request_movie_pages(self, id_to_movie_link):
        """
        Crawls single movie detail page. Returns a map of <movie_id, formatted data>.
        """
        batches = math.ceil(len(id_to_movie_link) / self.NUM_REQUEST_PER_BATCH)
        print('Starts to request and parse movie details.')
        links = []
        for (movie_id, movie_link) in id_to_movie_link:
            cast_link = '{}/title/{}/fullcredits?ref_=tt_cl_sm#cast'.format(
                self.DOMAIN, movie_id)
            links.append((movie_id, movie_link, cast_link))
        id_to_details = {}
        for batch in range(batches):
            st = batch * self.NUM_REQUEST_PER_BATCH
            ed = min(len(id_to_movie_link),
                     (batch + 1) * self.NUM_REQUEST_PER_BATCH)
            sub_results = await asyncio.gather(*[
                self.request_movie_and_cast_page(id, movie_link, cast_link)
                for id, movie_link, cast_link in links[st:ed]
            ])
            for res in sub_results:
                id_to_details.update(res)
            utils.progress_bar(len(id_to_details), self.TOTAL_NUM_OF_MOVIES)
        print('\nSuccessfully parsed {} movie details.'.format(
            len(id_to_details)))
        return id_to_details

    def run(self):
        loop = asyncio.get_event_loop()
        id_to_movie_link = loop.run_until_complete(self.request_list_pages())

        with open(const.ID_TO_MOVIE_FILE_PATH, 'w') as f:
            f.writelines([
                '{},{}\n'.format(movie_id, movie_link)
                for movie_id, movie_link in id_to_movie_link
            ])
            print('Results are written to file {}'.format(f.name))
        # To debug, check or use intermediate results, please remove the comments below.
        # with open(const.ID_TO_MOVIE_FILE_PATH, 'r') as input_f:
        #     lines = input_f.readlines()
        #     id_to_movie_link = [line[:-1].split(',') for line in lines]
        #     print('Successfully loaded {} movie ids and links.'.format(
        #         len(id_to_movie_link)))

        id_to_details = loop.run_until_complete(
            self.request_movie_pages(id_to_movie_link))

        sys.setrecursionlimit(100000)
        # Dumps formatted results a pickle file.
        with open(const.ID_TO_DETAIL_FILE_PATH, 'wb') as output_f:
            pickle.dump(id_to_details, output_f)
        print('Movie data were dump to {}'.format(
            const.ID_TO_DETAIL_FILE_PATH))


if __name__ == '__main__':
    crawler = IMDB1KCrawler()
    crawler.run()
