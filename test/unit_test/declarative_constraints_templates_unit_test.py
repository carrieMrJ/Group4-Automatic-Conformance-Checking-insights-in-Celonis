import unittest

from src.declarative_constraints.templates import startWith, endWith, never, atMostOnce, atLeastOnce, precedence, \
    alternate_precedence, \
    chain_precedence, responded_existence, response, alternate_response, chain_response, succession, \
    alternate_succession, chain_succession, not_coexistence, not_chain_succession, not_succession


class DeclarativeTestMethods(unittest.TestCase):

    # unit tests for constraint templates
    def test_startWith(self):
        input_symbols = ['a', 'b', 'c', 'd']
        self.assertEqual(startWith(input_symbols, 'a'), '^a')
        self.assertEqual(startWith(input_symbols, 'c'), '^c')

    def test_endWith(self):
        input_symbols = ['a', 'b', 'c', 'd']
        self.assertEqual(endWith(input_symbols, 'd'), 'd$')
        self.assertEqual(endWith(input_symbols, 'b'), 'b$')

    def test_atMostOnce(self):
        input_symbols = ['a', 'b', 'c', 'd']
        self.assertEqual(atMostOnce(input_symbols, 'a'), '^[^a]*a?[^a]*$')
        self.assertEqual(atMostOnce(input_symbols, 'c'), '^[^c]*c?[^c]*$')

    def test_atLeastOnce(self):
        input_symbols = ['a', 'b', 'c', 'd']
        self.assertEqual(atLeastOnce(input_symbols, 'a'), '^.*a.*$')
        self.assertEqual(atLeastOnce(input_symbols, 'c'), '^.*c.*$')

    def test_never(self):
        input_symbols = ['a', 'b', 'c', 'd']
        self.assertEqual(never(input_symbols, 'a'), '^(?!.*a).*')
        self.assertEqual(never(input_symbols, 'c'), '^(?!.*c).*')

    def test_precedence(self):
        input_symbols = ['a', 'b', 'c', 'd']
        self.assertEqual(precedence(input_symbols, 'a', 'b'), '[^b]*a.*b.*')
        self.assertEqual(precedence(input_symbols, 'c', 'd'), '[^d]*c.*d.*')

    def test_alternate_precedence(self):
        input_symbols = ['a', 'b', 'c', 'd']
        self.assertEqual(alternate_precedence(input_symbols, 'a', 'b'), '[^b]*(a(?!b)*)*')
        self.assertEqual(alternate_precedence(input_symbols, 'c', 'd'), '[^d]*(c(?!d)*)*')

    def test_chain_precedence(self):
        input_symbols = ['a', 'b', 'c', 'd']
        self.assertEqual(chain_precedence(input_symbols, 'a', 'b'), '[^b]*(ab)*[^b]*')
        self.assertEqual(chain_precedence(input_symbols, 'c', 'd'), '[^d]*(cd)*[^d]*')

    def test_responded_existence(self):
        input_symbols = ['a', 'b', 'c', 'd']
        self.assertEqual(responded_existence(input_symbols, 'a', 'b'), '[^a]*(a[^b]*b.*)?')
        self.assertEqual(responded_existence(input_symbols, 'c', 'd'), '[^c]*(c[^d]*d.*)?')

    def test_response(self):
        input_symbols = ['a', 'b', 'c', 'd']
        self.assertEqual(response(input_symbols, 'a', 'b'), '[^a]*(ab)*[^a]*')
        self.assertEqual(response(input_symbols, 'c', 'd'), '[^c]*(cd)*[^c]*')

    def test_alternate_response(self):
        input_symbols = ['a', 'b', 'c', 'd']
        self.assertEqual(alternate_response(input_symbols, 'a', 'b'), '[^a]*((a[^ab]*b[^a]*)+)?')
        self.assertEqual(alternate_response(input_symbols, 'c', 'd'), '[^c]*((c[^cd]*d[^c]*)+)?')

    def test_chain_response(self):
        input_symbols = ['a', 'b', 'c', 'd']
        self.assertEqual(chain_response(input_symbols, 'a', 'b'), '[^a]*((ab[^a]*)+)?')
        self.assertEqual(chain_response(input_symbols, 'c', 'd'), '[^c]*((cd[^c]*)+)?')

    def test_succession(self):
        input_symbols = ['a', 'b', 'c', 'd']
        self.assertEqual(succession(input_symbols, 'a', 'b'), '[^a]*(a[^b]*b[^a]*)*')
        self.assertEqual(succession(input_symbols, 'c', 'd'), '[^c]*(c[^d]*d[^c]*)*')

    def test_alternate_succession(self):
        input_symbols = ['a', 'b', 'c', 'd']
        self.assertEqual(alternate_succession(input_symbols, 'a', 'b'), '[^ab]*(a([^ab])*b)*([^ab])*')
        self.assertEqual(alternate_succession(input_symbols, 'c', 'd'), '[^cd]*(c([^cd])*d)*([^cd])*')

    def test_chain_succession(self):
        input_symbols = ['a', 'b', 'c', 'd']
        self.assertEqual(chain_succession(input_symbols, 'a', 'b'), '[^a]*(ab[^ab]*)*')
        self.assertEqual(chain_succession(input_symbols, 'c', 'd'), '[^c]*(cd[^cd]*)*')

    def test_not_coexistence(self):
        input_symbols = ['a', 'b', 'c', 'd']
        self.assertEqual(not_coexistence(input_symbols, 'a', 'b'), '[^ab]*(a[^b]*|b[^a]*)?')
        self.assertEqual(not_coexistence(input_symbols, 'c', 'd'), '[^cd]*(c[^d]*|d[^c]*)?')

    def test_not_succession(self):
        input_symbols = ['a', 'b', 'c', 'd']
        self.assertEqual(not_succession(input_symbols, 'a', 'b'), '[^a]*a[^b]*')
        self.assertEqual(not_succession(input_symbols, 'c', 'd'), '[^c]*c[^d]*')

    def test_not_chain_succession(self):
        input_symbols = ['a', 'b', 'c', 'd']
        self.assertEqual(not_chain_succession(input_symbols, 'a', 'b'), '[^a]*(a+[^ab][^a]*)*(a+)?')
        self.assertEqual(not_chain_succession(input_symbols, 'c', 'd'), '[^c]*(c+[^cd][^c]*)*(c+)?')


if __name__ == '__main__':
    unittest.main()
