#!/usr/bin/env python3
"""
Monitor de Ingressos
Interface Gráfica para Windows
Versão 1.0
Por: Jean Souto
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
import json
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import winsound  # Alerta sonoro nativo do Windows

class MonitorIngressosGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Monitor de Ingressos")
        self.root.geometry("800x700")
        self.root.resizable(False, False)
        
        # Variáveis de controle
        self.monitorando = False
        self.driver = None
        self.thread_monitor = None
        
        # Configurações
        self.config_file = "config_monitor.json"
        
        # Tipos de ingresso
        self.tipos_ingresso = {
            "Estudante + Traje de Atlética/República": "Estudante + Traje de Atlética/República",
            "Estudante OU Traje de Atlética/República": "Estudante OU Traje de Atlética/República"
        }
        
        self.criar_interface()
        self.carregar_configuracoes()
        
    def criar_interface(self):
        """Cria a interface gráfica"""
        
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Título
        titulo = ttk.Label(main_frame, text="🎫 Monitor de Ingressos", 
                          font=("Arial", 16, "bold"))
        titulo.grid(row=0, column=0, columnspan=2, pady=10)
        
        # Subtítulo
        subtitulo = ttk.Label(main_frame, text="Monitoramento Automático",
                             font=("Arial", 10))
        subtitulo.grid(row=1, column=0, columnspan=2, pady=(0, 20))
        
        # Seção de Configurações
        config_frame = ttk.LabelFrame(main_frame, text="Configurações", padding="10")
        config_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        # URL do Evento
        ttk.Label(config_frame, text="URL do Evento:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.url_entry = ttk.Entry(config_frame, width=70)
        self.url_entry.grid(row=0, column=1, pady=5, padx=5)
        
        # Data Alvo
        ttk.Label(config_frame, text="Data Alvo:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.data_entry = ttk.Entry(config_frame, width=30)
        self.data_entry.grid(row=1, column=1, sticky=tk.W, pady=5, padx=5)
        ttk.Label(config_frame, text="(ex: 24 OUT 2025)", 
                 font=("Arial", 8), foreground="gray").grid(row=1, column=1, sticky=tk.E, padx=5)
        
        # Tipo de Ingresso
        ttk.Label(config_frame, text="Tipo de Ingresso:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.tipo_combo = ttk.Combobox(config_frame, width=67, state="readonly")
        self.tipo_combo['values'] = list(self.tipos_ingresso.keys())
        self.tipo_combo.current(0)
        self.tipo_combo.grid(row=2, column=1, pady=5, padx=5)
        
        # Intervalo de Verificação
        ttk.Label(config_frame, text="Intervalo (segundos):").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.intervalo_spin = ttk.Spinbox(config_frame, from_=3, to=60, width=10)
        self.intervalo_spin.set(5)
        self.intervalo_spin.grid(row=3, column=1, sticky=tk.W, pady=5, padx=5)
        
        # Botões de Ação
        botoes_frame = ttk.Frame(main_frame)
        botoes_frame.grid(row=3, column=0, columnspan=2, pady=15)
        
        self.btn_iniciar = ttk.Button(botoes_frame, text="▶ Iniciar Monitoramento", 
                                      command=self.iniciar_monitoramento, width=25)
        self.btn_iniciar.grid(row=0, column=0, padx=5)
        
        self.btn_parar = ttk.Button(botoes_frame, text="⏹ Parar Monitoramento", 
                                    command=self.parar_monitoramento, width=25, state="disabled")
        self.btn_parar.grid(row=0, column=1, padx=5)
        
        ttk.Button(botoes_frame, text="💾 Salvar Configurações", 
                  command=self.salvar_configuracoes, width=25).grid(row=0, column=2, padx=5)
        
        # Status
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding="10")
        status_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        self.status_label = ttk.Label(status_frame, text="⚪ Aguardando início", 
                                     font=("Arial", 10, "bold"))
        self.status_label.grid(row=0, column=0, sticky=tk.W)
        
        self.tentativas_label = ttk.Label(status_frame, text="Tentativas: 0")
        self.tentativas_label.grid(row=1, column=0, sticky=tk.W)
        
        # Log de Atividades
        log_frame = ttk.LabelFrame(main_frame, text="Log de Atividades", padding="10")
        log_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, width=90, height=15, 
                                                  font=("Consolas", 9))
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Rodapé
        rodape = ttk.Label(main_frame, text="© 2025 - Monitor de Ingressos v1.0", 
                          font=("Arial", 8), foreground="gray")
        rodape.grid(row=6, column=0, columnspan=2, pady=10)
        
    def log(self, mensagem, tipo="info"):
        """Adiciona mensagem ao log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Cores por tipo
        cores = {
            "info": "black",
            "sucesso": "green",
            "erro": "red",
            "alerta": "orange"
        }
        
        self.log_text.insert(tk.END, f"[{timestamp}] {mensagem}\n")
        self.log_text.see(tk.END)
        self.root.update()
        
    def salvar_configuracoes(self):
        """Salva as configurações em arquivo JSON"""
        config = {
            "url": self.url_entry.get(),
            "data": self.data_entry.get(),
            "tipo_ingresso": self.tipo_combo.get(),
            "intervalo": self.intervalo_spin.get()
        }
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            self.log("✅ Configurações salvas com sucesso!", "sucesso")
            messagebox.showinfo("Sucesso", "Configurações salvas com sucesso!")
        except Exception as e:
            self.log(f"❌ Erro ao salvar configurações: {e}", "erro")
            
    def carregar_configuracoes(self):
        """Carrega configurações do arquivo JSON"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                self.url_entry.insert(0, config.get("url", ""))
                self.data_entry.insert(0, config.get("data", ""))
                
                tipo = config.get("tipo_ingresso", "")
                if tipo in self.tipos_ingresso:
                    self.tipo_combo.set(tipo)
                
                self.intervalo_spin.set(config.get("intervalo", 5))
                
                self.log("✅ Configurações carregadas", "sucesso")
            except Exception as e:
                self.log(f"⚠️ Erro ao carregar configurações: {e}", "alerta")
                
    def validar_configuracoes(self):
        """Valida as configurações antes de iniciar"""
        if not self.url_entry.get().strip():
            messagebox.showerror("Erro", "Por favor, insira a URL do evento!")
            return False
            
        if not self.data_entry.get().strip():
            messagebox.showerror("Erro", "Por favor, insira a data alvo!")
            return False
            
        return True
        
    def iniciar_monitoramento(self):
        """Inicia o monitoramento em thread separada"""
        if not self.validar_configuracoes():
            return
            
        self.monitorando = True
        self.btn_iniciar.config(state="disabled")
        self.btn_parar.config(state="normal")
        self.status_label.config(text="🟢 Monitoramento ativo")
        
        self.log("="*70, "info")
        self.log("🚀 INICIANDO MONITORAMENTO", "sucesso")
        self.log("="*70, "info")
        self.log(f"📅 Data alvo: {self.data_entry.get()}", "info")
        self.log(f"🎫 Ingresso: {self.tipo_combo.get()}", "info")
        self.log(f"⏱️ Intervalo: {self.intervalo_spin.get()}s", "info")
        self.log("="*70, "info")
        
        # Iniciar thread de monitoramento
        self.thread_monitor = threading.Thread(target=self.executar_monitoramento, daemon=True)
        self.thread_monitor.start()
        
    def parar_monitoramento(self):
        """Para o monitoramento"""
        self.monitorando = False
        self.btn_iniciar.config(state="normal")
        self.btn_parar.config(state="disabled")
        self.status_label.config(text="🔴 Monitoramento parado")
        
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None
            
        self.log("⏹ Monitoramento parado pelo usuário", "alerta")
        
    def configurar_driver(self):
        """Configura o Chrome WebDriver"""
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_experimental_option('prefs', {'intl.accept_languages': 'pt-BR,pt'})
        
        return webdriver.Chrome(options=chrome_options)
        
    def verificar_data_correta(self, driver, data_alvo):
        """Verifica se a data alvo está na página"""
        try:
            page_text = driver.find_element(By.TAG_NAME, "body").text
            termos = [data_alvo]
            
            if "/" in data_alvo:
                partes = data_alvo.split("/")
                if len(partes) >= 2:
                    dia = partes[0].lstrip('0')
                    mes = partes[1].lstrip('0')
                    termos.extend([
                        f"{dia}/{mes}",
                        f"{dia} OUT" if mes == "10" else f"{dia} NOV" if mes == "11" else f"{dia}",
                    ])
            
            return any(termo in page_text for termo in termos)
        except:
            return False
            
    def encontrar_e_clicar_data(self, driver, data_alvo):
        """Encontra e clica na data alvo"""
        try:
            time.sleep(2)
            
            termos_busca = [data_alvo]
            if "/" in data_alvo:
                partes = data_alvo.split("/")
                if len(partes) >= 2:
                    dia = partes[0].lstrip('0')
                    mes = partes[1].lstrip('0')
                    termos_busca.extend([
                        dia,
                        f"{dia}/{mes}",
                        f"{dia} OUT" if mes == "10" else f"{dia} NOV" if mes == "11" else f"{dia}",
                    ])
            
            for termo in termos_busca:
                try:
                    elementos = driver.find_elements(By.XPATH, f"//*[contains(text(), '{termo}')]")
                    for elemento in elementos:
                        if elemento.is_displayed():
                            try:
                                elemento.click()
                                time.sleep(2)
                                
                                if self.verificar_data_correta(driver, data_alvo):
                                    return True
                            except:
                                try:
                                    parent = elemento.find_element(By.XPATH, "./..")
                                    parent.click()
                                    time.sleep(2)
                                    
                                    if self.verificar_data_correta(driver, data_alvo):
                                        return True
                                except:
                                    continue
                except:
                    continue
            
            return False
        except:
            return False
            
    def selecionar_ingresso(self, driver, tipo_ingresso):
        """Seleciona o ingresso desejado"""
        try:
            time.sleep(2)
            
            script = f"""
            var elementos = document.querySelectorAll('*');
            
            for (var i = 0; i < elementos.length; i++) {{
                var el = elementos[i];
                if (el.textContent.includes('{tipo_ingresso}') && el.textContent.length < 200) {{
                    var parent = el.parentElement;
                    
                    for (var j = 0; j < 8; j++) {{
                        if (!parent) break;
                        
                        var divs = parent.querySelectorAll('div[onclick], div[style*="cursor: pointer"]');
                        var botoesAdd = parent.querySelectorAll('div.sc-etPtWW, div[class*="button"]');
                        var todosBotoes = Array.from(divs).concat(Array.from(botoesAdd));
                        
                        for (var k = 0; k < todosBotoes.length; k++) {{
                            var botao = todosBotoes[k];
                            var rect = botao.getBoundingClientRect();
                            
                            if (rect.width > 0 && rect.width < 100 && rect.height > 0 && rect.height < 100) {{
                                if (!botao.textContent.includes('remover')) {{
                                    botao.click();
                                    return 'sucesso';
                                }}
                            }}
                        }}
                        
                        parent = parent.parentElement;
                    }}
                }}
            }}
            return 'nao_encontrado';
            """
            
            resultado = driver.execute_script(script)
            return resultado == 'sucesso'
        except:
            return False
            
    def clicar_prosseguir(self, driver):
        """Clica no botão Prosseguir"""
        try:
            time.sleep(2)
            
            for texto in ["Prosseguir", "Proceed", "Continuar"]:
                try:
                    xpath = f"//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{texto.lower()}')]"
                    botoes = driver.find_elements(By.XPATH, xpath)
                    for botao in botoes:
                        if botao.is_displayed() and botao.is_enabled():
                            botao.click()
                            time.sleep(2)
                            return True
                except:
                    continue
            return True
        except:
            return True
            
    def emitir_alerta(self):
        """Emite alerta sonoro e visual no Windows"""
        # Alerta sonoro do Windows
        for _ in range(5):
            winsound.Beep(1000, 300)  # Frequência 1000Hz, duração 300ms
            time.sleep(0.1)
        
        # Messagebox de alerta
        self.root.after(0, lambda: messagebox.showwarning(
            "🎉 INGRESSO ENCONTRADO!",
            "O ingresso foi selecionado!\n\n"
            "FINALIZE A COMPRA AGORA no navegador!\n\n"
            "O monitoramento será pausado."
        ))
        
    def executar_monitoramento(self):
        """Executa o loop de monitoramento"""
        tentativas = 0
        
        try:
            self.log("🔧 Configurando navegador...", "info")
            self.driver = self.configurar_driver()
            self.log("✅ Navegador configurado", "sucesso")
            
            url = self.url_entry.get()
            data_alvo = self.data_entry.get()
            tipo_ingresso = self.tipo_combo.get()
            intervalo = int(self.intervalo_spin.get())
            
            while self.monitorando:
                tentativas += 1
                self.tentativas_label.config(text=f"Tentativas: {tentativas}")
                
                self.log(f"🔍 Tentativa {tentativas}: Verificando disponibilidade...", "info")
                
                # Acessar página
                self.driver.get(url)
                time.sleep(3)
                
                # Procurar data
                self.log(f"   📅 Procurando data: {data_alvo}", "info")
                data_encontrada = self.encontrar_e_clicar_data(self.driver, data_alvo)
                
                if not data_encontrada:
                    self.log(f"   ❌ Data '{data_alvo}' não disponível", "erro")
                    self.log(f"   ⏳ Aguardando {intervalo}s...", "info")
                    time.sleep(intervalo)
                    continue
                
                self.log(f"   ✅ Data encontrada!", "sucesso")
                
                # Verificar ingresso
                self.log(f"   🎫 Verificando ingresso: {tipo_ingresso}", "info")
                if self.selecionar_ingresso(self.driver, tipo_ingresso):
                    self.log("   ✅ INGRESSO SELECIONADO!", "sucesso")
                    self.log("="*70, "sucesso")
                    self.log("🎉 SUCESSO! INGRESSO ENCONTRADO E SELECIONADO!", "sucesso")
                    self.log("="*70, "sucesso")
                    
                    # Clicar em prosseguir
                    self.clicar_prosseguir(self.driver)
                    
                    # Emitir alerta
                    self.emitir_alerta()
                    
                    # Parar monitoramento
                    self.monitorando = False
                    self.root.after(0, lambda: self.btn_iniciar.config(state="normal"))
                    self.root.after(0, lambda: self.btn_parar.config(state="disabled"))
                    self.root.after(0, lambda: self.status_label.config(text="🟡 Ingresso encontrado - Finalize a compra!"))
                    
                    self.log("⚠️ FINALIZE A COMPRA NO NAVEGADOR!", "alerta")
                    self.log("⚠️ O navegador permanecerá aberto.", "alerta")
                    break
                else:
                    self.log(f"   ❌ Ingresso não disponível", "erro")
                
                self.log(f"   ⏳ Aguardando {intervalo}s...", "info")
                time.sleep(intervalo)
                
        except Exception as e:
            self.log(f"❌ Erro: {e}", "erro")
            self.monitorando = False
            self.root.after(0, lambda: self.btn_iniciar.config(state="normal"))
            self.root.after(0, lambda: self.btn_parar.config(state="disabled"))
            self.root.after(0, lambda: self.status_label.config(text="🔴 Erro no monitoramento"))

def main():
    root = tk.Tk()
    app = MonitorIngressosGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()

