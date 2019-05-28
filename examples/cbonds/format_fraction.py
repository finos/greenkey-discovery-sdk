from nlp.clean_text import clean_fractions


def formatting(entity):
  if len(entity.split('and')) > 1:
    return entity.split('and')[0].strip() + clean_fractions(entity.split('and')[-1]).strip()
  else:
    return entity
  #return entity.upper()
