#!/usr/bin/python3

rom = open("hp1.gbc", "rb")

class NotPointerException(ValueError): pass

def readpointer(bank=None):
    if not bank: bank = rom.tell()/0x4000
    s = readshort()
    if 0x4000 > s or 0x8000 <= s:
        raise NotPointerException(s)
    return (bank * 0x4000) + (s - 0x4000)

def readshort():
    return readbyte() + (readbyte() << 8)

def readbyte():
    return ord(rom.read(1))

rom.seek(0x4000*3 + 0x1c1f)
enemies = []
for i in range(61):
    enemy = []
    enemy.append(readbyte())
    enemy.append(readshort())
    enemy.append(readshort())
    for j in range(0x15-5):
        enemy.append(readbyte())
    enemies.append(enemy)


with open("enemies.html", "w") as out:
    out.write("""<!doctype html>
<html><head><meta charset='utf-8'>
<style>
    body {text-align: center;}
    x-enemy {width: 256px; height: 104px; display: inline-block; margin: 8px; text-align: left;
        border: 1px solid #bbb; vertical-align: top;}
    x-pic {display: block; width: 48px; height: 104px;  float: left;
        background-position: -33px -0px; margin: 0; padding: 0;}
    table x-pic {height: 24px; background-position: -33px -48px;}
    table {border-collapse: collapse; margin: auto;}
    td {border: 1px solid #bbb; text-align: right;}
    tr:first-child {font-weight: bold;}
</style>
</head>
<body>
""")
    
    out.write("<h2>Enemy stats</h2>")
    for i, enemy in enumerate(enemies):
        out.write("<x-enemy>")
        out.write("<x-pic style='background-image: url(\"enemies/enemy_{}.png\")'></x-pic>".format(i+2))
        out.write("HP: {}<br>".format(enemy[1]))
        out.write("MP: {}<br>".format(enemy[2]))
        out.write("{}<br>".format(", ".join(str(x) for x in enemy[2:])))
        out.write("</x-enemy>")
    
    out.write("<h2>table</h2>")
    out.write("""<table><tr><td>num</td><td>pic</td><td>hp</td><td>mp</td>
<td>2</td><td>3</td><td>4</td><td>5</td><td>6</td><td>7</td><td>8</td><td>9</td>
<td>10</td><td>11</td><td>12</td><td>13</td><td>14</td><td>15</td><td>16</td><td>17</td></tr>""")
    
    for i, enemy in enumerate(enemies):
        out.write("<tr>")
        out.write("<td>{}</td>".format(i+2))
        out.write("<td><x-pic style='background-image: url(\"enemies/enemy_{}.png\")'></x-pic></td>".format(i+2))
        for val in enemy[1:]:
            out.write("<td>{}</td>".format(val))
        out.write("</tr>")
    out.write("</table>")
    
    out.write("</body></html>")
