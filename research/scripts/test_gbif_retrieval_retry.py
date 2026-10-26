import json
import tempfile
import unittest
from pathlib import Path
from urllib.error import HTTPError
from reliable_source_json import ReliableJSON

class RetryTests(unittest.TestCase):
    def test_retry_after_and_cache(self):
        calls=[]; sleeps=[]
        def fetch(url):
            calls.append(url)
            if len(calls)==1:raise HTTPError(url,429,'rate',{'Retry-After':'7'},None)
            return {'count':0,'results':[]}
        with tempfile.TemporaryDirectory() as td:
            client=ReliableJSON(Path(td),fetch=fetch,sleep=sleeps.append,interval=0)
            self.assertEqual(client.get('https://example.test/a')['count'],0)
            self.assertEqual(client.get('https://example.test/a')['count'],0)
            self.assertEqual(len(calls),2)
            self.assertIn(7,sleeps)
            self.assertEqual(client.audit['cache_hits'],1)

    def test_error_not_cached_or_silently_zero(self):
        def fetch(url):raise HTTPError(url,429,'rate',{},None)
        with tempfile.TemporaryDirectory() as td:
            client=ReliableJSON(Path(td),fetch=fetch,sleep=lambda t:None,interval=0,attempts=2)
            with self.assertRaises(HTTPError):client.get('https://example.test/b')
            self.assertEqual(list(Path(td).glob('*.json')),[])

    def test_service_error_not_cached(self):
        with tempfile.TemporaryDirectory() as td:
            client=ReliableJSON(Path(td),fetch=lambda u:{'error':{'code':500}},interval=0)
            with self.assertRaises(ValueError):client.get('https://example.test/c')
            self.assertEqual(list(Path(td).glob('*.json')),[])

if __name__=='__main__':unittest.main()
