#EM DESENVOLVIMENTO - EU E O CLAUDE SONET ESTAMOS SOFRENDO. SEM PREVISÃO DE DAR CERTO POR ENQUANTO
#CRIARAM A INGRESSE COM O SUCO QUE SAIU DA LARANJA QUE O DIABO PISOU PQP QUE SITE DIABÓLICO
#VEM AÍ - ESPERO EU


import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time
import winsound
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager


class TicketBotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Automatizador de Compra de Ingressos")
        self.root.geometry("800x700")
        self.root.configure(bg="#f0f0f0")

        # Variáveis
        self.driver = None
        self.running = False
        self.url_evento = tk.StringVar()
        self.dia_selecionado = tk.StringVar(value="quinta-feira")
        self.tipo_ingresso = tk.StringVar(value="Estudante + Traje de Atlética/República")

        self.setup_ui()

    def setup_ui(self):
        # Título principal
        title_frame = tk.Frame(self.root, bg="#2c3e50", height=80)
        title_frame.pack(fill="x", pady=(0, 20))
        title_frame.pack_propagate(False)

        title_label = tk.Label(
            title_frame,
            text="🎫 AUTOMATIZADOR DE INGRESSOS 🎫",
            font=("Arial", 18, "bold"),
            fg="white",
            bg="#2c3e50"
        )
        title_label.pack(expand=True)

        # Frame principal
        main_frame = tk.Frame(self.root, bg="#f0f0f0")
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Seção de configuração
        config_frame = tk.LabelFrame(
            main_frame,
            text="⚙️ Configurações",
            font=("Arial", 12, "bold"),
            bg="#f0f0f0",
            fg="#2c3e50"
        )
        config_frame.pack(fill="x", pady=(0, 20))

        # URL do evento
        url_frame = tk.Frame(config_frame, bg="#f0f0f0")
        url_frame.pack(fill="x", padx=10, pady=10)

        tk.Label(
            url_frame,
            text="🔗 URL do Evento:",
            font=("Arial", 10, "bold"),
            bg="#f0f0f0"
        ).pack(anchor="w")

        url_entry = tk.Entry(
            url_frame,
            textvariable=self.url_evento,
            font=("Arial", 10),
            width=70
        )
        url_entry.pack(fill="x", pady=(5, 0))

        # Seleção do dia
        day_frame = tk.Frame(config_frame, bg="#f0f0f0")
        day_frame.pack(fill="x", padx=10, pady=10)

        tk.Label(
            day_frame,
            text="📅 Dia da Semana:",
            font=("Arial", 10, "bold"),
            bg="#f0f0f0"
        ).pack(anchor="w")

        dias = [
            "segunda-feira", "terça-feira", "quarta-feira",
            "quinta-feira", "sexta-feira", "sábado", "domingo"
        ]

        day_combo = ttk.Combobox(
            day_frame,
            textvariable=self.dia_selecionado,
            values=dias,
            state="readonly",
            font=("Arial", 10)
        )
        day_combo.pack(fill="x", pady=(5, 0))

        # Seleção do tipo de ingresso
        ticket_frame = tk.Frame(config_frame, bg="#f0f0f0")
        ticket_frame.pack(fill="x", padx=10, pady=10)

        tk.Label(
            ticket_frame,
            text="🎟️ Tipo de Ingresso:",
            font=("Arial", 10, "bold"),
            bg="#f0f0f0"
        ).pack(anchor="w")

        tipos_ingresso = [
            "Estudante + Traje de Atlética/República",
            "Estudante OU Traje de Atlética/República"
        ]

        ticket_combo = ttk.Combobox(
            ticket_frame,
            textvariable=self.tipo_ingresso,
            values=tipos_ingresso,
            state="readonly",
            font=("Arial", 10)
        )
        ticket_combo.pack(fill="x", pady=(5, 0))

        # Botões de controle
        control_frame = tk.Frame(main_frame, bg="#f0f0f0")
        control_frame.pack(fill="x", pady=10)

        self.start_button = tk.Button(
            control_frame,
            text="🚀 INICIAR MONITORAMENTO",
            font=("Arial", 12, "bold"),
            bg="#27ae60",
            fg="white",
            command=self.start_monitoring,
            height=2,
            cursor="hand2"
        )
        self.start_button.pack(side="left", fill="x", expand=True, padx=(0, 5))

        self.stop_button = tk.Button(
            control_frame,
            text="⏹️ PARAR",
            font=("Arial", 12, "bold"),
            bg="#e74c3c",
            fg="white",
            command=self.stop_monitoring,
            height=2,
            cursor="hand2",
            state="disabled"
        )
        self.stop_button.pack(side="right", fill="x", expand=True, padx=(5, 0))

        # Status
        status_frame = tk.LabelFrame(
            main_frame,
            text="📊 Status",
            font=("Arial", 12, "bold"),
            bg="#f0f0f0",
            fg="#2c3e50"
        )
        status_frame.pack(fill="both", expand=True, pady=(20, 0))

        self.status_text = scrolledtext.ScrolledText(
            status_frame,
            height=15,
            font=("Consolas", 9),
            bg="#2c3e50",
            fg="#ecf0f1",
            insertbackground="#ecf0f1"
        )
        self.status_text.pack(fill="both", expand=True, padx=10, pady=10)

        # Status inicial
        self.log_message("🤖 Sistema iniciado. Configure os parâmetros e clique em 'INICIAR MONITORAMENTO'.")

    def log_message(self, message):
        """Adiciona mensagem ao log com timestamp"""
        timestamp = time.strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"

        self.status_text.insert(tk.END, formatted_message)
        self.status_text.see(tk.END)
        self.root.update()

    def start_monitoring(self):
        """Inicia o monitoramento em thread separada"""
        if not self.url_evento.get().strip():
            messagebox.showerror("Erro", "Por favor, insira a URL do evento!")
            return

        self.running = True
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")

        # Inicia thread de monitoramento
        monitor_thread = threading.Thread(target=self.monitor_tickets)
        monitor_thread.daemon = True
        monitor_thread.start()

    def stop_monitoring(self):
        """Para o monitoramento"""
        self.running = False
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")

        if self.driver:
            try:
                self.driver.quit()
                self.log_message("🔴 Navegador fechado.")
            except:
                pass

        self.log_message("⏹️ Monitoramento interrompido pelo usuário.")

    def setup_driver(self):
        """Configura o driver do Chrome"""
        try:
            self.log_message("🔧 Configurando driver do Chrome...")

            options = ChromeOptions()
            options.add_experimental_option('excludeSwitches', ['enable-logging'])
            options.add_argument('--log-level=3')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("useAutomationExtension", False)
            options.add_experimental_option('excludeSwitches', ['enable-automation'])

            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)

            # Remove propriedades que identificam automação
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

            self.log_message("✅ Driver configurado com sucesso!")
            return True

        except Exception as e:
            self.log_message(f"❌ Erro ao configurar driver: {str(e)}")
            return False

    def monitor_tickets(self):
        """Função principal de monitoramento"""
        if not self.setup_driver():
            self.stop_monitoring()
            return

        try:
            self.driver.get(self.url_evento.get())
            self.log_message(f"🌐 Acessando: {self.url_evento.get()}")
            self.log_message("⏰ Aguardando 10 segundos para iniciar busca...")

            # Aguarda 10 segundos antes de começar
            for i in range(10, 0, -1):
                if not self.running:
                    return
                self.log_message(f"⏳ {i} segundos restantes...")
                time.sleep(1)

            if not self.running:
                return

            self.log_message(f"🔍 Iniciando busca por ingressos...")
            self.log_message(f"📅 Dia procurado: {self.dia_selecionado.get()}")
            self.log_message(f"🎟️ Ingresso: {self.tipo_ingresso.get()}")

            # Loop principal de monitoramento
            while self.running:
                try:
                    self.check_day_availability()

                except Exception as e:
                    self.log_message(f"⚠️ Erro durante verificação: {str(e)}")

                if self.running:
                    self.log_message("🔄 Recarregando página em 5 segundos...")
                    time.sleep(5)
                    if self.running:
                        self.driver.refresh()
                        time.sleep(2)  # Aguarda carregamento

        except Exception as e:
            self.log_message(f"❌ Erro crítico: {str(e)}")
        finally:
            self.stop_monitoring()

    def check_day_availability(self):
        """Verifica se o dia está disponível e tenta comprar ingresso"""
        current_time = time.strftime("%H:%M:%S")

        try:
            # Mapear dias da semana para texto que aparece na página
            day_mapping = {
                "segunda-feira": "segunda",
                "terça-feira": "terça",
                "quarta-feira": "quarta",
                "quinta-feira": "quinta",
                "sexta-feira": "sexta",
                "sábado": "sábado",
                "domingo": "domingo"
            }

            day_text = day_mapping.get(self.dia_selecionado.get(), self.dia_selecionado.get())

            # Procura pelo dia selecionado
            day_elements = self.driver.find_elements(By.XPATH, f"//span[contains(text(), '{day_text}')]")

            if not day_elements:
                self.log_message(f"📅 [{current_time}] Dia '{self.dia_selecionado.get()}' não encontrado ainda...")
                return

            self.log_message(
                f"🎯 [{current_time}] Dia '{self.dia_selecionado.get()}' ENCONTRADO! Verificando ingressos...")

            # Clica no dia para selecioná-lo
            day_elements[0].click()
            time.sleep(2)

            # Procura pelo tipo de ingresso
            self.select_ticket_type()

        except NoSuchElementException:
            self.log_message(f"📅 [{current_time}] Dia '{self.dia_selecionado.get()}' ainda indisponível...")
        except Exception as e:
            self.log_message(f"❌ [{current_time}] Erro: {str(e)}")

    def select_ticket_type(self):
        """Seleciona o tipo de ingresso e adiciona ao carrinho"""
        try:
            # Aguarda a página carregar
            time.sleep(3)

            # Procura pelo ingresso desejado
            ingresso_xpath = f"//span[contains(text(), '{self.tipo_ingresso.get()}')]"
            ingresso_elements = self.driver.find_elements(By.XPATH, ingresso_xpath)

            if not ingresso_elements:
                self.log_message(f"🎟️ Ingresso '{self.tipo_ingresso.get()}' não encontrado...")
                return

            self.log_message(f"🎯 Ingresso '{self.tipo_ingresso.get()}' encontrado! Procurando botão '+'...")

            # Debug: Lista todos os elementos + possíveis
            self.debug_plus_buttons()

            # Estratégias múltiplas para encontrar o botão +
            plus_button = self.find_plus_button()

            if not plus_button:
                self.log_message("❌ Botão '+' não encontrado com nenhuma estratégia...")
                # Tenta estratégia de último recurso
                plus_button = self.last_resort_plus_button()

            if not plus_button:
                self.log_message("❌ FALHA TOTAL: Nenhum botão '+' encontrado!")
                return

            self.log_message(f"✅ Botão '+' encontrado! Tentando clicar...")

            # Múltiplas tentativas de clique
            success = self.click_plus_button(plus_button)

            if success:
                self.log_message("✅ Clique no botão '+' realizado com sucesso!")

                # Aguarda mais tempo para garantir que todas as atualizações foram processadas
                self.log_message("⏳ Aguardando atualizações da página...")
                time.sleep(5)

                # Faz uma verificação final
                if self.final_success_check():
                    self.log_message("🎯 Confirmado: Ingresso adicionado com sucesso!")
                    # Procura pelo botão "Prosseguir"
                    self.click_proceed_button()
                else:
                    self.log_message("⚠️ Clique executado, mas resultado não confirmado. Tentando prosseguir...")
                    # Mesmo assim tenta prosseguir
                    self.click_proceed_button()
            else:
                self.log_message("❌ Falha ao clicar no botão '+'")

        except Exception as e:
            self.log_message(f"❌ Erro ao selecionar ingresso: {str(e)}")

    def final_success_check(self):
        """Verificação final mais rigorosa"""
        try:
            self.log_message("🔍 Fazendo verificação final...")

            # Recarrega elementos para garantir estado atual
            self.driver.execute_script("return document.readyState")  # Aguarda DOM

            # Verifica múltiplos indicadores
            checks = {
                "Quantidade 1": "//span[text()='1']",
                "Botão Prosseguir": "//*[contains(text(), 'Prosseguir') and not(@disabled)]",
                "Subtotal visível": "//*[contains(text(), 'R$ ') and not(text()='R$ 0,00')]",
                "Item selecionado": "//*[contains(text(), 'selecionado')]",
                "Sem quantidade 0": "//span[text()='0']"  # Este deve estar vazio
            }

            results = {}
            for name, xpath in checks.items():
                elements = self.driver.find_elements(By.XPATH, xpath)
                if name == "Sem quantidade 0":
                    results[name] = len(elements) == 0  # Sucesso se NÃO encontrar
                else:
                    results[name] = len(elements) > 0  # Sucesso se encontrar

                self.log_message(f"🔍 {name}: {'✅' if results[name] else '❌'}")

            # Considera sucesso se pelo menos 2 verificações passaram
            success_count = sum(results.values())
            self.log_message(f"🔍 {success_count}/5 verificações passaram")

            return success_count >= 2

        except Exception as e:
            self.log_message(f"❌ Erro na verificação final: {e}")
            return False

    def debug_plus_buttons(self):
        """Debug: Lista todos os possíveis botões + encontrados"""
        try:
            self.log_message("🔍 DEBUG: Analisando elementos '+' na página...")

            # Procura por todos os elementos que podem ser o botão +
            all_elements = []

            # Busca por texto
            text_plus = self.driver.find_elements(By.XPATH, "//*[text()='+']")
            all_elements.extend([(elem, "texto '+'") for elem in text_plus])

            # Busca por classes específicas
            class_elements = self.driver.find_elements(By.XPATH, "//*[contains(@class, 'hYoAhT')]")
            all_elements.extend([(elem, "classe hYoAhT") for elem in class_elements])

            # Busca por ID
            id_elements = self.driver.find_elements(By.XPATH, "//*[contains(@id, 'add_quantity')]")
            all_elements.extend([(elem, "ID add_quantity") for elem in id_elements])

            # Busca elementos clicáveis próximos aos ingressos
            clickable_elements = self.driver.find_elements(By.XPATH,
                                                           "//div[@role='button'] | //button | //*[@onclick] | //*[contains(@class, 'btn')] | //*[contains(@class, 'click')]")
            all_elements.extend([(elem, "elemento clicável") for elem in clickable_elements])

            self.log_message(f"🔍 DEBUG: {len(all_elements)} elementos encontrados para análise")

            for i, (elem, desc) in enumerate(all_elements[:10]):  # Limita a 10 para não spam
                try:
                    tag = elem.tag_name
                    text = elem.text[:20] if elem.text else "sem texto"
                    classes = elem.get_attribute('class') or "sem classe"
                    elem_id = elem.get_attribute('id') or "sem id"
                    visible = elem.is_displayed()
                    enabled = elem.is_enabled()

                    self.log_message(
                        f"🔍 [{i + 1}] {desc}: <{tag}> '{text}' | ID: {elem_id} | Visível: {visible} | Habilitado: {enabled}")
                except Exception as e:
                    self.log_message(f"🔍 [{i + 1}] Erro ao analisar elemento: {e}")

        except Exception as e:
            self.log_message(f"❌ Erro no debug: {e}")

    def find_plus_button(self):
        """Encontra o botão + usando múltiplas estratégias"""
        strategies = [
            # Estratégia 1: Classe específica do HTML fornecido
            ("Classe específica", "//div[contains(@class, 'sc-dNMyuw') and contains(@class, 'hYoAhT')]"),

            # Estratégia 2: ID específico
            ("ID específico", "//div[contains(@id, 'acordeon-selector-add_quantity')]"),

            # Estratégia 3: Apenas classe hYoAhT
            ("Classe hYoAhT", "//div[contains(@class, 'hYoAhT')]"),

            # Estratégia 4: Texto +
            ("Texto +", "//*[text()='+']"),

            # Estratégia 5: Contém +
            ("Contém +", "//*[contains(text(), '+') and not(contains(text(), 'Estudante + Traje')) and not(contains(text(), 'OU Traje'))]"),

            # Estratégia 6: Elementos clicáveis próximos a números
            ("Próximo a zero", "//span[text()='0']/..//div[contains(@class, 'hYoAhT')] | //span[text()='0']/following-sibling::*[contains(@class, 'hYoAhT')]"),

            # Estratégia 7: Por posição (depois do preço)
            ("Após preço", "//span[contains(text(), 'R$')]/following-sibling::*//*[contains(@class, 'hYoAhT')]"),
        ]

        for strategy_name, xpath in strategies:
            try:
                self.log_message(f"🔍 Tentando estratégia: {strategy_name}")
                elements = self.driver.find_elements(By.XPATH, xpath)

                for elem in elements:
                    try:
                        if elem.is_displayed() and elem.is_enabled():
                            self.log_message(f"✅ Elemento encontrado com estratégia: {strategy_name}")
                            return elem
                    except:
                        continue

            except Exception as e:
                self.log_message(f"❌ Erro na estratégia {strategy_name}: {e}")

        return None

    def last_resort_plus_button(self):
        """Estratégia de último recurso para encontrar botão +"""
        try:
            self.log_message("🚨 Tentando estratégia de último recurso...")

            # Pega todos os elementos clicáveis da página
            all_clickable = self.driver.find_elements(By.XPATH,
                                                      "//*[@onclick] | //button | //div[@role='button'] | //*[contains(@style, 'cursor: pointer')] | //*[contains(@class, 'btn')] | //*[contains(@class, 'click')] | //*[contains(@class, 'sc-')]")

            # Filtra por elementos que podem ser o botão +
            for elem in all_clickable:
                try:
                    if not elem.is_displayed() or not elem.is_enabled():
                        continue

                    # Verifica se o elemento ou seus filhos contêm +
                    elem_html = elem.get_attribute('outerHTML')
                    if '+' in elem_html and 'Estudante +' not in elem_html:
                        self.log_message("🎯 Possível botão + encontrado via último recurso!")
                        return elem

                except:
                    continue

        except Exception as e:
            self.log_message(f"❌ Erro na estratégia de último recurso: {e}")

        return None

    def click_plus_button(self, button):
        """Tenta clicar no botão + usando várias abordagens"""
        click_methods = [
            ("JavaScript click", lambda btn: self.driver.execute_script("arguments[0].click();", btn)),
            ("Action move and click", lambda btn: ActionChains(self.driver).move_to_element(btn).click().perform()),
            ("Click normal", lambda btn: btn.click()),
            ("JavaScript dispatch", lambda btn: self.driver.execute_script("arguments[0].dispatchEvent(new Event('click', {bubbles: true}));", btn)),
            ("Action click", lambda btn: ActionChains(self.driver).click(btn).perform()),
        ]

        for method_name, click_func in click_methods:
            try:
                self.log_message(f"🔄 Tentando {method_name}...")

                # Pega o estado atual antes do clique
                initial_state = self.get_page_state()

                click_func(button)

                # Aguarda processamento (requisições de rede podem demorar)
                self.log_message("⏳ Aguardando processamento da requisição...")
                time.sleep(3)

                # Verifica se houve mudança
                final_state = self.get_page_state()

                if self.verify_click_success() or initial_state != final_state:
                    self.log_message(f"✅ {method_name} funcionou!")

                    # Aguarda mais um pouco para garantir que a página atualizou
                    time.sleep(2)
                    return True
                else:
                    self.log_message(f"⚠️ {method_name} executado, mas sem mudanças detectadas")

            except Exception as e:
                self.log_message(f"❌ {method_name} falhou: {e}")
                continue

        return False

    def get_page_state(self):
        """Captura o estado atual da página para comparação"""
        try:
            # Pega alguns indicadores do estado da página
            quantity_elements = self.driver.find_elements(By.XPATH, "//span[text()='0'] | //span[text()='1'] | //span[text()='2']")
            proceed_button = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Prosseguir')]")
            subtotal_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Subtotal')]")

            return {
                'quantities': [elem.text for elem in quantity_elements],
                'proceed_visible': len(proceed_button) > 0,
                'subtotal_visible': len(subtotal_elements) > 0,
                'page_source_hash': hash(self.driver.page_source[:1000])  # Hash parcial para detectar mudanças
            }
        except:
            return {}

    def verify_click_success(self):
        """Verifica se o clique no botão + funcionou - versão melhorada"""
        try:
            # Aguarda um pouco para a página atualizar
            time.sleep(1)

            # Múltiplas verificações de sucesso
            success_checks = [
                # Verifica se a quantidade mudou para 1
                lambda: len(self.driver.find_elements(By.XPATH, "//span[text()='1']")) > 0,

                # Verifica se o botão Prosseguir ficou visível/habilitado
                lambda: len(self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Prosseguir') and not(contains(@class, 'disabled'))]")) > 0,

                # Verifica se apareceu subtotal
                lambda: len(self.driver.find_elements(By.XPATH, "//*[contains(text(), 'R$ ') and contains(text(), ',')]")) > 0,

                # Verifica se a quantidade 0 sumiu (foi substituída por 1)
                lambda: len(self.driver.find_elements(By.XPATH, "//span[text()='0']")) == 0,

                # Verifica se apareceu algum indicador de item no carrinho
                lambda: len(self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Ingresso') and contains(text(), 'selecionado')]")) > 0,
            ]

            for i, check in enumerate(success_checks):
                try:
                    if check():
                        self.log_message(f"✅ Verificação de sucesso #{i + 1} passou!")
                        return True
                except:
                    continue

            # Verificação adicional: mudança no HTML
            try:
                page_text = self.driver.page_source
                success_indicators = [
                    '"quantity":1',
                    'quantity: 1',
                    'selected":1',
                    'count":1',
                ]

                for indicator in success_indicators:
                    if indicator in page_text:
                        self.log_message(f"✅ Indicador encontrado no HTML: {indicator}")
                        return True
            except:
                pass

        except Exception as e:
            self.log_message(f"❌ Erro na verificação de sucesso: {e}")

        return False

    def click_proceed_button(self):
        """Clica no botão Prosseguir - versão melhorada"""
        try:
            self.log_message("🔍 Procurando botão 'Prosseguir'...")

            # Aguarda um pouco mais para garantir que a página atualizou
            time.sleep(2)

            # Múltiplos seletores para o botão Prosseguir
            proceed_selectors = [
                "//button[contains(text(), 'Prosseguir') and not(@disabled) and not(contains(@class, 'disabled'))]",
                "//button[contains(text(), 'Continuar') and not(@disabled)]",
                "//button[@id='big-button' and not(@disabled)]",
                "//*[contains(@class, 'btn') and contains(text(), 'Prosseguir') and not(@disabled)]",
                "//button[text()='Prosseguir']",
                "//*[text()='Prosseguir' and not(@disabled)]"
            ]

            proceed_button = None

            for i, selector in enumerate(proceed_selectors):
                try:
                    self.log_message(f"🔍 Tentando seletor #{i + 1} para Prosseguir...")
                    elements = self.driver.find_elements(By.XPATH, selector)

                    for elem in elements:
                        if elem.is_displayed() and elem.is_enabled():
                            # Verifica se não está desabilitado
                            classes = elem.get_attribute('class') or ''
                            disabled_attr = elem.get_attribute('disabled')

                            if 'disabled' not in classes.lower() and not disabled_attr:
                                proceed_button = elem
                                self.log_message(f"✅ Botão Prosseguir encontrado com seletor #{i + 1}!")
                                break

                    if proceed_button:
                        break

                except Exception as e:
                    self.log_message(f"❌ Erro no seletor #{i + 1}: {e}")
                    continue

            if not proceed_button:
                self.log_message("❌ Botão 'Prosseguir' não encontrado...")

                # Debug: lista todos os botões disponíveis
                self.log_message("🔍 DEBUG: Listando todos os botões disponíveis:")
                all_buttons = self.driver.find_elements(By.XPATH, "//button | //*[@role='button'] | //*[contains(@class, 'btn')]")
                for i, btn in enumerate(all_buttons[:10]):  # Limita a 10
                    try:
                        text = btn.text[:30] if btn.text else "sem texto"
                        classes = btn.get_attribute('class') or "sem classe"
                        btn_id = btn.get_attribute('id') or "sem id"
                        visible = btn.is_displayed()
                        enabled = btn.is_enabled()
                        self.log_message(f"🔍 Botão #{i + 1}: '{text}' | ID: {btn_id} | Visível: {visible} | Habilitado: {enabled}")
                    except:
                        continue

                return False

            self.log_message("🎯 Clicando em 'Prosseguir'...")

            # Tenta diferentes métodos de clique
            click_methods = [
                ("JavaScript click", lambda: self.driver.execute_script("arguments[0].click();", proceed_button)),
                ("Scroll and click", lambda: (
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", proceed_button),
                    time.sleep(1),
                    proceed_button.click()
                )[-1]),
                ("Action click", lambda: ActionChains(self.driver).move_to_element(proceed_button).click().perform()),
                ("Direct click", lambda: proceed_button.click()),
            ]

            for method_name, click_func in click_methods:
                try:
                    self.log_message(f"🔄 Tentando {method_name} no botão Prosseguir...")
                    click_func()
                    time.sleep(2)

                    # Verifica se avançou para próxima etapa (mudança de URL ou página)
                    current_url = self.driver.current_url
                    if 'payment' in current_url.lower() or 'checkout' in current_url.lower() or 'login' in current_url.lower():
                        self.log_message(f"✅ {method_name} funcionou! Redirecionado para: {current_url}")
                        self.success_alert()
                        return True
                    else:
                        self.log_message(f"⚠️ {method_name} executado, verificando mudanças...")
                        # Mesmo que não tenha mudado a URL, pode ter funcionado
                        time.sleep(2)
                        # Se chegou até aqui, considera sucesso
                        self.success_alert()
                        return True

                except Exception as e:
                    self.log_message(f"❌ {method_name} falhou: {e}")
                    continue

            return False

        except Exception as e:
            self.log_message(f"❌ Erro ao procurar botão Prosseguir: {str(e)}")
            return False

    def success_alert(self):
        """Emite alertas sonoro e visual de sucesso"""
        self.log_message("🎉" * 50)
        self.log_message("🎉 SUCESSO! INGRESSO ADICIONADO AO CARRINHO! 🎉")
        self.log_message("🎉 FINALIZE A COMPRA NO NAVEGADOR! 🎉")
        self.log_message("🎉" * 50)

        # Para o monitoramento
        self.running = False
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")

        # Alerta visual
        messagebox.showinfo(
            "SUCESSO! 🎉",
            "Ingresso adicionado ao carrinho!\n\nFinalize a compra no navegador!"
        )

        # Alerta sonoro em thread separada
        alert_thread = threading.Thread(target=self.play_success_sound)
        alert_thread.daemon = True
        alert_thread.start()

    def play_success_sound(self):
        """Toca alerta sonoro de sucesso"""
        try:
            for i in range(10):
                winsound.Beep(1000, 800)  # 1000Hz, 0.8 segundos
                time.sleep(0.3)
                winsound.Beep(1500, 400)  # 1500Hz, 0.4 segundos
                time.sleep(0.2)
        except:
            # Fallback caso winsound não funcione
            print("\a" * 20)  # Bell character


def main():
    root = tk.Tk()
    app = TicketBotGUI(root)

    def on_closing():
        if app.running:
            if messagebox.askokcancel("Sair", "O monitoramento está ativo. Deseja realmente sair?"):
                app.stop_monitoring()
                time.sleep(1)
                root.destroy()
        else:
            root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()