def printTable(tbl, borderHorizontal="-", borderVertical="|", borderCross="+"):
    cols = [list(x) for x in zip(*tbl)]
    lengths = [max(map(len, map(str, col))) for col in cols]
    
    f = borderVertical + borderVertical.join(" {:>%d} " % l for l in lengths) + borderVertical
    s = borderCross + borderCross.join(borderHorizontal * (l + 2) for l in lengths) + borderCross

    result = s + "\n"
    for row in tbl:
        result += f.format(*row) + "\n"
        result += s + "\n"
    return result
