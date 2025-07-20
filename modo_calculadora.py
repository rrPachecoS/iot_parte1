import math
import utime
from machine import Pin, I2C, ADC, PWM # Asegúrate de que estos imports estén en tu main.py o donde inicialices la OLED y el joystick
from ssd1306 import SSD1306_I2C # Necesitas esta librería SSD1306 para la OLED

# Operadores y funciones soportadas
operators = {'+':1, '-':1, '*':2, '/':2, '^':3}
functions = {'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
             'log': math.log, 'sqrt': math.sqrt, 'abs': abs}

# Teclado virtual
keyboard = [
    ['7','8','9','/','sin'],
    ['4','5','6','*','cos'],
    ['1','2','3','-','log'],
    ['0','.','x','+','sqrt'],
    ['(',')','^','[<]','[CLR]'],
    ['[OK]']
]

def tokenize(expr):
    """
    Realiza el análisis léxico de la expresión matemática.
    Divide la cadena de entrada en una lista de tokens (números, operadores, funciones, etc.).
    """
    tokens, i = [], 0
    while i < len(expr):
        c = expr[i]
        if c.isdigit() or c=='.':
            num = c; i += 1
            while i < len(expr) and (expr[i].isdigit() or expr[i]=='.'):
                num += expr[i]; i+=1
            tokens.append(num)
        elif c.isalpha():
            func = c; i += 1
            while i < len(expr) and expr[i].isalpha():
                func += expr[i]; i+=1
            tokens.append(func)
        elif c in operators or c in '(),':
            tokens.append(c); i+=1
        elif c=='x':
            tokens.append('x'); i+=1
        else:
            i+=1 # Ignorar espacios u otros caracteres no reconocidos
    return tokens

def to_rpn(tokens):
    """
    Convierte una lista de tokens a notación polaca inversa (RPN)
    utilizando el algoritmo Shunting-yard.
    """
    output, stack = [], []
    for token in tokens:
        if token in functions:
            stack.append(token)
        elif token=='x' or token.replace('.','',1).isdigit(): # Maneja números y 'x'
            output.append(token)
        elif token in operators:
            while stack and stack[-1] in operators and \
                operators[token]<=operators[stack[-1]]:
                output.append(stack.pop())
            stack.append(token)
        elif token=='(':
            stack.append(token)
        elif token==')':
            while stack and stack[-1]!='(':
                output.append(stack.pop())
            stack.pop() # Pop '('
            if stack and stack[-1] in functions: # Si hay una función antes del paréntesis
                output.append(stack.pop())
    while stack:
        output.append(stack.pop())
    return output

def eval_rpn(rpn, x_val):
    """
    Evalúa una expresión en notación polaca inversa (RPN)
    para un valor dado de 'x'.
    """
    stack = []
    for token in rpn:
        if token == 'x':
            stack.append(x_val)
        elif token.replace('.', '', 1).isdigit():
            stack.append(float(token))
        elif token in functions:
            if not stack:
                raise ValueError("Error de sintaxis: pila vacía para función")
            a = stack.pop()
            try:
                stack.append(functions[token](a))
            except Exception as e:
                # Manejo de errores para funciones como log(0) o sqrt(-1)
                # print(f"Error evaluating function {token}({a}): {e}") # Para depuración
                return float('nan') # Retorna NaN para valores indefinidos
        elif token in operators:
            if len(stack) < 2:
                raise ValueError("Error de sintaxis: pocos operandos para operador")
            b, a = stack.pop(), stack.pop()
            if token == '+': stack.append(a + b)
            elif token == '-': stack.append(a - b)
            elif token == '*': stack.append(a * b)
            elif token == '/': stack.append(a / b if b != 0 else float('nan')) # División por cero
            elif token == '^': stack.append(a ** b)
    return stack[0] if stack else 0

