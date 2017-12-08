# cython: old_style_globals=True
r"""
Base class for objects of a category

CLASS HIERARCHY:

- :class:`~sage.structure.sage_object.SageObject`

  - **CategoryObject**

    - :class:`~sage.structure.parent.Parent`

Many category objects in Sage are equipped with generators, which are
usually special elements of the object.  For example, the polynomial ring
`\ZZ[x,y,z]` is generated by `x`, `y`, and `z`.  In Sage the ``i`` th
generator of an object ``X`` is obtained using the notation
``X.gen(i)``.  From the Sage interactive prompt, the shorthand
notation ``X.i`` is also allowed.

The following examples illustrate these functions in the context of
multivariate polynomial rings and free modules.

EXAMPLES::

    sage: R = PolynomialRing(ZZ, 3, 'x')
    sage: R.ngens()
    3
    sage: R.gen(0)
    x0
    sage: R.gens()
    (x0, x1, x2)
    sage: R.variable_names()
    ('x0', 'x1', 'x2')

This example illustrates generators for a free module over `\ZZ`.

::

    sage: M = FreeModule(ZZ, 4)
    sage: M
    Ambient free module of rank 4 over the principal ideal domain Integer Ring
    sage: M.ngens()
    4
    sage: M.gen(0)
    (1, 0, 0, 0)
    sage: M.gens()
    ((1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1))
"""

#*****************************************************************************
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#                  http://www.gnu.org/licenses/
#*****************************************************************************

from __future__ import absolute_import, division, print_function

from sage.cpython.getattr import dir_with_other_class
from sage.cpython.getattr cimport getattr_from_other_class
from sage.categories.category import Category
from sage.structure.debug_options cimport debug
from sage.misc.cachefunc import cached_method
from sage.structure.dynamic_class import DynamicMetaclass


def guess_category(obj):
    from sage.misc.superseded import deprecation
    deprecation(24109, f"guess_category() is deprecated: CategoryObject of type {type(obj)} requires a category")

    # this should be obsolete if things declare their categories
    try:
        if obj.is_field():
            from sage.categories.all import Fields
            return Fields()
    except (AttributeError, NotImplementedError):
        pass
    try:
        if obj.is_ring():
            from sage.categories.all import CommutativeAlgebras, Algebras, CommutativeRings, Rings
            if obj.is_commutative():
                if obj._base is not obj:
                    return CommutativeAlgebras(obj._base)
                else:
                    return CommutativeRings()
            else:
                if obj._base is not obj:
                    return Algebras(obj._base)
                else:
                    return Rings()
    except Exception:
        pass
    from sage.structure.parent import Parent
    #if isinstance(obj, Parent):
    #    import sys
    #    sys.stderr.write("bla: %s"%obj)
    #    from sage.categories.all import Sets
    #    return Sets()
    return None # don't want to risk importing stuff...

cpdef inline check_default_category(default_category, category):
    ## The resulting category is guaranteed to be
    ## a sub-category of the default.
    if category is None:
        return default_category
    return default_category.join([default_category,category])

