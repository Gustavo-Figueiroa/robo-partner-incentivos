import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# --- CONFIGURAÇÕES ---
# DICA: Evite caminhos absolutos no Git. Coloque as planilhas na mesma pasta do script ou em uma subpasta "dados/".
ARQUIVO_ENTRADA = r"caminho/para/sua/planilha/minha_base_clientes.xlsx"
ARQUIVO_SAIDA = r"caminho/para/sua/planilha/resultado_incentivos.xlsx"
URL_CLAIMS = "https://partner.microsoft.com/dashboard/v2/incentives/customer-association/claims"

# --- CONFIGURAÇÕES DE E-MAIL ---
# ATENÇÃO: Nunca suba suas senhas reais para o GitHub. 
# Para uso local, preencha aqui, mas não faça commit disso. O ideal é usar variáveis de ambiente (.env).
EMAIL_REMETENTE = "seu_email@dominio.com"
EMAIL_SENHA     = "sua_senha_de_aplicativo_aqui"
SMTP_HOST       = "smtp.gmail.com"
SMTP_PORT       = 587

def enviar_email(destinatario, dominio, status, licencas):
    try:
        msg = MIMEMultipart("alternative")
        msg["From"]    = EMAIL_REMETENTE
        msg["To"]      = destinatario
        msg["Subject"] = f"[Partner] Incentivos Microsoft - {dominio}"
        if status == "Qualificado":
            lista = "".join(f"<li>{lic}</li>" for lic in licencas.split(" | "))
            corpo = f"<html><body><h2 style='color:#0078D4'>Licencas disponiveis para {dominio}</h2><ul>{lista}</ul></body></html>"
        else:
            corpo = f"<html><body><h2 style='color:#D4380D'>Sem licencas - {dominio}</h2><p>Cliente nao qualificado no momento.</p></body></html>"
        msg.attach(MIMEText(corpo, "html", "utf-8"))
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_REMETENTE, EMAIL_SENHA)
            server.sendmail(EMAIL_REMETENTE, destinatario, msg.as_string())
        print(f">>> E-mail enviado para: {destinatario}")
    except Exception as e:
        print(f"!!! Falha ao enviar e-mail: {e}")

