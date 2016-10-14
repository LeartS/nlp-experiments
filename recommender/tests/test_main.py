import random
import unittest
import unittest.mock as mock

from ..recommender import HashtagRecommender


def fake_zrevrangebyscore(
        key, max_, min_, start=None, num=None, withscores=False, **kwargs):
    multiplier = random.randint(1, 50)
    return [
        ('correlated_{}'.format(random_related), i*multiplier)
        for i, random_related in zip(range(num, 0, -1), random.sample(range(100), num))]


class TestRecommender(unittest.TestCase):

    def setUp(self):
        self.recommender = HashtagRecommender()

    @mock.patch('redis.StrictRedis')
    def test_whole(self, fakeRedis):
        fakeRedisInstance = fakeRedis.return_value
        fakeRedisInstance.zrevrangebyscore.side_effect = fake_zrevrangebyscore
        c = self.recommender.go('@test', [('ciao', 2), ('gente', 5), ('butta', 100)])
        self.assertAlmostEqual(c['vector'].sum(), 107)
        # Dato che fakeredis genera hashtag correlati che non sono mai fra
        # gli hashtag della matrice base, e dato che gli hashtag correlati
        # non sono mai correlati fra di loro ma solo con le nuove kewyords
        # perchè non andiamo a prendere i top hashtag correlati degli hashtag
        # correlati, tutto il peso iniziale dopo 2 passaggi (ed in generale
        # un numero pari di passaggi) può essere redistribuito solo fra le
        # kewyords passate
        self.assertEqual(sorted(h for h, s in c['best'][:3]), ['butta', 'ciao', 'gente'])


if __name__ == '__main__':
    unittest.main()
