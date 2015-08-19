# -*- coding: utf-8 -*-

# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""
test_jsonpath_rw_ext
----------------------------------

Tests for `jsonpath_rw_ext` module.
"""

from jsonpath_rw import jsonpath  # For setting the global auto_id_field flag
from jsonpath_rw import lexer  # For setting the global auto_id_field flag
from oslotest import base
from six import moves
import testscenarios

from jsonpath_rw_ext import parser


class TestJsonpath_rw_ext(testscenarios.WithScenarios,
                          base.BaseTestCase):
    scenarios = [
        ('sorted_list', dict(string='objects.`sorted`',
                             data={'objects': ['alpha', 'gamma', 'beta']},
                             target=['alpha', 'beta', 'gamma'])),
        ('sorted_dict', dict(string='objects.`sorted`',
                             data={'objects': {'cow': 'moo', 'horse': 'neigh',
                                               'cat': 'meow'}},
                             target=['cat', 'cow', 'horse'])),

        ('len_list', dict(string='objects.`len`',
                          data={'objects': ['alpha', 'gamma', 'beta']},
                          target=3)),
        ('len_dict', dict(string='objects.`len`',
                          data={'objects': {'cow': 'moo', 'cat': 'neigh'}},
                          target=2)),
        ('len_str', dict(string='objects[0].`len`',
                         data={'objects': ['alpha', 'gamma']},
                         target=5)),

        ('filter_exists_syntax1', dict(string='objects[?cow]',
                                       data={'objects': [{'cow': 'moo'},
                                                         {'cat': 'neigh'}]},
                                       target=[{'cow': 'moo'}])),
        ('filter_exists_syntax2', dict(string='objects[?@.cow]',
                                       data={'objects': [{'cow': 'moo'},
                                                         {'cat': 'neigh'}]},
                                       target=[{'cow': 'moo'}])),
        ('filter_exists_syntax3', dict(string='objects[?(@.cow)]',
                                       data={'objects': [{'cow': 'moo'},
                                                         {'cat': 'neigh'}]},
                                       target=[{'cow': 'moo'}])),
        ('filter_eq1', dict(string='objects[?cow="moo"]',
                            data={'objects': [{'cow': 'moo'},
                                              {'cow': 'neigh'},
                                              {'cat': 'neigh'}]},
                            target=[{'cow': 'moo'}])),
        ('filter_eq2', dict(string='objects[?(@.["cow"]="moo")]',
                            data={'objects': [{'cow': 'moo'},
                                              {'cow': 'neigh'},
                                              {'cat': 'neigh'}]},
                            target=[{'cow': 'moo'}])),
        ('filter_eq3', dict(string='objects[?cow=="moo"]',
                            data={'objects': [{'cow': 'moo'},
                                              {'cow': 'neigh'},
                                              {'cat': 'neigh'}]},
                            target=[{'cow': 'moo'}])),
        ('filter_gt', dict(string='objects[?cow>5]',
                           data={'objects': [{'cow': 8},
                                             {'cow': 7},
                                             {'cow': 5},
                                             {'cow': 'neigh'}]},
                           target=[{'cow': 8}, {'cow': 7}])),
        ('filter_and', dict(string='objects[?cow>5&cat=2]',
                            data={'objects': [{'cow': 8, 'cat': 2},
                                              {'cow': 7, 'cat': 2},
                                              {'cow': 5, 'cat': 3},
                                              {'cow': 8, 'cat': 3}]},
                            target=[{'cow': 8, 'cat': 2},
                                    {'cow': 7, 'cat': 2}])),

        ('sort1', dict(string='objects[/cow]',
                       data={'objects': [{'cat': 1, 'cow': 2},
                                         {'cat': 2, 'cow': 1},
                                         {'cat': 3, 'cow': 3}]},
                       target=[{'cat': 2, 'cow': 1},
                               {'cat': 1, 'cow': 2},
                               {'cat': 3, 'cow': 3}])),
        ('sort2', dict(string='objects[\cat]',
                       data={'objects': [{'cat': 2}, {'cat': 1}, {'cat': 3}]},
                       target=[{'cat': 3}, {'cat': 2}, {'cat': 1}])),
        ('sort3', dict(string='objects[/cow,\cat]',
                       data={'objects': [{'cat': 1, 'cow': 2},
                                         {'cat': 2, 'cow': 1},
                                         {'cat': 3, 'cow': 1},
                                         {'cat': 3, 'cow': 3}]},
                       target=[{'cat': 3, 'cow': 1},
                               {'cat': 2, 'cow': 1},
                               {'cat': 1, 'cow': 2},
                               {'cat': 3, 'cow': 3}])),
        ('sort4', dict(string='objects[/cat.cow]',
                       data={'objects': [{'cat': {'dog': 1, 'cow': 2}},
                                         {'cat': {'dog': 2, 'cow': 1}},
                                         {'cat': {'dog': 3, 'cow': 3}}]},
                       target=[{'cat': {'dog': 2, 'cow': 1}},
                               {'cat': {'dog': 1, 'cow': 2}},
                               {'cat': {'dog': 3, 'cow': 3}}])),
        ('sort5_twofields', dict(string='objects[/cat.(cow,bow)]',
                                 data={'objects':
                                       [{'cat': {'dog': 1, 'bow': 3}},
                                        {'cat': {'dog': 2, 'cow': 1}},
                                        {'cat': {'dog': 2, 'bow': 2}},
                                        {'cat': {'dog': 3, 'cow': 2}}]},
                                 target=[{'cat': {'dog': 2, 'cow': 1}},
                                         {'cat': {'dog': 2, 'bow': 2}},
                                         {'cat': {'dog': 3, 'cow': 2}},
                                         {'cat': {'dog': 1, 'bow': 3}}])),

        ('real_life_example1', dict(
            string="payload.metrics[?(@.name='cpu.frequency')].value",
            data={'payload': {'metrics': [
                {'timestamp': '2013-07-29T06:51:34.472416',
                 'name': 'cpu.frequency',
                 'value': 1600,
                 'source': 'libvirt.LibvirtDriver'},
                {'timestamp': '2013-07-29T06:51:34.472416',
                 'name': 'cpu.user.time',
                 'value': 17421440000000,
                 'source': 'libvirt.LibvirtDriver'}]}},
            target=[1600])),
    ]

    def test_fields_value(self):
        jsonpath.auto_id_field = None
        result = parser.parse(self.string, debug=True).find(self.data)
        if isinstance(self.target, list):
            self.assertEqual(self.target, [r.value for r in result])
        elif isinstance(self.target, set):
            self.assertEqual(self.target, set([r.value for r in result]))
        elif isinstance(self.target, (int, float)):
            self.assertEqual(self.target, result[0].value)
        else:
            self.assertEqual(self.target, result.value)

# NOTE(sileht): copy of tests/test_jsonpath.py
# to ensure we didn't break jsonpath_rw


class TestJsonPath(base.BaseTestCase):
    """Tests of the actual jsonpath functionality """

    #
    # Check that the data value returned is good
    #
    def check_cases(self, test_cases):
        # Note that just manually building an AST would avoid this dep and
        # isolate the tests, but that would suck a bit
        # Also, we coerce iterables, etc, into the desired target type

        for string, data, target in test_cases:
            print('parse("%s").find(%s) =?= %s' % (string, data, target))
            result = parser.parse(string).find(data)
            if isinstance(target, list):
                assert [r.value for r in result] == target
            elif isinstance(target, set):
                assert set([r.value for r in result]) == target
            else:
                assert result.value == target

    def test_fields_value(self):
        jsonpath.auto_id_field = None
        self.check_cases([('foo', {'foo': 'baz'}, ['baz']),
                          ('foo,baz', {'foo': 1, 'baz': 2}, [1, 2]),
                          ('@foo', {'@foo': 1}, [1]),
                          ('*', {'foo': 1, 'baz': 2}, set([1, 2]))])

        jsonpath.auto_id_field = 'id'
        self.check_cases([('*', {'foo': 1, 'baz': 2}, set([1, 2, '`this`']))])

    def test_root_value(self):
        jsonpath.auto_id_field = None
        self.check_cases([
            ('$', {'foo': 'baz'}, [{'foo': 'baz'}]),
            ('foo.$', {'foo': 'baz'}, [{'foo': 'baz'}]),
            ('foo.$.foo', {'foo': 'baz'}, ['baz']),
        ])

    def test_this_value(self):
        jsonpath.auto_id_field = None
        self.check_cases([
            ('`this`', {'foo': 'baz'}, [{'foo': 'baz'}]),
            ('foo.`this`', {'foo': 'baz'}, ['baz']),
            ('foo.`this`.baz', {'foo': {'baz': 3}}, [3]),
        ])

    def test_index_value(self):
        self.check_cases([
            ('[0]', [42], [42]),
            ('[5]', [42], []),
            ('[2]', [34, 65, 29, 59], [29])
        ])

    def test_slice_value(self):
        self.check_cases([('[*]', [1, 2, 3], [1, 2, 3]),
                          ('[*]', moves.range(1, 4), [1, 2, 3]),
                          ('[1:]', [1, 2, 3, 4], [2, 3, 4]),
                          ('[:2]', [1, 2, 3, 4], [1, 2])])

        # Funky slice hacks
        self.check_cases([
            ('[*]', 1, [1]),  # This is a funky hack
            ('[0:]', 1, [1]),  # This is a funky hack
            ('[*]', {'foo': 1}, [{'foo': 1}]),  # This is a funky hack
            ('[*].foo', {'foo': 1}, [1]),  # This is a funky hack
        ])

    def test_child_value(self):
        self.check_cases([('foo.baz', {'foo': {'baz': 3}}, [3]),
                          ('foo.baz', {'foo': {'baz': [3]}}, [[3]]),
                          ('foo.baz.bizzle', {'foo': {'baz': {'bizzle': 5}}},
                           [5])])

    def test_descendants_value(self):
        self.check_cases([
            ('foo..baz', {'foo': {'baz': 1, 'bing': {'baz': 2}}}, [1, 2]),
            ('foo..baz', {'foo': [{'baz': 1}, {'baz': 2}]}, [1, 2]),
        ])

    def test_parent_value(self):
        self.check_cases([('foo.baz.`parent`', {'foo': {'baz': 3}},
                           [{'baz': 3}]),
                          ('foo.`parent`.foo.baz.`parent`.baz.bizzle',
                           {'foo': {'baz': {'bizzle': 5}}}, [5])])

    def test_hyphen_key(self):
        self.check_cases([('foo.bar-baz', {'foo': {'bar-baz': 3}}, [3]),
                          ('foo.[bar-baz,blah-blah]',
                           {'foo': {'bar-baz': 3, 'blah-blah': 5}},
                           [3, 5])])
        self.assertRaises(lexer.JsonPathLexerError, self.check_cases,
                          [('foo.-baz', {'foo': {'-baz': 8}}, [8])])

    #
    # Check that the paths for the data are correct.
    # FIXME: merge these tests with the above, since the inputs are the same
    # anyhow
    #
    def check_paths(self, test_cases):
        # Note that just manually building an AST would avoid this dep and
        # isolate the tests, but that would suck a bit
        # Also, we coerce iterables, etc, into the desired target type

        for string, data, target in test_cases:
            print('parse("%s").find(%s).paths =?= %s' % (string, data, target))
            result = parser.parse(string).find(data)
            if isinstance(target, list):
                assert [str(r.full_path) for r in result] == target
            elif isinstance(target, set):
                assert set([str(r.full_path) for r in result]) == target
            else:
                assert str(result.path) == target

    def test_fields_paths(self):
        jsonpath.auto_id_field = None
        self.check_paths([('foo', {'foo': 'baz'}, ['foo']),
                          ('foo,baz', {'foo': 1, 'baz': 2}, ['foo', 'baz']),
                          ('*', {'foo': 1, 'baz': 2}, set(['foo', 'baz']))])

        jsonpath.auto_id_field = 'id'
        self.check_paths([('*', {'foo': 1, 'baz': 2},
                           set(['foo', 'baz', 'id']))])

    def test_root_paths(self):
        jsonpath.auto_id_field = None
        self.check_paths([
            ('$', {'foo': 'baz'}, ['$']),
            ('foo.$', {'foo': 'baz'}, ['$']),
            ('foo.$.foo', {'foo': 'baz'}, ['foo']),
        ])

    def test_this_paths(self):
        jsonpath.auto_id_field = None
        self.check_paths([
            ('`this`', {'foo': 'baz'}, ['`this`']),
            ('foo.`this`', {'foo': 'baz'}, ['foo']),
            ('foo.`this`.baz', {'foo': {'baz': 3}}, ['foo.baz']),
        ])

    def test_index_paths(self):
        self.check_paths([('[0]', [42], ['[0]']),
                          ('[2]', [34, 65, 29, 59], ['[2]'])])

    def test_slice_paths(self):
        self.check_paths([('[*]', [1, 2, 3], ['[0]', '[1]', '[2]']),
                          ('[1:]', [1, 2, 3, 4], ['[1]', '[2]', '[3]'])])

    def test_child_paths(self):
        self.check_paths([('foo.baz', {'foo': {'baz': 3}}, ['foo.baz']),
                          ('foo.baz', {'foo': {'baz': [3]}}, ['foo.baz']),
                          ('foo.baz.bizzle', {'foo': {'baz': {'bizzle': 5}}},
                           ['foo.baz.bizzle'])])

    def test_descendants_paths(self):
        self.check_paths([('foo..baz', {'foo': {'baz': 1, 'bing': {'baz': 2}}},
                           ['foo.baz', 'foo.bing.baz'])])

    #
    # Check the "auto_id_field" feature
    #
    def test_fields_auto_id(self):
        jsonpath.auto_id_field = "id"
        self.check_cases([('foo.id', {'foo': 'baz'}, ['foo']),
                          ('foo.id', {'foo': {'id': 'baz'}}, ['baz']),
                          ('foo,baz.id', {'foo': 1, 'baz': 2}, ['foo', 'baz']),
                          ('*.id',
                           {'foo': {'id': 1},
                            'baz': 2},
                           set(['1', 'baz']))])

    def test_root_auto_id(self):
        jsonpath.auto_id_field = 'id'
        self.check_cases([
            ('$.id', {'foo': 'baz'}, ['$']),  # This is a wonky case that is
                                              # not that interesting
            ('foo.$.id', {'foo': 'baz', 'id': 'bizzle'}, ['bizzle']),
            ('foo.$.baz.id', {'foo': 4, 'baz': 3}, ['baz']),
        ])

    def test_this_auto_id(self):
        jsonpath.auto_id_field = 'id'
        self.check_cases([
            ('id', {'foo': 'baz'}, ['`this`']),  # This is, again, a wonky case
                                                 # that is not that interesting
            ('foo.`this`.id', {'foo': 'baz'}, ['foo']),
            ('foo.`this`.baz.id', {'foo': {'baz': 3}}, ['foo.baz']),
        ])

    def test_index_auto_id(self):
        jsonpath.auto_id_field = "id"
        self.check_cases([('[0].id', [42], ['[0]']),
                          ('[2].id', [34, 65, 29, 59], ['[2]'])])

    def test_slice_auto_id(self):
        jsonpath.auto_id_field = "id"
        self.check_cases([('[*].id', [1, 2, 3], ['[0]', '[1]', '[2]']),
                          ('[1:].id', [1, 2, 3, 4], ['[1]', '[2]', '[3]'])])

    def test_child_auto_id(self):
        jsonpath.auto_id_field = "id"
        self.check_cases([('foo.baz.id', {'foo': {'baz': 3}}, ['foo.baz']),
                          ('foo.baz.id', {'foo': {'baz': [3]}}, ['foo.baz']),
                          ('foo.baz.id', {'foo': {'id': 'bizzle', 'baz': 3}},
                           ['bizzle.baz']),
                          ('foo.baz.id', {'foo': {'baz': {'id': 'hi'}}},
                           ['foo.hi']),
                          ('foo.baz.bizzle.id',
                           {'foo': {'baz': {'bizzle': 5}}},
                           ['foo.baz.bizzle'])])

    def test_descendants_auto_id(self):
        jsonpath.auto_id_field = "id"
        self.check_cases([('foo..baz.id',
                           {'foo': {
                               'baz': 1,
                               'bing': {
                                   'baz': 2
                               }
                           }},
                           ['foo.baz',
                            'foo.bing.baz'])])
