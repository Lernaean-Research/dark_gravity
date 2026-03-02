#!/usr/bin/env python3
"""
Fix all missing citation keys in manuscript_overleaf.tex
Maps descriptive citation keys to actual keys in references_formatted_complete.bib
"""

import re

# Complete mapping of wrong keys → correct keys
CITATION_MAP = {
    'BullockBoylanKolchin2017SmallScale': 'Bullock2017',
    'UndagoitiaRauch2016DirectDetection': 'Undagoitia2016',
    'McGaughSchombert2014ML': 'McGaugh2014',
    'DeserWoodard2007Nonlocal': 'Deser2007',
    'Rasanen2006Backreaction': 'Rasanen2006',
    'BuniyHsuMurray2006NEC': 'Buniy2006',
    'Buchert2000Averaging': 'Buchert2000',
    'Bardeen1980GaugeInvariant': 'Bardeen1980',
    'Lakatos1978Methodology': 'Lakatos1978',
    'RubinFord1970M31': 'Rubin1970',
    'Bosma1978Thesis': 'Bosma1978',
    'Donoghue1994EFTGR': 'Donoghue1994',
    'Burgess2004EFTGR': 'Burgess2004',
    'Bekenstein2004TeVeS': 'Bekenstein2004',
    'Carroll2004Spacetime': 'Carroll2004',
    'Ackermann2015Dwarfs': 'Ackermann2015',
    'Einstein1915Mercury': 'Einstein1915',
    'Einstein1916GR': 'Einstein1916',
    'Verlinde2017Emergent': 'Verlinde2017',
    'Aprile2018XENON1T': 'Aprile2018',
    'Cui2017PandaX': 'Cui2017',
    'Akerib2017LUX': 'Akerib2017',
    'Rubakov2006NEC': 'Rubakov2006',
    'Rubakov2014NECReview': 'Rubakov2014',
    'Carroll2019Spacetime': 'Carroll2019',
    'LeVerrier1859Mercury': 'LeVerrier1859',
    'Riess2019LMC': 'Riess2019',
    'Ivezic2019LSST': 'Ivezic2019',
    'Aguilar2013AMS': 'Aguilar2013',
    'Kuhn1962Revolutions': 'Kuhn1962',
    'Milgrom1983MOND': 'Milgrom1983',
    'Clowe2006Bullet': 'Clowe2006',
    'Fruscione2006CIAO': 'Fruscione2006',
    'Weisskopf2002Chandra': 'Weisskopf2002',
    'LZ2023FirstResults': 'LUX2023',
    'Planck2018CosmoParams': 'Planck2020',
    'Euclid2022WideSurvey': 'Euclid2022',
    'Euclid2025Overview': 'Euclid2025',
    'MAST2019HFF': 'MAST2019',
    'HEASARC2025Archive': 'HEASARC2025',
    'Zwicky1933Coma': 'Zwicky1933',
}

def fix_citations(filename='manuscript_overleaf.tex'):
    """Replace all wrong citation keys with correct ones"""
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    replacements_made = {}
    
    # Sort by length (longest first) to avoid partial replacements
    for wrong_key in sorted(CITATION_MAP.keys(), key=len, reverse=True):
        correct_key = CITATION_MAP[wrong_key]
        count = content.count(wrong_key)
        if count > 0:
            content = content.replace(wrong_key, correct_key)
            replacements_made[wrong_key] = (correct_key, count)
    
    # Write fixed content
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Report results
    print(f"✅ Fixed {len(replacements_made)} citation keys:\n")
    for wrong, (correct, count) in sorted(replacements_made.items()):
        print(f"  {wrong:45} → {correct:20} ({count} occurrences)")
    
    return len(replacements_made)

if __name__ == '__main__':
    import sys
    import os
    
    os.chdir(r'D:\#Documents\#Publication\Spacetime_Mechanics__git\Intrinsic_Response_Sector_as_Dark_Gravity')
    
    count = fix_citations()
    print(f"\n✅ Total: {count} citation keys fixed")
    sys.exit(0)