def draw_axes_advanced(oled, x_min, x_max, y_min, y_max):
    """
    Dibuja los ejes X e Y con marcas y escala basada en x_min, x_max, y_min, y_max.
    """
    oled.fill(0) # Limpiar pantalla antes de dibujar los ejes

    width, height = oled.width, oled.height
    
    # Calcular escalas de píxeles por unidad en los ejes
    x_scale_factor = width / (x_max - x_min)
    y_scale_factor = height / (y_max - y_min)
    
    # Calcular la posición del origen (0,0) en píxeles
    # El origen X se calcula desde x_min. Si x_min es -10, y el ancho es 128,
    # entonces 0 está a 10 unidades de distancia desde el borde izquierdo.
    origin_x_pixel = int(-x_min * x_scale_factor)
    # El origen Y se calcula desde y_max (parte superior de la pantalla).
    # Si y_max es 5 y la altura es 64, entonces 0 está a 5 unidades de distancia desde la parte superior.
    origin_y_pixel = int(y_max * y_scale_factor)
    
    # Asegurarse de que el origen esté dentro de los límites de la pantalla, o ajustar para dibujar lo que se pueda.
    # Si el origen está fuera de pantalla, los ejes se dibujarán en el borde más cercano.
    origin_x_pixel = max(0, min(origin_x_pixel, width - 1))
    origin_y_pixel = max(0, min(origin_y_pixel, height - 1))
    
    # Dibujar Eje X (horizontal)
    oled.hline(0, origin_y_pixel, width, 1) 
    # Dibujar Eje Y (vertical)
    oled.vline(origin_x_pixel, 0, height, 1)
    
    # Dibujar pequeñas marcas en el Eje X (cada unidad, si el rango lo permite)
    for x_val in range(int(x_min), int(x_max) + 1):
        if x_val != 0: # No dibujar marca en el origen otra vez
            # Convertir valor x a coordenada de píxel
            px = int((x_val - x_min) * x_scale_factor)
            # Dibujar marca vertical pequeña
            oled.vline(px, origin_y_pixel - 2, 5, 1) # Marca de 5 píxeles centrada en el eje

    # Dibujar pequeñas marcas en el Eje Y (cada unidad, si el rango lo permite)
    for y_val in range(int(y_min), int(y_max) + 1):
        if y_val != 0: # No dibujar marca en el origen otra vez
            # Convertir valor y a coordenada de píxel (recordar que 0,0 es arriba a la izquierda)
            py = int((y_max - y_val) * y_scale_factor)
            # Dibujar marca horizontal pequeña
            oled.hline(origin_x_pixel - 2, py, 5, 1) # Marca de 5 píxeles centrada en el eje

    # Retornar los factores de escala y el origen para plot_function
    return x_scale_factor, y_scale_factor, origin_x_pixel, origin_y_pixel


