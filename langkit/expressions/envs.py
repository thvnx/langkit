from functools import partial

from langkit import names
from langkit.compiled_types import (
    EnvElement, LexicalEnvType, Token, BoolType, T
)
from langkit.expressions.base import (
    AbstractVariable, AbstractExpression, ArrayExpr, BuiltinCallExpr,
    ResolvedExpression, construct, PropertyDef, BasicExpr, attr_expr,
    attr_call, auto_attr
)

Env = AbstractVariable(names.Name("Current_Env"), type=LexicalEnvType)
EmptyEnv = AbstractVariable(names.Name("AST_Envs.Empty_Env"),
                            type=LexicalEnvType)


@attr_call("get")
@attr_call("resolve_unique", resolve_unique=True)
class EnvGet(AbstractExpression):
    """
    Expression for lexical environment get operation.
    """

    def __init__(self, env_expr, token_expr, resolve_unique=False):
        """
        :param AbstractExpression env_expr: Expression that will yield the env
            to get the element from.
        :param AbstractExpression token_expr: Expression that will yield the
            token to use as a key on the env.
        :param bool resolve_unique: Wether we want an unique result or not.
            NOTE: For the moment, nothing will be done to ensure that only one
            result is available. The implementation will just take the first
            result.
        """
        super(EnvGet, self).__init__()
        self.env_expr = env_expr
        self.token_expr = token_expr
        self.resolve_unique = resolve_unique
        # TODO: Add a filter here. This will wait further developments in the
        # array machinery.

    def construct(self):
        array_expr = 'AST_Envs.Get ({}, Get_Symbol ({}))'

        make_expr = partial(
            BasicExpr, result_var_name="Env_Get_Result",
            sub_exprs=[construct(self.env_expr, LexicalEnvType),
                       construct(self.token_expr, Token)]
        )

        if self.resolve_unique:
            return make_expr("Get ({}, 0)".format(array_expr), EnvElement)
        else:
            EnvElement.array_type().add_to_context()
            return make_expr("Create ({})".format(array_expr),
                             EnvElement.array_type())


@attr_call("eval_in_env")
class EnvBind(AbstractExpression):
    """
    Expression that will evaluate a subexpression in the context of a
    particular lexical environment. Not meant to be used directly, but instead
    via the eval_in_env shortcut.
    """

    class Expr(ResolvedExpression):
        def __init__(self, env_expr, to_eval_expr):
            self.to_eval_expr = to_eval_expr
            self.env_expr = env_expr

            # Declare a variable that will hold the value of the
            # bound environment.
            self.static_type = self.to_eval_expr.type
            self.env_var = PropertyDef.get().vars.create("New_Env",
                                                         LexicalEnvType)

            super(EnvBind.Expr, self).__init__()

        def _render_pre(self):
            # First, compute the environment to bind using the current one and
            # store it in the "New_Env" local variable.
            #
            # We need to keep the environment live during the bind operation.
            # That is why we store this environment in a temporary so that it
            # is automatically deallocated when leaving the scope.
            result = (
                '{env_expr_pre}\n'
                '{env_var} := {env_expr};\n'
                'Inc_Ref ({env_var});'.format(
                    env_expr_pre=self.env_expr.render_pre(),
                    env_expr=self.env_expr.render_expr(),
                    env_var=self.env_var.name
                )
            )

            # Then we can compute the nested expression with the bound
            # environment.
            with Env.bind_name(self.env_var.name):
                return '{}\n{}'.format(result, self.to_eval_expr.render_pre())

        def _render_expr(self):
            # We just bind the name of the environment placeholder to our
            # variable.
            with Env.bind_name(self.env_var.name):
                return self.to_eval_expr.render_expr()

        def __repr__(self):
            return '<EnvBind.Expr>'

    def __init__(self, env_expr, to_eval_expr):
        """

        :param AbstractExpression env_expr: An expression that will return a
            lexical environment in which we will eval to_eval_expr.
        :param AbstractExpression to_eval_expr: The expression to eval.
        """
        super(EnvBind, self).__init__()
        self.env_expr = env_expr
        self.to_eval_expr = to_eval_expr

    def construct(self):
        return EnvBind.Expr(construct(self.env_expr, LexicalEnvType),
                            construct(self.to_eval_expr))


@attr_expr("env_orphan")
class EnvOrphan(AbstractExpression):
    """
    Expression that will create a lexical environment copy with no parent.
    """

    def __init__(self, env_expr):
        """
        :param AbstractExpression env_expr: Expression that will return a
            lexical environment.
        """
        super(EnvOrphan, self).__init__()
        self.env_expr = env_expr

    def construct(self):
        return BuiltinCallExpr(
            'AST_Envs.Orphan',
            LexicalEnvType,
            [construct(self.env_expr, LexicalEnvType)],
            'Orphan_Env'
        )


class EnvGroup(AbstractExpression):
    """
    Expression that will return a lexical environment thata logically groups
    together multiple lexical environments.
    """

    def __init__(self, *env_exprs):
        super(EnvGroup, self).__init__()
        self.env_exprs = list(env_exprs)

    def construct(self):
        env_exprs = [construct(e, LexicalEnvType) for e in self.env_exprs]
        return BuiltinCallExpr(
            'Group', LexicalEnvType,
            [ArrayExpr(env_exprs, LexicalEnvType)],
            'Group_Env'
        )


@attr_expr("env_group")
class EnvGroupArray(AbstractExpression):
    """
    Expression that will return a lexical environment that logically groups
    together multiple lexical environments from an array of lexical
    environments.
    """

    def __init__(self, env_array_expr):
        """
        :param AbstractExpression env_array_expr: Expression that will return
            an array of lexical environments. If this array is empty, the empty
            environment is returned.
        """
        super(EnvGroupArray, self).__init__()
        self.env_array_expr = env_array_expr

    def construct(self):
        return BuiltinCallExpr(
            'Group', LexicalEnvType,
            [construct(self.env_array_expr, LexicalEnvType.array_type())],
            'Group_Env'
        )


@attr_call("is_visible_from")
class IsVisibleFrom(AbstractExpression):
    """
    Expression that will return whether an env's associated compilation unit is
    visible from another env's compilation unit.

    TODO: This is mainly exposed on envs because the CompilationUnit type is
    not exposed in the DSL yet. We might want to change that eventually if
    there are other compelling reasons to do it.
    """

    def __init__(self, referenced_env, base_env):
        super(IsVisibleFrom, self).__init__()
        self.base_env = base_env
        self.referenced_env = referenced_env

    def construct(self):
        return BuiltinCallExpr(
            'Is_Visible_From', BoolType,
            [construct(self.base_env, LexicalEnvType),
             construct(self.referenced_env, LexicalEnvType)]
        )


@auto_attr
def env_node(env):
    """
    Return the node associated to this environment.
    """
    return BasicExpr('{}.Node', T.root_node, [construct(env, LexicalEnvType)])
