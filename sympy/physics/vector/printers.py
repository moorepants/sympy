from sympy import Derivative
from sympy.core.function import UndefinedFunction
from sympy.printing.conventions import split_super_sub
from sympy.printing.latex import LatexPrinter
from sympy.printing.pretty.pretty import PrettyPrinter
from sympy.printing.pretty.stringpict import prettyForm, stringPict
from sympy.printing.str import StrPrinter
from sympy.utilities import group
from sympy.physics.vector.dynamicsymbols import dynamicsymbols


class VectorStrPrinter(StrPrinter):
    """String Printer for vector expressions. """

    def _print_Derivative(self, e):
        t = dynamicsymbols._t
        if (bool(sum([i == t for i in e.variables])) &
                isinstance(type(e.args[0]), UndefinedFunction)):
            ol = str(e.args[0].func)
            for i, v in enumerate(e.variables):
                ol += dynamicsymbols._str
            return ol
        else:
            return StrPrinter().doprint(e)

    def _print_Function(self, e):
        t = dynamicsymbols._t
        if isinstance(type(e), UndefinedFunction):
            return StrPrinter().doprint(e).replace("(%s)" % t, '')
        return e.func.__name__ + "(%s)" % self.stringify(e.args, ", ")


class VectorLatexPrinter(LatexPrinter):
    """Latex Printer for vector expressions. """

    def _print_Function(self, expr, exp=None):
        func = expr.func.__name__
        t = dynamicsymbols._t

        if hasattr(self, '_print_' + func):
            return getattr(self, '_print_' + func)(expr, exp)
        elif isinstance(type(expr), UndefinedFunction) and (expr.args == (t,)):
            name, sup, sub = split_super_sub(func)
            if len(sup) != 0:
                sup = r"^{%s}" % "".join(sup)
            else:
                sup = r""
            if len(sub) != 0:
                sub = r"_{%s}" % "".join(sub)
            else:
                sub = r""
            if exp:
                sup += r"^{%s}" % self._print(exp)
            return r"%s" % (name + sup + sub)
        else:
            args = [str(self._print(arg)) for arg in expr.args]
            # How inverse trig functions should be displayed, formats are:
            # abbreviated: asin, full: arcsin, power: sin^-1
            inv_trig_style = self._settings['inv_trig_style']
            # If we are dealing with a power-style inverse trig function
            inv_trig_power_case = False
            # If it is applicable to fold the argument brackets
            can_fold_brackets = self._settings['fold_func_brackets'] and \
                len(args) == 1 and \
                not self._needs_function_brackets(expr.args[0])

            inv_trig_table = ["asin", "acos", "atan", "acot"]

            # If the function is an inverse trig function, handle the style
            if func in inv_trig_table:
                if inv_trig_style == "abbreviated":
                    func = func
                elif inv_trig_style == "full":
                    func = "arc" + func[1:]
                elif inv_trig_style == "power":
                    func = func[1:]
                    inv_trig_power_case = True

                    # Can never fold brackets if we're raised to a power
                    if exp is not None:
                        can_fold_brackets = False

            if inv_trig_power_case:
                name = r"\operatorname{%s}^{-1}" % func
            elif exp is not None:
                name = r"\operatorname{%s}^{%s}" % (func, exp)
            else:
                name = r"\operatorname{%s}" % func

            if can_fold_brackets:
                name += r"%s"
            else:
                name += r"\left(%s\right)"

            if inv_trig_power_case and exp is not None:
                name += r"^{%s}" % exp

            return name % ",".join(args)

    def _print_Derivative(self, der_expr):
        # make sure it is an the right form
        der_expr = der_expr.doit()
        if not isinstance(der_expr, Derivative):
            return self.doprint(der_expr)

        # check if expr is a dynamicsymbol
        from sympy.core.function import AppliedUndef
        t = dynamicsymbols._t
        expr = der_expr.expr
        red = expr.atoms(AppliedUndef)
        syms = der_expr.variables
        test1 = not all([True for i in red if i.atoms() == set([t])])
        test2 = not all([(t == i) for i in syms])
        if test1 or test2:
            return LatexPrinter().doprint(der_expr)

        # done checking
        dots = len(syms)
        base = self._print_Function(expr)
        base_split = base.split('_', 1)
        base = base_split[0]
        if dots == 1:
            base = r"\dot{%s}" % base
        elif dots == 2:
            base = r"\ddot{%s}" % base
        elif dots == 3:
            base = r"\dddot{%s}" % base
        if len(base_split) is not 1:
            base += '_' + base_split[1]
        return base


