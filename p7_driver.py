import subprocess
import json
import collections
import random
import sys

CLINGO = ".\\clingo\\clingo.exe"
GRINGO = ".\\clingo\\gringo.exe"
REIFY = ".\\clingo\\reify.exe"

# gringo = subprocess.Popen(['.\\clingo\\gringo.exe level-core.lp level-style.lp level-sim.lp level-shortcuts.lp -c width=7 | .\\clingo\reify.exe | .\\clingo\clingo.exe --outf=2'])
# out, err = gringo.communicate()
# print "end gringo"
# if err:
    # print (err)
print "gringo"
gringo = subprocess.Popen(
    [GRINGO, "level-core.lp", "level-style.lp", "level-sim.lp", "level-shortcuts.lp", "-c width=7"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    shell=True)
out, err = gringo.communicate()
print "end gringo"
if err:
    print (err)

print "reify"
reify = subprocess.Popen(
    [REIFY],
    stdin=gringo.stdout,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    shell=True)
out, err = reify.communicate()
print "end reify"
if err:
    print (err)

print "clingo"
clingo = subprocess.Popen(
    [CLINGO, "--outf=2"],
    stdin=reify.stdout,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    shell=True)
output, err = clingo.communicate()
print "end clingo"
if err:
    print (err)

def parse_json_result(out):
    """Parse the provided JSON text and extract a dict
    representing the predicates described in the first solver result."""

    result = json.loads(out)
    
    assert len(result['Call']) > 0
    assert len(result['Call'][0]['Witnesses']) > 0
    
    witness = result['Call'][0]['Witnesses'][0]['Value']
    
    class identitydefaultdict(collections.defaultdict):
        def __missing__(self, key):
            return key
    
    preds = collections.defaultdict(set)
    env = identitydefaultdict()
    
    for atom in witness:
        if '(' in atom:
            left = atom.index('(')
            functor = atom[:left]
            arg_string = atom[left:]
            try:
                preds[functor].add( eval(arg_string, env) )
            except TypeError:
                pass # at least we tried...
            
        else:
            preds[atom] = True
    
    return dict(preds)


def render_ascii_dungeon(design):
    """Given a dict of predicates, return an ASCII-art depiction of the a dungeon."""
    
    sprite = dict(design['sprite'])
    param = dict(design['param'])
    width = param['width']
    glyph = dict(space='.', wall='W', altar='a', gem='g', trap='_')
    block = ''.join([''.join([glyph[sprite.get((r,c),'space')]+' ' for c in range(width)])+'\n' for r in range(width)])
    return block

render_ascii_dungeon(parse_json_result(output))
