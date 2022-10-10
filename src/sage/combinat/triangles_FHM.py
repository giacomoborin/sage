"""
Combinatorial triangles for posets and fans

This provides several classes and methods to convert between them.
Elements of the classes are polynomials in two variables `x` and `y`,
possibly with other parameters. The conversion methods amount to specific
invertible rational change-of-variables involving `x` and `y`.

The M-triangle class is motivated by the generating series of Möbius numbers
for graded posets. A typical example is::

    sage: W = SymmetricGroup(4)
    sage: posets.NoncrossingPartitions(W).M_triangle()
    x^3*y^3 - 6*x^2*y^3 + 6*x^2*y^2 + 10*x*y^3 - 16*x*y^2 - 5*y^3
    + 6*x*y + 10*y^2 - 6*y + 1

The F-triangle class is motivated by the generating series of pure
simplicial complexes endowed with a distinguished facet. One can also
think about complete fans endowed with a distinguished maximal
cone. A typical example is::

    sage: C = ClusterComplex(['A',3])
    sage: f = C.greedy_facet()
    sage: C.F_triangle(f)
    5*x^3 + 5*x^2*y + 3*x*y^2 + y^3 + 10*x^2 + 8*x*y + 3*y^2 + 6*x + 3*y + 1

The H-triangles are related to the F-triangles by a relationship
similar to the classical link between the f-vector and the h-vector of a
simplicial complex.

The Gamma-triangles are related to the H-triangles by an
analog of the relationship between gamma-vectors and h-vectors of flag
simplicial complexes.
"""
from sage.matrix.constructor import matrix
from sage.rings.integer_ring import ZZ
from sage.rings.polynomial.polynomial_ring import polygen
from sage.rings.polynomial.polynomial_ring_constructor import PolynomialRing
from sage.structure.sage_object import SageObject


def _matrix_display(self, variables=None):
    """
    Return the 2-variables polynomial ``self`` as a matrix for display.

    INPUT:

    - ``variables`` -- optional choice of 2 variables

    OUPUT:

    matrix

    EXAMPLES::

        sage: from sage.combinat.triangles_FHM import _matrix_display
        sage: x, y = PolynomialRing(QQ,['x', 'y']).gens()
        sage: _matrix_display(x**2+x*y+y**3)
        [1 0 0]
        [0 0 0]
        [0 1 0]
        [0 0 1]

    With a specific choice of variables::

        sage: x, y, z = PolynomialRing(QQ,['x','y','z']).gens()
        sage: _matrix_display(x**2+z*x*y+z*y**3+z*x,[y,z])
        [  x   x   0   1]
        [x^2   0   0   0]
        sage: _matrix_display(x**2+z*x*y+z*y**3+z*x,[x,z])
        [  y^3 y + 1     0]
        [    0     0     1]
    """
    support = self.exponents()
    if variables is None:
        ring = self.parent().base_ring()
        x, y = self.parent().gens()
        ix = 0
        iy = 1
    else:
        x, y = variables
        ring = self.parent()
        toutes_vars = x.parent().gens()
        ix = toutes_vars.index(x)
        iy = toutes_vars.index(y)
    minx = min(u[ix] for u in support)
    maxy = max(u[iy] for u in support)
    deltax = max(u[ix] for u in support) - minx + 1
    deltay = maxy - min(u[iy] for u in support) + 1
    mat = matrix(ring, deltay, deltax)
    for u in support:
        ex = u[ix]
        ey = u[iy]
        mat[maxy - ey, ex - minx] = self.coefficient({x: ex, y: ey})
    return mat


