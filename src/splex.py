import re

def splex(split):
  return list(map(lambda x: float(x), split[2:-1].split(',')))

def parse(output, keymap={}):
  result = {}
  output = output[1:-1]
  output = output.split(' ')
  for split in output:
    if re.search("^\w\[", split) and split.endswith(']'):
      if split[0] in keymap:
        result[keymap[split[0]]] = splex(split)

  return result

if __name__ == "__main__":
  keymap = {
    's': 'soil',
    't': 'temp',
    'h': 'humid'
  }
  data = "#s[123,1023,514,123] t[514.12] h[123.321,6841.1]#"
  print(parse(data, keymap))