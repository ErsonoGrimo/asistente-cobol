import streamlit as st
import os

from PyPDF2 import PdfReader
from langchain.chat_models import ChatOpenAI
from langchain.chains.question_answering import load_qa_chain
from langchain.schema import HumanMessage
from langchain.prompts import PromptTemplate 
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain

# LEER PDF CON CONTEXTO PARA LA CREACION DE TABLAS
inputFile = "table.pdf"
pdf = open(inputFile, "rb")



pdf_reader = PdfReader(pdf)
contexto_tabla = ""
for page in pdf_reader.pages:
    contexto_tabla += page.extract_text()

# MODELO
# Add a slider to the sidebar:
with st.sidebar:
    st.sidebar.title("ASISTENTE COBOL")
    pregunta_esqueleto = st.text_input("Describe un proceso puro para hacer en COBOL")
    pregunta_tabla = st.text_input("Cuentame que tabla quieres crear en DB2")
    OPENAI_API_KEY = st.text_input('OpenAI API Key', type='password')


if OPENAI_API_KEY:
    os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY 
    chat = ChatOpenAI(model_name='gpt-3.5-turbo')

if pregunta_esqueleto:

    #Cadena para crear las tablas.
    prompt_esqueleto = '''Eres un experto en DB2, COBOL Y JCL. 
     Genera un programa COBOL simple y escribe en la PROCEDURE DIVISION un PARRAFO que realice la acción que te especifico ahora:
      {preguntaesqueleto}
      
      Ten en cuenta lo siguiente. El nombre del PARRAFO debe ser corto de no mas de 10 caracteres y que sea un nombre
      con relación a la tarea que se especifica se quiere hacer.

      '''
    chain_esqueleto = LLMChain(llm=chat, prompt=PromptTemplate.from_template(prompt_esqueleto))

    respuesta_esqueleto = chain_esqueleto.run({ "preguntaesqueleto":pregunta_esqueleto})
    import streamlit as st

    st.header('Aquí tienes tu proceso puro COBOL', divider='rainbow')
    st.header('_Esperamos que te_  :blue[guste] :santa:')
    st.code(respuesta_esqueleto, language='cobol')