class Triangle(SageObject):
    """
    Common class for different kinds of triangles.

    This serves as a base class for F-triangles, H-triangles, M-triangles
    and Gamma-triangles.

    The user should use these subclasses directly.

    The input is a polynomial in two variables. One can also give a
    polynomial with more variables and specify two chosen variables.

    EXAMPLES::

        sage: from sage.combinat.triangles_FHM import Triangle
        sage: x, y = polygens(ZZ, 'x,y')
        sage: ht = Triangle(1+4*x+2*x*y)
        sage: unicode_art(ht)
        ⎛0 2⎞
        ⎝1 4⎠
    """
    def __init__(self, poly, variables=None):
        """
        EXAMPLES::

            sage: from sage.combinat.triangles_FHM import Triangle
            sage: x, y = polygens(ZZ, 'x,y')
            sage: ht = Triangle(1+2*x*y)
            sage: unicode_art(ht)
            ⎛0 2⎞
            ⎝1 0⎠
        """
        if variables is None:
            self._vars = poly.parent().gens()
        else:
            self._vars = variables
        self._poly = poly
        self._n = max(self._poly.degree(v) for v in self._vars)

    def _unicode_art_(self):
        """
        Return the unicode representation (as a matrix).

        EXAMPLES::

            sage: from sage.combinat.triangles_FHM import H_triangle
            sage: x, y = polygens(ZZ, 'x,y')
            sage: ht = H_triangle(1+2*x*y)
            sage: unicode_art(ht)
            ⎛0 2⎞
            ⎝1 0⎠
        """
        return self.matrix()._unicode_art_()

    def _repr_(self) -> str:
        """
        Return the string representation (as a polynomial).

        EXAMPLES::

            sage: from sage.combinat.triangles_FHM import H_triangle
            sage: x, y = polygens(ZZ, 'x,y')
            sage: ht = H_triangle(1+2*x*y)
            sage: ht
            2*x*y + 1
        """
        return repr(self._poly)

    def __eq__(self, other) -> bool:
        """
        Test for equality.

        EXAMPLES::

            sage: from sage.combinat.triangles_FHM import H_triangle
            sage: x, y = polygens(ZZ, 'x,y')
            sage: h1 = H_triangle(1+2*x*y)
            sage: h2 = H_triangle(1+3*x*y)
            sage: h1 == h1
            True
            sage: h1 == h2
            False
        """
        if isinstance(other, Triangle):
            return self._poly == other._poly
        return self._poly == other

    def __ne__(self, other) -> bool:
        """
        Test for unequality.

        EXAMPLES::

            sage: from sage.combinat.triangles_FHM import H_triangle
            sage: x, y = polygens(ZZ, 'x,y')
            sage: h1 = H_triangle(1+2*x*y)
            sage: h2 = H_triangle(1+3*x*y)
            sage: h1 != h1
            False
            sage: h1 != h2
            True
        """
        return not self == other

    def __call__(self, *args):
        """
        Return the evaluation (as a polynomial).

        EXAMPLES::

            sage: from sage.combinat.triangles_FHM import H_triangle
            sage: x, y = polygens(ZZ, 'x,y')
            sage: h = H_triangle(1+3*x*y)
            sage: h(4,5)
            61
        """
        return self._poly(*args)

    def __getitem__(self, *args):
        """
        Return some coefficient.

        EXAMPLES::

            sage: from sage.combinat.triangles_FHM import H_triangle
            sage: x, y = polygens(ZZ, 'x,y')
            sage: h = H_triangle(1+2*x+3*x*y)
            sage: h[1,1]
            3
        """
        return self._poly.__getitem__(*args)

    def __hash__(self):
        """
        Return the hash value.

        EXAMPLES::

            sage: from sage.combinat.triangles_FHM import H_triangle
            sage: x, y = polygens(ZZ, 'x,y')
            sage: h = H_triangle(1+2*x*y)
            sage: g = H_triangle(1+2*x*y)
            sage: hash(h) == hash(g)
            True
        """
        return hash(self._poly)

    def matrix(self):
        """
        Return the associated matrix for display.

        EXAMPLES::

            sage: from sage.combinat.triangles_FHM import H_triangle
            sage: x, y = polygens(ZZ, 'x,y')
            sage: h = H_triangle(1+2*x*y)
            sage: h.matrix()
            [0 2]
            [1 0]
        """
        return _matrix_display(self._poly, variables=self._vars)

    def truncate(self, d):
        """
        Return the truncated triangle.

        INPUT:

        - ``d`` -- integer

        As a polynomial, this means that all monomials with a power
        of either `x` or `y` greater than or equal to ``d`` are dismissed.

        EXAMPLES::

            sage: from sage.combinat.triangles_FHM import H_triangle
            sage: x, y = polygens(ZZ, 'x,y')
            sage: h = H_triangle(1+2*x*y)
            sage: h.truncate(2)
            2*x*y + 1
        """
        p = self._poly
        for v in self._vars:
            p = p.truncate(v, d)
        return self.__class__(p, self._vars)


