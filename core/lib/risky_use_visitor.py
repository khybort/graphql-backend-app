import ast

from core.exception import UnexpectedIndentException


class RiskyFunctionVisitor(ast.NodeVisitor):
    RISKY_FUNCTIONS = [
        "os.system",
        "subprocess.call",
        "pickle.loads",
        "eval",
        "exec",
        "execfile",
    ]

    def __init__(self):
        self.node_risky_functions = []

    def visit_Call(self, node):
        if isinstance(node.func, ast.Attribute):
            module_name = node.func.value.id
            function_name = node.func.attr
        else:
            module_name = None
            function_name = node.func.id

        if function_name in self.RISKY_FUNCTIONS:
            self.node_risky_functions.append((module_name, function_name))

        self.generic_visit(node)


class RiskyLibraryVisitor(ast.NodeVisitor):
    RISKY_LIBRARIES = [
        "pickle",
        "os",
        "subprocess",
        "paramiko",
    ]

    def __init__(self):
        self.node_risky_libraries = []

    def visit_Import(self, node):
        for alias in node.names:
            if alias.name in self.RISKY_LIBRARIES:
                self.node_risky_libraries.append(alias.name)

    def visit_ImportFrom(self, node):
        if node.module in self.RISKY_LIBRARIES:
            self.node_risky_libraries.append(node.module)

    def visit_Call(self, node):
        if isinstance(node.func, ast.Attribute):
            module_name = node.func.value.id
        else:
            module_name = None

        if module_name in self.RISKY_LIBRARIES:
            self.node_risky_libraries.append(module_name)

        self.generic_visit(node)


def find_risky_functions_and_libraries(code: str) -> tuple[str, str]:
    try:
        tree = ast.parse(code)
    except:
        raise UnexpectedIndentException()

    function_visitor = RiskyFunctionVisitor()
    function_visitor.visit(tree)

    library_visitor = RiskyLibraryVisitor()
    library_visitor.visit(tree)

    risky_functions = " ,".join(
        [
            f"{module}.{function}" if module else function
            for module, function in set(function_visitor.risky_functions)
        ]
    )
    risky_libraries = " ,".join(set(library_visitor.risky_libraries))

    return risky_functions, risky_libraries
