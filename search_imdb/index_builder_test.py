import unittest

import index_builder


class TestIndexBuilder(unittest.TestCase):
    def setUp(self):
        self.builder = index_builder.IndexBuilder()

    def test_build_index(self):
        inputs = {
            '123': {
                'title': 'movie1',
                'year': '1991',
                'directors': ['dir name1', 'dir2'],
                'genres': ['genre name one'],
                'casts': [('a1', 'c1')]
            },
            '456': {
                'title': 'movie2',
                'year': '1992',
                'directors': [
                    'dir2',
                ],
                'genres': ['genre2'],
                'casts': [('a1', 'c1'), ('a2', 'c2')]
            }
        }
        expected_outputs = {
            'movie1': [('123', 'movie1')],
            'movie2': [('456', 'movie2')],
            '1991': [('123', 'movie1')],
            '1992': [('456', 'movie2')],
            'dir': [('123', 'movie1')],
            'name1': [('123', 'movie1')],
            'dir name1': [('123', 'movie1')],
            'dir2': [('123', 'movie1'), ('456', 'movie2')],
            'genre': [('123', 'movie1')],
            'name': [('123', 'movie1')],
            'one': [('123', 'movie1')],
            'genre name': [('123', 'movie1')],
            'name one': [('123', 'movie1')],
            'genre name one': [('123', 'movie1')],
            'genre2': [('456', 'movie2')],
            'a1': [('123', 'movie1'), ('456', 'movie2')],
            'c1': [('123', 'movie1'), ('456', 'movie2')],
            'a2': [('456', 'movie2')],
            'c2': [('456', 'movie2')],
        }
        sorted_expected_outputs = {
            k: sorted(v) if isinstance(v, list) else v
            for k, v in expected_outputs.items()
        }
        output = {
            k: sorted(v) if isinstance(v, list) else v
            for k, v in self.builder.build_index(inputs).items()
        }
        self.assertDictEqual(output, sorted_expected_outputs,
                             "Should be {}".format(sorted_expected_outputs))

    def test_flatten_instance(self):
        inputs = [
            'test_title', '1994', ['a', 'b'], ['a', ('b', 'c')],
            ['a', 'b', [('c', 'd')], [['e'], 'f']],
            ['a', 'b', [['c']], {
                'd': 'e',
                'f': 'g'
            }]
        ]
        expected_outputs = [['test_title'], ['1994'], ['a', 'b'],
                            ['a', 'b', 'c'], ['a', 'b', 'c', 'd', 'e', 'f'],
                            ['a', 'b', 'c', 'd', 'e', 'f', 'g']]
        for i in range(len(inputs)):
            self.assertEqual(self.builder.flatten_instance(inputs[i]),
                             expected_outputs[i],
                             "Should be {}".format(expected_outputs[i]))


if __name__ == '__main__':
    unittest.main()