class M_triangle(Triangle):
    """
    Class for the M-triangles.

    This is motivated by generating series of Möbius numbers of graded posets.

    EXAMPLES::

        sage: x, y = polygens(ZZ, 'x,y')
        sage: P = Poset({2:[1]})
        sage: P.M_triangle()
        x*y - y + 1
    """
    def dual(self):
        """
        Return the dual M-triangle.

        This is the M-triangle of the dual poset, hence an involution.

        When seen as a matrix, this performs a symmetry with respect to the
        northwest-southeast diagonal.

        EXAMPLES::

            sage: from sage.combinat.triangles_FHM import  M_triangle
            sage: x, y = polygens(ZZ, 'x,y')
            sage: mt = M_triangle(x*y - y + 1)
            sage: mt.dual() == mt
            True
        """
        x, y = self._vars
        n = self._n
        A = self._poly.parent()

        dict_dual = {(n - dy, n - dx): coeff
                     for (dx, dy), coeff in self._poly.dict().items()}
        return M_triangle(A(dict_dual), variables=(x, y))

    def transpose(self):
        """
        Return the image of ``self`` by an involution.

        OUTPUT:

        another M-triangle

        The involution is defined by converting to an H-triangle,
        transposing the matrix, and then converting back to an M-triangle.

        EXAMPLES::

            sage: from sage.combinat.triangles_FHM import  M_triangle
            sage: x, y = polygens(ZZ, 'x,y')
            sage: nc3 = x^2*y^2 - 3*x*y^2 + 3*x*y + 2*y^2 - 3*y + 1
            sage: m = M_triangle(nc3)
            sage: m2 = m.transpose(); m2
            2*x^2*y^2 - 3*x*y^2 + 2*x*y + y^2 - 2*y + 1
            sage: m2.transpose() == m
            True
        """
        return self.h().transpose().m()

    def h(self):
        """
        Return the associated H-triangle.

        EXAMPLES::

            sage: from sage.combinat.triangles_FHM import M_triangle
            sage: x, y = polygens(ZZ,'x,y')
            sage: M_triangle(1-y+x*y).h()
            x*y + 1

        TESTS::

            sage: h = polygen(ZZ, 'h')
            sage: x, y = polygens(h.parent(),'x,y')
            sage: mt = x**2*y**2+(-2*h+2)*x*y**2+(2*h-2)*x*y+(2*h-3)*y**2+(-2*h+2)*y+1
            sage: M_triangle(mt, [x,y]).h()
            x^2*y^2 + 2*x*y + (2*h - 4)*x + 1
        """
        x, y = self._vars
        n = self._n
        step = self._poly(x=y / (y - 1), y=(y - 1) * x / (1 + (y - 1) * x))
        step *= (1 + (y - 1) * x)**n
        polyh = step.numerator()
        return H_triangle(polyh, variables=(x, y))

    def f(self):
        """
        Return the associated F-triangle.

        EXAMPLES::

            sage: from sage.combinat.triangles_FHM import M_triangle
            sage: x, y = polygens(ZZ,'x,y')
            sage: M_triangle(1-y+x*y).f()
            x + y + 1

        TESTS::

            sage: h = polygen(ZZ, 'h')
            sage: x, y = polygens(h.parent(),'x,y')
            sage: mt = x**2*y**2+(-2*h+2)*x*y**2+(2*h-2)*x*y+(2*h-3)*y**2+(-2*h+2)*y+1
            sage: M_triangle(mt, [x,y]).f()
            (2*h - 3)*x^2 + 2*x*y + y^2 + (2*h - 2)*x + 2*y + 1
        """
        return self.h().f()


