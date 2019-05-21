
# Replicate quotes interpreter (80/20) + test_discovery.py to compute metrics
(1) replicating quotes/ interpreter setup (same data/directory structure) except with 80/20 train/test split
(2) modify test_discovery.py so it computes metrics directly


# POST TO GREENKEYTECH SLACK WORKSPACE - channel #ageojo_test
(1) wrote tests.txt file BUT need to send these to slack #ageojo_test cha

- first POST each quote from test_quote_20.txt into slack
- then POST  each not_quote from test_not_quotes_20.txt into slack `#ageojo_test`
- test separately so metrics for both are more easily ascertained


- sanity check: compare with mixed tests.txt (metrics via `test_discovery`) to ensure no difference in output for given input
string


# POST to chat_slack/process 
- payload is request_dict
- 2 keys
- service_type: str, 'slack'
- 'params': dict --> passed to
  Slack().get_chats(param_dict=request_dict['params'])


- output of `get_chats()` --> List[Segment]
    - each Dict is a segment object --> process_json converts to Segment
      objects to JSON; important keys: 'transcript', 'formatted_transcript'
    

--> **Need place to add expected Intent! so more easily compared**git 


# POST to discovery/process
- post unformatted text (same data as in tests.txt
- discovery augments matrix, adding an 'intent' ? <<--- what key???


# Save output
- data from discovery --> save to `custom\`
- also save models/model.bin and intents.train 
