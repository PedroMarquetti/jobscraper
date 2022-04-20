import requests as req
from bs4 import BeautifulSoup as bs
from datetime import datetime
import re


def get_s_lucas():  # lab s. Lucas
    get = req.request(
        "GET",
        r"https://api.solides.jobs/v2/vacancy/search?reference_id=92055&search=&vacancyType=jobs",
        headers={
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:99.0) Gecko/20100101 Firefox/99.0"
        }
    )
    return get.json()


def get_diag_br(date: str):  # DB diag. do Brasil
    post = req.request(
        "POST", "https://platform.senior.com.br/t/senior.com.br/bridge/1.0/anonymous/rest/hcm/vacancymanagement/queries/searchPublicVacancies",
        headers={
                "Host": "platform.senior.com.br",
                "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:99.0) Gecko/20100101 Firefox/99.0",
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "pt-BR",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": "https://platform.senior.com.br/hcmrs/hcm/curriculo/?tenant=dbdiagnosticos&tenantdomain=dbdiagnosticos.com.br",
                "Content-Type": "application/json;charset=utf-8",
                "x-tenant": "dbdiagnosticos",
                "X-TenantDomain": "dbdiagnosticos.com.br",
                "Origin": "https://platform.senior.com.br",
        },

        json={
            "q": "",
            "hqId": "",
            "currentDate": date,
            "order": "HIGHLIGHT",
            "page": 0,
            "size": 100
        }
    )
    return post.json()


if __name__ == '__main__':
    today = datetime.today().strftime('%Y-%m-%d')
    s_lucas = get_s_lucas()
    db = get_diag_br(today)
    print(f"Hoje é:{today}\nColetando dados...\n\n")
    print(f"S. Lucas possui {s_lucas['totalRecords']} vagas: ")
    for item in s_lucas["data"]:
        nome_vaga = item["name"]
        cidade = item["city"]["name"]
        empresa = item["company"]["name"]
        url = item["linkVacancy"]
        print(
            f"""
        \rVaga: {nome_vaga}
        \rCidade: {cidade}
        \rEmpresa: {empresa}
        \rLink: {url}
    """)

    print(
        f"\n\nDB Diagnósticos possui {db['found']} vagas, \nMostrando aquelas que contém Biomédico ou Laboratório:"
    )
    # TODO: make this async??

    for items in db["vacancies"]:
        vaga_titulo = items["title"]
        vaga_local = items["location"]
        regex = r"(.LAB.)|(.?BIO.)"  # filtrando vagas..
        if bool(re.search(regex, vaga_titulo)):
            print(
                f"""
                \rVaga: {vaga_titulo}
                \rLocal: {vaga_local}
                """
            )
