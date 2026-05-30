from flask import Flask,redirect, url_for, render_template, request, session,flash
import psycopg2
from dotenv import load_dotenv
import os   


#carregar .ENV  
load_dotenv()

#comecar o Flask
app = Flask(__name__)   

    #configurar a chave secreta para sessões
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")


# conexão com o banco de dados PostgreSQL
conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    port=os.getenv("DB_PORT")
)

# criar um cursor para executar comandos SQL
cursor = conn.cursor()

#rota principal
@app.route('/')
def index():
    return render_template('index.html')    



#MOSTRAR PRODUTOS CADASTRADOS
@app.route('/produtos', methods=['GET'])
def listar_produtos():
    cursor.execute("SELECT * FROM produtos")
    produtos = cursor.fetchall()
    return render_template('clientescadastro.html', produtos=produtos)

# Cadastrar produto
@app.route('/add', methods=['POST'])
def add_produto ():
    # produto = request.form['produto']
    # preco = request.form['preco']
    # quantidade = request.form['quantidade']
    # categoria = request.form['categoria']   
    # 1. Capturar os dados usando .get() por segurança
    produto = request.form.get('produto')
    preco = request.form.get('preco')
    quantidade = request.form.get('quantidade')
    categoria = request.form.get('categoria')   

    # 2. Dicionário mapeando o name do HTML para o nome que aparece no erro
    campos_obrigatorios = {
        'produto': 'Nome do Produto',
        'preco': 'Preço',
        'quantidade': 'Quantidade',
        'categoria': 'Categoria'
    }
    
    erro_encontrado = False
    
    # 3. Validar se algum campo está vazio
    for chave, nome_exibicao in campos_obrigatorios.items():
        # Pega o valor da variável dinamicamente usando as variáveis locais do Python
        valor = locals().get(chave) 
        
        if not valor or str(valor).strip() == "":
            flash(f"O campo '{nome_exibicao}' não pode ficar vazio!", "error")
            erro_encontrado = True

    # 4. Se houver erro, interrompe o cadastro e redireciona de volta
    if erro_encontrado:
        return redirect('/') # Ou para a página onde está o formulário

    # Inserir o produto no banco de dados
    cursor.execute("""INSERT INTO produtos 
                   (nome,
                   preco,
                   quantidade,
                   categoria) 
                   VALUES (%s, %s, %s, %s)""",(produto,
                     preco,
                       quantidade,
                         categoria))
    conn.commit()  # Salvar as alterações no banco de dados
    return redirect('/')  # Redirecionar para a página principal

# Atualizar quantidade

@app.route('/editar/<int:id>')
def editar_produto(id):

    cursor.execute(
        "SELECT * FROM produtos WHERE id = %s",
        (id,)
    )

    produto = cursor.fetchone()

    return render_template(
        'editarproduto.html',
        produto=produto
    )

# Salvar alterações
@app.route('/update/<int:id>', methods=['POST'])
def update_produto(id):

    nome = request.form['produto']
    preco = request.form['preco']
    quantidade = request.form['quantidade']
    categoria = request.form['categoria']

    cursor.execute("""
        UPDATE produtos
        SET
            nome = %s,
            preco = %s,
            quantidade = %s,
            categoria = %s
        WHERE id = %s
    """, (
        nome,
        preco,
        quantidade,
        categoria,
        id
    ))

    conn.commit()

    flash("Produto atualizado com sucesso!", "success")

    return redirect('/produtos')

# apagar produto
@app.route('/delete/<int:id>', methods=['POST', 'GET', 'DELETE'])
def delete_produto(id):
    cursor.execute("DELETE FROM produtos WHERE id = %s", (id,))
    conn.commit()# Salvar as alterações no banco de dados

    return redirect('/produtos')  # Redirecionar para a página de produtos


if __name__ == "__main__":
    app.run(debug=True)