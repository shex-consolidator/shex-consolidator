entrada = input("Voy a seguir haciendo cosas hasta que escribas X: ")
while entrada != "X":
    "Comienza el bucle..."
    while True:
        print("Esto es un bucle con un while True... se supone que es infinito, no puede terminar")
        print("Pero si ejecuto break, obligo al programa a terminar este bucle.")
        print("Verás que el print de la línea 9 no aparece. Porque break hace que este while termine")
        break
        print("ESTO NO SE IMPRIME, ESTÁ DESPUÉS DEL BRAKE")
    print("Pero el break solo se termina ese bucle. Esta sentencia ya pertenece al bucle más externo (línea 2). "
          "Así que vuelta a empezar con el bucle más externo")
    entrada = input("Escribe algo de nuevo. Voy a seguir haciendo cosas hasta que escribas X: ")