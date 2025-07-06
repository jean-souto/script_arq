import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.common.exceptions import NoSuchElementException

# Importa o gerenciador específico para o Chrome
from webdriver_manager.chrome import ChromeDriverManager

# --- Configurações ---
URL_DO_EVENTO = "https://www.ingressolive.com/0507-funk-delas-60946"
TIPO_DE_INGRESSO_INDEX = 0  # 0: Estudante, 1: Estudante, 2: Inteira
INTERVALO_DE_ATUALIZACAO = 5  # Segundos entre cada verificação


# --- Fim das Configurações ---

def configurar_driver():
    """Configura o driver para o Google Chrome de forma automática."""
    try:
        print("Configurando o driver para o Google Chrome...")
        options = ChromeOptions()
        # options.add_argument("--headless") # Descomente para rodar sem abrir a janela

        #detecta sua versão e baixa o driver correto.
        service = Service(ChromeDriverManager().install())

        driver = webdriver.Chrome(service=service, options=options)

        print("Driver do Chrome configurado com sucesso!")
        return driver
    except Exception as e:
        print(f"Ocorreu um erro ao configurar o driver do Chrome: {e}")
        print("Certifique-se de que o Google Chrome está instalado corretamente.")
        return None


def procurar_ingresso(driver):
    """Função principal para encontrar o ingresso."""
    if driver is None:
        return

    driver.get(URL_DO_EVENTO)
    print(">>> ATENÇÃO: A janela do Google Chrome foi aberta.")
    print(">>> Faça login no site manualmente AGORA e depois aguarde.")

    print("\n*** SAI DESSA VIDA MEU FI ***")
    print("********************************************************\n")
    print(">>> O script começará a verificar em 20 segundos...")
    time.sleep(20)

    while True:
        try:
            print(f"Atualizando a página... Verificando disponibilidade às {time.strftime('%H:%M:%S')}")
            linha_do_ingresso = driver.find_element(By.XPATH,
                                                    f'//div[@class="tickets-table"]//tbody/tr[{TIPO_DE_INGRESSO_INDEX + 1}]')
            status_ingresso = linha_do_ingresso.find_element(By.XPATH, './td[5]').text
            if "esgotado" in status_ingresso.lower():
                print(f"Status: ESGOTADO. Tentando novamente em {INTERVALO_DE_ATUALIZACAO} segundos.")
                time.sleep(INTERVALO_DE_ATUALIZACAO)
                driver.refresh()
            else:
                print("\n" * 5)
                print("=" * 40)
                print("INGRESSO DISPONÍVEL! SELECIONANDO...")
                print("=" * 40)
                campo_quantidade = linha_do_ingresso.find_element(By.XPATH, './td[5]//input')
                campo_quantidade.clear()
                campo_quantidade.send_keys("1")
                print("Ingresso selecionado. Clicando em 'Continuar'...")
                botao_continuar = driver.find_element(By.XPATH, '//button[contains(text(), "Continuar")]')
                botao_continuar.click()
                print("\n>>> AÇÃO NECESSÁRIA! PROSSIGA COM A COMPRA NA JANELA DO NAVEGADOR! <<<")
                break
        except Exception as e:
            print(f"Ocorreu um erro inesperado: {e}")
            time.sleep(INTERVALO_DE_ATUALIZACAO)
            driver.refresh()

    time.sleep(3600)  # Mantém a janela aberta por 1 hora
    driver.quit()


if __name__ == "__main__":
    driver = configurar_driver()
    procurar_ingresso(driver)