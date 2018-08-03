'''
This contains the entity definition for the most popular street names in Chicago, Illinois.
Replace these streets with whatever street names you please.
'''
import sys
sys.path.append('../../nlp/')
from cleaning_functions import capitalize

STREET_NAME = {
  'label':
    'STREET_NAME',
  'values':
    (
      'abbott', 'aberdeen', 'academy', 'access', 'ada', 'adams', 'addison', 'administration', 'agatite', 'airport',
      'albany', 'albion', 'aldine', 'alexander', 'algonquin', 'allen', 'allport', 'alta', 'altgeld', 'anchor', 'ancona',
      'anderson', 'anson', 'anthon', 'anthony', 'arbor', 'arcade', 'archer', 'argyle', 'armitage', 'armon', 'armour',
      'armstrong', 'artesian', 'arthington', 'arthur', 'asher', 'ashland', 'astor', 'augusta', 'austin', 'avalon',
      'avers', 'avondale', 'baker', 'balbo', 'baldwin', 'balmoral', 'baltimore', 'banks', 'barber', 'barry', 'bay',
      'beach', 'beacon', 'beaubien', 'belden', 'bell', 'belle', 'bellevue', 'belmont', 'bennett', 'bensley', 'benson',
      'benton', 'berenice', 'bernard', 'berteau', 'berwyn', 'best', 'beverly', 'bingham', 'birchwood', 'bishop',
      'bissell', 'bittersweet', 'black', 'blackhawk', 'blackstone', 'bliss', 'bloomingdale', 'blue', 'blvd', 'bonfield',
      'bosworth', 'boundary', 'bowen', 'bowler', 'bowmanville', 'bp', 'bradley', 'brandon', 'brayton', 'brennan',
      'briar', 'bridge', 'brien', 'broad', 'broadway', 'brodman', 'brompton', 'bross', 'bryn', 'buckingham', 'buena',
      'buffalo', 'burkhardt', 'burley', 'burling', 'burnham', 'burnside', 'burton', 'butler', 'byron', 'cabrini',
      'cahill', 'caldwell', 'calhoun', 'california', 'calumet', 'cambridge', 'campbell', 'campus', 'canal', 'canalport',
      'canfield', 'cannon', 'carmen', 'carondolet', 'carpenter', 'carroll', 'carver', 'casas', 'casteisland',
      'castleisland', 'castlewood', 'catalpa', 'catherine', 'caton', 'center', 'central', 'cermak', 'chalmers',
      'champlain', 'chappel', 'charles', 'charleston', 'chelsea', 'cheltenham', 'cherry', 'chestnut', 'chicago',
      'chicora', 'childrens', 'china', 'christiana', 'church', 'churchill', 'cicero', 'circle', 'cityfront', 'clair',
      'claremont', 'clarence', 'clark', 'cleaver', 'cleveland', 'clifford', 'clifton', 'clinton', 'clover', 'clurg',
      'clybourn', 'clyde', 'coles', 'colfax', 'college', 'columbia', 'columbus', 'commercial', 'commodove', 'commons',
      'commonwealth', 'concord', 'congress', 'conservatory', 'corbett', 'corcoran', 'corliss', 'cornelia', 'cornell',
      'cortez', 'cortland', 'cotta', 'cottage', 'couch', 'coulter', 'court', 'coyle', 'crandon', 'cregier', 'crilly',
      'crosby', 'crosse', 'crowell', 'crystal', 'cul', 'cullerton', 'cumberland', 'cusic', 'cuyler', 'cyril', 'dakin',
      'damen', 'dan', 'daniel', 'dauphin', 'davlin', 'davol', 'dawson', 'dayton', 'de', 'dean', 'dearborn', 'delaware',
      'deming', 'denvir', 'desplaines', 'dewitt', 'dickens', 'dickinson', 'diversey', 'division', 'dobson', 'doctor',
      'dominick', 'dorchester', 'doty', 'douglas', 'dover', 'dowagiac', 'dr', 'drake', 'draper', 'drew', 'drexel',
      'drummond', 'dunbar', 'dwight', 'early', 'eastgate', 'eastlake', 'eberhart', 'edbrooke', 'eddy', 'edens',
      'edgebrook', 'edgewater', 'edmaire', 'edmunds', 'edward', 'eggleston', 'eisenhower', 'elaine', 'elbridge',
      'eleanor', 'elizabeth', 'ellen', 'elliott', 'ellis', 'elmdale', 'elston', 'elsworth', 'emerald', 'emmett', 'end',
      'england', 'englewood', 'erie', 'ernst', 'escanaba', 'esmond', 'essex', 'estes', 'euclid', 'eugenie', 'evans',
      'evelyn', 'everell', 'everett', 'ewing', 'exchange', 'exd', 'fair', 'fairbanks', 'fairfield', 'fairhope',
      'farragut', 'farrar', 'farrell', 'farwell', 'federal', 'felton', 'ferdinand', 'fern', 'field', 'fielding',
      'fillmore', 'financial', 'finsbury', 'fitch', 'fletcher', 'flournoy', 'ford', 'foreman', 'forest', 'forrestville',
      'foster', 'francis', 'francisco', 'franklin', 'freeway', 'front', 'frontenac', 'frontier', 'fry', 'fuller',
      'fullerton', 'fulton', 'gale', 'garfield', 'garland', 'garvey', 'geneva', 'genoa', 'gentile', 'george',
      'germania', 'giddings', 'gilbert', 'givins', 'gladys', 'glen', 'glenlake', 'glenroy', 'glenwood', 'goethe',
      'golf', 'goodman', 'gordon', 'governors', 'grace', 'grady', 'grand', 'granville', 'gratten', 'green', 'greenleaf',
      'greenview', 'greenwood', 'gregory', 'grenshaw', 'grove', 'groveland', 'grover', 'gunnison', 'haddock', 'haddon',
      'hale', 'halsted', 'hamilton', 'hamlet', 'hamlin', 'hampshire', 'hanson', 'harbor', 'harding', 'harlem', 'harper',
      'harrington', 'harrison', 'hart', 'hartland', 'hartwell', 'harvard', 'haskins', 'hastings', 'haussen',
      'hawthorne', 'hayes', 'hayford', 'hayne', 'haynes', 'heath', 'henderson', 'henke', 'henry', 'hermitage',
      'hermosa', 'hiawatha', 'higgins', 'highbridge', 'highland', 'hill', 'hillock', 'hinsdale', 'hirsch', 'hobart',
      'hobbie', 'hobson', 'hoey', 'holbrook', 'holden', 'holland', 'hollett', 'holly', 'hollywood', 'homan', 'homer',
      'homewood', 'honore', 'hood', 'hooker', 'hopkins', 'hortense', 'houston', 'howard', 'howland', 'hoxie', 'hoyne',
      'hoyt', 'hubbard', 'hudson', 'humboldt', 'hunt', 'hurlbut', 'huron', 'hutchinson', 'hyde', 'ibm', 'ibsen', 'ii',
      'illinois', 'imlay', 'independence', 'indian', 'indianapolis', 'ingleside', 'international', 'interstate', 'iowa',
      'irene', 'isham', 'island', 'jackson', 'james', 'janssen', 'jarlath', 'jasper', 'jefferson', 'jeffery', 'jensen',
      'jersey', 'jesse', 'jessie', 'john', 'johns', 'jones', 'joseph', 'jourdan', 'julia', 'julian', 'juneway',
      'junior', 'justine', 'kamerling', 'kanst', 'karlov', 'kasson', 'kearsarge', 'keating', 'kedvale', 'kedzie',
      'keefe', 'keeler', 'keeley', 'keene', 'kelso', 'kemper', 'kenmore', 'kennedy', 'kenneth', 'kennison', 'kenosha',
      'kensington', 'kenton', 'kenwood', 'keokuk', 'keota', 'kerbs', 'kerfoot', 'keystone', 'kilbourn', 'kildare',
      'kilpatrick', 'kimball', 'kimbark', 'kimberly', 'king', 'kingsbury', 'kingston', 'kinzie', 'kinzua', 'kirby',
      'kirkland', 'kirkwood', 'knox', 'kolin', 'kolmar', 'komensky', 'kostner', 'koven', 'kreiter', 'kruger', 'la',
      'lacey', 'lafayette', 'laflin', 'lake', 'lakeside', 'lakeview', 'lakewood', 'lambert', 'lamon', 'landers',
      'langley', 'lansing', 'laporte', 'laramie', 'larchmont', 'larrabee', 'las', 'lasalle', 'latham', 'latrobe',
      'lavergne', 'lawler', 'lawndale', 'lawrence', 'le', 'leader', 'leamington', 'lean', 'leavitt', 'leclaire', 'lee',
      'legett', 'lehigh', 'lehmann', 'leland', 'lemont', 'lenox', 'leod', 'leona', 'leonard', 'leoti', 'leroy',
      'lessing', 'levee', 'lexington', 'liano', 'liberty', 'lieb', 'lightfoot', 'lill', 'lincoln', 'linden', 'linder',
      'linn', 'lipps', 'lister', 'lithuanian', 'lituanica', 'livermore', 'lloyd', 'lock', 'lockwood', 'locust', 'loft',
      'logan', 'loleta', 'london', 'long', 'longwood', 'loomis', 'loop', 'lorel', 'loring', 'loron', 'lothair', 'lotus',
      'louie', 'louis', 'louise', 'lovejoy', 'lowe', 'lowell', 'lower', 'loyola', 'lucerne', 'ludlam', 'luella', 'luis',
      'lumber', 'luna', 'lundy', 'lunt', 'luther', 'lutz', 'lyman', 'lynch', 'lyon', 'lytle', 'macchesneyer',
      'mackinaw', 'madison', 'magnolia', 'major', 'malden', 'malt', 'malta', 'mandell', 'mango', 'manila', 'manistee',
      'mankato', 'mann', 'manor', 'manton', 'maplewood', 'marble', 'marcey', 'margate', 'maria', 'marin', 'marine',
      'marion', 'market', 'markham', 'marmora', 'marquette', 'marshall', 'marshfield', 'mart', 'martin', 'mary',
      'maryland', 'mason', 'massasoit', 'matson', 'maud', 'mautene', 'mawr', 'maxwell', 'may', 'mayfield', 'maypole',
      'mc', 'mcalpin', 'mcclellan', 'mcclurg', 'mccook', 'mccrea', 'mcdowell', 'mcfetridge', 'mclean', 'mcnonough',
      'mcvicker', 'meade', 'medford', 'medill', 'medina', 'melody', 'melrose', 'melvina', 'menard', 'mendota',
      'menomonee', 'merchandise', 'meredith', 'merrill', 'merrimac', 'merrion', 'metron', 'meyer', 'miami', 'michaels',
      'michigan', 'midway', 'mildred', 'millard', 'miller', 'miltimore', 'minnetonka', 'mobile', 'moffat', 'mohawk',
      'monitor', 'monon', 'monroe', 'montana', 'montclare', 'montgomery', 'monticello', 'montrose', 'montvale', 'moody',
      'moorman', 'morgan', 'moselle', 'moyne', 'mozart', 'mulligan', 'multilevel', 'munoz', 'museum', 'music',
      'muskegon', 'myrick', 'myrtle', 'nancy', 'naper', 'naples', 'napoleon', 'narragansett', 'nashotah', 'nashville',
      'nassau', 'natchez', 'natoma', 'navajo', 'neenah', 'nelson', 'neola', 'nettleton', 'neva', 'new', 'newark',
      'newberry', 'newburg', 'newcastle', 'newland', 'newport', 'niagara', 'nickerson', 'nicolet', 'nina', 'nixon',
      'noble', 'nokomis', 'nora', 'nordica', 'normal', 'normandy', 'northcott', 'northeast', 'northwest', 'norwood',
      'nottingham', 'nursery', 'oak', 'oakdale', 'oakenwald', 'oakland', 'oakley', 'oakview', 'oakwood', 'oconto',
      'octavia', 'odell', 'ogallah', 'ogden', 'oglesby', 'ohio', 'oketo', 'olcott', 'old', 'oleander', 'oliphant',
      'olive', 'olmsted', 'olympia', 'onarga', 'oneida', 'ontario', 'orchard', 'orleans', 'osage', 'osceola', 'oshkosh',
      'oswego', 'otis', 'ottawa', 'outer', 'overhill', 'oxford', 'ozark', 'pacific', 'packers', 'page', 'palatine',
      'palmer', 'panama', 'paris', 'park', 'parker', 'parkside', 'parkway', 'parnell', 'passage', 'patterson', 'paul',
      'paulina', 'paxton', 'payne', 'pearson', 'pedestrian', 'penn', 'pensacola', 'peoria', 'perry', 'pershing',
      'peterson', 'phillips', 'pier', 'pierce', 'pine', 'pioneer', 'pippin', 'pitney', 'pittsburgh', 'plaine',
      'plainfield', 'plaisance', 'plaza', 'pleasant', 'point', 'polk', 'pontiac', 'pool', 'pope', 'poplar', 'post',
      'potawatomie', 'potomac', 'prairie', 'prescott', 'preserve', 'prindiville', 'promontory', 'prospect', 'pryor',
      'public', 'pulaski', 'quincy', 'quinn', 'race', 'racine', 'railroad', 'rainey', 'ramp', 'randolph', 'rascher',
      'raven', 'ravenswood', 'recreation', 'redfield', 'reilly', 'reserve', 'reta', 'rhodes', 'rice', 'richard',
      'richards', 'richmond', 'ridge', 'ridgeway', 'ridgewood', 'ritchie', 'river', 'riverside', 'riverview',
      'riverwalk', 'robinson', 'rochdale', 'rockwell', 'rogers', 'roosevelt', 'root', 'roscoe', 'rose', 'rosedale',
      'rosemont', 'ross', 'route', 'ruble', 'rumsey', 'rundell', 'russell', 'rutherford', 'ryan', 'sac', 'sacramento',
      'saginaw', 'saible', 'saint', 'salle', 'sandburg', 'sangamon', 'sawyer', 'sayre', 'schick', 'schiller', 'schmidt',
      'school', 'schorsch', 'schrader', 'schreiber', 'schubert', 'science', 'scott', 'scottsdale', 'sedgwick', 'seeley',
      'seipp', 'sell', 'seminole', 'senour', 'serbian', 'service', 'shakespeare', 'sheffield', 'sheridan', 'sherwin',
      'shields', 'shore', 'sidewalk', 'simonds', 'sioux', 'skyway', 'solidarity', 'somerset', 'southport', 'spaulding',
      'spokane', 'springfield', 'square', 'stark', 'state', 'stave', 'stetson', 'stevenson', 'stewart', 'stockton',
      'stokes', 'stone', 'stony', 'streeter', 'student', 'sub', 'summerdale', 'sunnyside', 'superior', 'surf', 'tahoma',
      'talcott', 'talman', 'tan', 'taylor', 'terra', 'terrace', 'thomas', 'thome', 'thompson', 'thorndale', 'throop',
      'tilden', 'tom', 'tonty', 'torrence', 'tower', 'tract', 'transit', 'tremont', 'troy', 'trumbull', 'union',
      'university', 'urban', 'van', 'vanderpoel', 'vermont', 'vernon', 'veterans', 'vicker', 'victoria', 'view',
      'village', 'vincennes', 'virginia', 'vista', 'vlissingen', 'vough', 'wabansia', 'wabash', 'wacker', 'walden',
      'waldron', 'wallace', 'waller', 'walnut', 'walton', 'warner', 'warren', 'warwick', 'waseca', 'washburne',
      'washington', 'washtenaw', 'water', 'waterloo', 'waterside', 'waterway', 'watkins', 'waukesha', 'waveland',
      'wayman', 'wayne', 'weed', 'wellington', 'wells', 'wendell', 'wentworth', 'wesley', 'western', 'westgate',
      'westshore', 'whalen', 'whipple', 'white', 'wicker', 'wieland', 'wilcox', 'willard', 'willetts', 'wilmot',
      'wilson', 'wilton', 'winchester', 'windsor', 'winnebago', 'winneconna', 'winnemac', 'winona', 'winston',
      'winthrop', 'wisconsin', 'wisner', 'wolcott', 'wolf', 'wolfram', 'wong', 'wood', 'woodard', 'woodland',
      'woodlawn', 'wrightwood', 'yale', 'yates', 'young'
    )
}


