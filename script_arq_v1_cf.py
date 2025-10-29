import time
import os
import winsound
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.common.exceptions import NoSuchElementException

# MUDANÇA 1: Importando a classe 'Select' para interagir com caixas de seleção
from selenium.webdriver.support.ui import Select

# Importa o gerenciador específico para o Chrome
from webdriver_manager.chrome import ChromeDriverManager

# Variáveis globais
URL_DO_EVENTO = None
NOME_DO_INGRESSO_DESEJADO = None
INTERVALO_DE_ATUALIZACAO = None


# Configurações
def configura_variaveis():
    global URL_DO_EVENTO
    global NOME_DO_INGRESSO_DESEJADO
    global INTERVALO_DE_ATUALIZACAO
    URL_DO_EVENTO = input("Informe a URL do evento: ") # Com o https e tudo mais
    opcao = input("Digite 1 para 'Estudante + Traje de atlética' ou 2 para 'Estudante OU traje de atlética': ")
    if opcao == "1":
        NOME_DO_INGRESSO_DESEJADO = "Estudante + Traje de atlética"
    elif opcao == "2":
        NOME_DO_INGRESSO_DESEJADO = "Estudante OU traje de atlética"
    else:
        print("Opção inválida. Usando opção padrão: Estudante + Traje de atlética")
        NOME_DO_INGRESSO_DESEJADO = "Estudante + Traje de atlética"
    INTERVALO_DE_ATUALIZACAO = 5 # Menos que 5 vai dar ruim

# Alerta sonoro
def alerta_sonoro():
    """Emite 10 bipes longos """
    print("Emitindo alerta sonoro...")
    for _ in range(15):
        winsound.Beep(1000, 800) # Frequência 1000Hz, duração 0,8 segundo
        time.sleep(0.3)

def configurar_driver():
    """Configura o driver para o Google Chrome de forma automática"""
    try:
        print("Configurando o driver para o Google Chrome")
        options = ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_argument('--log-level=3')
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        print("Driver do Chrome configurado com sucesso!")
        return driver
    except Exception as e:
        print(f"Ocorreu um erro ao configurar o driver do Chrome: {e}")
        return None


def procurar_ingresso(driver):
    """Função principal - busca a caixa de seleção do ingresso """
    if driver is None:
        return

    driver.get(URL_DO_EVENTO)
    print(">>> ATENÇÃO: A janela do Google Chrome foi aberta.")
    print(">>> Faça login no site manualmente AGORA e depois aguarde.")
    print("*** SAI DESSA VIDA FI ***")
    print(">>> O script começará a verificar em 30 segundos...")
    print(">>> Buscando por 'Estudante + traje de atlética'\n")

    time.sleep(30)

    while True:
        try:
            print(f"Atualizando a página... Verificando disponibilidade às {time.strftime('%H:%M:%S')}")

            linha_do_ingresso = driver.find_element(By.XPATH, f'//tr[contains(., "{NOME_DO_INGRESSO_DESEJADO}")]')

            # Procura pela caixa de seleção dentro da linha do ingresso
            seletor_quantidade_element = linha_do_ingresso.find_element(By.XPATH,
                                                                        ".//select[contains(@class, 'ingresso-quantidade')]")

            # Se a linha acima funcionou, a caixa de seleção existe, então o ingresso está disponível
            print("\n")
            print("=" * 40)
            print(f"INGRESSO '{NOME_DO_INGRESSO_DESEJADO}' DISPONÍVEL! SELECIONANDO...")
            print("=" * 40)

            # Escolher a opção com valor "1"
            caixa_de_selecao = Select(seletor_quantidade_element)
            caixa_de_selecao.select_by_value("1")

            print("Quantidade '1' selecionada. Clicando em 'Continuar'...")
            botao_continuar = driver.find_element(By.XPATH, '//button[contains(text(), "Continuar")]')
            botao_continuar.click()
            print("\n>>> AÇÃO NECESSÁRIA! PROSSIGA COM A COMPRA NA JANELA DO NAVEGADOR! <<<")

            # Chama o alerta sonoro
            alerta_sonoro()
            break

        except NoSuchElementException:
            # Se a caixa de seleção não for encontrada, o ingresso NÃO está disponível
            print(f"Status para '{NOME_DO_INGRESSO_DESEJADO}': INDISPONÍVEL.")
            time.sleep(INTERVALO_DE_ATUALIZACAO)
            driver.refresh()
        except Exception as e:
            # Captura outros erros inesperados
            print(f"Ocorreu um erro inesperado. Mensagem: {e}")
            time.sleep(INTERVALO_DE_ATUALIZACAO)
            driver.refresh()

    time.sleep(3600)
    driver.quit()


if __name__ == "__main__":
    driver = configurar_driver()
    configura_variaveis()
    procurar_ingresso(driver)
