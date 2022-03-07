import numpy as np
from sympy import prime
import parser
import matplotlib.pyplot as plt
from flask import render_template
from math import *
import os
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
points_matrix = np.zeros((10, 10))
x_solution = np.zeros(10)

method=""
interpolated_polynoms=[]

def set_global_method(m):
  global method
  method=m
  
def set_global_polynom():
  global interpolated_polynoms
  interpolated_polynoms=[]
  
def calculate_coefficient(x, p):
    coeff = 0
    for i in range(len(x)):
        coeff += np.power(x[i], p)
    return coeff


def calculate_vector(x, y, p):
    vector = 0
    for i in range(len(x)):
        vector += np.power(x[i], p)*y[i]
    return vector

def submit_values(a, number_of_points):
    global points_matrix
    points_matrix = np.zeros((number_of_points, 2))
    counter = 0
    for i in range(number_of_points):
        if len(a) != 0:
            for j in range(2):
                points_matrix[i][j] = float(a[counter])
                counter += 1
    x = []
    y = []
    for i in range(len(points_matrix)):
            x.append(points_matrix[i][0])
            y.append(points_matrix[i][1])
    return (points_matrix)
  
  
def button_select_points_lin_used(points_matrix, number_of_points, number_of_equations):
    global selected_points,  augmented_matrix, nonlin
    nonlin = False
    if number_of_points >= number_of_equations:
        augmented_matrix = np.zeros(
            (int(number_of_equations), int(number_of_equations) + 1)
        )
    else:
        raise AssertionError
    counter = 0
    x = []
    y = []
    for i in range(len(points_matrix)):
        x.append(points_matrix[i][0])
        y.append(points_matrix[i][1])
        counter += 1
    counter = 0
    for i in range(number_of_equations):
        for j in range(number_of_equations+1):
            sum = 0
            if(j < number_of_equations):
                sum = calculate_coefficient(x, (j+counter))
            else:
                sum = calculate_vector(x, y, i)
            augmented_matrix[i][j] = sum
        counter += 1
    return gauss_method(augmented_matrix, nonlin, number_of_equations)
    
def button_select_points_pow_used(points_matrix, number_of_points):
    global selected_points, augmented_matrix, nonlin, method
    number_of_equations = 2
    method = "pow"
    if number_of_points >= number_of_equations:
        augmented_matrix = np.zeros(
            (int(number_of_equations), int(number_of_equations) + 1)
        )
    counter = 0
    x = []
    y = []
    # Y<0 i Y==0 ne smije biti za ln
    for i in range(len(points_matrix)):
        if(points_matrix[i][0] < 0 or points_matrix[i][0] == 0):
            return 'X mora biti veće ili različito od 0'
        else:
            x.append(np.log(points_matrix[i][0]))
        if(points_matrix[i][1] < 0 or points_matrix[i][1] == 0):

            return 'Y mora biti veće ili različito od 0'
        else:
            y.append(np.log(points_matrix[i][1]))
        counter += 1
    counter = 0
    for i in range(number_of_equations):
        for j in range(number_of_equations+1):
            sum = 0
            if(j < number_of_equations):
                sum = calculate_coefficient(x, (j+counter))
            else:
                sum = calculate_vector(x, y, i)
            augmented_matrix[i][j] = sum
        counter += 1
    nonlin = True
    return gauss_method(augmented_matrix, nonlin, number_of_equations)
  
  
def button_select_points_log_used(points_matrix, number_of_points):
    global selected_points, number_of_equations, augmented_matrix, nonlin, method
    number_of_equations = 2
    method = "log"
    if number_of_points >= number_of_equations:
        augmented_matrix = np.zeros(
            (int(number_of_equations), int(number_of_equations) + 1)
        )
    counter = 0
    x = []
    y = []
    err_message = ""
    # Y<0 i Y==0 ne smije biti za ln
    for i in range(len(points_matrix)):
        x.append(points_matrix[i][0])
        y.append(points_matrix[i][1])
        counter += 1
    counter = 0
    for i in range(number_of_equations):
        for j in range(number_of_equations+1):
            sum = 0
            if(j < number_of_equations):
                sum = calculate_coefficient(x, (j+counter))
            else:
                sum = calculate_vector(x, y, i)
            augmented_matrix[i][j] = sum
        counter += 1
    nonlin = True
    return gauss_method(augmented_matrix, nonlin, number_of_equations)
  
