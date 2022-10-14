
def FindDivEnd(html : str, startPos = 0):
    html = html[startPos:]
    tempStr = html
    nextStart = 0
    nextEnd = 1
    cutoff = 0

    while nextEnd > nextStart and nextStart != -1:
        nextStart = tempStr.find("<div ")
        nextEnd = tempStr.find("</div>")

        tempStr = html[cutoff + nextEnd + 5:]
        cutoff += nextEnd + 5

    return cutoff+1+startPos