cdef class CategoryObject(SageObject):
    """
    An object in some category.
    """
    def __init__(self, category = None, base = None):
        """
        Initializes an object in a category

        INPUT:

        - ``category`` - The category this object belongs to. If this object
          belongs to multiple categories, those can be passed as a tuple
        - ``base`` - If this object has another object that should be
          considered a base in its primary category, you can include that base
          here.

        EXAMPLES::

            sage: from sage.structure.category_object import CategoryObject
            sage: A = CategoryObject()
            sage: A.category()
            Category of objects
            sage: A.base()

            sage: A = CategoryObject(category = Rings(), base = QQ)
            sage: A.category()
            Category of rings
            sage: A.base()
            Rational Field

            sage: A = CategoryObject(category = (Semigroups(), CommutativeAdditiveSemigroups()))
            sage: A.category()
            Join of Category of semigroups and Category of commutative additive semigroups

        FIXME: the base and generators attributes have nothing to do with categories, do they?
        """
        if base is not None:
            self._base = base
        if category is not None:
            self._init_category_(category)

    def __cinit__(self):
        self.__cached_methods = {}
        self._hash_value = -1

    def _init_category_(self, category):
        """
        Sets the category or categories of this object.

        INPUT:

        - ``category`` -- a category, or list or tuple thereof, or ``None``

        EXAMPLES::

            sage: A = sage.structure.category_object.CategoryObject()
            sage: A._init_category_(Rings())
            sage: A.category()
            Category of rings
            sage: A._init_category_((Semigroups(), CommutativeAdditiveSemigroups()))
            sage: A.category()
            Join of Category of semigroups and Category of commutative additive semigroups
            sage: P = Parent(category=None)
            sage: P.category()
            Category of sets

        TESTS::

            sage: A = sage.structure.category_object.CategoryObject()
            sage: A._init_category_(None)
            doctest:...: DeprecationWarning: guess_category() is deprecated: CategoryObject of type <type 'sage.structure.category_object.CategoryObject'> requires a category
            See http://trac.sagemath.org/24109 for details.
            sage: A.category()
            Category of objects
        """
        if category is None:
            # Deprecated in Trac #24109
            category = guess_category(self)
        if isinstance(category, (list, tuple)):
            category = Category.join(category)
        self._category = category

    def _refine_category_(self, category):
        """
        Changes the category of ``self`` into a subcategory.

        INPUT:

        - ``category`` -- a category or list or tuple thereof

        The new category is obtained by adjoining ``category`` to the
        current one.

        .. SEEALSO:: :function:`Category.join`

        EXAMPLES::

            sage: P = Parent()
            sage: P.category()
            Category of sets
            sage: P._refine_category_(Magmas())
            sage: P.category()
            Category of magmas
            sage: P._refine_category_(Magmas())
            sage: P.category()
            Category of magmas
            sage: P._refine_category_(EnumeratedSets())
            sage: P.category()
            Category of enumerated magmas
            sage: P._refine_category_([Semigroups(), CommutativeAdditiveSemigroups()])
            sage: P.category()
            Join of Category of semigroups and Category of commutative additive semigroups and Category of enumerated sets
            sage: P._refine_category_((CommutativeAdditiveMonoids(), Monoids()))
            sage: P.category()
            Join of Category of monoids and Category of commutative additive monoids and Category of enumerated sets
        """
        if self._category is None:
            self._init_category_(category)
            return
        if not (type(category) == tuple or type(category) == list):
            category = [category]
        self._category = self._category.join([self._category]+list(category))

    def _is_category_initialized(self):
        return self._category is not None

    def category(self):
        if self._category is None:
            # COERCE TODO: we shouldn't need this
            from sage.categories.objects import Objects
            self._category = Objects()
        return self._category

    def categories(self):
        """
        Return the categories of ``self``.

        EXAMPLES::

            sage: ZZ.categories()
            [Join of Category of euclidean domains
                 and Category of infinite enumerated sets
                 and Category of metric spaces,
             Category of euclidean domains,
             Category of principal ideal domains,
             Category of unique factorization domains,
             Category of gcd domains,
             Category of integral domains,
             Category of domains,
             Category of commutative rings, ...
             Category of monoids, ...,
             Category of commutative additive groups, ...,
             Category of sets, ...,
             Category of objects]
        """
        return self.category().all_super_categories()

    def _underlying_class(self):
        r"""
        Return the underlying class (class without the attached
        categories) of the given object.

        OUTPUT: A class

        EXAMPLES::

            sage: type(QQ)
            <class 'sage.rings.rational_field.RationalField_with_category'>
            sage: QQ._underlying_class()
            <class 'sage.rings.rational_field.RationalField'>
            sage: type(ZZ)
            <type 'sage.rings.integer_ring.IntegerRing_class'>
            sage: ZZ._underlying_class()
            <type 'sage.rings.integer_ring.IntegerRing_class'>
        """
        cls = type(self)
        if isinstance(cls, DynamicMetaclass):
            return cls.__bases__[0]
        else:
            return cls

    ##############################################################################
    # Generators
    ##############################################################################

    def gens_dict(self):
        r"""
        Return a dictionary whose entries are ``{name:variable,...}``,
        where ``name`` stands for the variable names of this
        object (as strings) and ``variable`` stands for the
        corresponding defining generators (as elements of this object).

        EXAMPLES::

            sage: B.<a,b,c,d> = BooleanPolynomialRing()
            sage: B.gens_dict()
            {'a': a, 'b': b, 'c': c, 'd': d}
        """
        cdef dict v = {}
        for x in self._defining_names():
            v[str(x)] = x
        return v

    def gens_dict_recursive(self):
        r"""
        Return the dictionary of generators of ``self`` and its base rings.

        OUTPUT:

        - a dictionary with string names of generators as keys and
          generators of ``self`` and its base rings as values.

        EXAMPLES::

            sage: R = QQ['x,y']['z,w']
            sage: sorted(R.gens_dict_recursive().items())
            [('w', w), ('x', x), ('y', y), ('z', z)]
        """
        B = self.base_ring()
        if B is self:
            return {}
        GDR = B.gens_dict_recursive()
        GDR.update(self.gens_dict())
        return GDR

    def objgens(self):
        """
        Return the tuple ``(self, self.gens())``.

        EXAMPLES::

            sage: R = PolynomialRing(QQ, 3, 'x'); R
            Multivariate Polynomial Ring in x0, x1, x2 over Rational Field
            sage: R.objgens()
            (Multivariate Polynomial Ring in x0, x1, x2 over Rational Field, (x0, x1, x2))
        """
        return self, self.gens()

    def objgen(self):
        """
        Return the tuple ``(self, self.gen())``.

        EXAMPLES::

            sage: R, x = PolynomialRing(QQ,'x').objgen()
            sage: R
            Univariate Polynomial Ring in x over Rational Field
            sage: x
            x
        """
        return self, self.gen()

    def _first_ngens(self, n):
        """
        Used by the preparser for ``R.<x> = ...``.

        EXAMPLES::

            sage: R.<x> = PolynomialRing(QQ)
            sage: x
            x
            sage: parent(x)
            Univariate Polynomial Ring in x over Rational Field

        For orders, we correctly use the ring generator, see
        :trac:`15348`::

            sage: A.<i> = ZZ.extension(x^2 + 1)
            sage: i
            i
            sage: parent(i)
            Order in Number Field in i with defining polynomial x^2 + 1

        ::

            sage: B.<z> = EquationOrder(x^2 + 3)
            sage: z.minpoly()
            x^2 + 3
        """
        return self._defining_names()[:n]

    @cached_method
    def _defining_names(self):
        """
        The elements used to "define" this object.

        What this means depends on the type of object: for rings, it
        usually means generators as a ring. The result of this function
        is not required to generate the object, but it should contain
        all named elements if the object was constructed using a
        ``names'' argument.

        This function is used by the preparser to implement
        ``R.<x> = ...`` and it is also used by :meth:`gens_dict`.

        EXAMPLES::

            sage: R.<x> = PolynomialRing(QQ)
            sage: R._defining_names()
            (x,)

        For orders, we correctly use the ring generator, see
        :trac:`15348`::

            sage: B.<z> = EquationOrder(x^2 + 3)
            sage: B._defining_names()
            (z,)

        For vector spaces and free modules, we get a basis (which can
        be different from the given generators)::

            sage: V = ZZ^3
            sage: V._defining_names()
            ((1, 0, 0), (0, 1, 0), (0, 0, 1))
            sage: W = V.span([(0, 1, 0), (1/2, 1, 0)])
            sage: W._defining_names()
            ((1/2, 0, 0), (0, 1, 0))
        """
        return self.gens()

    #################################################################################################
    # Names and Printers
    #################################################################################################

    def _assign_names(self, names=None, normalize=True, ngens=None):
        """
        Set the names of the generator of this object.

        This can only be done once because objects with generators
        are immutable, and is typically done during creation of the object.


        EXAMPLES:
        When we create this polynomial ring, self._assign_names is called by the constructor::

            sage: R = QQ['x,y,abc']; R
            Multivariate Polynomial Ring in x, y, abc over Rational Field
            sage: R.2
            abc

        We can't rename the variables::

            sage: R._assign_names(['a','b','c'])
            Traceback (most recent call last):
            ...
            ValueError: variable names cannot be changed after object creation.
        """
        # this will eventually all be handled by the printer
        if names is None: return
        if normalize:
            if ngens is None:
                ngens = -1  # unknown
            names = normalize_names(ngens, names)
        if self._names is not None and names != self._names:
            raise ValueError('variable names cannot be changed after object creation.')
        if isinstance(names, str):
            names = (names, )  # make it a tuple
        elif isinstance(names, list):
            names = tuple(names)
        elif not isinstance(names, tuple):
            raise TypeError("names must be a tuple of strings")
        self._names = names

    def variable_names(self):
        """
        Return the list of variable names corresponding to the generators.

        OUTPUT: a tuple of strings

        EXAMPLES::

            sage: R.<z,y,a42> = QQ[]
            sage: R.variable_names()
            ('z', 'y', 'a42')
            sage: S = R.quotient_ring(z+y)
            sage: S.variable_names()
            ('zbar', 'ybar', 'a42bar')

        ::

            sage: T.<x> = InfinitePolynomialRing(ZZ)
            sage: T.variable_names()
            ('x',)
        """
        if self._names is not None:
            return self._names
        raise ValueError("variable names have not yet been set using self._assign_names(...)")

    def variable_name(self):
        """
        Return the first variable name.

        OUTPUT: a string

        EXAMPLES::

            sage: R.<z,y,a42> = ZZ[]
            sage: R.variable_name()
            'z'
            sage: R.<x> = InfinitePolynomialRing(ZZ)
            sage: R.variable_name()
            'x'
        """
        return self.variable_names()[0]

    def __temporarily_change_names(self, names, latex_names):
        """
        This is used by the variable names context manager.

        TESTS:

        In an old version, it was impossible to temporarily change
        the names if no names were previously assigned. But if one
        wants to print elements of the quotient of such an "unnamed"
        ring, an error resulted. That was fixed in :trac:`11068`::

            sage: MS = MatrixSpace(GF(5),2,2)
            sage: I = MS*[MS.0*MS.1,MS.2+MS.3]*MS
            sage: Q.<a,b,c,d> = MS.quo(I)
            sage: a     #indirect doctest
            [1 0]
            [0 0]

        """
        #old = self._names, self._latex_names
        # We can not assume that self *has* _latex_variable_names.
        # But there is a method that returns them and sets
        # the attribute at the same time, if needed.
        # Simon King: It is not necessarily the case that variable
        # names are assigned. In that case, self._names is None,
        # and self.variable_names() raises a ValueError
        try:
            old = self.variable_names(), self.latex_variable_names()
        except ValueError:
            old = None, None
        self._names, self._latex_names = names, latex_names
        return old

    def inject_variables(self, scope=None, verbose=True):
        """
        Inject the generators of self with their names into the
        namespace of the Python code from which this function is
        called.  Thus, e.g., if the generators of self are labeled
        'a', 'b', and 'c', then after calling this method the
        variables a, b, and c in the current scope will be set
        equal to the generators of self.

        NOTE: If Foo is a constructor for a Sage object with generators, and
        Foo is defined in Cython, then it would typically call
        ``inject_variables()`` on the object it creates.  E.g.,
        ``PolynomialRing(QQ, 'y')`` does this so that the variable y is the
        generator of the polynomial ring.
        """
        vs = self.variable_names()
        gs = self.gens()
        if scope is None:
            scope = globals()
        if verbose:
            print("Defining %s" % (', '.join(vs)))
        for v, g in zip(vs, gs):
            scope[v] = g

    #################################################################################################
    # Bases
    #################################################################################################

    def has_base(self, category=None):
        from sage.misc.superseded import deprecation
        deprecation(21395, "The method has_base() is deprecated and will be removed")
        if category is None:
            return self._base is not None
        else:
            return category._obj_base(self) is not None

    def base_ring(self):
        """
        Return the base ring of ``self``.

        INPUT:

        - ``self`` -- an object over a base ring; typically a module

        EXAMPLES::

            sage: from sage.modules.module import Module
            sage: Module(ZZ).base_ring()
            Integer Ring

            sage: F = FreeModule(ZZ,3)
            sage: F.base_ring()
            Integer Ring
            sage: F.__class__.base_ring
            <method 'base_ring' of 'sage.structure.category_object.CategoryObject' objects>

        Note that the coordinates of the elements of a module can lie
        in a bigger ring, the ``coordinate_ring``::

            sage: M = (ZZ^2) * (1/2)
            sage: v = M([1/2, 0])
            sage: v.base_ring()
            Integer Ring
            sage: parent(v[0])
            Rational Field
            sage: v.coordinate_ring()
            Rational Field

        More examples::

            sage: F = FreeAlgebra(QQ, 'x')
            sage: F.base_ring()
            Rational Field
            sage: F.__class__.base_ring
            <method 'base_ring' of 'sage.structure.category_object.CategoryObject' objects>

            sage: E = CombinatorialFreeModule(ZZ, [1,2,3])
            sage: F = CombinatorialFreeModule(ZZ, [2,3,4])
            sage: H = Hom(E, F)
            sage: H.base_ring()
            Integer Ring
            sage: H.__class__.base_ring
            <method 'base_ring' of 'sage.structure.category_object.CategoryObject' objects>

        .. TODO::

            Move this method elsewhere (typically in the Modules
            category) so as not to pollute the namespace of all
            category objects.
        """
        return self._base

    def base(self):
        return self._base

    ############################################################################
    # Homomorphism --
    ############################################################################
    def Hom(self, codomain, cat=None):
        r"""
        Return the homspace ``Hom(self, codomain, cat)`` of all
        homomorphisms from self to codomain in the category cat.  The
        default category is determined by ``self.category()`` and
        ``codomain.category()``.

        EXAMPLES::

            sage: R.<x,y> = PolynomialRing(QQ, 2)
            sage: R.Hom(QQ)
            Set of Homomorphisms from Multivariate Polynomial Ring in x, y over Rational Field to Rational Field

        Homspaces are defined for very general Sage objects, even elements of familiar rings.

        ::

            sage: n = 5; Hom(n,7)
            Set of Morphisms from 5 to 7 in Category of elements of Integer Ring
            sage: z=(2/3); Hom(z,8/1)
            Set of Morphisms from 2/3 to 8 in Category of elements of Rational Field

        This example illustrates the optional third argument::

            sage: QQ.Hom(ZZ, Sets())
            Set of Morphisms from Rational Field to Integer Ring in Category of sets
        """
        try:
            return self._Hom_(codomain, cat)
        except (AttributeError, TypeError):
            pass
        from sage.categories.all import Hom
        return Hom(self, codomain, cat)

    def latex_variable_names(self):
        """
        Returns the list of variable names suitable for latex output.

        All ``_SOMETHING`` substrings are replaced by ``_{SOMETHING}``
        recursively so that subscripts of subscripts work.

        EXAMPLES::

            sage: R, x = PolynomialRing(QQ, 'x', 12).objgens()
            sage: x
            (x0, x1, x2, x3, x4, x5, x6, x7, x8, x9, x10, x11)
            sage: R.latex_variable_names ()
            ['x_{0}', 'x_{1}', 'x_{2}', 'x_{3}', 'x_{4}', 'x_{5}', 'x_{6}', 'x_{7}', 'x_{8}', 'x_{9}', 'x_{10}', 'x_{11}']
            sage: f = x[0]^3 + 15/3 * x[1]^10
            sage: print(latex(f))
            5 x_{1}^{10} + x_{0}^{3}
        """
        from sage.misc.latex import latex, latex_variable_name
        try:
            names = self._latex_names
            if names is not None:
                return names
        except AttributeError:
            pass
        # Compute the latex versions of the variable names.
        self._latex_names = [latex_variable_name(x) for x in self.variable_names()]
        return self._latex_names

    def latex_name(self):
        return self.latex_variable_names()[0]

    #################################################################################
    # Give all objects with generators a dictionary, so that attribute setting
    # works.   It would be nice if this functionality were standard in Cython,
    # i.e., just define __dict__ as an attribute and all this code gets generated.
    #################################################################################
    def __getstate__(self):
        try:
            d = self.__dict__.copy()  # so we can add elements
        except AttributeError:
            d = {}
        d['_category'] = self._category
        d['_base'] = self._base
        d['_names'] = self._names
        ###########
        # The _pickle_version ensures that the unpickling for objects created
        # in different versions of sage works across versions.
        # Update this integer if you change any of these attributes
        ###########
        d['_pickle_version'] = 1

        return d

    def __setstate__(self,d):
        try:
            version = d['_pickle_version']
        except KeyError:
            version = 0
        try:
            if version == 1:
                if d['_category'] is not None:
                    # We must not erase the category information of
                    # self.  Otherwise, pickles break (e.g., QQ should
                    # be a commutative ring, but when QQ._category is
                    # None then it only knows that it is a ring!
                    if self._category is None:
                        self._category = d['_category']
                    else:
                        self._category = self._category.join([self._category,d['_category']])
                self._base = d['_base']
                self._names = d['_names']
            elif version == 0:
                # In the old code, this functionality was in parent_gens,
                # but there were parents that didn't inherit from parent_gens.
                # If we have such, then we only need to deal with the dictionary.
                try:
                    self._base = d['_base']
                    self._names = d['_names']
                    # We throw away d['_latex_names'] and d['_list']
                except (AttributeError, KeyError):
                    pass
            try:
                self.__dict__ = d
            except AttributeError:
                pass
        except (AttributeError, KeyError):
            raise
            #raise RuntimeError, "If you change the pickling code in parent or category_object, you need to update the _pickle_version field"

    def __hash__(self):
        """
        A default hash is provide based on the string representation of the
        self. It is cached to remain consistent throughout a session, even
        if the representation changes.

        EXAMPLES::

            sage: bla = PolynomialRing(ZZ,"x")
            sage: hash(bla)
            -5279516879544852222  # 64-bit
            -1056120574           # 32-bit
            sage: bla.rename("toto")
            sage: hash(bla)
            -5279516879544852222  # 64-bit
            -1056120574           # 32-bit
        """
        if self._hash_value == -1:
            self._hash_value = hash(repr(self))
        return self._hash_value

    ##############################################################################
    # Getting attributes from the category
    ##############################################################################

    def __getattr__(self, name):
        """
        Let cat be the category of ``self``. This method emulates
        ``self`` being an instance of both ``CategoryObject`` and
        ``cat.parent_class``, in that order, for attribute lookup.

        This attribute lookup is cached for speed.

        EXAMPLES:

        We test that ZZ (an extension type) inherits the methods from
        its categories, that is from ``EuclideanDomains().parent_class``::

            sage: ZZ._test_associativity
            <bound method JoinCategory.parent_class._test_associativity of Integer Ring>
            sage: ZZ._test_associativity(verbose = True)
            sage: TestSuite(ZZ).run(verbose = True)
            running ._test_additive_associativity() . . . pass
            running ._test_an_element() . . . pass
            running ._test_associativity() . . . pass
            running ._test_cardinality() . . . pass
            running ._test_category() . . . pass
            running ._test_characteristic() . . . pass
            running ._test_distributivity() . . . pass
            running ._test_elements() . . .
              Running the test suite of self.an_element()
              running ._test_category() . . . pass
              running ._test_eq() . . . pass
              running ._test_new() . . . pass
              running ._test_nonzero_equal() . . . pass
              running ._test_not_implemented_methods() . . . pass
              running ._test_pickling() . . . pass
              pass
            running ._test_elements_eq_reflexive() . . . pass
            running ._test_elements_eq_symmetric() . . . pass
            running ._test_elements_eq_transitive() . . . pass
            running ._test_elements_neq() . . . pass
            running ._test_enumerated_set_contains() . . . pass
            running ._test_enumerated_set_iter_cardinality() . . . pass
            running ._test_enumerated_set_iter_list() . . . pass
            running ._test_eq() . . . pass
            running ._test_euclidean_degree() . . . pass
            running ._test_fraction_field() . . . pass
            running ._test_gcd_vs_xgcd() . . . pass
            running ._test_metric() . . . pass
            running ._test_new() . . . pass
            running ._test_not_implemented_methods() . . . pass
            running ._test_one() . . . pass
            running ._test_pickling() . . . pass
            running ._test_prod() . . . pass
            running ._test_quo_rem() . . . pass
            running ._test_some_elements() . . . pass
            running ._test_zero() . . . pass
            running ._test_zero_divisors() . . . pass

            sage: Sets().example().sadfasdf
            Traceback (most recent call last):
            ...
            AttributeError: 'PrimeNumbers_with_category' object has no attribute 'sadfasdf'
        """
        return self.getattr_from_category(name)

    cdef getattr_from_category(self, name):
        # Lookup a method or attribute from the category abstract classes.
        # See __getattr__ above for documentation.
        try:
            return self.__cached_methods[name]
        except KeyError:
            if self._category is None:
                # Usually, this will just raise AttributeError in
                # getattr_from_other_class().
                cls = type
            else:
                cls = self._category.parent_class

            attr = getattr_from_other_class(self, cls, name)
            self.__cached_methods[name] = attr
            return attr

    def __dir__(self):
        """
        Let cat be the category of ``self``. This method emulates
        ``self`` being an instance of both ``CategoryObject`` and
        ``cat.parent_class``, in that order, for attribute directory.

        EXAMPLES::

            sage: for s in dir(ZZ):
            ....:     if s[:6] == "_test_": print(s)
            _test_additive_associativity
            _test_an_element
            _test_associativity
            _test_cardinality
            _test_category
            _test_characteristic
            _test_distributivity
            _test_elements
            _test_elements_eq_reflexive
            _test_elements_eq_symmetric
            _test_elements_eq_transitive
            _test_elements_neq
            _test_enumerated_set_contains
            _test_enumerated_set_iter_cardinality
            _test_enumerated_set_iter_list
            _test_eq
            _test_euclidean_degree
            _test_fraction_field
            _test_gcd_vs_xgcd
            _test_metric
            _test_new
            _test_not_implemented_methods
            _test_one
            _test_pickling
            _test_prod
            _test_quo_rem
            _test_some_elements
            _test_zero
            _test_zero_divisors
            sage: F = GF(9,'a')
            sage: dir(F)
            [..., '__class__', ..., '_test_pickling', ..., 'extension', ...]

        """
        return dir_with_other_class(self, self.category().parent_class)

    ##############################################################################
    # For compatibility with Python 2
    ##############################################################################
    def __div__(self, other):
        """
        Implement Python 2 division as true division.

        EXAMPLES::

            sage: V = QQ^2
            sage: V.__div__(V.span([(1,3)]))
            Vector space quotient V/W of dimension 1 over Rational Field where
            V: Vector space of dimension 2 over Rational Field
            W: Vector space of degree 2 and dimension 1 over Rational Field
            Basis matrix:
            [1 3]
            sage: V.__truediv__(V.span([(1,3)]))
            Vector space quotient V/W of dimension 1 over Rational Field where
            V: Vector space of dimension 2 over Rational Field
            W: Vector space of degree 2 and dimension 1 over Rational Field
            Basis matrix:
            [1 3]
        """
        return self / other