class H_triangle(Triangle):
    """
    Class for the H-triangles.
    """
    def transpose(self):
        """
        Return the transposed H-triangle.

        OUTPUT:

        another H-triangle

        This operation is an involution.  When seen as a matrix, it
        performs a symmetry with respect to the northwest-southeast
        diagonal.

        EXAMPLES::

            sage: from sage.combinat.triangles_FHM import H_triangle
            sage: x, y = polygens(ZZ,'x,y')
            sage: H_triangle(1+x*y).transpose()
            x*y + 1
            sage: H_triangle(x^2*y^2 + 2*x*y + x + 1).transpose()
            x^2*y^2 + x^2*y + 2*x*y + 1
        """
        x, y = self._vars
        n = self._n
        A = self._poly.parent()

        dict_dual = {(n - dy, n - dx): coeff
                     for (dx, dy), coeff in self._poly.dict().items()}
        return H_triangle(A(dict_dual), variables=(x, y))

    def m(self):
        """
        Return the associated M-triangle.

        EXAMPLES::

            sage: from sage.combinat.triangles_FHM import H_triangle
            sage: h = polygen(ZZ, 'h')
            sage: x, y = polygens(h.parent(),'x,y')
            sage: ht = H_triangle(x^2*y^2 + 2*x*y + 2*x*h - 4*x + 1, variables=[x,y])
            sage: ht.m()
            x^2*y^2 + (-2*h + 2)*x*y^2 + (2*h - 2)*x*y + (2*h - 3)*y^2 +
            (-2*h + 2)*y + 1
        """
        x, y = self._vars
        n = self._n
        step = self._poly(x=(x - 1) * y / (1 - y), y=x / (x - 1)) * (1 - y)**n
        polym = step.numerator()
        return M_triangle(polym, variables=(x, y))

    def f(self):
        """
        Return the associated F-triangle.

        EXAMPLES::

            sage: from sage.combinat.triangles_FHM import H_triangle
            sage: x, y = polygens(ZZ,'x,y')
            sage: H_triangle(1+x*y).f()
            x + y + 1
            sage: H_triangle(x^2*y^2 + 2*x*y + x + 1).f()
            2*x^2 + 2*x*y + y^2 + 3*x + 2*y + 1
            sage: flo = H_triangle(1+4*x+2*x**2+x*y*(4+8*x)+
            ....:   x**2*y**2*(6+4*x)+4*(x*y)**3+(x*y)**4).f(); flo
            7*x^4 + 12*x^3*y + 10*x^2*y^2 + 4*x*y^3 + y^4 + 20*x^3 + 28*x^2*y
            + 16*x*y^2 + 4*y^3 + 20*x^2 + 20*x*y + 6*y^2 + 8*x + 4*y + 1
            sage: flo(-1-x,-1-y) == flo
            True

        TESTS::

            sage: x,y,h = polygens(ZZ,'x,y,h')
            sage: ht = x^2*y^2 + 2*x*y + 2*x*h - 4*x + 1
            sage: H_triangle(ht,[x,y]).f()
            2*x^2*h - 3*x^2 + 2*x*y + y^2 + 2*x*h - 2*x + 2*y + 1
        """
        x, y = self._vars
        n = self._n
        step1 = self._poly(x=x / (1 + x), y=y) * (x + 1)**n
        step2 = step1(x=x, y=y / x)
        polyf = step2.numerator()
        return F_triangle(polyf, variables=(x, y))

    def gamma(self):
        """
        Return the associated Gamma-triangle.

        In some cases, this is a more condensed way to encode
        the same amount of information.

        EXAMPLES::

            sage: from sage.combinat.triangles_FHM import H_triangle
            sage: x, y = polygen(ZZ,'x,y')
            sage: ht = x**2*y**2 + 2*x*y + x + 1
            sage: H_triangle(ht).gamma()
            y^2 + x

            sage: W = SymmetricGroup(5)
            sage: P = posets.NoncrossingPartitions(W)
            sage: P.M_triangle().h().gamma()
            y^4 + 3*x*y^2 + 2*x^2 + 2*x*y + x
        """
        x, y = self._vars
        n = self._n
        remain = self._poly
        gamma = x.parent().zero()
        for k in range(n, -1, -1):
            step = remain.coefficient({x: k})
            gamma += x**(n - k) * step
            remain -= x**(n - k) * step.homogenize(x)(x=1 + x, y=1 + x * y)
        return Gamma_triangle(gamma, variables=(x, y))

    def vector(self):
        """
        Return the h-vector as a polynomial in one variable.

        This is obtained by letting `y=1`.

        EXAMPLES::

            sage: from sage.combinat.triangles_FHM import H_triangle
            sage: x, y = polygen(ZZ,'x,y')
            sage: ht = x**2*y**2 + 2*x*y + x + 1
            sage: H_triangle(ht).vector()
            x^2 + 3*x + 1
        """
        anneau = PolynomialRing(ZZ, 'x')
        return anneau(self._poly(y=1))


