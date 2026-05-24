# Jogo de Adivinhação (Kubernetes)

## 📌 1. Descrição do Projeto

Este projeto implementa um jogo de adivinhação em ambiente web.  O sistema permite que um usuário crie um jogo definindo uma palavra secreta e outro usuário tente adivinhar essa palavra com base em dicas fornecidas pelo sistema. A aplicação foi originalmente desenvolvida com Docker e posteriormente reorganizada para execução em Kubernetes, utilizando **k3d** como ambiente local de cluster.  
O objetivo desta entrega é demonstrar a migração da aplicação para uma arquitetura orquestrada em Kubernetes, permitindo sua execução de forma reproduzível, organizada e alinhada aos conceitos de implantação declarativa.

---

## 🏗️ 2. Arquitetura da Solução

A aplicação foi organizada em uma arquitetura composta por serviços independentes, cada um com uma responsabilidade específica dentro do ambiente Kubernetes:  
- **Frontend (React)**: responsável pela interface web com a qual o usuário interage.   
- **Backend (Flask)**: responsável pela lógica do jogo, processamento das tentativas e comunicação com o banco de dados.   
- **PostgreSQL**: responsável pela persistência dos dados da aplicação.   
- **NGINX**: atua como proxy reverso e ponto de entrada da aplicação, encaminhando as requisições para os serviços internos adequados.   
- **Kubernetes (k3d)**: responsável pela orquestração dos contêineres, gerenciamento dos recursos e comunicação entre os componentes.   
- **HPA (Horizontal Pod Autoscaler)**: configurado para escalar horizontalmente o backend de acordo com o uso de CPU.   
No fluxo da aplicação, o usuário acessa o sistema por meio do NGINX, que recebe as requisições externas e faz o roteamento para o frontend e para o backend. O backend, por sua vez, processa a lógica da aplicação e realiza as operações necessárias no PostgreSQL. Dentro do Kubernetes, a comunicação entre os componentes ocorre por meio de Services, que fornecem endereçamento interno estável e permitem o acesso aos pods correspondentes.  
Essa organização permite separar responsabilidades, facilitar a manutenção da aplicação e suportar escalabilidade no backend sem comprometer a estrutura geral do sistema.

---

## ☸️ 3. Ambiente Kubernetes (k3d)


Este projeto utiliza k3d como ambiente local para execução do cluster Kubernetes. O k3d foi escolhido por permitir a criação de clusters leves e rápidos sobre Docker, facilitando o desenvolvimento, os testes e a reprodução do ambiente da aplicação.  
Para executar o projeto, o primeiro passo é criar o cluster Kubernetes local:  
**Criar o cluster** 
```bash 
k3d cluster create guess-game  
```
Após a criação, é importante verificar se o cluster está ativo e acessível pelo kubectl:  
**Verificar o cluster**  
```bash
kubectl cluster-info
```
Com o cluster em funcionamento, o ambiente estará pronto para receber os componentes necessários da aplicação e os manifests definidos no diretório k8s/.

---

## 📦 4. Imagens Docker

As imagens utilizadas no projeto devem estar disponíveis no Docker Hub para que o Kubernetes consiga criar os pods corretamente. As imagens referenciadas são:  
- Frontend: zicmabr/guess-game-frontend:v1.0.0   
- Backend: zicmabr/guess-game-backend:v1.0.1   
- NGINX:  zicmabr/guess-game-nginx:v1.0.0  
- PostgreSQL: postgres:15 (utiliza o Postgres do Docker Hub)  
Certifique-se de que o cluster possui acesso à internet para realizar o pull dessas imagens.

---

## 📁 5. Estrutura Kubernetes

Os manifests Kubernetes da aplicação estão organizados no diretório k8s/. Esses arquivos definem os recursos necessários para implantação, comunicação entre os componentes, persistência de dados e escalabilidade do sistema.  
A estrutura é composta pelos seguintes arquivos:  
- **postgres.yaml** — define os recursos do PostgreSQL, incluindo implantação, serviço e persistência de dados.   
- **backend.yaml** — define a implantação e a exposição interna do backend Flask.   
- **frontend.yaml** — define a implantação e a exposição interna do frontend React.   
- **nginx.yaml** — define a implantação do NGINX, sua configuração como proxy reverso e a exposição da aplicação para acesso externo.   
- **hpa.yaml** — define o Horizontal Pod Autoscaler do backend, responsável pelo ajuste automático do número de réplicas com base no uso de CPU.   
- **kustomization.yaml** — agrega os manifests da aplicação, permitindo aplicar toda a stack de forma declarativa por meio de um único comando.   
Essa organização facilita a manutenção dos recursos e permite recriar o ambiente Kubernetes da aplicação de forma mais consistente e reproduzível.

