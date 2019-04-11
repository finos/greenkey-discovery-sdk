import argparse
import requests
import json


parser = argparse.ArgumentParser(description="Retrieve chats from Slack via Chat_Slack, Post to Discovery, and evaluate custom-trained Discovery model by comparing expected and observed intents")
parser.add_argument('--chat-slack-port', default=8005, help='Port that Chat_Slack is listening for requests')
parser.add_argument('--discovery-port', default=8006, help='Port that Discovery is listening on')
parser.add_argument('--gk-api-url', required=True, default='http://scribeapi.com', help='API url to access GK services; authentication')
parser.add_argument('--gk-username', required=True, help='username for scribe api')
parser.add_argument('--gk-secretkey', required=True, help="secret key that goes with gk_username")

# TODO - create group for chat_slack microservice
#TODO add 
# slack_api_url
# slack_secretkey
# slack_channel_name or slack_channel_id
# ??
parser.add_argument('--channel_name', default='ageojo_test', help='Name of channel to get chats from')
#TODO add channel_id for Slack Channel #ageojo_test
parser.add_argument('--channel_id', default=' ', help='Unique ID of channel to get chats from')
parser.add_argument('--channels_file', help='File containing mapping between channels and their ids + metadata')
parser.add_argument('--count', default=100, help='Number of messages to fetch in a single API call')
parser.add_argument('--pages', default=1, type=int, help='Number of pages of chats to get')
parser.add_argument('--latest', default=None, help='Timestamp of most recent message') #TODO -> can this be datetime.now().timestamp()
parser.add_argument('--fetch-all', default=True, type=bool, help='Whether to retrieve all chat messages from Slack')

parser.add_argument('--num-retries', default=3, type=int, help="Number of times to try to send request (if failed)")
parser.add_argument('--sleep', default=2, type=int, help="Numver if seconds to wait before making another request")


# TODO  should update this so it is in the appropriate order, taking into consideration the failed_posts files
parser.add_argument('--test-file', default='tests.txt', help='Path to tests.txt file corresponding to Test Data')
# parser.add_argument('--failed_posts', defalut=None, type=list, help='List of paths to files containing transcripts that failed to be posted')

#TODO add relevant Discovery parameters
parser.add_argument('--num-intents', default=2, type=int, help="Number of intents that data can be classified as instance")


args = parser.parse_args()


###########################################################################################


def bucket(some_list, n):
  pass



def dump_json(data, infile):
  return json.dump(data, open(infile, 'w+'))
  
  
def load_json(infile):
  return json.load(open(infile, 'r+'))


###########################################################################################  



def load_tests():
  test_data = Path(args.test_file).read_text().splitlines() 
  
  tests = bucket(
  [
    line.strip().split(":") #[1].strip()  ??
    for line in test_data
    if line.strip() and line.split(":")[0].strip() in ['test', 'transcript', 'intent']
  ], 3)
  return dict(tests)
  
  
def load_failed_posts(total_tests):
  """
  total_tests: int, total number of tests in tests.txt
  :return: Tuple(Dict[int:str], Dict[int:str])
    keys are digits that correspond to the test number in tests.txt
    values are str; the transcript at that test_no     -> tests.txt[test_no]['transcript'] == out_dict[test_no]
  """
  failed_posts = load_json(infile=args.failed_post)  
  failed_keys_sorted= sorted([int(key) for key in failed_posts])
  
  success_, failed_ = [], []

  for test_no in range(total_tests):
    transcript = failed_posts[test_no]
    
    if test_no not in failed_keys_sorted:
      success_[test_no] = transcript
    else:
      failed_[test_no] = transcript      # failed_.append(test_no)
  
  return success_, failed_   #return List[Dict[{int:str-transcript}]], failed_posts
  

def filter_tests(tests, part_tests):
  """
  tests: List[Dict]; keys=test, transcript, intent
  part_tests: List[Dict]: keys=test_no, transcript at that test_no
          equivalent to saying part_tests key & transcript related to tests as follows:
                        key = tests['test'].split()[-1].strip()    # key should be a digit; assert key.isdigit() 
                        transcript = tests[test_no]['transcript']
  # transcript = tests[test_no]['test'].split()[-1].strip()  # should be .digit()
  """
  return [
     tests[test_no] 
     for test_no, transcript in part_tests.items()     
     if transcript == tests[test_no]['transcript']    # if the transcripts match for the test number
     and int(test_no) == int(tests[test_no]['test'].split()[-1].strip())      # TODO what if these don't line up??
   ]  