cpdef normalize_names(Py_ssize_t ngens, names):
    r"""
    Return a tuple of strings of variable names of length ngens given
    the input names.

    INPUT:

    - ``ngens`` -- integer: number of generators. The value ``ngens=-1``
      means that the number of generators is unknown a priori.

    - ``names`` -- any of the following:

      - a tuple or list of strings, such as ``('x', 'y')``

      - a comma-separated string, such as ``x,y``

      - a string prefix, such as 'alpha'

      - a string of single character names, such as 'xyz'

    OUTPUT: a tuple of ``ngens`` strings to be used as variable names.

    EXAMPLES::

        sage: from sage.structure.category_object import normalize_names as nn
        sage: nn(0, "")
        ()
        sage: nn(0, [])
        ()
        sage: nn(0, None)
        ()
        sage: nn(1, 'a')
        ('a',)
        sage: nn(2, 'z_z')
        ('z_z0', 'z_z1')
        sage: nn(3, 'x, y, z')
        ('x', 'y', 'z')
        sage: nn(2, 'ab')
        ('a', 'b')
        sage: nn(2, 'x0')
        ('x00', 'x01')
        sage: nn(3, (' a ', ' bb ', ' ccc '))
        ('a', 'bb', 'ccc')
        sage: nn(4, ['a1', 'a2', 'b1', 'b11'])
        ('a1', 'a2', 'b1', 'b11')

    Arguments are converted to strings::

        sage: nn(1, u'a')
        ('a',)
        sage: var('alpha')
        alpha
        sage: nn(2, alpha)
        ('alpha0', 'alpha1')
        sage: nn(1, [alpha])
        ('alpha',)

    With an unknown number of generators::

        sage: nn(-1, 'a')
        ('a',)
        sage: nn(-1, 'x, y, z')
        ('x', 'y', 'z')

    Test errors::

        sage: nn(3, ["x", "y"])
        Traceback (most recent call last):
        ...
        IndexError: the number of names must equal the number of generators
        sage: nn(None, "a")
        Traceback (most recent call last):
        ...
        TypeError: 'NoneType' object cannot be interpreted as an index
        sage: nn(1, "")
        Traceback (most recent call last):
        ...
        ValueError: variable name must be nonempty
        sage: nn(1, "foo@")
        Traceback (most recent call last):
        ...
        ValueError: variable name 'foo@' is not alphanumeric
        sage: nn(2, "_foo")
        Traceback (most recent call last):
        ...
        ValueError: variable name '_foo0' does not start with a letter
        sage: nn(1, 3/2)
        Traceback (most recent call last):
        ...
        ValueError: variable name '3/2' is not alphanumeric
    """
    if isinstance(names, (tuple, list)):
        # Convert names to strings and strip whitespace
        names = [str(x).strip() for x in names]
    else:
        # Interpret names as string and convert to tuple of strings
        names = str(names)

        if ',' in names:
            names = [x.strip() for x in names.split(',')]
        elif ngens > 1 and len(names) == ngens:
            # Split a name like "xyz" into ("x", "y", "z")
            try:
                certify_names(names)
                names = tuple(names)
            except ValueError:
                pass
        if isinstance(names, basestring):
            if ngens < 0:
                names = [names]
            else:
                import sage.misc.defaults
                names = sage.misc.defaults.variable_names(ngens, names)

    certify_names(names)
    if ngens >= 0 and len(names) != ngens:
       raise IndexError("the number of names must equal the number of generators")
    return tuple(names)


