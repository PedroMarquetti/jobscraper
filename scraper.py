import requests as req
from bs4 import BeautifulSoup as bs
from datetime import datetime
import re

today = datetime.today().strftime('%Y-%m-%d')
regex = r"(.*[Ll][A|a][B|b].*)|(.*[Bb][Ii][oO].*)"  # filtrando vagas..
USR_AGENT = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:99.0) Gecko/20100101 Firefox/99.0"

# TODO: make all this async


class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def get_s_lucas():  # lab s. Lucas
    get = req.request(
        "GET",
        r"https://api.solides.jobs/v2/vacancy/search?reference_id=92055&search=&vacancyType=jobs",
        headers={
            "User-Agent": USR_AGENT
        }
    )
    return get.json()


def get_diag_br():  # DB diag. do Brasil
    post = req.request(
        "POST", "https://platform.senior.com.br/t/senior.com.br/bridge/1.0/anonymous/rest/hcm/vacancymanagement/queries/searchPublicVacancies",
        headers={
                "Host": "platform.senior.com.br",
                "User-Agent": USR_AGENT,
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
            "currentDate": today,
            "order": "HIGHLIGHT",
            "page": 0,
            "size": 100
        }
    )
    return post.json()


def get_diagbr_info(id: str):  # links para as postagens
    post = req.request(
        "POST", "https://platform.senior.com.br/t/senior.com.br/bridge/1.0/anonymous/rest/hcm/vacancymanagement/queries/publishedVacancyDetails",
        headers={
                "Host": "platform.senior.com.br",
                "User-Agent": USR_AGENT,
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "pt-BR",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": f"https://platform.senior.com.br/hcmrs/hcm/curriculo/?tenant=dbdiagnosticos&tenantdomain=dbdiagnosticos.com.br&vacancyId={id}&fromRecruitment=false",
                "Content-Type": "application/json;charset=utf-8",
                "x-tenant": "dbdiagnosticos",
                "X-TenantDomain": "dbdiagnosticos.com.br",
                "Origin": "https://platform.senior.com.br",
        },

        json={
            "id": f"{id}",
            "currentDate": today
        }
    )
    return post.json()


def sabin():
    jobs = []
    get = req.request(
        "GET", "https://jobs.kenoby.com/sabin-site/position?search=&=")
    soup = bs(get.text, "lxml")
    area_tecnica = soup.find_all(
        "a",
        {
            "data-segment": "Área Técnica",
            "data-state": "SP",
            "data-title": re.compile(regex)
        }
    )
    for items in area_tecnica:
        name = items["data-title"]
        city = items["data-city"]
        neighborhood = items["data-neighborhood"]
        state = items["data-state"]
        link = items["href"]
        jobs.append(
            {
                "name": name,
                "city": city,
                "neighborhood": neighborhood,
                "state": state,
                "link": link,
                "qtd": len(area_tecnica)
            }
        )

    return jobs


def main():
    db = get_diag_br()
    s_lucas = get_s_lucas()
    lab_sabin = sabin()

    print(f"{Colors.HEADER}Hoje é: {today}\nColetando dados...\n\n{Colors.ENDC}")
    print(
        f"{Colors.BOLD}S. Lucas possui {s_lucas['totalRecords']} vagas:{Colors.ENDC}")
    for item in s_lucas["data"]:
        nome_vaga = item["name"]
        cidade = item["city"]["name"]
        empresa = item["company"]["name"]
        url = item["linkVacancy"]
        print(
            f"""
        \r{Colors.OKGREEN}Vaga: {nome_vaga}{Colors.ENDC}
        \rCidade: {cidade}
        \rEmpresa: {empresa}
        \rLink: {url}
    """)

    print(
        f"{Colors.BOLD}\n\nDB Diagnósticos possui {db['found']} vagas, \nMostrando aquelas que contém Biomédico ou Laboratório: {Colors.ENDC}"
    )

    for items in db["vacancies"]:
        vaga_titulo = items["title"]
        vaga_local = items["location"]
        vaga_id = items["id"]
        if bool(re.search(regex, vaga_titulo)):
            link = f"https://platform.senior.com.br/hcmrs/hcm/curriculo/?tenant=dbdiagnosticos&tenantdomain=dbdiagnosticos.com.br&vacancyId={vaga_id}&fromRecruitment=false#!/vacancies/details/{vaga_id}/?order=HIGHLIGHT&page=0&fromRecruitment=false"
            mais_info = get_diagbr_info(vaga_id)
            print(
                f"""
                \r{Colors.OKGREEN}Vaga: {vaga_titulo}{Colors.ENDC}
                \rLocal: {vaga_local}
                \rLink da vaga: {link}
                \rData-fim da vaga: {mais_info['endDate']}
                """
            )
    print(
        f"{Colors.BOLD}\n\nSabin Med. Diag {lab_sabin[0]['qtd']} vagas, \nMostrando aquelas que contém Biomédico ou Laboratório: {Colors.ENDC}"
    )
    for items in lab_sabin:
        print(
            f"""
            \r{Colors.OKGREEN}Vaga: {items["name"]} {Colors.ENDC}
            \rlocal: {items["city"]} - {items["state"]}
            link: \r{items["link"]}
            """
        )


if __name__ == '__main__':
    main()