def order_tests():  
  tests = load_tests()
  total_tests = len(tests)
  success_, failed_ = load_failed_posts(total_tests)  
  first, last = filter_tests(tests, part_tests=success_), filter_tests(tests, part_tests=failed_)
  return first + last    # ordered = first+last

###########################################################################################  

  
# POST   

def post(url, data, headers=None):
  if not headers:
    headers = {"Content-Type": "application/json"}
  r = requests.post(url, json=data)
  return r.json()
    

  
###########################################################################################  
class ChatSlackApi:
  cls.slack_api_url = "http://slack.com/api"
  cls.channels_list = "channels.list"
  cls.channels_history = "channels.history"
  cls.post_message = "post.Message"
  channel_name_to_id = json.load(open(args.channels_file, 'r+'))
  # channel_dict = post(urllib.urljoin(cls.slack_api_url, 'channels.list'))  

    
###########################################################################################    
class FocusApi:  
  chat_slack_url = "http://localhost:{}/process".format(args.chat_slack_port)
  discovery_url = "http://localhost:{}/process".format(args.discovery_port)
  headers = {"Content-Type": "application/json")
  
  #TODO where to add GK_USERNAME and GK_SECRETKEY and GK_API_URL -> all used at docker run to launch containers
  
  def __init__(self, tests=None, *args, **kwargs):
    self.tests = order_tests().reverse()    # reverse list of tests
    self.tests_ = []    # forward order
    self.chats = []   #TODO initialize list os it is as long as the list of tests
    self.ts = []
    self.transcripts = []
    self.expected = []
    self.observed = []
    self.no_match = []
    self.discovery = []
  
  RETRIES = args.retries
  SLEEP = args.sleep
  FETCH_ALL = fetch_all = args.fetch_all
  before_first_message = BEFORE_FIRST_MESSAGE
  # chat_no should be in reverse order from test_no in tests.txt
  
  
  latest_ts = timestamp = datetime.datetime.now().timestamp()
  while latest_ts > before_first_message:
    fetched_chats = self.fetch_slack_chats(timestamp)     
    chat_segments_to_post, transcripts_to_post, latest_ts = self.batch_process_chats(timestamp=latest_ts, chats=fetched_chats)
    
    if not transcripts_to_post:
      break
      
    # NOW POSt TO DISCOVERY            latest_ts  = most recent timestamp of all chats in fetched_chats/chat_segments_to_post
    # for num, transcript in transcripts_to_post:
          # self.post_to_discovery(transcript)   
    # List[Dict] <- each Dict is an augmented version of the chat_segment that was the input 
    timed_outfile = "discovery_chat_output_{}.json".format(latest_ts)   # NOTE: IMPORTANT THAT THIS IS JSON
    discovery_chat_lattice = self.batch_process_discovery(chat_segments=chat_segments_to_post, outfile=timed_outfile)
    self.discovery.append(discovery_chat_lattice) # KEEP EACH BATCH SEPARATE

  
  
