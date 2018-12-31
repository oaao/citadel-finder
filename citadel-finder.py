import requests as r
from bs4 import BeautifulSoup as bs


def citadel_filter(cit_input):

    CIT_CASE   = {
                    'citadel' : ['astrahus', 'fortizar', 'keepstar'],
                    'ec'      : ['raitaru', 'azbel', 'sotiyo'],
                    'refinery': ['athanor', 'tatara'],
                    'm'       : ['astrahus', 'raitaru', 'athanor'],
                    'l'       : ['fortizar', 'keepstar', 'azbel', 'sotiyo', 'tatara']
                }

    cits_wanted = []
    filters     = (cit.strip() for cit in cit_input.split(','))

    for item in filters:

        if item in CIT_CASE:
            cits_wanted.extend(CIT_CASE[item])
        elif item in CIT_CASE['m'] + CIT_CASE['l']:
            cits_wanted.append(item)
        elif item == 'all':
            cits_wanted = CIT_CASE['m'] + CIT_CASE['l']
            break

    cit_types = set(cits_wanted)

    return cit_types


def get_config():

    RANGE_URL  = 'http://evemaps.dotlan.net/range/{},5/{}'
    RANGE_CASE = {
                    '6': 'Nyx',
                    '7': 'Archon'
                 }

    system    = input('System name?\n')

    ly_input  = input('6 LY (super, titan) or 7 LY range (carrier, dread)?\n')
    ly_range  = ''.join(s for s in ly_input if s.isdigit())

    cit_input = str(
                    input('Which citadel types are you interested in?\n'
                          '[Separate inputs by commas. '
                          'Supports: "all", specific names, "citadel"/"EC"/"refinery", "M"/"L"]\n')
                ).lower()

    cit_types = citadel_filter(cit_input)

    url_config  = RANGE_URL.format(RANGE_CASE[ly_range], system)

    return system, url_config, cit_types


def retrieve_systems(url):

    page  = r.get(url)
    data  = bs(page.content, 'html.parser')
    hrefs = data.find_all('a', class_='igb')

    systems = list(a['href'].split('/')[-1].upper() for a in hrefs if 'system' in a['href'])

    return systems


def parse_citadel_list(citadels):

    with open(citadels, 'r', encoding='utf-8') as f:

        cits_by_name = list(cit.replace("\n","").split(",", 1) for cit in f.readlines())
        cits_by_sys  = list([cit_name.split(" - ")[0], cit_type, cit_name] for (cit_type, cit_name) in cits_by_name)

        return cits_by_sys


def match_in_range(cit_list):

    system, url_config, cit_types = get_config()
    sys_in_range                  = retrieve_systems(url_config)
    citadels_unsorted             = parse_citadel_list(cit_list)

    citadels = sorted(citadels_unsorted, key=lambda x: x[0])
    sys_in_range.sort()

    cits_in_range = list(cit for cit in citadels if cit[0] in sys_in_range and cit[1].lower() in cit_types)

    print("The following desired citadels are in range of {}:".format(system.upper()))
    for cit in cits_in_range:
        print("{} [{}]: {}".format(cit[0], cit[1], cit[2]))


match_in_range('citadels.txt')
