# Manual de Utilização — Front-End

Este manual explica como rodar o projeto de maneira simples, possibilitando o acesso ao front-end e suas funcionalidades via terminal.

## Pré-requisitos

- Python 3.10+
- Docker
- Git

## Ativação do Ambiente Virtual

```bash
python -m venv venv
```
e na sequência:

```bash
.\venv\Scripts\activate
```

## Rodando o Projeto:

Com o Docker aberto, executar o seguinte comando pela primeira vez:

```bash
docker-compose up --build -d
```
ou em execuções seguintes simplificar para:

```bash
docker-compose up --build -d
```

## Acessando Página Web:

Para o primeiro acesso na web, instale o pacote Streamlit:

```bash
pip install streamlit
```
selecione a pasta "frontend" e, para execuções seguintes, execute:

```bash
streamlit run app.py
```
então, ao seguir o link http://192.168.0.12:8501/, deve encontrar a seguinte página:

<img width="1919" height="1010" alt="Image" src="https://github.com/user-attachments/assets/4ef908d7-5a88-4010-8bd1-3a8b89dc648b" />

## Funcionalidades
<img width="1919" height="1007" alt="Image" src="https://github.com/user-attachments/assets/31a5dfe9-28a8-4332-9c0b-cc6ca49a5ae0" />
Ao acessar a interface, deve encontrar quatro abas, três para ingestão de documentos e uma para consulta. A primeira, conforme a imagem anterior, serve para salvar uma e apenas uma URL por vez.
<img width="1919" height="1005" alt="Image" src="https://github.com/user-attachments/assets/85e8567e-95b9-4f84-bf16-166913ec7166" />
A segunda aba possibilita a ingestão de múltiplas URL's por vez, desde escrita uma em cada linha.
<img width="1919" height="1005" alt="Image" src="https://github.com/user-attachments/assets/478b826f-e21e-4a0f-a9c6-bd31184f7cba" />
A terceira possibilita a ingestão de arquivos PDF salvos através de Drag and Drop. Ao final dos passos anteriores, não se esqueça de confirmar clicando no botão "Enviar" equivalente.
<img width="1919" height="1003" alt="Image" src="https://github.com/user-attachments/assets/b5c2adb4-6a00-48da-9dbf-92d04d3d0867" />
A aba de consulta exerce a função fundamental do projeto de reunir informação de forma organizada. Após realizar sua pergunta, não se esqueça de confirmar com o botão "Consultar".

## Extra: Caso de Erro
Ao longo do desenvolvimento foi enfrentado um erro após a execução do código "docker-compose up --build -d" ao rodar o projeto.
<img width="1919" height="1007" alt="Image" src="https://github.com/user-attachments/assets/8594986e-434e-48b7-8a7b-cc68a5cb358b" />
Para resolver foram executados dois comandos:
```bash
docker-compose down
```
o primeiro para parar a execução inicial e, em seguida, para resolver o erro:
```bash
wsl--shutdown
```
<img width="1919" height="1007" alt="Image" src="https://github.com/user-attachments/assets/3dce1181-04d6-4c89-bdd2-01525d01a6cb" />
Após isso, a nova execução do "docker-compose up --build -d" foi um sucesso.