---

## ⚙️ 6. Pré-requisitos

Antes de executar a aplicação, é necessário que o ambiente tenha os seguintes componentes instalados e disponíveis:  
- Docker   
- k3d   
- kubectl   
- Acesso à internet para download de imagens e instalação de componentes do cluster

---

## 📊 7. HPA (Auto Scaling)


O backend da aplicação utiliza Horizontal Pod Autoscaler (HPA) para ajustar automaticamente a quantidade de réplicas de acordo com o uso de CPU. Esse recurso foi aplicado ao serviço responsável pela lógica do sistema, permitindo que a aplicação responda melhor a variações de carga.  
A configuração adotada define:  
- alvo de utilização de CPU: 50%   
- mínimo de réplicas: 1   
- máximo de réplicas: 3     

Para que o HPA funcione corretamente, é necessário que o metrics-server esteja instalado no cluster, pois ele é responsável por disponibilizar as métricas usadas no processo de escalabilidade.
Durante os testes realizados no ambiente Kubernetes, o autoscaling do backend foi validado com sucesso, apresentando aumento do número de réplicas sob carga e redução posterior após a normalização do uso de CPU.

**Monitoramento** 
```bash 
kubectl get hpa  
kubectl describe hpa  
```

---

## 🚀 8. Como Executar


Siga os passos abaixo para executar a aplicação no ambiente Kubernetes local:

1. Clonar o repositório
```bash
git clone https://github.com/Zicmafal/guess_game_k8s.git
``` 

2. Acessar a pasta do projeto
```bash
cd guess_game
``` 

3. Criar o cluster Kubernetes com k3d  
```bash
k3d cluster create guess-game
``` 

4. Verificar se o cluster está ativo  
```bash
kubectl cluster-info
``` 

5. Instalar o metrics-server  
O metrics-server é necessário para o funcionamento do HPA no backend.  
```bash
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
```

6. Aplicar os manifests da aplicação  
```bash
kubectl apply -k k8s/
```

7. Verificar os recursos criados 
```bash 
kubectl get deployments  
kubectl get pods  
kubectl get svc  
kubectl get hpa  
```

Após a execução, verifique se os pods estão em estado Running, se o volume persistente do PostgreSQL está em estado Bound e se o HPA do backend foi criado corretamente.

---

## 🌐 9. Acesso ao Sistema


Após a implantação da aplicação no cluster Kubernetes, o acesso ao sistema pode ser feito por meio do serviço do NGINX, que está exposto externamente.

### Acesso principal
A forma principal de acesso à aplicação é pelo NodePort configurado no serviço do NGINX:
http://localhost:30080  
(também funciona http://localhost/ )

### Acesso alternativo
Como alternativa, também é possível acessar a aplicação utilizando redirecionamento de porta com o comando abaixo:  
```
kubectl port-forward svc/nginx 8080:80
```
Nesse caso, o sistema ficará disponível em:  
http://localhost:8080

---


## 🎮 10. Uso do Sistema 

1. **Criar um jogo**:  
    - Clique em "Create a Game" ou "Maker".   
    - Insira uma palavra secreta.   
    - Clique em "Create Game". Anote o ID do jogo para compartilhar.   
2. **Fazer uma tentativa**:  
    - Clique em "Join a Game" ou "Breaker".   
    - Insira o ID do jogo.   
    - Digite sua tentativa em "your Guess".   
    - Clique em "Submit Guess".   
    - Veja as dicas.   
Os dados são salvos no banco e persistem mesmo ao reiniciar os containers.


---

## ✅ 11. Conclusão


O projeto demonstra a migração de uma aplicação originalmente executada em contêineres para uma arquitetura orquestrada em Kubernetes, com organização dos recursos em manifests declarativos. A solução final contempla frontend em React, backend em Flask, PostgreSQL com persistência de dados, NGINX como proxy reverso e autoscaling horizontal do backend com HPA.  
Com essa estrutura, a aplicação passa a contar com melhor organização dos componentes, separação de responsabilidades, escalabilidade no backend e maior consistência no processo de implantação. Além disso, a centralização dos manifests no diretório k8s/ contribui para a reprodutibilidade do ambiente, permitindo recriar a stack de forma padronizada.



























