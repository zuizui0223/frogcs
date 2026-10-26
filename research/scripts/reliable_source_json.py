"""Serialized, paced public-source retrieval with successful-response cache."""
import hashlib
import json
import threading
import time
from collections import Counter
from datetime import datetime,timezone
from email.utils import parsedate_to_datetime
from urllib.error import HTTPError,URLError
from urllib.request import Request,urlopen

class ReliableJSON:
    def __init__(self,cache,fetch=None,sleep=time.sleep,interval=1.5,attempts=6):
        self.cache=cache;cache.mkdir(parents=True,exist_ok=True)
        self.fetch=fetch or self._fetch;self.sleep=sleep;self.interval=interval;self.attempts=attempts
        self.lock=threading.Lock();self.audit=Counter();self.failed_requests=0
    @staticmethod
    def _fetch(url):
        req=Request(url,headers={'User-Agent':'frogcs-source-coverage-repair/1.0','Accept':'application/json'})
        with urlopen(req,timeout=40) as r:return json.load(r)
    def get(self,url,timeout=40):
        # Hold through request/backoff: six old workers cannot cause a burst.
        with self.lock:
            p=self.cache/(hashlib.sha256(url.encode()).hexdigest()+'.json')
            if p.exists():
                value=json.loads(p.read_text(encoding='utf8'))
                if not isinstance(value,dict) or 'error' in value:raise ValueError('Invalid cached source')
                self.audit['cache_hits']+=1;return value
            if self.failed_requests>=3:raise RuntimeError('Circuit open after three exhausted source requests')
            for attempt in range(self.attempts):
                self.sleep(self.interval);self.audit['http_attempts']+=1
                try:
                    value=self.fetch(url)
                    if not isinstance(value,dict) or 'error' in value:raise ValueError('Invalid source JSON/error response')
                    p.write_text(json.dumps(value),encoding='utf8');self.audit['successful_requests']+=1
                    self.failed_requests=0
                    return value
                except (HTTPError,URLError,TimeoutError) as exc:
                    retry=isinstance(exc,(URLError,TimeoutError)) and not isinstance(exc,HTTPError)
                    if isinstance(exc,HTTPError):
                        self.audit['http_'+str(exc.code)]+=1
                        retry=exc.code in (429,500,502,503,504)
                    if not retry or attempt==self.attempts-1:
                        self.failed_requests+=1;self.audit['failed_requests']+=1;raise
                    wait=min(40,2**(attempt+1))
                    header=exc.headers.get('Retry-After') if isinstance(exc,HTTPError) and exc.headers else None
                    if header:
                        try:wait=max(wait,float(header))
                        except ValueError:
                            try:wait=max(wait,(parsedate_to_datetime(header)-datetime.now(timezone.utc)).total_seconds())
                            except (TypeError,ValueError):pass
                    self.audit['retries']+=1
                    while wait>60:self.sleep(60);wait-=60
                    self.sleep(wait)