def draw_graph(oled, expr, xmin, xmax, ymin, ymax, cursor_x):
    """
    Dibuja la gráfica de la función en la pantalla OLED,
    incluyendo los ejes, la función y un cursor.
    """
    # Dibuja los ejes con el nuevo método avanzado
    x_scale_factor, y_scale_factor, origin_x_pixel, origin_y_pixel = draw_axes_advanced(oled, xmin, xmax, ymin, ymax)

    tokens = tokenize(expr)
    rpn = to_rpn(tokens)
    
    # Dibujar la función
    prev_px, prev_py = None, None
    for px in range(oled.width):
        # Convertir coordenada de píxel a valor x matemático
        x_val_at_pixel = xmin + (px / oled.width) * (xmax - xmin)
        
        try:
            y = eval_rpn(rpn, x_val_at_pixel)
            
            # Asegurarse de que el valor y esté dentro de los límites matemáticos definidos
            if math.isnan(y) or y < ymin or y > ymax:
                prev_px, prev_py = None, None # Romper la línea si el valor es inválido o fuera de rango
                continue

            # Escalar y al rango de píxeles de la pantalla
            # Recordar que la coordenada Y de la OLED aumenta hacia abajo
            py = int(oled.height - ((y - ymin) / (ymax - ymin)) * oled.height)
            
            # Asegurarse de que el punto esté dentro de los límites de la pantalla
            if 0 <= py < oled.height:
                if prev_px is not None and prev_py is not None:
                    # Dibujar línea entre puntos para una gráfica continua
                    oled.line(prev_px, prev_py, px, py, 1)
                else:
                    oled.pixel(px, py, 1) # Dibujar el primer punto
                prev_px, prev_py = px, py
            else:
                prev_px, prev_py = None, None # Romper la línea si el punto está fuera de pantalla (por redondeo, etc.)
        except Exception as e:
            # print(f"Error al evaluar en x={x_val_at_pixel}: {e}") # Para depuración
            prev_px, prev_py = None, None # Romper la línea si hay error en la evaluación

    # Dibujar cursor y mostrar valores de x e y
    # Mapear cursor_x al píxel horizontal
    cursor_px = int(((cursor_x - xmin) / (xmax - xmin)) * oled.width)
    
    if 0 <= cursor_px < oled.width:
        oled.vline(cursor_px, 0, oled.height, 1) # Dibujar línea vertical del cursor
        
        # Calcular el valor y en la posición del cursor
        try:
            cursor_y = eval_rpn(rpn, cursor_x)
            # Mostrar valores en la parte superior
            oled.text(f"x={cursor_x:.2f}", 0, 0)
            if not math.isnan(cursor_y):
                oled.text(f"y={cursor_y:.2f}", 0, 10)
            else:
                oled.text("y=NaN", 0, 10) # Mostrar NaN si el valor es indefinido
        except Exception:
            oled.text(f"x={cursor_x:.2f}", 0, 0)
            oled.text("y=ERR", 0, 10)
    
    oled.show()

def draw_keyboard(oled, expr, sel_row, sel_col):
    """
    Dibuja el teclado virtual en la pantalla OLED.
    """
    oled.fill(0)
    # Muestra la parte final de la expresión si es muy larga
    display_expr = expr if len(expr) <= 21 else "..." + expr[-18:] # Muestra los últimos 18 caracteres con puntos suspensivos
    oled.text(display_expr, 0, 0)
    
    y_start = 12 # Espacio para la expresión
    for row_idx, row in enumerate(keyboard):
        y = y_start + row_idx * 9
        for col_idx, key in enumerate(row):
            # Ajustar el ancho para la última fila con [OK]
            key_width = 22
            if key == '[OK]':
                x = 0  # Centrar el botón OK
                key_width = oled.width - 2 # Ajustar al ancho de la pantalla
            else:
                x = col_idx * 24 # Espacio para cada botón
                
            if row_idx == sel_row and col_idx == sel_col:
                oled.fill_rect(x, y, key_width, 8, 1)
                oled.text(key[:6], x + 1, y, 0) # Texto en color inverso
            else:
                oled.text(key[:6], x + 1, y, 1) # Texto normal
    oled.show()

