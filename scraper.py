import requests as req
from bs4 import BeautifulSoup as bs
from datetime import datetime
import re
import time

TODAY = datetime.today().strftime('%Y-%m-%d')
REGEX = r"(.*[Ll][Aa][Bb].*)|(.*[Bb][Ii][oO].*)"  # filtrando vagas..
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
        "https://api.solides.jobs/v2/vacancy/search?reference_id=92055&search=&pagination=255&vacancyType=jobs",
        headers={
            "User-Agent": USR_AGENT
        }
    )
    return get.json()


def get_biofast():  # lab biofast
    get = req.request(
        "GET",
        "https://api.solides.jobs/v2/vacancy/search?reference_id=83325&search=&pagination=255&vacancyType=jobs",
        headers={
            "User-Agent": USR_AGENT
        }
    )
    return get.json()


def get_pasteur():  # lab s. Lucas
    get = req.request(
        "GET",
        "https://api.solides.jobs/v2/vacancy/search?reference_id=107102&page=1&pagination=255&vacancyType=jobs",
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
            "currentDate": TODAY,
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
            "currentDate": TODAY
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
            "data-title": re.compile(REGEX)
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
    print(f"{Colors.HEADER}Hoje é: {TODAY}\nColetando dados...\n\n{Colors.ENDC}")

    biofast = get_biofast()
    s_lucas = get_s_lucas()
    db = get_diag_br()
    lab_sabin = sabin()
    pasteur = get_pasteur()

    if s_lucas['totalRecords'] == 0:
        print(f"{Colors.FAIL}Nenhuma vaga para S. Lucas{Colors.ENDC}")
    else:
        print(
            f"{Colors.BOLD}S. Lucas possui {s_lucas['totalRecords']} vagas:{Colors.ENDC}"
        )
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
                """
            )

    if biofast['totalRecords'] == 0:
        print(f"{Colors.FAIL}Nenhuma vaga para S. Lucas{Colors.ENDC}")
    else:
        print(
            f"{Colors.BOLD}Biofast possui {biofast['totalRecords']} vagas:{Colors.ENDC}"
        )
        for item in biofast["data"]:
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

    if pasteur['totalRecords'] == 0:
        print(f"{Colors.FAIL}Nenhuma vaga para Pasteur{Colors.ENDC}")
    else:
        print(
            f"{Colors.BOLD}Lab. Pasteur possui {pasteur['totalRecords']} vagas:{Colors.ENDC}")
        for item in pasteur["data"]:
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

    if db["vacancies"] == 0:
        print(f"{Colors.FAIL}Nenhuma vaga para DB Diagnósticos{Colors.ENDC}")
    else:
        print(
            f"{Colors.BOLD}\n\nDB Diagnósticos possui {db['found']} vagas, \nMostrando aquelas que contém Biomédico ou Laboratório: {Colors.ENDC}"
        )
        for items in db["vacancies"]:
            vaga_titulo = items["title"]
            vaga_local = items["location"]
            vaga_id = items["id"]
            if bool(re.search(REGEX, vaga_titulo)):
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

    # checar se a lista de vagas está vazia
    if len(lab_sabin) == 0:
        print(f"{Colors.FAIL}Nenhuma vaga para Sabin{Colors.ENDC}")
    else:
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
    start = time.time()
    main()
    end = time.time()
    total = end-start
    print(f"{Colors.OKBLUE}tempo total de execução: {round(total,2)}s{Colors.ENDC}")
