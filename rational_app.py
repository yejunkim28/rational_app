import streamlit as st
from sympy import symbols, sympify, latex, factor
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application,
)
from PyDesmos import Graph
from rational_function import rational_function
import streamlit.components.v1 as components


def change_to_latex(expr):
    try:
        sym_expr = sympify(expr)
        return latex(sym_expr)
    except Exception:
        # fallback to string parsing if needed
        expr_str = str(expr)
        expr_str = expr_str.replace('*', ' ')
        expr_str = expr_str.replace('(', '\\left(').replace(')', '\\right)')
        return expr_str


x = symbols('x')

st.title("Rational Function Analyzer")
st.write("Enter a rational function (use `x` as the variable):")
st.set_page_config(layout="wide")

equation_str = st.text_input("Enter a rational function:", "")
"""
Examples: \n
((x - 9) / (12 * (7*x - 9))) / (((x - 4) * (x -  9)) / (8 * (x + 1) * (x - 4))) \n
((5*x+15)/(x^2 - 3*x-10)) / ((3*x^2 + 4 * x - 15) / (3 *x^2 - 20*x + 25)) \n
(25 * x-35)/(5 * x ^ 2 + 3 * x -14) - 4/(x + 2)
"""

if st.button("Analyze & Graph"):
    try:
        expr_input = equation_str.strip()
        if not expr_input:
            st.error("Please enter an expression again")
        else:
            analyzer = rational_function(expr_input)

            asymptotes = analyzer.asymptote()
            points = analyzer.holes_coords()
            simplified_expression = analyzer.create_simplified()

            st.title("Desmos Graph in Streamlit")
            col1, col2 = st.columns([10, 10])

            with col2:
                st.subheader("Graph")

                desmos_code = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <script src="https://www.desmos.com/api/v1.6/calculator.js?apiKey=dcb31709b452b1cf9dc26972add0fda6"></script>
                </head>
                <body>
                    <div id="calculator" style="width: 100%; height: 500px;"></div>
                    <script>
                        var elt = document.getElementById('calculator');
                        var calculator = Desmos.GraphingCalculator(elt, {{
                            expressions: false,
                            settingsMenu: false,
                            zoomButtons: false
                            }});
                
                        calculator.setExpression({{
                            id: 'original',
                            latex: 'y={expr_input}',
                            color: '#2d70b3'
                        }});
                
                        """

                for i, asym in enumerate(asymptotes):
                    desmos_code += f"""\t\tcalculator.setExpression({{id: 'asymptote{i}',latex: 'x={asym}',color: '#c74440',lineStyle: Desmos.Styles.DASHED}});"""

                # Add holes
                for i, point in enumerate(points):
                    px, py = point
                    desmos_code += f"""
                    \t\tcalculator.setExpression({{
                        id: 'hole{i}',
                        latex: '({px},{py})',
                        color: '#c74440',
                        pointStyle: Desmos.Styles.OPEN
                    }});
                    """

                desmos_code += "\t</script>\n</body>\n</html>"
                components.html(desmos_code, height=520)

            with col1:
                st.subheader("Analysis")

                st.write("**Simplified Expression:**")
                latex_expr = change_to_latex(simplified_expression)

                st.latex(f"y = {latex_expr}")

                st.write("**Vertical Asymptotes:**")
                if asymptotes:
                    for a in asymptotes:
                        st.latex(f"x = {a}")

                else:
                    st.write("None")

                st.write(f"**Undefined Points:**")
                if points:
                    for p in points:
                        st.latex(f"({p[0]}, {p[1]})")
                else:
                    st.write("None")

    except Exception as e:
        st.error(f"Error: {e}")


"""
streamlit run Algebra2/rational_app.py
"""
