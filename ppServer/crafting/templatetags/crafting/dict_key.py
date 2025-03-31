from django import template

register = template.Library()

@register.filter
def dict_key(d: dict, key: str):
   '''Returns the given key from a dictionary.'''
   if key in d: return d[key]

   if str(key) in d: return d[str(key)]

   return None

@register.filter
def dict_key_sum_until(d: dict, num: int) -> int:
   '''Accepts dict with numerical keys. Returns the sum of values whose keys are smaller or equal to "num".'''
   return int(sum([d[k] for k in d if int(k) <= num]))