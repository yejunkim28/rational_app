from PyDesmos import Graph
from sympy import symbols, sympify, factor, solve
import re
from sympy.parsing.sympy_parser import parse_expr
import json
from sympy.parsing.sympy_parser import (parse_expr,
                                        standard_transformations,
                                        implicit_multiplication_application)

equation = "((x - 9)/(12*(7*x - 9))) / (((x - 4)*(x - 9))/(8*(x + 1)*(x - 4)))"


class rational_function:
    def __init__(self, equation_str: str):
        self.equation_str = equation_str.replace(" ", "")
        self.x = symbols('x')
        self.equation = sympify(equation_str)
        self.factored = factor(self.equation)

    def create_simplified(self):
        return self.factored

    def asymptote(self):
        _, den = self.factored.as_numer_denom()

        return list(set(solve(den, self.x)))

    def holes(self):
        all_holes = []
        all_ends = []

        equation = self.equation_str

        for m in re.finditer(r"/\(", equation):
            all_ends.append(m.end()-1)

        left = 0
        right = 0
        for idx in all_ends:
            a = True
            last_idx = idx
            while a and last_idx < len(equation) + 1:
                if equation[last_idx] == "(":
                    left += 1
                elif equation[last_idx] == ')':
                    right += 1
                else:
                    pass

                if left == right:
                    part_equation = equation[idx: last_idx+1]

                    x = symbols('x')
                    hole_individual = solve(part_equation, x)
                    all_holes += hole_individual
                    a = False

                last_idx += 1

        return list(set(all_holes))

    def real_holes(self):
        asymptotes = self.asymptote()
        all_holes = self.holes()
        return [x for x in all_holes if x not in asymptotes]

    def holes_coords(self):
        hole = self.real_holes()
        expr = self.create_simplified()
        all_coords = []

        for i in hole:
            value = expr.subs(self.x, i)
            all_coords.append((i, value))

        return all_coords

    def draw_in_desmos(self):
        expressions = []

        func_expr = self.create_simplified()
        func_latex = str(func_expr)
        if not func_latex.startswith("y="):
            func_latex = "y=" + func_latex
        expressions.append({"id": "f", "latex": func_latex})

        for i, a in enumerate(self.asymptote() or []):
            expressions.append({
                "id": f"a{i}",
                "latex": str(a),
                "color": "#FF0000",
                "lineStyle": "DASHED",
            })

        for i, p in enumerate(self.holes_coords() or []):
            try:
                px, py = p
                px_f = float(px)
                py_f = float(py)
                expressions.append(
                    {"id": f"h{i}", "latex": f"({px_f},{py_f})"})
            except Exception:
                expressions.append({"id": f"h{i}", "latex": str(p)})

        expr_json = json.dumps(expressions)

        html = f"""
        <div id="calculator" style="width:100%; height:600px;"></div>
        <script src="https://www.desmos.com/api/v1.7/calculator.js"></script>
        <script>
          const data = {expr_json};
          const elt = document.getElementById('calculator');
          const calculator = Desmos.GraphingCalculator(elt, {{ expressions: false }});
          calculator.setExpressions(data);
        </script>
        """

        return html


if __name__ == "__main__":
    expr = (
        "((x - 9) / (12 * (7*x - 9))) / (((x - 4) * (x -  9)) / (8 * (x + 1) * (x - 4)))")
    analyzer = rational_function(expr)

    analyzer.draw_in_desmos()