cpdef bint certify_names(names) except -1:
    """
    Check that ``names`` are valid variable names.

    INPUT:

    - ``names`` -- an iterable with strings representing variable names

    OUTPUT: ``True`` (for efficiency of the Cython call)

    EXAMPLES::

        sage: from sage.structure.category_object import certify_names as cn
        sage: cn(["a", "b", "c"])
        1
        sage: cn("abc")
        1
        sage: cn([])
        1
        sage: cn([""])
        Traceback (most recent call last):
        ...
        ValueError: variable name must be nonempty
        sage: cn(["_foo"])
        Traceback (most recent call last):
        ...
        ValueError: variable name '_foo' does not start with a letter
        sage: cn(["x'"])
        Traceback (most recent call last):
        ...
        ValueError: variable name "x'" is not alphanumeric
        sage: cn(["a", "b", "b"])
        Traceback (most recent call last):
        ...
        ValueError: variable name 'b' appears more than once
    """
    cdef set s = set()
    for N in names:
        if not isinstance(N, str):
            raise TypeError("variable name {!r} must be a string, not {}".format(N, type(N)))
        if not N:
            raise ValueError("variable name must be nonempty")
        if not N.replace("_", "").isalnum():
            # We must be alphanumeric, but we make an exception for non-leading '_' characters.
            raise ValueError("variable name {!r} is not alphanumeric".format(N))
        if not N[0].isalpha():
            raise ValueError("variable name {!r} does not start with a letter".format(N))
        if N in s:
            raise ValueError("variable name {!r} appears more than once".format(N))
        s.add(N)
    return True
