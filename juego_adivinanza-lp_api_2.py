import random

def juego_adivinanza():
    print("""
    **************************************
    *   JUEGO DE ADIVINANZAS TECHGAMES   *
    *                                    *
    *  ¡Adivina el número secreto!       *
    **************************************
    """)
    while True:
        try:
            print("\nConfiguración del juego:")
            limite_inferior = int(input("Ingresa el número MÍNIMO del rango: "))
            limite_superior = int(input("Ingresa el número MÁXIMO del rango: "))
            
            if limite_superior <= limite_inferior:
                print("\n¡Error! El número máximo debe ser mayor que el mínimo.")
                print(f"Has ingresado: mínimo={limite_inferior}, máximo={limite_superior}")
                continue
                
            intentos_maximos = int(input("¿Cuántos intentos deseas tener? "))
            
            if intentos_maximos < 1:
                print("\n¡Debes tener al menos 1 intento!")
                continue
                
            break
        except ValueError:
            print("\n¡Oops! Solo se permiten números enteros. Intenta nuevamente.")

    numero_secreto = random.randint(limite_inferior, limite_superior)
    
    print(f"""
    \n¡LISTO! He elegido un número entre {limite_inferior} y {limite_superior}.
    Tienes {intentos_maximos} intentos para adivinarlo.
    ¡Buena suerte!
    """)

    intentos = 0
    adivinado = False
    
    while intentos < intentos_maximos and not adivinado:
        try:
            intentos_restantes = intentos_maximos - intentos
            print(f"\n--- Intento {intentos + 1} de {intentos_maximos} ---")
            print(f"Intentos restantes: {intentos_restantes}")
            
            intento = int(input("Ingresa tu número: "))
            
            if intento < limite_inferior or intento > limite_superior:
                print(f"\n¡Fuera de rango! El número debe estar entre {limite_inferior} y {limite_superior}.")
                print("Este intento no cuenta. ¡Intenta con un número válido!")
                continue
                
            if intento == numero_secreto:
                adivinado = True
                print(f"""
                \n¡FELICITACIONES! 🎉
                ¡Adivinaste el número secreto ({numero_secreto}) en {intentos + 1} intentos!
                """)
            else:
                diferencia = abs(numero_secreto - intento)
                if intento < numero_secreto:
                    mensaje = "MAYOR"
                else:
                    mensaje = "MENOR"
                
                if diferencia > 50:
                    pista = "¡Estás muy lejos!"
                elif diferencia > 20:
                    pista = "¡Todavía lejos!"
                elif diferencia > 10:
                    pista = "¡Cerca!"
                else:
                    pista = "¡Muy cerca!"
                
                print(f"\nEl número secreto es {mensaje} que {intento}. {pista}")
                
            intentos += 1
            
        except ValueError:
            print("\n¡Error! Solo se permiten números enteros. Este intento no cuenta.")

    if not adivinado:
        print(f"""
        \n¡LO SIENTO! 😢
        Has agotado tus {intentos_maximos} intentos.
        El número secreto era: {numero_secreto}
        """)

    jugar_nuevamente = input("\n¿Quieres jugar otra vez? (s/n): ").lower()
    if jugar_nuevamente == 's':
        juego_adivinanza()
    else:
        print("\n¡Gracias por jugar al juego de adivinanzas de TechGames! ¡Hasta pronto!")


juego_adivinanza()

"""
Muestra de lo arrojado en consola:

    **************************************
    *   JUEGO DE ADIVINANZAS TECHGAMES   *
    *                                    *
    *  ¡Adivina el número secreto!       *
    **************************************

Configuración del juego:
Ingresa el número MÍNIMO del rango: 1
Ingresa el número MÁXIMO del rango: 10
¿Cuántos intentos deseas tener? 3

    
¡LISTO! He elegido un número entre 1 y 10.
    Tienes 3 intentos para adivinarlo.
    ¡Buena suerte!
    

--- Intento 1 de 3 ---
Intentos restantes: 3
Ingresa tu número: 5

El número secreto es MAYOR que 5. ¡Muy cerca!

--- Intento 2 de 3 ---
Intentos restantes: 2
Ingresa tu número: 8

El número secreto es MAYOR que 8. ¡Muy cerca!

--- Intento 3 de 3 ---
Intentos restantes: 1
Ingresa tu número: 9

                
¡FELICITACIONES! 🎉
                ¡Adivinaste el número secreto (9) en 3 intentos!
                

¿Quieres jugar otra vez? (s/n): n

¡Gracias por jugar al juego de adivinanzas de TechGames! ¡Hasta pronto!
"""
