import aiohttp
import asyncio
from bs4 import BeautifulSoup as bs
from datetime import datetime
import re

today = datetime.today().strftime('%Y-%m-%d')
regex = r"(.*[Ll][Aa][Bb].*)|(.*[Bb][Ii][oO].*)"  # filtrando vagas..
USR_AGENT = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:99.0) Gecko/20100101 Firefox/99.0"


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


async def get_s_lucas():  # lab s. Lucas
    async with aiohttp.ClientSession() as sess:
        async with sess.get(
            r"https://api.solides.jobs/v2/vacancy/search?reference_id=92055&search=&vacancyType=jobs",
            headers={
                "User-Agent": USR_AGENT
            }
        ) as response:
            return await response.json()


async def get_diag_br():  # DB diag. do Brasil
    async with aiohttp.ClientSession() as sess:
        async with sess.post(
            "https://platform.senior.com.br/t/senior.com.br/bridge/1.0/anonymous/rest/hcm/vacancymanagement/queries/searchPublicVacancies",
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
        ) as response:
            return await response.json()


async def get_diagbr_info(id: str):  # links para as postagens
    async with aiohttp.ClientSession() as sess:
        async with sess.post(
            "https://platform.senior.com.br/t/senior.com.br/bridge/1.0/anonymous/rest/hcm/vacancymanagement/queries/publishedVacancyDetails",
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
        ) as response:
            return await response.json()


async def sabin():
    jobs = []
    async with aiohttp.ClientSession() as sess:
        async with sess.get(
            "https://jobs.kenoby.com/sabin-site/position?search=&="
        ) as response:
            # response.text() << aiohttp get html text (and await it)
            soup = bs(await response.text(), "lxml")
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


async def main():
    print(f"{Colors.HEADER}Hoje é: {today}\nColetando dados...\n\n{Colors.ENDC}")
    lab_sabin = await sabin()

    db = await get_diag_br()
    s_lucas = await get_s_lucas()

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
            mais_info = await get_diagbr_info(vaga_id)
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

    asyncio.run(main())
