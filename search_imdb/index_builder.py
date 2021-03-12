import pickle
import sys

import const
import utils


class IndexBuilder:
    def build_index(self, id_to_details):
        """
        Builds reverse index with 1 gram, 2 gram and 3 gram.
        """
        reversed_index = {}
        i = 1
        for (movie_id, details) in id_to_details.items():
            utils.progress_bar(i, len(id_to_details))
            bag_of_strings = set()
            for v in details.values():
                bag_of_strings.update(self.flatten_instance(v))
            tokens = set()
            for s in bag_of_strings:
                words = s.lower().split(' ')
                tokens.update(words)
                # 2 gram
                for i in range(len(words) - 1):
                    tokens.add(' '.join(words[i:i + 2]))
                # 3 gram
                for i in range(len(words) - 2):
                    tokens.add(' '.join(words[i:i + 3]))
            for token in tokens:
                if token not in reversed_index:
                    reversed_index[token] = set()
                reversed_index[token].add((movie_id, details['title']))
            i += 1
        for (token, movie) in reversed_index.items():
            reversed_index[token] = list(movie)
        return reversed_index

    def flatten_instance(self, a):
        """
        Flattens instance to a list of non-iterable items.
        """
        if a == []:
            return a
        if not isinstance(a, (list, tuple, dict)):
            return [a]
        ans = []
        for item in a:
            if isinstance(item, (list, tuple, dict)):
                ans.extend(self.flatten_instance(item))
            else:
                ans.append(item)
        return ans

    def run(self, input_file_path, output_file_path):
        print('Loading movie file {}.'.format(input_file_path))
        with open(input_file_path, 'rb') as f:
            id_to_details = pickle.load(f)
        reversed_index = self.build_index(id_to_details)
        sys.setrecursionlimit(100000)
        with open(output_file_path, 'wb') as out_f:
            pickle.dump(reversed_index, out_f)
        print('Index data were dump to {}'.format(output_file_path))


if __name__ == '__main__':
    ib = IndexBuilder()
    ib.run(const.ID_TO_DETAIL_FILE_PATH, const.TOKEN_TO_INDEX_FILE_PATH)
