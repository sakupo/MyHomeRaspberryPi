# coding: utf-8
vowel = ['a', 'i', 'u', 'e', 'o']
kana_table = {'a' : 'あ',  'i': 'い',  'u': 'う',  'e': 'え',  'o': 'お', \
              'ka': 'か', 'ki': 'き', 'ku': 'く', 'ke': 'け', 'ko': 'こ', \
              'sa': 'さ', 'si': 'し', 'su': 'す', 'se': 'せ', 'so': 'そ', \
              'ta': 'た', 'ti': 'ち', 'tu': 'つ', 'te': 'て', 'to': 'と', \
              'na': 'な', 'ni': 'に', 'nu': 'ぬ', 'ne': 'ね', 'no': 'の', \
              'ha': 'は', 'hi': 'ひ', 'hu': 'ふ', 'he': 'へ', 'ho': 'ほ', \
              'ma': 'ま', 'mi': 'み', 'mu': 'む', 'me': 'め', 'mo': 'も', \
              'ya': 'や', 'yi': 'い', 'yu': 'ゆ', 'ye': 'え', 'yo': 'よ', \
              'ra': 'ら', 'ri': 'り', 'ru': 'る', 're': 'れ', 'ro': 'ろ', \
              'wa': 'わ', 'wi': 'ゐ', 'wu': 'う', 'we': 'ゑ', 'wo': 'を', \
              'nn': 'ん' \
             }
consonant = ['k', 's', 't', 'n', 'h', 'm', 'y', 'r', 'w']

def find(l, x, default=-1):
  if x in l:
    return l.index(x)
  else:
    return default

def romajiToKana(romaji: str):
  kana = ""
  tmp_kana = ""
  for char in romaji:
    tmp_kana += char
    vowel_index = find(vowel, char)
    if vowel_index != -1 or tmp_kana == "nn":
      kana += kana_table[tmp_kana]
      tmp_kana = ""
    else:
      consonant_index = find(consonant, char)
      if consonant_index == -1:
        return kana
  return kana
