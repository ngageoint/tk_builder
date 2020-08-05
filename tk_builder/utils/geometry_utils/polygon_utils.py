def point_inside_polygon(x, y, poly):
    """
    x and y are float parameters. poly is a list of x/y tuple values that define the polygon's vertices
    Parameters
    ----------
    x : float
    y : float
    poly : [tuple]

    Returns
    -------

    """

    n = len(poly)
    inside = False

    p1x, p1y = poly[0]
    for i in range(n+1):
        p2x, p2y = poly[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                    if p1x == p2x or x <= xinters:
                        inside = True
        p1x, p1y = p2x, p2y
    return inside