class VectorPrettyPrinter(PrettyPrinter):
    """Pretty Printer for vectorialexpressions. """

    def _print_Derivative(self, deriv):
        # XXX use U('PARTIAL DIFFERENTIAL') here ?
        t = dynamicsymbols._t
        dots = 0
        can_break = True
        syms = list(reversed(deriv.variables))
        x = None

        while len(syms) > 0:
            if syms[-1] == t:
                syms.pop()
                dots += 1
            else:
                break

        f = prettyForm(binding=prettyForm.FUNC, *self._print(deriv.expr))
        if not (isinstance(type(deriv.expr), UndefinedFunction)
                and (deriv.expr.args == (t,))):
            dots = 0
            can_break = False
            f = prettyForm(binding=prettyForm.FUNC,
                    *self._print(deriv.expr).parens())

        if dots == 0:
            dots = u("")
        elif dots == 1:
            dots = u("\u0307")
        elif dots == 2:
            dots = u("\u0308")
        elif dots == 3:
            dots = u("\u20db")
        elif dots == 4:
            dots = u("\u20dc")

        uni_subs = [u("\u2080"), u("\u2081"), u("\u2082"), u("\u2083"), u("\u2084"),
                    u("\u2085"), u("\u2086"), u("\u2087"), u("\u2088"), u("\u2089"),
                    u("\u208a"), u("\u208b"), u("\u208c"), u("\u208d"), u("\u208e"),
                    u("\u208f"), u("\u2090"), u("\u2091"), u("\u2092"), u("\u2093"),
                    u("\u2094"), u("\u2095"), u("\u2096"), u("\u2097"), u("\u2098"),
                    u("\u2099"), u("\u209a"), u("\u209b"), u("\u209c"), u("\u209d"),
                    u("\u209e"), u("\u209f")]

        fpic = f.__dict__['picture']
        funi = f.__dict__['unicode']
        ind = len(funi)
        val = ""

        for i in uni_subs:
            cur_ind = funi.find(i)
            if (cur_ind != -1) and (cur_ind < ind):
                ind = cur_ind
                val = i
        if ind == len(funi):
            funi += dots
        else:
            funi = funi.replace(val, dots + val)

        if f.__dict__['picture'] == [f.__dict__['unicode']]:
            fpic = [funi]
        f.__dict__['picture'] = fpic
        f.__dict__['unicode'] = funi

        if (len(syms)) == 0 and can_break:
            return f

        for sym, num in group(syms, multiple=False):
            s = self._print(sym)
            ds = prettyForm(*s.left('d'))

            if num > 1:
                ds = ds**prettyForm(str(num))

            if x is None:
                x = ds
            else:
                x = prettyForm(*x.right(' '))
                x = prettyForm(*x.right(ds))
        pform = prettyForm('d')
        if len(syms) > 1:
            pform = pform**prettyForm(str(len(syms)))
        pform = prettyForm(*pform.below(stringPict.LINE, x))
        pform.baseline = pform.baseline + 1
        pform = prettyForm(*stringPict.next(pform, f))
        return pform

    def _print_Function(self, e):
        t = dynamicsymbols._t
        # XXX works only for applied functions
        func = e.func
        args = e.args
        func_name = func.__name__
        prettyFunc = self._print(C.Symbol(func_name))
        prettyArgs = prettyForm(*self._print_seq(args).parens())
        # If this function is an Undefined function of t, it is probably a
        # dynamic symbol, so we'll skip the (t). The rest of the code is
        # identical to the normal PrettyPrinter code
        if isinstance(func, UndefinedFunction) and (args == (t,)):
            pform = prettyForm(binding=prettyForm.FUNC,
                       *stringPict.next(prettyFunc))
        else:
            pform = prettyForm(binding=prettyForm.FUNC,
                       *stringPict.next(prettyFunc, prettyArgs))
        # store pform parts so it can be reassembled e.g. when powered
        pform.prettyFunc = prettyFunc
        pform.prettyArgs = prettyArgs
        return pform


class VectorTypeError(TypeError):

    def __init__(self, other, type_str):
        super(VectorialTypeError, self).__init__("Expected an instance of %s, "
                "instead received an object '%s' of type %s." % (
                    type_str, other, type(other)))
