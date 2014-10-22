"""
Examples of Lie Algebras

There are the following examples of Lie algebras:

- All 3-dimensional Lie algebras
- The Lie algebra of affine transformations of the line
- All abelian Lie algebras
- The Lie algebra of upper triangular matrices
- The Lie algebra of strictly upper triangular matrices

AUTHORS:

- Travis Scrimshaw (07-15-2013): Initial implementation
"""
#*****************************************************************************
#  Copyright (C) 2013 Travis Scrimshaw <tscrim at ucdavis.edu>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenses/
#******************************************************************************

#from sage.algebras.lie_algebras.classical_lie_algebra import gl, sl, so, sp
from sage.algebras.lie_algebras.virasoro import VirasoroAlgebra

def three_dimensional(R, a, b, c, d, names=['X', 'Y', 'Z']):
    r"""
    The 3 dimensional Lie algebra generated by `X, Y, Z` defined by
    the relations:

    .. MATH::

        [X, Y] = aZ + dY, \quad [Y, Z] = bX, \quad [Z, X] = cY - dZ

    where `a,b,c,d \in R`.

    EXAMPLES::

        sage: L = lie_algebras.three_dimensional(QQ, 4, 1, -1, 2)
        sage: L.structure_coefficients()
        {[X, Y]: ((Y, 2), (Z, 4)), [X, Z]: ((Y, 1), (Z, 2)), [Y, Z]: ((X, 1),)}
        sage: L = lie_algebras.three_dimensional(QQ, 1, 0, 0, 0)
        sage: L.structure_coefficients()
        {[X, Y]: ((Z, 1),)}
        sage: L = lie_algebras.three_dimensional(QQ, 0, 0, -1, -1)
        sage: L.structure_coefficients()
        {[X, Y]: ((Y, -1),), [X, Z]: ((Y, 1), (Z, -1))}
        sage: L = lie_algebras.three_dimensional(QQ, 0, 1, 0, 0)
        sage: L.structure_coefficients()
        {[Y, Z]: ((X, 1),)}
        sage: lie_algebras.three_dimensional(QQ, 0, 0, 0, 0)
        Abelian Lie algebra on 3 generators (X, Y, Z) over Rational Field
    """
    if isinstance(names, str):
        names = names.split(',')
    X = names[0]
    Y = names[1]
    Z = names[2]
    from sage.algebras.lie_algebras.structure_coefficients import LieAlgebraWithStructureCoefficients
    s_coeff = {(X,Y): {Z:a, Y:d}, (Y,Z): {X:b}, (Z,X): {Y:c, Z:-d}}
    return LieAlgebraWithStructureCoefficients(R, s_coeff, tuple(names))

def cross_product(R, names=['X', 'Y', 'Z']):
    r"""
    The Lie algebra of `\RR^3` defined by `\times` as the usual cross product.

    EXAMPLES::

        sage: L = lie_algebras.cross_product(QQ)
        sage: L.structure_coefficients()
        {[X, Y]: ((Z, 1),), [X, Z]: ((Y, -1),), [Y, Z]: ((X, 1),)}
    """
    L = three_dimensional(R, 1, 1, 1, 0, names)
    L.rename("Lie algebra of RR^3 under cross product over {}".format(R))
    return L

