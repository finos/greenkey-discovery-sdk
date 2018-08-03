# cleaning functions expect to take a 'spacer' as an argument, which is why we list
# them as arguments in the following functions even though we overwrite "spacer" in the function body
def capitalize(wordList, spacer):
  """ Generally, capitalize all words for discover """

  return spacer.join(word.capitalize() for word in wordList) if isinstance(wordList, list) else wordList.capitalize()
