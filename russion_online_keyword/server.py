#-*- coding:utf-8 -*-
import argparse
import thriftpy
from keywords_server import Keywords
from thriftpy.rpc import make_server
from thriftpy.utils import serialize
from datetime import datetime


parser = argparse.ArgumentParser()
parser.add_argument("--port", dest='port', default=6040, help='port of service', type=int)
args = parser.parse_args()

keywords_v2_thrift = thriftpy.load("keywords_v2.thrift", module_name="keywords_v2_thrift")
from keywords_v2_thrift import *

STOP_FILE = './data/ru/stopwords_en.txt'
PUN_FILE = './data/ru/punctuation.txt'
COMMON_WORDS_FILE = './data/ru/common_words_en.txt'
SPECIAL_FILE = './data/ru/special_words_en.txt'

class Dispatcher(object):

  def __init__(self,):
      self.root_predictor = Keywords(PUN_FILE, STOP_FILE, COMMON_WORDS_FILE, SPECIAL_FILE, 'en')

  def find_keywords(self, request):
      """

      :param request:
      :return:
      """
      try:
          start = datetime.now()
          content, title, url, topK = request.news.main_content, request.news.title, request.news.url, request.topK
          full_result,title_reuslt = self.root_predictor.top_keywords_news(title, content, topK)
          full_keywords = [Keyword(w[0], w[1], w[2]) for w in full_result]
          title_keywords = [Keyword(w[0],w[1],w[2]) for w in title_reuslt]

          keyword_result = KeywordResult(full_keywords, title_keywords, [], [])
          duration = datetime.now() - start
          print "find similar keywords total duration:", duration.total_seconds(), "nid:", request.news.nid
          return keyword_result
      except Exception as Inst:
          print datetime.now(), "failed to find similar keywords", request.news.nid
          print "error is:", Inst
          return KeywordResult([], [], [], [])
def main():
    server = make_server(keywords_v2_thrift.Keywords_v2, Dispatcher(),
                         '0.0.0.0', args.port)
    server.trans.client_timeout = None
    server.serve()


if __name__ == '__main__':
    main()