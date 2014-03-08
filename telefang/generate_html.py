# this is too large and will freeze Firefox...

import os
import sys
arg = sys.argv[1]
files = []
for f in sorted(os.listdir(arg)):
    # 1967-0x7ed4c8-8bpp.png
    fn = "-".join(f.split('-')[0:2])
    if fn not in files:
        files.append(fn)

print (len(files))

out = """<!doctype html>
<head>
    <meta charset="utf-8">
    <title>Telefang 2 compressed gfx</title>
    <style>
    
    </style>
</head>
<body>
    <h1>Telefang 2 compressed gfx</h1>
    <p>Images are clickable and lead to a version stored on my server, so you can link it to others.
    <table><tr><td>i</td><td>offset</td><td>4bpp</td><td>8bpp</td><td>comment</td></tr>
    
"""

for fname in files:
    i, offset = fname.split('-')
    row = "<tr><td>{}</td><td>{}</td><td><a href='http://sanky.rustedlogic.net/etc/t2gfx/pngs/{}-4bpp.png'><img src='pngs/{}-4bpp.png'></a></td><td><a href='http://sanky.rustedlogic.net/etc/t2gfx/pngs/{}-8bpp.png'><img src='pngs/{}-8bpp.png'></a></td><td><textarea id='g-{}'></textarea></td></tr>\n".format(i, offset, fname, fname, fname, fname, i)
    out += row

out += """
</table>
EOB
</body>
</html>
"""

open('gfx.html', 'w').write(out)
print ("Done")