def three_dimensional_by_rank(R, n, a=None, names=['X', 'Y', 'Z']):
    """
    Return the 3-dimensional Lie algebra of rank ``n``.

    INPUT:

    - ``R`` -- the base ring
    - ``n`` -- the rank
    - ``a`` -- the deformation parameter, if 0 then returns the degenerate case
    - ``names`` -- (optional) the generator names

    EXAMPLES::

        sage: lie_algebras.three_dimensional_by_rank(QQ, 0)
        Abelian Lie algebra on 3 generators (X, Y, Z) over Rational Field
        sage: L = lie_algebras.three_dimensional_by_rank(QQ, 1)
        sage: L.structure_coefficients()
        {[Y, Z]: ((X, 1),)}
        sage: L = lie_algebras.three_dimensional_by_rank(QQ, 2, 4)
        sage: L.structure_coefficients()
        {[X, Y]: ((Y, 1),), [X, Z]: ((Y, 1), (Z, 1))}
        sage: L = lie_algebras.three_dimensional_by_rank(QQ, 2, 0)
        sage: L.structure_coefficients()
        {[X, Y]: ((Y, 1),)}
        sage: lie_algebras.three_dimensional_by_rank(QQ, 3)
        Special linear Lie algebra of rank 2 over Rational Field
    """
    if isinstance(names, str):
        names = names.split(',')
    names = tuple(names)

    if n == 0:
        from sage.algebras.lie_algebras.structure_coefficients import AbelianLieAlgebra
        return AbelianLieAlgebra(R, names)

    if n == 1:
        L = three_dimensional(R, 0, 1, 0, 0, names) # Strictly upper triangular matrices
        L.rename("Lie algebra of 3x3 strictly upper triangular matrices over {}".format(R))
        return L

    if n == 2:
        if a is None:
            raise ValueError("The parameter 'a' must be specified")
        X = names[0]
        Y = names[1]
        Z = names[2]
        from sage.algebras.lie_algebras.structure_coefficients import LieAlgebraWithStructureCoefficients
        if a == 0:
            s_coeff = {(X,Y): {Y:R.one()}, (X,Z): {Y:R(a)}}
            L = LieAlgebraWithStructureCoefficients(R, s_coeff, tuple(names))
            L.rename("Degenerate Lie algebra of dimension 3 and rank 2 over {}".format(R))
        else:
            s_coeff = {(X,Y): {Y:R.one()}, (X,Z): {Y:R.one(), Z:R.one()}}
            L = LieAlgebraWithStructureCoefficients(R, s_coeff, tuple(names))
            L.rename("Lie algebra of dimension 3 and rank 2 with parameter {} over {}".format(a, R))
        return L

    if n == 3:
        #return sl(R, 2)
        from sage.algebras.lie_algebras.structure_coefficients import LieAlgebraWithStructureCoefficients
        E = names[0]
        F = names[1]
        H = names[2]
        s_coeff = { (E,F): {H:R.one()}, (H,E): {E:R(2)}, (H,F): {E:R(-2)} }
        L = LieAlgebraWithStructureCoefficients(R, s_coeff, tuple(names))
        L.rename("sl2 over {}".format(R))
        return L

    raise ValueError("Invalid rank")

# This can probably be replaced (removed) by sl once the classical Lie
#   algebras are implemented
def sl(R, n, representation='bracket'):
    r"""
    Return the Lie algebra `\mathfrak{sl}_n`.

    EXAMPLES::

        sage: lie_algebras.sl(QQ, 2)
        sl2 over Rational Field
    """
    if n != 2:
        raise NotImplementedError("only n=2 is implemented")

    if representation == 'matrix':
        from sage.matrix.matrix_space import MatrixSpace
        from sage.algebras.lie_algebras.lie_algebra import LieAlgebraFromAssociative
        MS = MatrixSpace(R, 2)
        E = MS([[0,1],[0,0]])
        F = MS([[0,0],[1,0]])
        H = MS([[1,0],[-1,0]])
        L = LieAlgebraFromAssociative(R, MS, [E, F, H], ['E', 'F', 'H'])
        L.rename("sl2 as a matrix Lie algebra over {}".format(R))
    elif representation == 'bracket':
        L = three_dimensional_by_rank(R, 3)
    else:
        raise ValueError("invalid representation")

    return L

def affine_transformations_line(R, names=['X', 'Y'], representation='bracket'):
    """
    The Lie algebra of affine transformations of the line.

    EXAMPLES::

        sage: L = lie_algebras.affine_transformations_line(QQ)
        sage: L.structure_coefficients()
        {[X, Y]: ((Y, 1),)}
    """
    if isinstance(names, str):
        names = names.split(',')
    names = tuple(names)
    if representation == 'matrix':
        from sage.matrix.matrix_space import MatrixSpace
        MS = MatrixSpace(R, 2, sparse=True)
        one = R.one()
        gens = tuple(MS({(0,i):one}) for i in range(2))
        from sage.algebras.lie_algebras.lie_algebra import LieAlgebraFromAssociative
        return LieAlgebraFromAssociative(R, MS, gens, names)
    X = names[0]
    Y = names[1]
    from sage.algebras.lie_algebras.structure_coefficients import LieAlgebraWithStructureCoefficients
    s_coeff = {(X,Y): {Y:R.one()}}
    L = LieAlgebraWithStructureCoefficients(R, s_coeff, names)
    L.rename("Lie algebra of affine transformations of a line over {}".format(R))
    return L