def edit_expression(oled, get_direction, play_sound):
    """
    Permite al usuario ingresar una expresión matemática
    utilizando un teclado virtual y el joystick.
    """
    expr = ""
    sel_row, sel_col = 0, 0
    # Posiciones iniciales para el joystick para que el cursor no salte
    # Asumimos que get_direction devuelve "none" si no hay movimiento
    utime.sleep_ms(200) # Pequeña pausa inicial para que el joystick se asiente
    while True:
        draw_keyboard(oled, expr, sel_row, sel_col)
        dir = get_direction() # Obtener la dirección del joystick/botón
        
        if dir == "up":
            play_sound(300, 50)
            if sel_row > 0:
                sel_row -= 1
            else: # Wrap around to the last row
                sel_row = len(keyboard) - 1
            # Adjust col if new row is shorter
            if sel_col >= len(keyboard[sel_row]):
                sel_col = len(keyboard[sel_row]) - 1
        elif dir == "down":
            play_sound(300, 50)
            if sel_row < len(keyboard) - 1:
                sel_row += 1
            else: # Wrap around to the first row
                sel_row = 0
            # Adjust col if new row is shorter
            if sel_col >= len(keyboard[sel_row]):
                sel_col = len(keyboard[sel_row]) - 1
        elif dir == "left":
            play_sound(400, 50)
            if sel_col > 0:
                sel_col -= 1
            else: # Wrap around to the end of the row
                sel_col = len(keyboard[sel_row]) - 1
        elif dir == "right":
            play_sound(400, 50)
            if sel_col < len(keyboard[sel_row]) - 1:
                sel_col += 1
            else: # Wrap around to the beginning of the row
                sel_col = 0
        elif dir == "center":
            play_sound(600, 100)
            key = keyboard[sel_row][sel_col]
            if key == '[OK]':
                return expr
            elif key == '[CLR]':
                expr = ""
            elif key == '[<]':
                expr = expr[:-1] # Borrar último caracter
            else:
                expr += key
        elif dir == "double_click":
            play_sound(200, 100)
            play_sound(100, 100)
            return None # Salir al menú principal
        
        utime.sleep_ms(150) # Pequeña pausa para evitar múltiples entradas rápidas

def main(oled, get_direction, play_sound):
    """
    Función principal del modo calculadora/graficador.
    """
    # Iniciar con una expresión por defecto si no se ingresa ninguna
    expr = edit_expression(oled, get_direction, play_sound)
    if expr is None: # Si el usuario salió con doble click del teclado virtual
        return
    if not expr: 
        expr = "sin(x)" # Expresión por defecto si se dejó vacío

    xmin, xmax = -10.0, 10.0
    ymin, ymax = -5.0, 5.0 # Rango inicial de Y para mejor visualización
    cursor_x = 0.0

    while True:
        draw_graph(oled, expr, xmin, xmax, ymin, ymax, cursor_x)
        dir = get_direction()
        
        if dir == "left":
            play_sound(400, 50)
            # Mover cursor dentro del rango X
            cursor_x -= (xmax - xmin) / 20.0 
            cursor_x = max(min(cursor_x, xmax), xmin) # Asegurar que el cursor esté dentro del rango
        elif dir == "right":
            play_sound(400, 50)
            # Mover cursor dentro del rango X
            cursor_x += (xmax - xmin) / 20.0 
            cursor_x = max(min(cursor_x, xmax), xmin) # Asegurar que el cursor esté dentro del rango
        elif dir == "up":
            play_sound(500, 50)
            # Zoom In: reducir el rango x y y
            xmid = (xmin + xmax) / 2.0
            ymid = (ymin + ymax) / 2.0
            x_span = (xmax - xmin) / 2.0 / 1.2 # Reducir el span en un factor
            y_span = (ymax - ymin) / 2.0 / 1.2
            xmin, xmax = xmid - x_span, xmid + x_span
            ymin, ymax = ymid - y_span, ymid + y_span
            cursor_x = max(min(cursor_x, xmax), xmin) # Asegurar que el cursor siga en el rango
        elif dir == "down":
            play_sound(500, 50)
            # Zoom Out: aumentar el rango x y y
            xmid = (xmin + xmax) / 2.0
            ymid = (ymin + ymax) / 2.0
            x_span = (xmax - xmin) / 2.0 * 1.2 # Aumentar el span en un factor
            y_span = (ymax - ymin) / 2.0 * 1.2
            xmin, xmax = xmid - x_span, xmid + x_span
            ymin, ymax = ymid - y_span, ymid + y_span
            cursor_x = max(min(cursor_x, xmax), xmin) # Asegurar que el cursor siga en el rango
        elif dir == "double_click":
            play_sound(200, 100)
            play_sound(100, 100)
            break # Salir al menú principal
        
        utime.sleep_ms(100) # Pequeña pausa