def button_select_points_exp_used(points_matrix, number_of_points):
    global selected_points, number_of_equations, augmented_matrix, nonlin, method
    try:
        number_of_equations = 2
        method = "exp"
        if number_of_points >= number_of_equations:
            augmented_matrix = np.zeros(
                (int(number_of_equations), int(number_of_equations) + 1)
            )
        counter = 0
        x = []
        y = []
        # Y<0 i Y==0 ne smije biti za ln
        for i in range(len(points_matrix)):
            x.append(points_matrix[i][0])
            if(points_matrix[i][1] < 0 or points_matrix[i][1] == 0):
                return 'Y mora biti veće ili različito od 0'
            else:
                y.append(np.log(points_matrix[i][1]))
            counter += 1
        counter = 0
        for i in range(number_of_equations):
            for j in range(number_of_equations+1):
                sum = 0
                if(j < number_of_equations):
                    sum = calculate_coefficient(x, (j+counter))
                else:
                    sum = calculate_vector(x, y, i)
                augmented_matrix[i][j] = sum
            counter += 1
       
        nonlin = True
        return gauss_method(augmented_matrix, nonlin, number_of_equations)
    except ValueError:
        number_of_equations = 0
        
    
def gauss_method(augmented_matrix, nonlin, number_of_equations):
    column_count = 0
    row_count = 0
    global x_solution, interpolated_polynom_parsed, interpolated_polynom, initial_function_parsed, method
    # Prolazak kroz redove
    for i in range(number_of_equations):
        # Prolazak kroz glavne elemente te zadavanje konstante kojom se množe redovi- glavni element se mijenja prilikom svake iteracije i predstavlja element na dijagonali sa indeksom [i][i]
        for j in range(i + 1, number_of_equations):
            multiply_constant = augmented_matrix[j][i] / augmented_matrix[i][i]

            # Mnozenje redova kako bi se dobila gornja trougaona matrica, uključujući i vektora kolone nehomogenih članova;
            for k in range(number_of_equations + 1):
                augmented_matrix[j][k] = augmented_matrix[j][k] - (
                    multiply_constant * augmented_matrix[i][k]
                )

        if column_count > 6:
            row_count += 1
        column_count += 1
    x_solution = np.zeros((number_of_equations))
    # Zamjena unazad
    x_solution[number_of_equations - 1] = (
        augmented_matrix[number_of_equations - 1][number_of_equations]
        / augmented_matrix[number_of_equations - 1][number_of_equations - 1]
    )
    for i in range(number_of_equations - 2, -1, -1):
        x_solution[i] = augmented_matrix[i][number_of_equations]
        for j in range(i + 1, number_of_equations):
            x_solution[i] = x_solution[i] - \
                augmented_matrix[i][j] * x_solution[j]

        x_solution[i] = x_solution[i] / augmented_matrix[i][i]
    interpolated_polynom = ""
    if nonlin == False:
        for i in range(number_of_equations):
            if x_solution[i] < 0 or i == 0:
                if i == 0:
                    interpolated_polynom += f"{round(x_solution[i],9)}"
                elif i == 1:
                    interpolated_polynom += f"{round(x_solution[i],9)}*x"
                else:
                    interpolated_polynom += f"{round(x_solution[i],9)}*x^{i}"
            elif x_solution[i] == 0:
                continue
            else:
                if i == 1:
                    interpolated_polynom += f"+{round(x_solution[i],9)}*x"
                else:
                    interpolated_polynom += f"+{round(x_solution[i],9)}*x^{i}"
    else:
        for i in range(number_of_equations):
            if x_solution[i] < 0 or i == 0:
                if i == 0:
                    if method != "log":
                        interpolated_polynom += f"e^{round(x_solution[i],9)}"
                    else:
                        interpolated_polynom += f"{round(x_solution[i],9)}"
                elif i == 1:
                    if method == "exp":
                        interpolated_polynom += f"+e^{round(x_solution[i],9)}*x"
                    else:
                        interpolated_polynom += f"{round(x_solution[i],9)}*x"
                else:
                    interpolated_polynom += f"{round(x_solution[i],9)}*x^{i}"
            elif x_solution[i] == 0:
                continue
            else:
                if i == 1:
                    if method == "exp":
                        interpolated_polynom += f"+e^{round(x_solution[i],9)}*x"
                    else:
                        interpolated_polynom += f"+{round(x_solution[i],9)}*x"
                else:
                    interpolated_polynom += f"+{round(x_solution[i],9)}*x^{i}"

    if nonlin == True:
        number_of_equations = 0
   
    #helper_parser = interpolated_polynom.replace("^", "**")
    #interpolated_polynom_parsed = parser.expr(helper_parser).compile()
    helper_parser = interpolated_polynom.replace("^", "**")
    interpolated_polynom_parsed = parser.expr(helper_parser).compile()
    draw_function_graphs(interpolated_polynom, interpolated_polynom_parsed, 1)
    return(interpolated_polynom)


