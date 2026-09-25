"""Testes de extração — um caso por produto.

Execute com ``python -m unittest discover -s tests`` a partir da raiz do projeto.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from extractor.extractor import extract_record


class ProductExtractionTests(unittest.TestCase):
    def test_allianz(self):
        texto = (
            "ALLIANZ SEGUROS\n"
            "Assistência: 123456\n"
            "Serviço: REBOQUE LEVE\n"
            "Local: Rua A, 100\n"
            "Cidade: São Paulo\n"
            "Destino: Rua B, 200\n"
            "Cidade: Campinas\n"
        )
        r = extract_record(texto)
        self.assertEqual(r["CLIENTE"], "ALLIANZ")
        self.assertEqual(r["ASSISTENCIA"], "123456")
        self.assertEqual(r["CATEGORIA"], "LEVE")
        self.assertEqual(r["ORIGEM"], "São Paulo")
        self.assertEqual(r["DESTINO"], "Campinas")

    def test_azul(self):
        texto = (
            "AZUL SEGUROS\n"
            "SERVIÇO: 987654\n"
            "Tipo de Serviço: REBOQUE LEVE\n"
            "Endereço Ocorrência: Rua X, 10 - São Paulo - SP\n"
            "Endereço Destino: Rua Y, 20 - Campinas - SP\n"
        )
        r = extract_record(texto)
        self.assertEqual(r["CLIENTE"], "AZUL")
        self.assertEqual(r["ASSISTENCIA"], "987654")
        self.assertEqual(r["CATEGORIA"], "LEVE")
        self.assertEqual(r["ORIGEM"], "São Paulo")
        self.assertEqual(r["DESTINO"], "Campinas")

    def test_bradesco(self):
        texto = (
            "BRADESCO AUTORE COMPANHIA DE SEGUROS\n"
            "# Serviço: 555666\n"
            "Tipo de serviço: REBOQUE - LEVE\n"
            "LOCAIS DO ATENDIMENTO\n"
            "(1) Rua A, 100 - São Paulo - SP\n"
            "(2) Rua B, 200 - Campinas - SP\n"
        )
        r = extract_record(texto)
        self.assertEqual(r["CLIENTE"], "BRADESCO")
        self.assertEqual(r["ASSISTENCIA"], "555666")
        self.assertEqual(r["CATEGORIA"], "LEVE")
        self.assertEqual(r["ORIGEM"], "São Paulo")
        self.assertEqual(r["DESTINO"], "Campinas")

    def test_caoa_chery(self):
        texto = (
            "CAOA MONTADORA DE VEÍCULOS\n"
            "Assistência: 111222\n"
            "Serviço: REBOQUE/UTILITÁRIO\n"
            "Local: Rua A\n"
            "Cidade: Ituverava\n"
            "Destino: Rua B\n"
            "Cidade: Itamogi\n"
        )
        r = extract_record(texto)
        self.assertEqual(r["CLIENTE"], "CAOA CHERY")
        self.assertEqual(r["CATEGORIA"], "UTILITARIO")
        self.assertEqual(r["ORIGEM"], "Ituverava")
        self.assertEqual(r["DESTINO"], "Itamogi")

    def test_fca_fiat(self):
        texto = (
            "FCA FIAT CHRYSLER\n"
            "# Serviço: 333444\n"
            "Tipo de serviço: REBOQUE - PESADO\n"
            "LOCAIS DO ATENDIMENTO\n"
            "(1) Rua A - Belo Horizonte - MG\n"
            "(2) Rua B - Contagem - MG\n"
        )
        r = extract_record(texto)
        self.assertEqual(r["CLIENTE"], "FCA FIAT")
        self.assertEqual(r["ASSISTENCIA"], "333444")
        self.assertEqual(r["CATEGORIA"], "PESADO")
        self.assertEqual(r["ORIGEM"], "Belo Horizonte")
        self.assertEqual(r["DESTINO"], "Contagem")

    def test_hdi(self):
        texto = (
            "HDI SEGUROS S.A.\n"
            "Assistência: 777888\n"
            "Serviço: GUINCHO LEVE\n"
            "ORIGEM:\n"
            "Cidade: Itamogi\n"
            "DESTINO:\n"
            "Cidade: Ituverava\n"
            "KM DESLOCAMENTO: 83\n"
            "KM EXCEDENTE: 290\n"
        )
        r = extract_record(texto)
        self.assertEqual(r["CLIENTE"], "HDI")
        self.assertEqual(r["CATEGORIA"], "LEVE")
        self.assertEqual(r["ORIGEM"], "Itamogi")
        self.assertEqual(r["DESTINO"], "Ituverava")
        self.assertEqual(r["KM TOTAL"], "413")
        self.assertEqual(r["VALOR"], "")

    def test_movida(self):
        texto = (
            "Movida Participacoes S.A.\n"
            "Protocolo: 2001\n"
            "Tipo de serviço: Reboque Leve\n"
            "Origem: Passos\n"
            "Destino: Alpinópolis\n"
            "Percurso Total: 120\n"
            "Valor Total: 350,00\n"
        )
        r = extract_record(texto)
        self.assertEqual(r["CLIENTE"], "MOVIDA")
        self.assertEqual(r["ASSISTENCIA"], "2001")
        self.assertEqual(r["CATEGORIA"], "LEVE")
        self.assertEqual(r["ORIGEM"], "Passos")
        self.assertEqual(r["DESTINO"], "Alpinópolis")
        self.assertEqual(r["KM TOTAL"], "120")
        self.assertEqual(r["VALOR"], "350")

    def test_porto(self):
        texto = (
            "PORTO SERVIÇO S.A.\n"
            "SERVIÇO: 888999\n"
            "Tipo de Serviço: TRANSPORTE\n"
            "Endereço Ocorrência: Rua X - Curitiba - PR\n"
            "Endereço Destino: Rua Y - São Paulo - SP\n"
        )
        r = extract_record(texto)
        self.assertEqual(r["CLIENTE"], "PORTO")
        self.assertEqual(r["ASSISTENCIA"], "888999")
        self.assertEqual(r["CATEGORIA"], "TAXI")
        self.assertEqual(r["ORIGEM"], "Curitiba")
        self.assertEqual(r["DESTINO"], "São Paulo")

    def test_resolve_assist(self):
        texto = (
            "RESOLVE ASSIST\n"
            "Protocolo: RES12345\n"
            "Tipo de serviço: Reboque Utilitário\n"
            "Origem: Itau de Minas\n"
            "Destino: Passos\n"
            "Percurso Total: 90\n"
        )
        r = extract_record(texto)
        self.assertEqual(r["CLIENTE"], "RESOLVE ASSIST")
        self.assertEqual(r["ASSISTENCIA"], "RES12345")
        self.assertEqual(r["CATEGORIA"], "UTILITARIO")
        self.assertEqual(r["ORIGEM"], "Itau de Minas")
        self.assertEqual(r["DESTINO"], "Passos")
        self.assertEqual(r["KM TOTAL"], "90")

    def test_santander(self):
        texto = (
            "SANTANDER AUTO\n"
            "Assistência: 1010\n"
            "Serviço: GUINCHO UTILITÁRIOS\n"
            "ORIGEM:\n"
            "Cidade: Itamogi\n"
            "DESTINO:\n"
            "Cidade: Ituverava\n"
            "KM DESLOCAMENTO: 83\n"
            "KM EXCEDENTE: 290\n"
        )
        r = extract_record(texto)
        self.assertEqual(r["CLIENTE"], "SANTANDER")
        self.assertEqual(r["ASSISTENCIA"], "1010")
        self.assertEqual(r["CATEGORIA"], "UTILITARIO")
        self.assertEqual(r["ORIGEM"], "Itamogi")
        self.assertEqual(r["DESTINO"], "Ituverava")
        self.assertEqual(r["KM TOTAL"], "413")

    def test_suhai(self):
        texto = (
            "SUHAI SEGURADORA\n"
            "Assistência: 2020\n"
            "Serviço: REBOQUE/PLATAFORMA\n"
            "Cidade: Passos\n"
            "Destino:\n"
            "Cidade: Guaxupé\n"
            "KM DESLOCAMENTO: 40\n"
            "KM EXCEDENTE: 60\n"
        )
        r = extract_record(texto)
        self.assertEqual(r["CLIENTE"], "SUHAI")
        self.assertEqual(r["CATEGORIA"], "LEVE")
        self.assertEqual(r["ORIGEM"], "Passos")
        self.assertEqual(r["DESTINO"], "Guaxupé")
        self.assertEqual(r["KM TOTAL"], "140")

    def test_sura(self):
        texto = (
            "SURA SEGUROS\n"
            "Assistência: 3030\n"
            "Serviço: REBOQUE/REBOQUE PATINS\n"
            "Cidade: Franca\n"
            "Destino:\n"
            "Cidade: Ribeirão Preto\n"
        )
        r = extract_record(texto)
        self.assertEqual(r["CLIENTE"], "SURA")
        self.assertEqual(r["CATEGORIA"], "LEVE")
        self.assertEqual(r["ORIGEM"], "Franca")
        self.assertEqual(r["DESTINO"], "Ribeirão Preto")

    def test_tato_assist(self):
        texto = (
            "TATO ASSIST\n"
            "Protocolo: 202456\n"
            "Tipo de serviço: Reboque Utilitário\n"
            "Origem: São Paulo\n"
            "Destino: Campinas\n"
            "Percurso Total: 95\n"
        )
        r = extract_record(texto)
        self.assertEqual(r["CLIENTE"], "TATO ASSIST")
        self.assertEqual(r["ASSISTENCIA"], "202456")
        self.assertEqual(r["CATEGORIA"], "UTILITARIO")
        self.assertEqual(r["ORIGEM"], "São Paulo")
        self.assertEqual(r["DESTINO"], "Campinas")
        self.assertEqual(r["KM TOTAL"], "95")

    def test_tokio(self):
        texto = (
            "Ordem de Serviço: OS998877\n"
            "Tipo de Evento: REBOQUE LEVE\n"
            "Origem: São Paulo - SP\n"
        )
        r = extract_record(texto)
        self.assertEqual(r["CLIENTE"], "TOKIO")
        self.assertEqual(r["ASSISTENCIA"], "OS998877")
        self.assertEqual(r["CATEGORIA"], "LEVE")
        self.assertEqual(r["ORIGEM"], "São Paulo")
        self.assertEqual(r["DESTINO"], "")

    def test_universo_agv(self):
        texto = (
            "Universo Agv\n"
            "Protocolo: 4040\n"
            "Tipo de Serviço: Reboque Utilitario\n"
            "Endereço de Acionamento:\n"
            "Origem: Itau de Minas - MG\n"
            "Destino: Passos - MG\n"
            "Percurso Total: 80\n"
            "Valor: 250,00\n"
        )
        r = extract_record(texto)
        self.assertEqual(r["CLIENTE"], "UNIVERSO AGV")
        self.assertEqual(r["ASSISTENCIA"], "4040")
        self.assertEqual(r["CATEGORIA"], "UTILITARIO")
        self.assertEqual(r["ORIGEM"], "Itau de Minas")
        self.assertEqual(r["DESTINO"], "Passos")
        self.assertEqual(r["KM TOTAL"], "80")
        self.assertEqual(r["VALOR"], "250")

    def test_velox(self):
        texto = (
            "VELOX\n"
            "Protocolo: 5050\n"
            "Serviço assistência: REBOQUE UTILITARIO\n"
            "ENDEREÇO DO ATENDIMENTO:\n"
            "ORIGEM: Passos - MG\n"
            "DESTINO: Guaxupé - MG\n"
            "Distância Total: 70\n"
            "Valor Total do Serviço: 300,00\n"
        )
        r = extract_record(texto)
        self.assertEqual(r["CLIENTE"], "VELOX")
        self.assertEqual(r["ASSISTENCIA"], "5050")
        self.assertEqual(r["CATEGORIA"], "UTILITARIO")
        self.assertEqual(r["ORIGEM"], "Passos")
        self.assertEqual(r["DESTINO"], "Guaxupé")
        self.assertEqual(r["KM TOTAL"], "70")
        self.assertEqual(r["VALOR"], "300")

    def test_yelum(self):
        texto = (
            "YELUM\n"
            "Assistência: 9887901\n"
            "Serviço: GUINCHO UTILITÁRIOS\n"
            "ORIGEM:\n"
            "Cidade: Itamogi\n"
            "DESTINO:\n"
            "Cidade: Ituverava\n"
            "KM DESLOCAMENTO: 83\n"
            "KM EXCEDENTE: 290\n"
        )
        r = extract_record(texto)
        self.assertEqual(r["CLIENTE"], "YELUM")
        self.assertEqual(r["ASSISTENCIA"], "9887901")
        self.assertEqual(r["CATEGORIA"], "UTILITARIO")
        self.assertEqual(r["ORIGEM"], "Itamogi")
        self.assertEqual(r["DESTINO"], "Ituverava")
        self.assertEqual(r["KM TOTAL"], "413")

    def test_yelum_real_portal_tabular(self):
        texto = (
            "Assistência\t\tSolicitação\t\tProduto\t\tData solicitação\n"
            "9651512\n"
            "2\n"
            "YELUM\n"
            "28/05/2026 12:16\n"
            "SERVIÇO #1\n"
            "GUINCHO - GUINCHO LEVE (AUTO)\n"
            "ORIGEM\t\n"
            "R. Orquídeas, 480, Capitólio - MG\n"
            "Bairro\t\tCidade\t\tEstado\t\tCEP\n"
            "Centro\n"
            "Capitólio\n"
            "MG\n"
            "DESTINO\n"
            "Av. Juca Stockler, 1777 - Passos, MG\n"
            "Bairro\t\tCidade\t\tEstado\t\tCEP\n"
            "Jardim Belo Horizonte\n"
            "Passos\n"
            "MG\n"
            "SENHA\tTARIFA\tQUANTIDADE\n"
            "107\tKM (EXCEDENTE)\t116\n"
            "109\tSAÍDA\t1\n"
        )
        r = extract_record(texto)
        self.assertEqual(r["CLIENTE"], "YELUM")
        self.assertEqual(r["ASSISTENCIA"], "9651512/2")
        self.assertEqual(r["CATEGORIA"], "LEVE")
        self.assertEqual(r["ORIGEM"], "Capitólio")
        self.assertEqual(r["DESTINO"], "Passos")
        self.assertEqual(r["KM TOTAL"], "156")
        self.assertEqual(r["OBS"], "")

    def test_youse(self):
        texto = (
            "YOUSE SEGUROS\n"
            "Ordem de Serviço: A26080208724/2\n"
            "Tipo de serviço: Reboque leve\n"
            "Origem: Passos\n"
            "Destino: Alpinópolis\n"
            "Percurso Total: 110\n"
            "Valor Total: 400,00\n"
        )
        r = extract_record(texto)
        self.assertEqual(r["CLIENTE"], "YOUSE")
        self.assertEqual(r["ASSISTENCIA"], "A26080208724/2")
        self.assertEqual(r["CATEGORIA"], "LEVE")
        self.assertEqual(r["ORIGEM"], "Passos")
        self.assertEqual(r["DESTINO"], "Alpinópolis")
        self.assertEqual(r["KM TOTAL"], "110")
        self.assertEqual(r["VALOR"], "400")

    def test_unknown(self):
        texto = "Bom dia, pessoal!\nConversa interna sem dados de assistência."
        r = extract_record(texto)
        self.assertEqual(r["PRODUTO"], "unknown")
        self.assertIn("produto nao identificado", r["OBS"])


if __name__ == "__main__":
    unittest.main()
