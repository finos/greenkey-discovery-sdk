# 4/3/19      (Friday) 

======================================================
- test_discovery.py : modify so some stats beyond accuracy are output even when the majority of one class is incorrect
- using imstrings.txt and security_db.txt  (both from google groups for Jeffries runs) compared:

======================================================
two tests:
    * classifier trained on textclassifier formatted training data
    * test on textclassifier formatted not_quote test data  + runs (formatted - raw data- class=quote)

====================================================== 
 two tests: UNFORMATTED
    * classifier trained on textclassifier unformatted
    * test on textclassifier unformatted not_quote + runs (unformatted via clean_up; class=quote)


#######################################################
# imstring.txt
########################################################


# test data quote: unformatted imstrings.txt
test: part 'imstrings.txt'
(28482 / 28817) tests passed in 364 seconds

Number of failed Tests: 335

(ins)amelie@amu:~/src/gree...vate/examples/quotes$ cat test_metrics.json | jq .
{
  "accuracy_score": 98.8374917583371,
  "quote": {
    "TP": 23492,
    "FN": 87,
    "FP": 248,
    "TN": 4990,
    "precision": 0.9895534962089301,
    "recall": 0.9963102760931337,
    "f1_score": 0.992920391386124
  },
  "not_quote": {
    "TP": 4990,
    "FN": 248,
    "FP": 87,
    "TN": 23492,
    "precision": 0.9828638960015758,
    "recall": 0.9526536846124475,
    "f1_score": 0.9675230247212796


#######################################################
# security_db.txt
#######################################################

test data 'quote': unformatted 'security_db.txt'
---
(5014 / 5632) tests passed in 69 seconds
Number of failed Tests: 618

{
  "accuracy_score": 89.02698863636364,
  "not_quote": {
    "TP": 4992,
    "FN": 246,
    "FP": 372,
    "TN": 22,
    "precision": 0.930648769574944,
    "recall": 0.9530355097365406,
    "f1_score": 0.9417091114883983
  },
  "quote": {
    "TP": 22,
    "FN": 372,1
    "FP": 246,
    "TN": 4992,
    "precision": 0.08208955223880597,
    "recall": 0.05583756345177665,
    "f1_score": 0.06646525679758307
  }
}


# test_file = "unformatted_runs_security_db_round_3_tests.txt


{
  "accuracy_score": 99.7337120539677,
  "quote": {
    "TP": 383,
    "FN": 11,
    "FP": 4,
    "TN": 5235,
    "precision": 0.9896640826873385,
    "recall": 0.9720812182741116,
    "f1_score": 0.9807938540332907
  },
  "not_quote": {
    "TP": 5235,
    "FN": 4,
    "FP": 11,
    "TN": 383,
    "precision": 0.9979031643156691,
    "recall": 0.9992364955144112,
    "f1_score": 0.9985693848354793
  }
}



####################################################



test_file = "formatted_runs_imstrings_tests.txt"



--------------------------

unformatted training textclassifiers
test data: not_quote_10 unformatted (textclassifiers)
   N = 5239
test data: quote -> security_db.txt unformatted, round(3)
   N = 394      #39 (340 b/c 0 start?)
                                                            ---                            
(5618 / 5633) tests passed in 67 seconds
Number of failed Tests: 15     

{
  "accuracy_score": 99.7337120539677,
  
  "not_quote": {
    "TP": 5235,
    "FN": 4,
    "FP": 11,
    "TN": 383,
    "precision": 0.9979031643156691,
    "recall": 0.9992364955144112,
    "f1_score": 0.9985693848354793
  },
  
  "quote": {
    "TP": 383,
    "FN": 11,
    "FP": 4,
    "TN": 5235,
    "precision": 0.9896640826873385,
    "recall": 0.9720812182741116,
    "f1_score": 0.9807938540332907
  }
}



#######################################
# IM Strings 

# test=formatted_runs_imstrings_tests.txt
{
  "accuracy_score": 98.09834472707082,
  "not_quote": {
    "TP": 5014,
    "FN": 224,
    "FP": 324,
    "TN": 23255,
    "precision": 0.9393031097789434,
    "recall": 0.9572355861015654,
    "f1_score": 0.9481845688350983
  },
  "quote": {
    "TP": 23255,
    "FN": 324,
    "FP": 224,
    "TN": 5014,
    "precision": 0.9904595596064568,
    "recall": 0.9862589592433946,
    "f1_score": 0.9883547962089336
  }
}
















======================================================
# RUNS DATA ONLY


393 security_db.txt
======================================================
# Train/Test with specific type of runs

training with runs:
- training with X% of runs
- testing with X% of runs
- testing with same type

conditions:
    train imstrings   
    test imstrings
    
    train security_db
    test security_db

======================================================
Test Genenralization across Run Types:
: train - imstrings.txt
: test - security_db.txt
-
and vice versa
: train - security_db.txt
: test - imstrings.txt

======================================================

# 4/6/19      (Today)






======================================================
# TODO

(1) & (2) 
train textclassifiers 
test textclassifiers
train/test data: formatted & unformatted
better on formatted but really high performance for both

##################################################
(3) 
train testclassifiers - formatted
test imstrings.txt (formatted/raw)
--> very poor performance


(4)
repeat with 'security_db.txt'
--> poor erformancels ex    


##################################################
(5)
train testclassifiers - unformatted
test imstrings.txt -> unformatted version


(6) 
train testclassifiers - unformatted
test security_db.txt - unformatted

##################################################

(7)
train (1/2 textclassifiers | 1/2 runs)
test (1/2 textclassifiers | 1/2 runs)

- imstrings.txt
- _db.txt

- formatted & unformatted version (kee constant for text classifiers and runs)