def button_read_values_used(filename):
  global points_matrix,  augmented_matrix
  
  # with open('./uploads/test_docs/'+filename) as file_in:
  #     lines = [line.rstrip('\n') for line in file_in]
  x = []
  y=[]
  f = open('./uploads/test_docs/'+filename, "r")
  for i in f:
      split = i.split()
      x.append(float(split[0]))
      y.append(float(split[1]))
      z = x+y
  return str(z)
   
       
def button_select_function_used(initial_function, a, number_of_points):
    global  initial_function_parsed, points_matrix,x,y,z
    try:
        helper_parser = initial_function.replace("^", "**")
        if parser.expr(helper_parser).compile():
            initial_function_parsed = parser.expr(helper_parser).compile()
        else:
            raise SyntaxError
        if len(a) != 0:
            for i in range(len(a)):
                if not type(float(a[i])) is float:
                    raise ValueError
        counter = 0
        xa = []
        ya = []
        for i in range(number_of_points):
            if len(a) != 0:
                xa.append(float(a[counter]))
                counter += 1
        for i in range(len(xa)):
            x = xa[i]
            y = eval(initial_function_parsed)
            ya.append(y)
            z = xa+ya
        return z;
    except SyntaxError:
       ''
    except ValueError:
        ''
    except AssertionError:
      ''
      

interpolated_polynom = ""
interpolated_polynom_parsed = ""
interpolated_polynoms = []
interpolated_polynoms_parsed = []
def draw_function_graphs(interpolated_polynom, interpolated_polynom_parsed, col):
    global initial_function_parsed, initial_function, root, interpolated_polynoms_parsed, interpolated_polynoms, root
    if interpolated_polynom not in interpolated_polynoms:
        interpolated_polynoms.append(interpolated_polynom)
        interpolated_polynoms_parsed.append(interpolated_polynom_parsed)
        colors = ["lightcoral", "sienna",
                  "teal", "darkviolet", "gold", "darkorange", "deeppink"]

        x = np.linspace(-3, 3, 100)

        # setting the axes at the centre
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        ax.spines["left"].set_position("zero")
        ax.spines["bottom"].set_position("zero")
        ax.spines["right"].set_color("none")
        ax.spines["top"].set_color("none")
        ax.xaxis.set_ticks_position("bottom")
        ax.yaxis.set_ticks_position("left")
        counter = 0
        for i in range(len(interpolated_polynoms)):
            plt.plot(x, eval(
                interpolated_polynoms_parsed[i]), colors[counter], label=f"y={interpolated_polynoms[i]}")
            if counter < len(colors):
                counter += 1
            else:
                counter = 0
            # plot the function
        # plot the function
        plt.legend(loc="upper center")
        plt.savefig('plot.png')
        plt.close(fig)  
        button_close_plt_used()
   
def button_close_plt_used():
    plt.close(1)