# cleaning functions expect to take a 'spacer' as an argument, which is why we list
# them as arguments in the following functions even though we overwrite "spacer" in the function body
def format_ordinal(wordList, spacer):
  """ Add suffix to ordinals to make output more human-readable

  >>> format_ordinal(["one"], '')
  '1st'
  >>> format_ordinal(["five"], '')
  '5th'
  >>> format_ordinal("one five", '')
  '15th'
  >>> format_ordinal("five three", ' ')
  '5th 3rd'
  """
  from cleanText import text2int

  def add_suffix(n):
    return str(n) + 'tsnrhtdd' [n % 5 * (n % 100 ^ 15 > 4 > n % 10)::4]

  wordList = text2int(wordList, spacer)
  if spacer:
    numList = list(map(int, wordList.split(spacer)))
  else:
    numList = int(wordList)

  return spacer.join((add_suffix(_) for _ in numList) if spacer else add_suffix(numList))


STREET_NAME_PATTERN = [[['STREET_NAME', 'NUM_ORD']]]

ENTITY_DEFINITION = {
  'patterns': STREET_NAME_PATTERN,
  'extraTokens': (STREET_NAME,),
  'extraCleaning':
    {
      'STREET_NAME': capitalize,
      'NUM_ORD': format_ordinal,
    },
  'spacing': {
    'NUM_ORD': '',
  }
}

if __name__ == '__main__':
  import sys
  sys.path.append('../')
  from discovery_utils import validate_entity_definition
  validate_entity_definition(ENTITY_DEFINITION)
