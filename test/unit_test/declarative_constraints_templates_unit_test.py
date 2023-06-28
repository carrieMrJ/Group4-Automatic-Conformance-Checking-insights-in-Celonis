import unittest

from src.declarative_constraints.templates import startWith, endWith, never, atMostOnce, atLeastOnce, precedence, \
    alternate_precedence, \
    chain_precedence, responded_existence, response, alternate_response, chain_response, succession, \
    alternate_succession, chain_succession, not_coexistence, not_chain_succession, not_succession


class DeclarativeTestMethods(unittest.TestCase):

    # unit tests for constraint templates
    def test_startWith(self):
        input_symbols = ['a', 'b', 'c', 'd']
        self.assertEqual(startWith(input_symbols, 'a'), 'a(a|b|c|d)*')
        self.assertEqual(startWith(input_symbols, 'c'), 'c(a|b|c|d)*')

    def test_endWith(self):
        input_symbols = ['a', 'b', 'c', 'd']
        self.assertEqual(endWith(input_symbols, 'd'), '(a|b|c|d)*d')
        self.assertEqual(endWith(input_symbols, 'b'), '(a|b|c|d)*b')

    def test_atMostOnce(self):
        input_symbols = ['a', 'b', 'c', 'd']
        self.assertEqual(atMostOnce(input_symbols, 'a'), '(b|c|d)*a?(b|c|d)*')
        self.assertEqual(atMostOnce(input_symbols, 'c'), '(a|b|d)*c?(a|b|d)*')

    def test_atLeastOnce(self):
        input_symbols = ['a', 'b', 'c', 'd']
        self.assertEqual(atLeastOnce(input_symbols, 'a'), '(a|b|c|d)*a(a|b|c|d)*')
        self.assertEqual(atLeastOnce(input_symbols, 'c'), '(a|b|c|d)*c(a|b|c|d)*')

    def test_never(self):
        input_symbols = ['a', 'b', 'c', 'd']
        self.assertEqual(never(input_symbols, 'a'), '(b|c|d)*')
        self.assertEqual(never(input_symbols, 'c'), '(a|b|d)*')

    def test_precedence(self):
        input_symbols = ['a', 'b', 'c', 'd']
        self.assertEqual(precedence(input_symbols, 'a', 'b'), '(c|d)*(a(a|b|c|d)*)?')
        self.assertEqual(precedence(input_symbols, 'c', 'd'), '(a|b)*(c(a|b|c|d)*)?')

    def test_alternate_precedence(self):
        input_symbols = ['a', 'b', 'c', 'd']
        self.assertEqual(alternate_precedence(input_symbols, 'a', 'b'), '(c|d)*((a(a|c|d)*b(c|d)*)|(a(c|d)*))*')
        self.assertEqual(alternate_precedence(input_symbols, 'c', 'd'), '(a|b)*((c(a|b|c)*d(a|b)*)|(c(a|b)*))*')

    def test_chain_precedence(self):
        input_symbols = ['a', 'b', 'c', 'd']
        self.assertEqual(chain_precedence(input_symbols, 'a', 'b'), '(c|d)*((a+b(c|d)*)|(a(c|d)*))*')
        self.assertEqual(chain_precedence(input_symbols, 'c', 'd'), '(a|b)*((c+d(a|b)*)|(c(a|b)*))*')

    def test_responded_existence(self):
        input_symbols = ['a', 'b', 'c', 'd']
        self.assertEqual(responded_existence(input_symbols, 'a', 'b'), '(b|c|d)*(a(a|c|d)*b(a|b|c|d)*)?')
        self.assertEqual(responded_existence(input_symbols, 'c', 'd'), '(a|b|d)*(c(a|b|c)*d(a|b|c|d)*)?')

    def test_response(self):
        input_symbols = ['a', 'b', 'c', 'd']
        self.assertEqual(response(input_symbols, 'a', 'b'), '(c|d)*((b(b|c|d)*)|(a(a|c|d)*b(b|c|d)*))?')
        self.assertEqual(response(input_symbols, 'c', 'd'), '(a|b)*((d(a|b|d)*)|(c(a|b|c)*d(a|b|d)*))?')

    def test_alternate_response(self):
        input_symbols = ['a', 'b', 'c', 'd']
        self.assertEqual(alternate_response(input_symbols, 'a', 'b'), '(b|c|d)*((a(c|d)*b(b|c|d)*)+)?')
        self.assertEqual(alternate_response(input_symbols, 'c', 'd'), '(a|b|d)*((c(a|b)*d(a|b|d)*)+)?')

    def test_chain_response(self):
        input_symbols = ['a', 'b', 'c', 'd']
        self.assertEqual(chain_response(input_symbols, 'a', 'b'), '(b|c|d)*((ab(b|c|d)*)+)?')
        self.assertEqual(chain_response(input_symbols, 'c', 'd'), '(a|b|d)*((cd(a|b|d)*)+)?')

    def test_succession(self):
        input_symbols = ['a', 'b', 'c', 'd']
        self.assertEqual(succession(input_symbols, 'a', 'b'), '(b|c|d)*(a(a|c|d)*b(b|c|d)*)*')
        self.assertEqual(succession(input_symbols, 'c', 'd'), '(a|b|d)*(c(a|b|c)*d(a|b|d)*)*')

    def test_alternate_succession(self):
        input_symbols = ['a', 'b', 'c', 'd']
        self.assertEqual(alternate_succession(input_symbols, 'a', 'b'), '(c|d)*(a(c|d)*b(c|d)*)*')
        self.assertEqual(alternate_succession(input_symbols, 'c', 'd'), '(a|b)*(c(a|b)*d(a|b)*)*')

    def test_chain_succession(self):
        input_symbols = ['a', 'b', 'c', 'd']
        self.assertEqual(chain_succession(input_symbols, 'a', 'b'), '(b|c|d)*(ab(c|d)*)*')
        self.assertEqual(chain_succession(input_symbols, 'c', 'd'), '(a|b|d)*(cd(a|b)*)*')

    def test_not_coexistence(self):
        input_symbols = ['a', 'b', 'c', 'd']
        self.assertEqual(not_coexistence(input_symbols, 'a', 'b'), '(c|d)*(a(a|c|d)*|b(b|c|d)*)?')
        self.assertEqual(not_coexistence(input_symbols, 'c', 'd'), '(a|b)*(c(a|b|c)*|d(a|b|d)*)?')

    def test_not_succession(self):
        input_symbols = ['a', 'b', 'c', 'd']
        self.assertEqual(not_succession(input_symbols, 'a', 'b'), '(b|c|d)*a(a|c|d)*')
        self.assertEqual(not_succession(input_symbols, 'c', 'd'), '(a|b|d)*c(a|b|c)*')

    def test_not_chain_succession(self):
        input_symbols = ['a', 'b', 'c', 'd']
        self.assertEqual(not_chain_succession(input_symbols, 'a', 'b'), '(b|c|d)*(a+(c|d)(b|c|d)*)*(a+)?')
        self.assertEqual(not_chain_succession(input_symbols, 'c', 'd'), '(a|b|d)*(c+(a|b)(a|b|d)*)*(c+)?')


if __name__ == '__main__':
    unittest.main()
