from fpdf import FPDF
from config.conexao import conectar_banco


def calcular_inss(salario):
    if salario <= 1518.00:
        return salario * 0.075
    elif salario <= 2793.88:
        return salario * 0.09
    elif salario <= 4190.83:
        return salario * 0.12
    else:
        return salario * 0.14


def gerar_contracheque(id_funcionario):

    conn = conectar_banco()

    if conn:
        try:
            cursor = conn.cursor()

            sql = """
                SELECT nome, cargo, salario_base, vale_transporte
                FROM funcionario
                WHERE id = %s
            """

            cursor.execute(sql, (id_funcionario,))
            funcionario = cursor.fetchone()

            if not funcionario:
                print("Funcionário não encontrado.")
                return

            nome = funcionario[0]
            cargo = funcionario[1]
            salario = float(funcionario[2])
            vt = funcionario[3]

            desconto_vt = salario * 0.06 if vt == "S" else 0
            desconto_inss = calcular_inss(salario)
            desconto_fgts = salario * 0.08  # FGTS é encargo da empresa, mas exibimos
            salario_liquido = salario - desconto_vt - desconto_inss

            print(f"""
===================================
CONTRACHEQUE
===================================
Funcionário : {nome}
Cargo       : {cargo}
-----------------------------------
Salário Base: R$ {salario:.2f}
-----------------------------------
DESCONTOS:
INSS        : R$ {desconto_inss:.2f}
Vale Transp.: R$ {desconto_vt:.2f}
-----------------------------------
FGTS (ref.) : R$ {desconto_fgts:.2f}
-----------------------------------
SALÁRIO LÍQUIDO: R$ {salario_liquido:.2f}
===================================
""")

        except Exception as e:
            print(f"Erro: {e}")

        finally:
            conn.close()


def exportar_relatorio_pdf(id_funcionario, dia_inicio, mes_inicio, ano_inicio, dia_fim, mes_fim, ano_fim):

    conn = conectar_banco()

    if conn:
        try:
            cursor = conn.cursor()

            # Busca dados do funcionário
            cursor.execute("""
                SELECT nome, cargo, salario_base, vale_transporte
                FROM funcionario WHERE id = %s
            """, (id_funcionario,))
            funcionario = cursor.fetchone()

            if not funcionario:
                print("\n⚠️  Funcionário não encontrado.")
                return

            # Busca registros de ponto no período
            data_inicio = f"{ano_inicio}-{mes_inicio:02d}-{dia_inicio:02d}"
            data_fim = f"{ano_fim}-{mes_fim:02d}-{dia_fim:02d}"

            cursor.execute("""
                SELECT data_registro, entrada, saida
                FROM registro_ponto
                WHERE id_funcionario = %s
                AND data_registro BETWEEN %s AND %s
            """, (id_funcionario, data_inicio, data_fim))

            registros = cursor.fetchall()

            if not registros:
                print(f"""
⚠️  Nenhum registro encontrado para o período
    {dia_inicio:02d}/{mes_inicio:02d}/{ano_inicio} 
    até {dia_fim:02d}/{mes_fim:02d}/{ano_fim}.

    Possíveis motivos:
    - O sistema ainda não possui registros nesse período
    - O funcionário não bateu ponto nesse intervalo
""")
                return

            nome = funcionario[0]
            cargo = funcionario[1]
            salario = float(funcionario[2])
            vt = funcionario[3]

            desconto_vt = salario * 0.06 if vt == "S" else 0
            desconto_inss = calcular_inss(salario)
            desconto_fgts = salario * 0.08
            salario_liquido = salario - desconto_vt - desconto_inss

            pdf = FPDF()
            pdf.add_page()

            pdf.set_font("Arial", "B", 16)
            pdf.cell(200, 10, txt="CONTRACHEQUE", ln=True, align="C")
            pdf.ln(5)

            pdf.set_font("Arial", size=12)
            pdf.cell(200, 8, txt=f"Funcionário: {nome}", ln=True)
            pdf.cell(200, 8, txt=f"Cargo: {cargo}", ln=True)
            pdf.cell(200, 8, txt=f"Período: {dia_inicio:02d}/{mes_inicio:02d}/{ano_inicio} até {dia_fim:02d}/{mes_fim:02d}/{ano_fim}", ln=True)
            pdf.ln(5)

            pdf.set_font("Arial", "B", 12)
            pdf.cell(200, 8, txt="REGISTROS DE PONTO", ln=True)
            pdf.set_font("Arial", size=11)
            for r in registros:
                pdf.cell(200, 7, txt=f"Data: {r[0]}  |  Entrada: {r[1]}  |  Saída: {r[2]}", ln=True)
            pdf.ln(5)

            pdf.set_font("Arial", "B", 12)
            pdf.cell(200, 8, txt="VENCIMENTOS", ln=True)
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 8, txt=f"Salário Base: R$ {salario:.2f}", ln=True)
            pdf.ln(3)

            pdf.set_font("Arial", "B", 12)
            pdf.cell(200, 8, txt="DESCONTOS", ln=True)
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 8, txt=f"INSS: R$ {desconto_inss:.2f}", ln=True)
            pdf.cell(200, 8, txt=f"Vale Transporte: R$ {desconto_vt:.2f}", ln=True)
            pdf.ln(3)

            pdf.set_font("Arial", "B", 12)
            pdf.cell(200, 8, txt=f"FGTS (referência): R$ {desconto_fgts:.2f}", ln=True)
            pdf.ln(5)

            pdf.set_font("Arial", "B", 14)
            pdf.cell(200, 10, txt=f"SALÁRIO LÍQUIDO: R$ {salario_liquido:.2f}", ln=True)

            nome_arquivo = f"contracheque_{id_funcionario}{dia_inicio:02d}{mes_inicio:02d}{ano_inicio}_a{dia_fim:02d}{mes_fim:02d}{ano_fim}.pdf"
            pdf.output(nome_arquivo)

            print(f"\n✅ PDF exportado com sucesso: {nome_arquivo}")

        except Exception as e:
            print(f"Erro: {e}")

        finally:
            conn.close()