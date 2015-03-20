r"""
Semisimple Algebras
"""
#*****************************************************************************
#  Copyright (C) 2011 Nicolas M. Thiery <nthiery at users.sf.net>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenses/
#******************************************************************************

from category_types import Category_over_base_ring
from sage.categories.category_with_axiom import CategoryWithAxiom_over_base_ring
from sage.misc.cachefunc import cached_method
from algebras import Algebras


class SemisimpleAlgebras(Category_over_base_ring):
    """
    The category of semisimple algebras over a given base ring.

    EXAMPLES::

        from sage.categories.semisimple_algebras import SemisimpleAlgebras
        sage: C = SemisimpleAlgebras(QQ); C
        Category of semisimple algebras over Rational Field

    This category is best constructed as::

        sage: D = Algebras(QQ).Semisimple(); D
        Category of semisimple algebras over Rational Field
        sage: D is C
        True

        sage: C.super_categories()
        [Category of algebras over Rational Field]

    Typically, finite group algebras are semisimple::

        sage: DihedralGroup(5).algebra(QQ) in SemisimpleAlgebras
        True

    Unless the characteristic of the field divides the order of the group::

        sage: DihedralGroup(5).algebra(IntegerModRing(5)) in SemisimpleAlgebras
        False

        sage: DihedralGroup(5).algebra(IntegerModRing(7)) in SemisimpleAlgebras
        True

    .. SEEALSO:: `<http://en.wikipedia.org/wiki/Semisimple_algebra>`_

    TESTS::

        sage: TestSuite(C).run()
    """
    @cached_method
    def super_categories(self):
        """
        EXAMPLES::

            sage: SemisimpleAlgebras(QQ).super_categories()
            [Category of algebras over Rational Field]
        """
        R = self.base_ring()
        return [Algebras(R)]

    class FiniteDimensional(CategoryWithAxiom_over_base_ring):

        class WithBasis(CategoryWithAxiom_over_base_ring):

            class ParentMethods:

                @cached_method
                def orthogonal_idempotents(self):
                    r"""
                    Return a maximal list of orthogonal idempotents of
                    ``self``.

                    INPUT:

                    - ``self`` -- semisimple algebra

                    EXAMPLES::

                        sage: A3 = SymmetricGroup(3).algebra(QQ)
                        sage: A3.orthogonal_idempotents()
                        [2/3*() - 1/3*(1,2,3) - 1/3*(1,3,2), 1/6*() + 1/6*(2,3)
                        + 1/6*(1,2) + 1/6*(1,2,3) + 1/6*(1,3,2) + 1/6*(1,3),
                        1/6*() - 1/6*(2,3) - 1/6*(1,2) + 1/6*(1,2,3) +
                        1/6*(1,3,2) - 1/6*(1,3)]


                    ::

                        sage: A = FiniteDimensionalAlgebrasWithBasis(QQ).example(); A
                        An example of a finite dimensional algebra with basis:
                        the path algebra of the Kronecker quiver (containing
                        the arrows a:x->y and b:x->y) over Rational Field 
                        sage: Aquo = A.semisimple_quotient()
                        sage: Aquo.orthogonal_idempotents()
                        [B['y'], B['x']]
                    """
                    return [x.lift()
                            for x in self.center().central_orthogonal_idempotents()]

            class Commutative(CategoryWithAxiom_over_base_ring):

                class ParentMethods:

                    @cached_method
                    def _orthogonal_decomposition(self, generators=None, topLevel=True):
                        r"""
                        Return a list of orthogonal idempotents of a semisimple
                        commutative finite dimensional algebra ``self``.

                        INPUT:

                        - ``self`` a finite dimensional semisimple commutative
                          algebra.
                        - ``generators`` a list of generators of ``self``. By
                          default it will be the basis of ``self``.

                        OUTPUT:

                        - list of elements of ``self`` each generating a one
                          dimensional simple submodule of ``self`` in direct
                          sum with the others. The list is maximal.

                        EXAMPLES::

                            sage: G5 = SymmetricGroup(5)
                            sage: A5 = G5.algebra(QQ)
                            sage: Z5 = A5.center()
                            sage: Z5._orthogonal_decomposition()
                            [B[0] - 1/3*B[2] + 1/6*B[6], B[0] + B[1] + B[2] +
                            B[3] + B[4] + B[5] + B[6], B[0] - B[1] + B[2] + B[3]
                            - B[4] - B[5] + B[6], B[0] + 1/5*B[1] + 1/5*B[2] -
                            1/5*B[3] + 1/5*B[4] - 1/5*B[5], B[0] - 1/5*B[1] +
                            1/5*B[2] - 1/5*B[3] - 1/5*B[4] + 1/5*B[5], B[0] +
                            1/2*B[1] + 1/4*B[3] - 1/4*B[4] - 1/4*B[6], B[0] -
                            1/2*B[1] + 1/4*B[3] + 1/4*B[4] - 1/4*B[6]]

                        .. TODO::

                            Improve the function by only using matrix
                            operations.
                        """
                        # Terminal case and stuffs
                        if generators is None:
                            generators = self.basis().list()
                        if self.dimension() == 1:
                            if topLevel:
                                return self.basis().list()
                            else:
                                return [x.lift() for x in self.basis()]

                        # Searching for a good generator...
                        res = []
                        B = self.basis()
                        while len(res) < 2:
                            if generators == []:
                                raise Exception("Unable to fully decompose...")
                            gen = generators.pop()
                            phi = self.module_morphism(on_basis=lambda i:
                                    gen*B[i],
                                    codomain=self,
                                    triangular=True)
                            res = phi.matrix(self.base_ring()).eigenspaces_right()

                        # Gotcha! Let's settle the algebra...

                        res = [vector_space for _, vector_space in res]
                        res = [[self.from_vector(vector)
                            for vector in eigenspace.basis()]
                            for eigenspace in res]

                        decomp = [self.submodule(v,
                            category=SemisimpleAlgebras(self.base_ring()).WithBasis().FiniteDimensional().Commutative().Subobjects())
                            for v in res]

                        # Recursive on decomp
                        res = [x for space in decomp for x in
                                space._orthogonal_decomposition(topLevel=False)]
                        if topLevel:
                            return res
                        else:
                            return map(lambda x: x.lift(), res)

                    @cached_method
                    def central_orthogonal_idempotents(self, dimSimple=False):
                        r"""
                        Return the minimum set of central orthogonal idempotents of ``self``.

                        INPUT:

                        - ``self`` a commutative semisimple algebra

                        OUTPUT:

                        - list of idempotents of ``self``

                        EXAMPLES::

                            sage: A5 = SymmetricGroup(5).algebra(QQ)
                            sage: Z5 = A5.center()
                            sage: orth = Z5.central_orthogonal_idempotents()
                            sage: orth
                            [3/10*B[0] - 1/10*B[2] + 1/20*B[6], 1/120*B[0] +
                            1/120*B[1] + 1/120*B[2] + 1/120*B[3] + 1/120*B[4] +
                            1/120*B[5] + 1/120*B[6], 1/120*B[0] - 1/120*B[1] +
                            1/120*B[2] + 1/120*B[3] - 1/120*B[4] - 1/120*B[5] +
                            1/120*B[6], 5/24*B[0] + 1/24*B[1] + 1/24*B[2] -
                            1/24*B[3] + 1/24*B[4] - 1/24*B[5], 5/24*B[0] -
                            1/24*B[1] + 1/24*B[2] - 1/24*B[3] - 1/24*B[4] +
                            1/24*B[5], 2/15*B[0] + 1/15*B[1] + 1/30*B[3] -
                            1/30*B[4] - 1/30*B[6], 2/15*B[0] - 1/15*B[1] +
                            1/30*B[3] + 1/30*B[4] - 1/30*B[6]]
                            sage: orth[2] * orth[4]
                            0
                            sage: orth[1] ** 2 == orth[1]
                            True
                        """
                        return [(e.leading_coefficient()/(e*e).leading_coefficient())*e for
                            e in self._orthogonal_decomposition()]
