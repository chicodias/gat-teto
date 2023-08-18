# -*- coding: utf-8 -*-
"""tjsp.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1fqRZ68AyMltTs62AggtqMPcMa3XBTgt7
"""

import requests

# note: its needed to ahve an open session in https://esaj.tjsp.jus.br/cjsg/resultadoCompleta.do
url = "https://esaj.tjsp.jus.br/cjsg/resultadoCompleta.do"
headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "pt-BR,en-US;q=0.7,en;q=0.3",
    "Content-Type": "application/x-www-form-urlencoded",
    "Cookie": "JSESSIONID=B2C7FE00CAE1080EC3FC49E5E74EE31D.cjsg2; K-JSESSIONID-lnmpmgnp=FD8E6FF9C539FD93981EFDE8CBBD6D7D",
    "DNT": "1",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0",
}


data = {
    "conversationId": "",
    "dados.buscaInteiroTeor": "gat+E+teto",
    "dados.pesquisarComSinonimos": ["S", "S"],
    "dados.buscaEmenta": "",
    "dados.nuProcOrigem": "",
    "dados.nuRegistro": "",
    "agenteSelectedEntitiesList": "",
    "contadoragente": "0",
    "contadorMaioragente": "0",
    "codigoCr": "",
    "codigoTr": "",
    "nmAgente": "",
    "juizProlatorSelectedEntitiesList": "",
    "contadorjuizProlator": "0",
    "contadorMaiorjuizProlator": "0",
    "codigoJuizCr": "",
    "codigoJuizTr": "",
    "nmJuiz": "",
    "classesTreeSelection.values": "",
    "classesTreeSelection.text": "",
    "assuntosTreeSelection.values": "",
    "assuntosTreeSelection.text": "",
    "comarcaSelectedEntitiesList": "",
    "contadorcomarca": "0",
    "contadorMaiorcomarca": "0",
    "cdComarca": "",
    "nmComarca": "",
    "secoesTreeSelection.values": "",
    "secoesTreeSelection.text": "",
    "dados.dtJulgamentoInicio": "",
    "dados.dtJulgamentoFim": "",
    "dados.dtPublicacaoInicio": "",
    "dados.dtPublicacaoFim": "",
    "dados.origensSelecionadas": ["T", "R"],
    "tipoDecisaoSelecionados": "A",
    "dados.ordenarPor": "dtPublicacao",
}


response = requests.post(url, data=data, headers=headers)

# Print the response
# it should return [200] (Ok)
print(response)

from bs4 import BeautifulSoup
import pandas as pd
import requests


def extract_data(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    data_list = []

    # Iterate through rows with class 'ementaClass' to extract Acordao and Ementa
    for row in soup.find_all("tr", class_="ementaClass"):
        data = {}
        acordao_anchor = row.find("a", title="Visualizar Inteiro Teor")
        data["Acordao"] = acordao_anchor.text.strip() if acordao_anchor else ""

        ementa_div = row.find("div", class_="mensagemSemFormatacao")
        data["Ementa"] = ementa_div.text.strip() if ementa_div else ""

        # Find the next sibling row(s) with class 'ementaClass2' and extract other fields
        sibling_row = row.find_next_sibling("tr", class_="ementaClass2")
        while sibling_row:
            field_name = sibling_row.strong.text.strip().replace(":", "")
            field_value = sibling_row.td.text.replace(
                sibling_row.strong.text, ""
            ).strip()
            data[field_name] = field_value
            sibling_row = sibling_row.find_next_sibling("tr", class_="ementaClass2")

        data_list.append(data)

    return pd.DataFrame(data_list)


# Master DataFrame to store all the data
df_master = pd.DataFrame()

# Number of pages (adjust based on the total number of entries) - 1215
total_pages = 61

# Iterate through the pages
for page_number in range(1, total_pages + 1):
    url = f"https://esaj.tjsp.jus.br/cjsg/trocaDePagina.do?tipoDeDecisao=A&pagina={page_number}&conversationId="
    response = requests.get(url, data=data, headers=headers)
    if response.status_code == 200:
        df_page = extract_data(response.text)
        df_master = pd.concat([df_master, df_page], ignore_index=True)
        print(f"Scraped page {page_number}")
    else:
        print(f"Error on page {page_number}")

# Print or save the master DataFrame
# print(df_master)

df_master

df_master.to_csv("gat.csv", index=False)