#############################################################################################################  
  def batch_process_chats(self, timestamp, chats):
    chat_segments_to_post, transcripts_to_post = [], []
    
    for chat_no, chat_dict in self.fetch_slack_chats(timestamp):
      message = chat_dict['message']
      timestamp = chat_dict['ts']
    
      try:
        test_dict = self.tests[chat_no]
        if message == test_dict['transcript']:       
      except IndexError:          
        try:
          test_no, test_dict = self.match_search(message)

        except (ValueError, IndexError):
          tup = (chat_no, chat_dict)
          self.no_match.append(tup)
          print(tup)     # TODO LOG
          continue
        
      finally:
        if chat_dict['message'] == test_dict['transcript']:
          # return chat_dict, test_dict          
          # chat_dict, test_dict = self.get_batch_chats(timestamp)
          self.transcripts.append(chat_dict['message'])   # str        
          self.ts.append(chat_dict['ts'])   # timestamp chat was posted
          self.chats.append(chat_dict)  # dict -> entire RESP from post to fetch chat from chat slack
          # FROM tests.txt
          self.expected.append(test['intent'])       # intent
          self.tests.append(test_dict)      # test dict with matching transcript
          chat_segments_to_post.append(chat_dict)
          transcripts_to_post.append(chat_dict['message'])
    return chat_segments_to_post, transcripts_to_post, timestamp
  

    # else:   # This test is out of order - if found; else ??
  def match_search(self, message):
    """
    tests: self.tests -> List[Dict], each a test from tests.txt 
    return: 30tuple
      True (bool), test_no (int), test (dict)
      False      , chat_no      , chat_dict
    """
    found = [    #test['transcript'] 
      (test_no, test)
      for test_no, test in enumerate(self.tests) 
      if test['transcript'] == message
    ]
    return found
   

  
  def get_channel_id(self, args.channel_name):    
    return channel_name_to_id[args.channel_name]
  
  
  def prep_chat_data(self, **kwargs):
    """
    kargs: dict; in addition to args specified above, 
    can include any of the other params for slack api channels.history
    """              
    payload = defaultdict(dict)
    if not args.channel_id:
      channel_id = get_channel_id(args.channel_name)
    payload['channel'] = channel_id
        
    payload['channel_id'] = channel_id
    payload['count'] = args.count  # number of chats to fetch per page (excluded chats may mean this is less)
    if not args.fetch_all:
      payload['pages'] = args.pages
      payload['latest'] = str_to_timestamp(args.latest)

    #TODO FIX THIS
    return payload
  
    
  def fetch_slack_chats(self, timestamp):        
    # TODO where to add SLACK_API_URL and SLACK_ACCESS_TOKEN ??      
    payload = self.prep_chat_data(**kwargs)
    num_retries = 0
    while num_retries <= RETRIES:        
      r = post(cls.chat_slack_url, headers=cls.headers, json=payload)
      if r.status_code in requests.ok_codes:   #TODO FIX
        yield r.json()     # Success
      # if cannot get data, sleep and try again until hit max retries
      time.sleep(SLEEP)
      num_retries += 1
      return self.fetch_slack_chats(timestamp)
    return {}
      
#############################################################################################################    
    def post_to_discovery(self, chat):
      url = cls.discovery_url
      assert isinstance(chat, dict)   # shoudl be a dict with one key 'segments' that takes a List of Dicts
      # here payload sent --> should be output from chat_slack, not just the transcript which is what I have below
      while RETRIES > 0:
        r = post(url, headers=cls.headers, json=chat)   #TODO FIX -> sent entire segments dict from chat_slack not just transcript
        if r.status_code in requests.ok_codes: #TODO check this
          yield r.json()
        time.sleep(SLEEP)
        RETRIES -= 1
        return self.post_to_discovery(chat)
      return {}
      
    
    def batch_process_discovery(self, chat_segments, outfile):
      """
      {"segments" : [{"label": __ ...}. Dict] }
      chat_segments['segments'] -> List[Dict]
        each Dict, chat_segment output from chat_slack
      """
      output_dict = defaultdict(dict)
      for chat_no, chat_segment in enumerate(chat_segments):        
        discovery_lattice = self.post_to_discovery(chat_segment)
        # if discovery_lattice: #and how to validate
        output_dict[chat_no] = discovery_lattice
      outfile = join_path("/custom", outfile)      # os.path.join -> join_path -> make sure saved to custom/ direcotry
      json_dump(output_dict, outfile)
      return output_dict
            
          
          
      
      
        
        
      
    
    
if __name__ == '__main__':
  ordered_tests = order_tests()    # List[Dict] -: keys: test, transcript, intent    
  
  latest = datetime.time.now().timestamp
  
  focus = FocusApi()
  
  focus.fetch_slack_chats()
        


    
  
  
  
 
class ChatSegment:
  cls.channels_dict = json.load(open(args.channels_file, 'r+'))
  
  def __init__(chat_dict, chat_message, formatted=True, test_no=None, expected=None, observed=None):
    # channel_name, channel_id, start_time, end_time,
    # ^ add as attributes
    if formatted:
      self.transcript = unformat_transcript(chat_message)
      self.formatted_transcript = chat_message
    else:
      self.transcript = chat_message
      self.formatted_transcript = format_transcript(chat_message)
    
    self.start_time = chat_dict['ts']
      
    # self.transcript = transcript     # c0hat | expected by segment JSON
    # self.formatted_transcript = chat_message
    
    self.test_no = self.__dict__('test_no', test_no)
    self.__setattr__(self, "expected", expected)
    self.__setattr__(self, "observed", observed)
    
    
  
  
      
      
  




get_chats(url, data, headers=None)