def abelian(R, names):
    """
    Return the abelian Lie algebra generated by ``names``.

    EXAMPLES::

        sage: lie_algebras.abelian(QQ, 'x, y, z')
        Abelian Lie algebra on 3 generators (x, y, z) over Rational Field
    """
    if isinstance(names, str):
        names = names.split(',')
    from sage.algebras.lie_algebras.structure_coefficients import AbelianLieAlgebra
    return AbelianLieAlgebra(R, tuple(names))

def Heisenberg(R, n, representation="structure"):
    """
    Return the rank ``n`` Heisenberg algebra in the given representation.

    INPUT:

    - ``R`` -- the base ring
    - ``n`` -- the rank
    - ``representation`` -- (default: "structure") can be one of the following:

      - ``"structure"`` -- using structure coefficients
      - ``"matrix"`` -- using matrices

    EXAMPLES::

        sage: lie_algebras.Heisenberg(QQ, 3)
        Heisenberg algebra of rank 3 over Rational Field
    """
    from sage.rings.infinity import infinity
    if n == infinity:
        from sage.algebras.lie_algebras.heisenberg import InfiniteHeisenbergAlgebra
        return InfiniteHeisenbergAlgebra(R)
    if representation == "matrix":
        from sage.algebras.lie_algebras.heisenberg import HeisenbergAlgebra_matrix
        return HeisenbergAlgebra_matrix(R, n)
    from sage.algebras.lie_algebras.heisenberg import HeisenbergAlgebra
    return HeisenbergAlgebra(R, n)

def regular_vector_fields(R):
    r"""
    Return the Lie algebra of regular vector fields of `\CC^{\times}`.

    EXAMPLES::

        sage: lie_algebras.regular_vector_fields(QQ)
        The Lie algebra of regular vector fields over Rational Field
    """
    from sage.algebras.lie_algebras.virasoro import LieAlgebraRegularVectorFields
    return LieAlgebraRegularVectorFields(R)

def upper_triangluar_matrices(R, n):
    r"""
    Return the Lie algebra `\mathfrak{b}_k` of strictly `k \times k` upper
    triangular matrices.

    EXAMPLES::

        sage: lie_algebras.upper_triangluar_matrices(QQ, 4)
        Lie algebra of 4-dimensional upper triangular matrices over Rational Field
    """
    from sage.matrix.matrix_space import MatrixSpace
    from sage.algebras.lie_algebras.lie_algebra import LieAlgebraFromAssociative
    MS = MatrixSpace(R, n, sparse=True)
    one = R.one()
    names = tuple('n{}'.format(i) for i in range(n-1))
    names = tuple('t{}'.format(i) for i in range(n))
    gens = [MS({(i,i+1):one}) for i in range(n-1)]
    gens += [MS({(i,i):one}) for i in range(n)]
    L = LieAlgebraFromAssociative(R, MS, gens, names)
    L.rename("Lie algebra of {}-dimensional upper triangular matrices over {}".format(n, L.base_ring()))
    return L

def strictly_upper_triangular_matrices(R, n):
    r"""
    Return the Lie algebra `\mathfrak{n}_k` of strictly `k \times k` upper
    triangular matrices.

    EXAMPLES::

        sage: lie_algebras.strictly_upper_triangular_matrices(QQ, 4)
        Lie algebra of 4-dimensional strictly upper triangular matrices over Rational Field
    """
    from sage.matrix.matrix_space import MatrixSpace
    from sage.algebras.lie_algebras.lie_algebra import LieAlgebraFromAssociative
    MS = MatrixSpace(R, n, sparse=True)
    one = R.one()
    names = tuple('n{}'.format(i) for i in range(n-1))
    gens = tuple(MS({(i,i+1):one}) for i in range(n-1))
    L = LieAlgebraFromAssociative(R, MS, gens, names)
    L.rename("Lie algebra of {}-dimensional strictly upper triangular matrices over {}".format(n, L.base_ring()))
    return L

