import unittest

from src.declarative_constraints.templates import startWith, endWith, never, atMostOnce, atLeastOnce, precedence, \
    alternate_precedence, \
    chain_precedence, responded_existence, response, alternate_response, chain_response, succession, \
    alternate_succession, chain_succession, not_coexistence, not_chain_succession, not_succession


class DeclarativeTestMethods(unittest.TestCase):

    # unit tests for constraint templates
    def test_startWith(self):
        self.assertEqual(startWith('a'), '^a')
        self.assertEqual(startWith('c'), '^c')

    def test_endWith(self):
        self.assertEqual(endWith('d'), 'd$')
        self.assertEqual(endWith('b'), 'b$')

    def test_atMostOnce(self):
        self.assertEqual(atMostOnce('a'), '^[^a]*a?[^a]*$')
        self.assertEqual(atMostOnce('c'), '^[^c]*c?[^c]*$')

    def test_atLeastOnce(self):
        self.assertEqual(atLeastOnce('a'), '^.*a.*$')
        self.assertEqual(atLeastOnce('c'), '^.*c.*$')

    def test_never(self):
        self.assertEqual(never('a'), '^(?!.*a).*')
        self.assertEqual(never('c'), '^(?!.*c).*')

    def test_precedence(self):
        self.assertEqual(precedence('a', 'b'), '[^b]*a.*b.*')
        self.assertEqual(precedence('c', 'd'), '[^d]*c.*d.*')

    def test_alternate_precedence(self):
        self.assertEqual(alternate_precedence('a', 'b'), '[^b]*(a(?!b)*)*')
        self.assertEqual(alternate_precedence('c', 'd'), '[^d]*(c(?!d)*)*')

    def test_chain_precedence(self):
        self.assertEqual(chain_precedence('a', 'b'), '[^b]*(ab)*[^b]*')
        self.assertEqual(chain_precedence('c', 'd'), '[^d]*(cd)*[^d]*')

    def test_responded_existence(self):
        self.assertEqual(responded_existence('a', 'b'), '[^a]*(a[^b]*b.*)?')
        self.assertEqual(responded_existence('c', 'd'), '[^c]*(c[^d]*d.*)?')

    def test_response(self):
        self.assertEqual(response('a', 'b'), '[^a]*(ab)*[^a]*')
        self.assertEqual(response('c', 'd'), '[^c]*(cd)*[^c]*')

    def test_alternate_response(self):
        self.assertEqual(alternate_response('a', 'b'), '[^a]*((a[^ab]*b[^a]*)+)?')
        self.assertEqual(alternate_response('c', 'd'), '[^c]*((c[^cd]*d[^c]*)+)?')

    def test_chain_response(self):
        self.assertEqual(chain_response('a', 'b'), '[^a]*((ab[^a]*)+)?')
        self.assertEqual(chain_response('c', 'd'), '[^c]*((cd[^c]*)+)?')

    def test_succession(self):
        self.assertEqual(succession('a', 'b'), '[^a]*(a[^b]*b[^a]*)*')
        self.assertEqual(succession('c', 'd'), '[^c]*(c[^d]*d[^c]*)*')

    def test_alternate_succession(self):
        self.assertEqual(alternate_succession('a', 'b'), '[^ab]*(a([^ab])*b)*([^ab])*')
        self.assertEqual(alternate_succession('c', 'd'), '[^cd]*(c([^cd])*d)*([^cd])*')

    def test_chain_succession(self):
        self.assertEqual(chain_succession('a', 'b'), '[^a]*(ab[^ab]*)*')
        self.assertEqual(chain_succession('c', 'd'), '[^c]*(cd[^cd]*)*')

    def test_not_coexistence(self):
        self.assertEqual(not_coexistence('a', 'b'), '[^ab]*(a[^b]*|b[^a]*)?')
        self.assertEqual(not_coexistence('c', 'd'), '[^cd]*(c[^d]*|d[^c]*)?')

    def test_not_succession(self):
        self.assertEqual(not_succession('a', 'b'), '[^a]*a[^b]*')
        self.assertEqual(not_succession('c', 'd'), '[^c]*c[^d]*')

    def test_not_chain_succession(self):
        self.assertEqual(not_chain_succession('a', 'b'), '[^a]*(a+[^ab][^a]*)*(a+)?')
        self.assertEqual(not_chain_succession('c', 'd'), '[^c]*(c+[^cd][^c]*)*(c+)?')


if __name__ == '__main__':
    unittest.main()