def rodar_automacao():
    print("Iniciando leitura da planilha...")
    try:
        df = pd.read_excel(ARQUIVO_ENTRADA)
        if 'Status' not in df.columns:
            df['Status'] = ""
        if 'Licencas_Disponiveis' not in df.columns:
            df['Licencas_Disponiveis'] = ""
        if 'Email_Responsavel' not in df.columns:
            df['Email_Responsavel'] = ""
    except Exception as e:
        print(f"ERRO: Planilha não encontrada: {e}")
        return

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.maximize_window()
    wait = WebDriverWait(driver, 20)

    try:
        driver.get(URL_CLAIMS)
        print("\n--- AGUARDANDO LOGIN ---")
        input("Faça o login. Quando estiver vendo a tela INICIAL com o botão 'Adicionar cliente', aperte ENTER aqui...")

        for index, row in df.iterrows():
            dominio = str(row['Dominio']).strip()
            print(f"\n=====================================")
            print(f"Processando cliente: {dominio}")

            try:
                # Garante que está na tela inicial limpa
                driver.get(URL_CLAIMS)
               
                # PASSO 0: CLIQUES AUTOMÁTICOS
                print("Passo 0: Aguardando 10s para a página inicial carregar...")
                time.sleep(10)
               
                print("Passo 0: Clicando em 'Adicionar cliente'...")
                try:
                    btn_adicionar = driver.find_element(By.XPATH, "//*[contains(text(), 'Adicionar cliente')]")
                    driver.execute_script("arguments[0].click();", btn_adicionar)
                except:
                    driver.execute_script("""
                        var elements = document.querySelectorAll('*');
                        for(var i=0; i<elements.length; i++){
                            if(elements[i].innerText && elements[i].innerText.includes('Adicionar cliente')){
                                elements[i].click(); break;
                            }
                        }
                    """)
               
                print("Passo 0: Aguardando 5s para o menu abrir...")
                time.sleep(5)

                print("Passo 0: Clicando em 'Atividades de parceiros'...")
                try:
                    btn_atividades = driver.find_element(By.XPATH, "//*[contains(text(), 'Atividades de parceiros')]")
                    driver.execute_script("arguments[0].click();", btn_atividades)
                except:
                    driver.execute_script("""
                        var elements = document.querySelectorAll('*');
                        for(var i=0; i<elements.length; i++){
                            if(elements[i].innerText && elements[i].innerText.includes('Atividades de parceiros')){
                                elements[i].click(); break;
                            }
                        }
                    """)
               
                print("Passo 0: Aguardando 5s para iniciar a busca...")
                time.sleep(5)

                # PASSO 1: NOME DA DECLARAÇÃO
                print("Passo 1: Preenchendo Nome...")
                js_nome = 'return document.querySelector("#claimName").shadowRoot.querySelector("input")'
                campo_nome = driver.execute_script(js_nome)
                campo_nome.clear()
                campo_nome.send_keys(dominio)
                time.sleep(1)

                # PASSO 2: LOCALIZAÇÃO
                print("Passo 2: Selecionando Localização...")
                js_loc = 'return document.querySelector("#step1 > div:nth-child(5) > he-select_ca").shadowRoot.querySelector("#input")'
                campo_loc = driver.execute_script(js_loc)
               
                driver.execute_script("arguments[0].focus();", campo_loc)
                time.sleep(1)
               
                actions = ActionChains(driver)
                actions.send_keys(Keys.ARROW_DOWN).perform()
                time.sleep(1.5)
                for i in range(20):
                    ActionChains(driver).send_keys(Keys.ARROW_DOWN).perform()
                    time.sleep(0.05)
               
                ActionChains(driver).send_keys(Keys.ENTER).perform()
                time.sleep(0.5)
                ActionChains(driver).send_keys(Keys.TAB).perform()
                time.sleep(1)

                # PASSO 3: ID DO CLIENTE
                print("Passo 3: Preenchendo ID...")
                js_id = 'return document.querySelector("#originalPartnerInputCustomerIdValue").shadowRoot.querySelector("#input")'
                campo_id = driver.execute_script(js_id)
               
                driver.execute_script("arguments[0].focus();", campo_id)
                campo_id.clear()
                campo_id.send_keys(dominio)
                time.sleep(1)

                # PASSO 4: AVANÇAR (com retry se der erro de validação)
                print("Passo 4: Clicando em Avançar...")
                js_botao = 'return document.querySelector("#wizardAddClaim").shadowRoot.querySelector("he-button_ca.next-button").shadowRoot.querySelector("button")'
                btn_avancar = driver.execute_script(js_botao)
                driver.execute_script("arguments[0].click();", btn_avancar)
                time.sleep(5)

                # Verifica se caiu em erro de validação e tenta novamente
                for tentativa in range(3):
                    pagina_atual = driver.page_source.lower()
                    if "ocorreu um erro" in pagina_atual or "tentar novamente" in pagina_atual:
                        print(f"Passo 4: Erro detectado, tentando novamente ({tentativa + 1}/3)...")
                        try:
                            btn_retry = driver.find_element(By.XPATH, "//*[contains(text(), 'Tentar novamente')]")
                            driver.execute_script("arguments[0].click();", btn_retry)
                            time.sleep(3)
                        except:
                            pass
                        try:
                            btn_avancar = driver.execute_script(js_botao)
                            driver.execute_script("arguments[0].click();", btn_avancar)
                        except:
                            pass
                        time.sleep(5)
                    elif "compromisso do associado" in pagina_atual or "qualificado" in pagina_atual:
                        print("Passo 4: Navegacao bem-sucedida!")
                        break

                # PASSO 5: EXTRAÇÃO DIRETA DO PAINEL QUALIFICADO
                print("Passo 5: Lendo licencas do painel eligible...")
                time.sleep(5)

                js_licencas = r"""
                function getDeepText(node) {
                    var text = "";
                    if (node.nodeType === 3) { text += node.nodeValue; }
                    else {
                        if (node.shadowRoot) text += getDeepText(node.shadowRoot);
                        for (var c of node.childNodes) text += getDeepText(c);
                    }
                    return text;
                }
                function findPanel(node) {
                    if (node.nodeType === 1) {
                        if (node.id === "panel-0") return node;
                        if (node.shadowRoot) { var f = findPanel(node.shadowRoot); if (f) return f; }
                        for (var c of node.childNodes) { var f = findPanel(c); if (f) return f; }
                    }
                    return null;
                }
                function findCheckboxes(node, results) {
                    if (node.nodeType === 1) {
                        var tag = node.tagName ? node.tagName.toLowerCase() : "";
                        if (tag === "he-checkbox_ca" || tag === "he-checkbox") {
                            var txt = getDeepText(node).replace(/\s+/g, " ").trim();
                            if (txt.length > 5) results.push(txt);
                        }
                        if (node.shadowRoot) findCheckboxes(node.shadowRoot, results);
                        for (var c of node.childNodes) findCheckboxes(c, results);
                    }
                }
                var panel = findPanel(document.body);
                if (!panel) return {status: "erro", licencas: []};
                var panelText = getDeepText(panel).toLowerCase();
                if (panelText.indexOf("nao estao qualificados") > -1 || panelText.indexOf("nenhum compromisso") > -1 || panelText.indexOf("não estão qualificados") > -1) {
                    return {status: "nao_qualificado", licencas: []};
                }
                var licencas = [];
                findCheckboxes(panel, licencas);
                licencas = licencas.filter(function(v,i,a){ return a.indexOf(v)===i; });
                if (licencas.length > 0) return {status: "qualificado", licencas: licencas};
                return {status: "nao_qualificado", licencas: []};
                """

                resultado = driver.execute_script(js_licencas)
                print(f"Resultado JS: {resultado}")

                if resultado and resultado.get("status") == "qualificado":
                    status = "Qualificado"
                    texto_licencas = " | ".join(resultado.get("licencas", []))
                else:
                    status = "Não Qualificado"
                    texto_licencas = "Nenhuma licença disponível"

                df.at[index, 'Status'] = status
                df.at[index, 'Licencas_Disponiveis'] = texto_licencas
                print(f">>> Status: {status}")
                print(f">>> Licencas: {texto_licencas}")

                # PASSO 6: ENVIO DE E-MAIL
                try:
                    email_resp = str(df.at[index, 'Email_Responsavel']).strip()
                    print(f">>> Email lido da planilha: [{email_resp}]")
                    if email_resp and email_resp.lower() not in ('nan', '') and '@' in email_resp:
                        enviar_email(email_resp, dominio, status, texto_licencas)
                    else:
                        print('>>> Email_Responsavel vazio ou invalido, e-mail nao enviado.')
                except Exception as e_mail:
                    print(f'!!! Erro no envio de e-mail: {e_mail}')

            except Exception as e:
                print(f"!!! Erro no cliente {dominio}: {e}")
                df.at[index, 'Status'] = "Erro Técnico"
                df.at[index, 'Licencas_Disponiveis'] = "Erro"
                time.sleep(3)

            # SALVAMENTO COM PROTEÇÃO
            salvou = False
            while not salvou:
                try:
                    df.to_excel(ARQUIVO_SAIDA, index=False)
                    salvou = True
                except PermissionError:
                    print("\n⚠️ ATENÇÃO: Feche o arquivo 'resultado_incentivos.xlsx' para o robô salvar.")
                    time.sleep(5)

    finally:
        print("\n=====================================")
        print("Robô finalizado! Planilha salva com sucesso.")
        driver.quit()

if __name__ == "__main__":
    rodar_automacao()