class F_triangle(Triangle):
    """
    Class for the F-triangles.
    """
    def h(self):
        """
        Return the associated H-triangle.

        EXAMPLES::

            sage: from sage.combinat.triangles_FHM import F_triangle
            sage: x,y = polygens(ZZ,'x,y')
            sage: ft = F_triangle(1+x+y)
            sage: ft.h()
            x*y + 1

        TESTS::

            sage: h = polygen(ZZ, 'h')
            sage: x, y = polygens(h.parent(),'x,y')
            sage: ft = 1+2*y+(2*h-2)*x+y**2+2*x*y+(2*h-3)*x**2
            sage: F_triangle(ft, [x,y]).h()
            x^2*y^2 + 2*x*y + (2*h - 4)*x + 1
        """
        x, y = self._vars
        n = self._n
        step = (1 - x)**n * self._poly(x=x / (1 - x), y=x * y / (1 - x))
        polyh = step.numerator()
        return H_triangle(polyh, variables=(x, y))

    def m(self):
        """
        Return the associated M-triangle.

        EXAMPLES::

            sage: from sage.combinat.triangles_FHM import H_triangle
            sage: x, y = polygens(ZZ,'x,y')
            sage: H_triangle(1+x*y).f()
            x + y + 1
            sage: _.m()
            x*y - y + 1

            sage: H_triangle(x^2*y^2 + 2*x*y + x + 1).f()
            2*x^2 + 2*x*y + y^2 + 3*x + 2*y + 1
            sage: _.m()
            x^2*y^2 - 3*x*y^2 + 3*x*y + 2*y^2 - 3*y + 1

        TESTS::

            sage: p = 1+4*x+2*x**2+x*y*(4+8*x)
            sage: p += x**2*y**2*(6+4*x)+4*(x*y)**3+(x*y)**4
            sage: flo = H_triangle(p).f(); flo
            7*x^4 + 12*x^3*y + 10*x^2*y^2 + 4*x*y^3 + y^4 + 20*x^3
            + 28*x^2*y + 16*x*y^2 + 4*y^3 + 20*x^2 + 20*x*y + 6*y^2
            + 8*x + 4*y + 1
            sage: flo.m()
            x^4*y^4 - 8*x^3*y^4 + 8*x^3*y^3 + 20*x^2*y^4
            - 36*x^2*y^3 - 20*x*y^4
            + 16*x^2*y^2 + 48*x*y^3 + 7*y^4 - 36*x*y^2 - 20*y^3 + 8*x*y
            + 20*y^2 - 8*y + 1

            sage: from sage.combinat.triangles_FHM import F_triangle
            sage: h = polygen(ZZ, 'h')
            sage: x, y = polygens(h.parent(),'x,y')
            sage: ft = F_triangle(1+2*y+(2*h-2)*x+y**2+2*x*y+(2*h-3)*x**2,(x,y))
            sage: ft.m()
            x^2*y^2 + (-2*h + 2)*x*y^2 + (2*h - 2)*x*y + (2*h - 3)*y^2
            + (-2*h + 2)*y + 1
        """
        x, y = self._vars
        n = self._n
        step = self._poly(x=y * (x - 1) / (1 - x * y), y=x * y / (1 - x * y))
        step *= (1 - x * y)**n
        polym = step.numerator()
        return M_triangle(polym, variables=(x, y))

    def vector(self):
        """
        Return the f-vector as a polynomial in one variable.

        This is obtained by letting `y=x`.

        EXAMPLES::

            sage: from sage.combinat.triangles_FHM import F_triangle
            sage: x, y = polygen(ZZ,'x,y')
            sage: ft = 2*x^2 + 2*x*y + y^2 + 3*x + 2*y + 1
            sage: F_triangle(ft).vector()
            5*x^2 + 5*x + 1
        """
        anneau = PolynomialRing(ZZ, 'x')
        x = anneau.gen()
        return anneau(self._poly(y=x))



class Gamma_triangle(Triangle):
    """
    Class for the Gamma-triangles.
    """
    def h(self):
        r"""
        Return the associated H-triangle.

        The transition between Gamma-triangles and H-triangles is defined by

        .. MATH::

            H(x,y) = (1+x)^d \sum_{0\leq i; 0\leq j \leq d-2i} gamma_{i,j}
            (\frac{x}{(1+x)^2})^i (\frac{1+xy}{1+x})^j

        EXAMPLES::

            sage: from sage.combinat.triangles_FHM import Gamma_triangle
            sage: x, y = polygen(ZZ,'x,y')
            sage: g = y**2 + x
            sage: Gamma_triangle(g).h()
            x^2*y^2 + 2*x*y + x + 1

            sage: a, b = polygen(ZZ, 'a, b')
            sage: x, y = polygens(a.parent(),'x,y')
            sage: g = Gamma_triangle(y**3+a*x*y+b*x,(x,y))
            sage: hh = g.h()
            sage: hh.gamma() == g
            True
        """
        x, y = self._vars
        n = self._n
        resu = (1 + x)**n * self._poly(x=x / (1 + x)**2,
                                       y=(1 + x * y) / (1 + x))
        polyh = resu.numerator()
        return H_triangle(polyh, variables=(x, y))

    def vector(self):
        """
        Return the gamma-vector as a polynomial in one variable.

        This is obtained by letting `y=1`.

        EXAMPLES::

            sage: from sage.combinat.triangles_FHM import Gamma_triangle
            sage: x, y = polygen(ZZ,'x,y')
            sage: gt = y**2 + x
            sage: Gamma_triangle(gt).vector()
            x + 1
        """
        anneau = PolynomialRing(ZZ, 'x')
        return anneau(self._poly(y=1))
