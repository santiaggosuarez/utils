#!/bin/bash

# Parámetro que indica cuántas queries se agrupan por ejecución
QUERIES_POR_EJECUCION=3

# Leer CSV y procesar cada fila
while IFS=',' read -r name queries fake_group fake_type fake_detailed_type likely_face_id link
do
    # Saltar la primera línea si es el encabezado
    if [[ "$name" == "name" ]]; then
        continue
    fi

    # Eliminar comillas de la columna queries
    queries=$(echo "$queries" | sed 's/"//g')

    # Convertir la columna queries a un array usando solo la coma como separador
    IFS=',' read -r -a queries_array <<< "$queries"

    # Particionar queries en grupos según QUERIES_POR_EJECUCION
    for (( i=0; i<${#queries_array[@]}; i+=QUERIES_POR_EJECUCION )); do
        # Crear un array con las queries en el chunk actual, recortando espacios adicionales
        queries_chunk=("${queries_array[@]:i:QUERIES_POR_EJECUCION}")
        
        # Unir las queries en una sola cadena separada por comas, eliminando espacios extra
        queries_str=$(IFS=', '; echo "${queries_chunk[*]}" | sed 's/^ *//;s/ *$//')

        echo "Procesando las queries: $queries_str"

        # Ejecutar update_settings con las variables obtenidas
        nice -n 10 python3 src/main/python/crawlers/update_settings.py src/test/files/config/execution.ini "search_settings+queries+${queries_str}"
        nice -n 10 python3 src/main/python/crawlers/update_settings.py src/test/files/config/execution.ini "dataset_info+fake_group+${fake_group}"
        nice -n 10 python3 src/main/python/crawlers/update_settings.py src/test/files/config/execution.ini "dataset_info+fake_type+${fake_type}"
        nice -n 10 python3 src/main/python/crawlers/update_settings.py src/test/files/config/execution.ini "dataset_info+fake_info.fake_detailed_type+${fake_detailed_type}"
        nice -n 10 python3 src/main/python/crawlers/update_settings.py src/test/files/config/execution.ini "dataset_info+fake_info.ss_inventory_id+${likely_face_id}"
        nice -n 10 python3 src/main/python/crawlers/update_settings.py src/test/files/config/execution.ini "likely_face_info+likely_face_identifier+fake_info.ss_inventory_id"

        # Ejecutar dataset_builder
        nice -n 10 python3 src/main/python/crawlers/dataset_builder.py --execution src/test/files/config/execution.ini --user src/test/files/config/user.ini --sources src/main/files/config/source_config --hashes src/main/files/existing_hashes --ids src/main/files/ids_management
    done

done < "/mnt/6a32262d-10d7-4d1f-afd1-e1a2e3db7aed/Descargas/[SS] Configuración crawler - inventario_fakes.csv"


<<COMMENT
chmod +x src/test/files/config/run_fakes_inventoried.sh
./src/test/files/config/run_fakes_inventoried.sh
COMMENT
