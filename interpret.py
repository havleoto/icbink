from rpython.rlib import jit

import kernel_type as kt
import parse
import primitive
import sys


def empty_environment():
    return kt.Environment([], {})

_ground_env = kt.Environment([], primitive.exports)

def standard_environment():
    return kt.Environment([_ground_env], {})

def run_one_expr(val, env):
    cont = kt.TerminalCont()
    try:
        while True:
            driver.jit_merge_point(val=val, env=env, cont=cont)
            val, env, cont = val.interpret(env, cont)
    except kt.Done as e:
        return e.value

def get_printable_location(green_val):
    if green_val is None:
        return "No green val"
    else:
        return green_val.tostring()
driver = jit.JitDriver(reds=['env', 'cont'],
                       greens=['val'],
                       get_printable_location=get_printable_location)


def keval(expr_str, env):
    expr, = parse.parse(expr_str).data
    return run_one_expr(expr, env)

def test():
    env = standard_environment()
    env.set(kt.get_interned('x'), kt.String('the-value-bound-by-x'))
    for expr_str, typ, value in [('"one"', kt.String, 'one'),
                                 ('x', kt.String, 'the-value-bound-by-x'),
                                 ('(string-append)', kt.String, ''),
                                 ('(string-append "one")', kt.String, 'one'),
                                 ('(string-append "one" "two")', kt.String, 'onetwo'),
                                 ]:
        result = keval(expr_str, env)
        assert isinstance(result, typ)
        assert result.value == value
    assert isinstance(keval('string-append', env), kt.Applicative)
    print "All OK."

def load(filename, env):
    src = open(filename).read()
    program = parse.parse(src)
    for expr in program.data:
        run_one_expr(expr, env)

def run(args):
    env = standard_environment()
    _, filename = args
    load("library.k", env)
    load(filename, env)
    return 0

if __name__ == '__main__':
    run(sys.argv)