else:

    if pregunta_tabla:

        #Cadena para crear las tablas.
        prompt_tabla = "Eres un experto en DB2, COBOL Y JCL. Quiero que resuelvas, usando estas directrices: ' {contextotabla} ', la siguiente solicitud de creacion de tabla del usuario: {preguntatabla}"

        chain_tabla = LLMChain(llm=chat, prompt=PromptTemplate.from_template(prompt_tabla))

        respuesta_tabla = chain_tabla.run({"contextotabla": contexto_tabla, "preguntatabla":pregunta_tabla})

        #Cadena crear programa de mantenimiento tabla

        prompt_programa = '''Eres un experto programador en COBOL
        
        Con la información detallada de esta tabla: {resputatabla} crea un programa cobol con las siguientes instrucciones:
        Este programa realizará el mantenimiento de la tabla y debe realizar estas 4 funciones con instrucciones SLQ DB2: 
        Dar de alta un registro con INSERT INTO
        Modificar un registro con UPDATE
        Eliminar un registro
        Consultar un registro.

        Este SERA UN SUBPROGRAMA, se podra llamar desde otros programas y se comunicara con un registro desde la LINKAGE-SECTION.

        EL registro se escribirá en la LINKAGE-SECTION del programa y tendra los siguientes campos:

        Un campo OPCIÓN para indicarle que funcion de las 4 anteriores debe realizar y que tendran los valores.

        OPCION = 'A' Dar de alta un registro con INSERT INTO
        OPCION = 'M' Modificar un registro con UPDATE
        OPCION = 'E' Eliminar un registro
        OPCION = 'C' Consultar un registro

        Este campo se llamara OPCION y tendra niveles 88 con esos 4 valores.

        El resto de Campos del registro de la LINKAGE tendra los campos cobol de la tabla

        Ademas de un campo RESULTADO, que el programa informará con OK si la operación ha ido bien o KO si ha ido mal

        Cada funcion del programa irá en un parrafo diferente

        Utiliza la instruccion EVALUTE en lugar de IF

        Crea el programa de forma que se pueda copiar y escribe SOLO CODIGO COBOL no incluyas frases tuyas
        NO ESCRIBAS algo como : 'Aquí tienes el código COBOL para el programa que realiza el mantenimiento de la tabla...',
        repito SOLO CODIGO COBOL

        ESTRUCTURA DE EJEMPLO.

        Crea el programa COBOL siguiendo la ESTRUCTURA DE codigo de ejemplo que te pongo a continuación:

        IDENTIFICATION DIVISION.
    PROGRAM-ID. MANTENIMIENTO-TABLA.

    AUTHOR. ERSONO.
    DATA DIVISION.
    WORKING-STORAGE SECTION.

    LINKAGE-SECTION
    01 ALUMNO-REG.
    02 ID PIC S9(9) COMP.
    02 NOMBRE PIC X(50).
    02 FECHA-NACIMIENTO PIC X(10).
    02 DIRECCION PIC X(80).
    02 OBSERVACIONES PIC X(150).
    02 IMPORTE PIC S9(13)V99.
    01 OPCION PIC X.
    88 OPCION-ALTA VALUE 'A'.
    88 OPCION-MODIFICAR VALUE 'M'.
    88 OPCION-ELIMINAR VALUE 'E'.
    88 OPCION-CONSULTAR VALUE 'C'.
    01 RESULTADO PIC X(2).
    88 OK VALUE 'OK'.
    88 KO VALUE 'KO'.

    PROCEDURE DIVISION USING ALUMNO-REG.

    PERFORM INICIO
    PERFORM PROCESO
    GO TO FINALIZAR


    INICIO.
        MOVE ESPACES TO RESULTADO.

    PROCESO.
        EVALUATE TRUE
            WHEN OPCION-ALTA
                PERFORM DAR-DE-ALTA
            WHEN OPCION-MODIFICAR
                PERFORM MODIFICAR
            WHEN OPCION-ELIMINAR
                PERFORM ELIMINAR
            WHEN OPCION-CONSULTAR
                PERFORM CONSULTAR
            WHEN OTHER
                MOVE 'KO' TO RESULTADO
        END-EVALUATE.

        DISPLAY 'Resultado: ' RESULTADO.
    FINALIZAR.
        STOP RUN.

    DAR-DE-ALTA.
        EXEC SQL
            INSERT INTO alumnos 
            (nombre, 
            fecha_nacimiento, 
            direccion, 
            observaciones, 
            importe)
            VALUES (:NOMBRE, 
            :FECHA-NACIMIENTO, 
            :DIRECCION, 
            :OBSERVACIONES, 
            :IMPORTE)
        END-EXEC.
        IF SQLCODE = 0
            MOVE 'OK' TO RESULTADO
        ELSE
            MOVE 'KO' TO RESULTADO.

    MODIFICAR.
        EXEC SQL
            UPDATE alumnos
            SET nombre = :NOMBRE, 
            fecha_nacimiento = :FECHA-NACIMIENTO, 
            direccion = :DIRECCION,
            observaciones = :OBSERVACIONES, 
            importe = :IMPORTE
            WHERE id = :ID
        END-EXEC.

        IF SQLCODE = 0
            MOVE 'OK' TO RESULTADO
        ELSE
            MOVE 'KO' TO RESULTADO.

    ELIMINAR.
        EXEC SQL
            DELETE FROM alumnos
            WHERE id = :ID
        END-EXEC.
        IF SQLCODE = 0
            MOVE 'OK' TO RESULTADO
        ELSE
            MOVE 'KO' TO RESULTADO.

    CONSULTAR.
        EXEC SQL
            SELECT id, nombre, 
            fecha_nacimiento, 
            direccion, 
            observaciones, 
            importe
            INTO :ID, :NOMBRE, 
            :FECHA-NACIMIENTO, 
            :DIRECCION, 
            :OBSERVACIONES, 
            :IMPORTE
            FROM alumnos
            WHERE id = :ID
        END-EXEC.
        IF SQLCODE = 0
            MOVE 'OK' TO RESULTADO
        ELSE
            MOVE 'KO' TO RESULTADO.


    Asta aquí el ejemplo de programa.

    IMPORTANTE, debes de escribir el codigo de forma que ocupe las columanas para que en COBOL
    pueda funcionar. En cada linea tienes que dejar los espacios en blanco necesarios para que la instruccion
    comience en la columna que debe.
    '''

        chain_programa = LLMChain(llm=chat, prompt=PromptTemplate.from_template(prompt_programa))

        respuesta_programa = chain_programa.run({"resputatabla": respuesta_tabla})

        st.header('Aquí tienes tu mantenimiento en COBOL', divider='rainbow')
        st.header('_Esperamos que te_  :blue[guste] :santa:')
        st.code(respuesta_programa, language='cobol')

        prompt_sql = "Eres un experto en DB2. Quiero que resuelvas, usando estos dato ' {resputatabla} ', crees el codigo SQL, DB2 para crear la tabla y su indice único.Tambien el registro COBOL para los campos de la tabla. NO DES MÁS SUGERENCIAS QUE ESTO QUE TE PIDO"

        chain_sql = LLMChain(llm=chat, prompt=PromptTemplate.from_template(prompt_sql))

        respuesta_SQL = chain_sql.run({"resputatabla": respuesta_tabla})

        st.code(respuesta_SQL, language='sql')
    else:

        st.title ("Asistente IA para desarrollar COBOL en un Mainframe")
        st.header('Laboratorio de desarrolllo', divider='rainbow')
        st.header('_by_  :blue[Ersono] :santa:')
        st.text ('''     Estamos desarrollando un asistente que te permita codificar tus programas COBOL
        de forma automatizada con breves indicaciones el el SIDEBAR de tu derecha.

        Por ahora solo hemos implementado que pudas pedir un proceso puro que 
        se te mostrara en un programa COBOL simple dentro de un parrafo para 
        que lo puedas probar y validar.

        Y un uso más potente donde puedes darle instrucciones sobre una tabla
        y te crea el código en DB2 para poder generarla en el Mainframe
        y un módulo de mantenimiento en COBOL.

        Seguiremos ampliando este asistente y mejorandolo hasta que 
        sea funcional.''', )