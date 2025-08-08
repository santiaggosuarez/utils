import random

def juego_adivinanza():
    print("¡Bienvenido al juego de adivinanzas de TechGames!")
    print("Por favor, establece el rango de números y los intentos.")
    
    while True:
        try:
            limite_inferior = int(input("Ingresa el límite inferior del rango: "))
            limite_superior = int(input("Ingresa el límite superior del rango: "))
            
            if limite_superior <= limite_inferior:
                print("El límite superior debe ser mayor que el inferior. Intenta nuevamente.")
                continue
                
            intentos_maximos = int(input("Ingresa la cantidad máxima de intentos: "))
            
            if intentos_maximos < 1:
                print("Debe haber al menos 1 intento. Intenta nuevamente.")
                continue
                
            break
        except ValueError:
            print("Por favor ingresa solo números enteros. Intenta nuevamente.")

    numero_secreto = random.randint(limite_inferior, limite_superior)
    print(f"\n¡He elegido un número entre {limite_inferior} y {limite_superior}!")
    print(f"Tienes {intentos_maximos} intentos para adivinarlo. ¡Buena suerte!\n")

    intentos = 0
    adivinado = False
    
    while intentos < intentos_maximos and not adivinado:
        try:
            intento = int(input(f"Intento {intentos + 1} - Ingresa tu número: "))
            
            if intento < limite_inferior or intento > limite_superior:
                print(f"El número debe estar entre {limite_inferior} y {limite_superior}.")
                continue
                
            if intento == numero_secreto:
                adivinado = True
                print(f"\n¡Felicidades! ¡Adivinaste el número en {intentos + 1} intentos!")
            elif intento < numero_secreto:
                print("El número secreto es mayor. ¡Sigue intentando!")
            else:
                print("El número secreto es menor. ¡Sigue intentando!")
                
            intentos += 1
            
        except ValueError:
            print("Por favor ingresa solo números enteros.")

    if not adivinado:
        print(f"\n¡Agotaste tus intentos! El número secreto era {numero_secreto}.")

    print("\n¡Gracias por jugar al juego de adivinanzas de TechGames!")

juego_adivinanza()


"""
Muestra de la salida en consola:

¡Bienvenido al juego de adivinanzas de TechGames!
Por favor, establece el rango de números y los intentos.
Ingresa el límite inferior del rango: 1
Ingresa el límite superior del rango: 10
Ingresa la cantidad máxima de intentos: 3

¡He elegido un número entre 1 y 10!
Tienes 3 intentos para adivinarlo. ¡Buena suerte!

Intento 1 - Ingresa tu número: 5
El número secreto es mayor. ¡Sigue intentando!
Intento 2 - Ingresa tu número: 8
El número secreto es menor. ¡Sigue intentando!
Intento 3 - Ingresa tu número: 7

¡Felicidades! ¡Adivinaste el número en 3 intentos!

¡Gracias por jugar al juego de adivinanzas de TechGames!
"""
