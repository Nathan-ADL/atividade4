from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import mysql.connector
import datetime
import hashlib
from database import obter_conexao

app = Flask(__name__)
app.secret_key = "barbearia_secret_key_2026"

SENHA_ADMIN = "barber@admin123"


def fmt_time(t):
    if t is None:
        return None
    if isinstance(t, datetime.timedelta):
        total = int(t.total_seconds())
        h = total // 3600
        m = (total % 3600) // 60
        return f"{h:02d}:{m:02d}"
    s = str(t)[:5].strip()
    return None if s == '' else s


def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()


# ─── AUTENTICAÇÃO ────────────────────────────────────────────────────────────

@app.route("/login")
def login():
    if "usuario_id" in session:
        if session.get("tipo") == "barbeiro":
            return redirect(url_for("painel_barbeiro"))
        return redirect(url_for("home"))
    return render_template("login.html")


@app.route("/cadastro")
def cadastro():
    tipo = request.args.get("tipo", "cliente")
    return render_template("cadastro.html", tipo=tipo)


@app.route("/api/login", methods=["POST"])
def api_login():
    dados = request.get_json()
    tipo = dados.get("tipo")
    email = dados.get("email", "").strip().lower()
    senha = dados.get("senha", "")

    if not email or not senha:
        return jsonify({"ok": False, "erro": "Preencha todos os campos."}), 400

    conexao = obter_conexao()
    cursor = conexao.cursor(dictionary=True)

    if tipo == "barbeiro":
        cursor.execute("SELECT id, nome, senha FROM barbeiro WHERE email=%s", (email,))
        user = cursor.fetchone()
        if not user or user["senha"] != hash_senha(senha):
            cursor.close(); conexao.close()
            return jsonify({"ok": False, "erro": "Email ou senha incorretos."}), 401
        session["usuario_id"] = user["id"]
        session["nome"] = user["nome"]
        session["tipo"] = "barbeiro"
        cursor.close(); conexao.close()
        return jsonify({"ok": True, "redirect": "/barbeiro"})

    else:
        cursor.execute("SELECT id, nome, senha FROM cliente WHERE email=%s", (email,))
        user = cursor.fetchone()
        if not user or user["senha"] != hash_senha(senha):
            cursor.close(); conexao.close()
            return jsonify({"ok": False, "erro": "Email ou senha incorretos."}), 401
        session["usuario_id"] = user["id"]
        session["nome"] = user["nome"]
        session["tipo"] = "cliente"
        cursor.close(); conexao.close()
        return jsonify({"ok": True, "redirect": "/"})


@app.route("/api/cadastro", methods=["POST"])
def api_cadastro():
    dados = request.get_json()
    tipo = dados.get("tipo")
    nome = dados.get("nome", "").strip()
    email = dados.get("email", "").strip().lower()
    senha = dados.get("senha", "")
    senha_admin = dados.get("senha_admin", "")

    if not all([nome, email, senha]):
        return jsonify({"ok": False, "erro": "Preencha todos os campos."}), 400

    conexao = obter_conexao()
    cursor = conexao.cursor(dictionary=True)

    if tipo == "barbeiro":
        if senha_admin != SENHA_ADMIN:
            cursor.close(); conexao.close()
            return jsonify({"ok": False, "erro": "Senha administrativa incorreta."}), 403
        cursor.execute("SELECT id FROM barbeiro WHERE email=%s", (email,))
        if cursor.fetchone():
            cursor.close(); conexao.close()
            return jsonify({"ok": False, "erro": "Email já cadastrado."}), 409
        cursor.execute(
            "INSERT INTO barbeiro (nome, email, senha) VALUES (%s, %s, %s)",
            (nome, email, hash_senha(senha))
        )
        conexao.commit()
        novo_id = cursor.lastrowid
        session["usuario_id"] = novo_id
        session["nome"] = nome
        session["tipo"] = "barbeiro"
        cursor.close(); conexao.close()
        return jsonify({"ok": True, "redirect": "/barbeiro"})

    else:
        cursor.execute("SELECT id FROM cliente WHERE email=%s", (email,))
        if cursor.fetchone():
            cursor.close(); conexao.close()
            return jsonify({"ok": False, "erro": "Email já cadastrado."}), 409
        cursor.execute(
            "INSERT INTO cliente (nome, email, senha) VALUES (%s, %s, %s)",
            (nome, email, hash_senha(senha))
        )
        conexao.commit()
        novo_id = cursor.lastrowid
        session["usuario_id"] = novo_id
        session["nome"] = nome
        session["tipo"] = "cliente"
        cursor.close(); conexao.close()
        return jsonify({"ok": True, "redirect": "/"})


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ─── PÁGINA PRINCIPAL (agendamento) ──────────────────────────────────────────

@app.route("/")
def home():
    if "usuario_id" not in session or session.get("tipo") != "cliente":
        return redirect(url_for("login"))

    try:
        conexao = obter_conexao()
        cursor = conexao.cursor(dictionary=True)

        cursor.execute("SELECT id, nome, `preco` AS preco, descricao, duracao_min FROM servicos")
        rows_servicos = cursor.fetchall()
        lista_servicos = []
        for s in rows_servicos:
            lista_servicos.append({
                "id": s["id"],
                "nome": s["nome"],
                "preco": float(s["preco"]),
                "descricao": s["descricao"],
                "duracao_min": s["duracao_min"]
            })

        cursor.execute("SELECT id, nome, especialidade FROM barbeiro")
        lista_barbeiros = cursor.fetchall()

        cursor.execute(
            "SELECT id, barbeiro_id, dia_semana, hora_inicio, hora_fim "
            "FROM disponibilidade "
            "WHERE hora_inicio IS NOT NULL AND hora_fim IS NOT NULL"
        )
        rows_dispo = cursor.fetchall()
        lista_disponibilidade = []
        for d in rows_dispo:
            lista_disponibilidade.append({
                "id": d["id"],
                "barbeiro_id": int(d["barbeiro_id"]),
                "dia_semana": int(d["dia_semana"]),
                "hora_inicio": fmt_time(d["hora_inicio"]),
                "hora_fim": fmt_time(d["hora_fim"])
            })

        # Exceções de disponibilidade (dias com horário diferente ou folga)
        cursor.execute(
            "SELECT barbeiro_id, data, hora_inicio, hora_fim "
            "FROM disponibilidade_excecao"
        )
        rows_excecao = cursor.fetchall()
        lista_excecoes = []
        for e in rows_excecao:
            lista_excecoes.append({
                "barbeiro_id": int(e["barbeiro_id"]),
                "data": e["data"].strftime("%Y-%m-%d") if e["data"] else "",
                "hora_inicio": fmt_time(e["hora_inicio"]),
                "hora_fim": fmt_time(e["hora_fim"])
            })

        cursor.execute(
            "SELECT a.id, a.barbeiro_id, a.data, a.horario "
            "FROM agendamento a"
        )
        rows_agend = cursor.fetchall()
        lista_agendamentos = []
        for a in rows_agend:
            cursor2 = conexao.cursor(dictionary=True)
            cursor2.execute(
                "SELECT servico_id FROM agendamento_servicos WHERE agendamento_id=%s",
                (a["id"],)
            )
            sids = [r["servico_id"] for r in cursor2.fetchall()]
            cursor2.close()
            lista_agendamentos.append({
                "barbeiro_id": int(a["barbeiro_id"]),
                "servico_ids": sids,
                "data":        a["data"].strftime("%Y-%m-%d") if a["data"] else "",
                "horario":     fmt_time(a["horario"])
            })

        cursor.close()
        conexao.close()

    except Exception as erro:
        print(f"ERRO DETALHADO: {erro}")
        lista_servicos = []
        lista_barbeiros = []
        lista_disponibilidade = []
        lista_excecoes = []
        lista_agendamentos = []

    return render_template(
        "index.html",
        servicos=lista_servicos,
        barbeiros=lista_barbeiros,
        disponibilidade=lista_disponibilidade,
        excecoes=lista_excecoes,
        agendamentos=lista_agendamentos,
        nome_cliente=session.get("nome", "")
    )


# ─── HISTÓRICO DO CLIENTE ─────────────────────────────────────────────────────

@app.route("/meus-agendamentos")
def meus_agendamentos():
    if "usuario_id" not in session or session.get("tipo") != "cliente":
        return redirect(url_for("login"))

    cliente_id = session["usuario_id"]
    try:
        conexao = obter_conexao()
        cursor = conexao.cursor(dictionary=True)
        cursor.execute("""
            SELECT a.id, a.data, a.horario, b.nome AS barbeiro
            FROM agendamento a
            JOIN barbeiro b ON b.id = a.barbeiro_id
            WHERE a.cliente_id = %s
            ORDER BY a.data DESC, a.horario DESC
        """, (cliente_id,))
        rows = cursor.fetchall()
        agendamentos = []
        for a in rows:
            cursor2 = conexao.cursor(dictionary=True)
            cursor2.execute("""
                SELECT s.nome, s.preco, s.duracao_min
                FROM agendamento_servicos asv
                JOIN servicos s ON s.id = asv.servico_id
                WHERE asv.agendamento_id = %s
            """, (a["id"],))
            servicos_ag = cursor2.fetchall()
            cursor2.close()
            agendamentos.append({
                "id": a["id"],
                "data": a["data"],
                "horario": fmt_time(a["horario"]),
                "barbeiro": a["barbeiro"],
                "servico": ", ".join([s["nome"] for s in servicos_ag]),
                "preco": sum(float(s["preco"]) for s in servicos_ag),
                "duracao": sum(s["duracao_min"] for s in servicos_ag)
            })

        hoje = datetime.date.today()
        futuros = [a for a in agendamentos if a["data"] >= hoje]
        passados = [a for a in agendamentos if a["data"] < hoje]

        cursor.close()
        conexao.close()
    except Exception as e:
        print(f"ERRO: {e}")
        futuros = []
        passados = []

    return render_template("meus_agendamentos.html",
                           futuros=futuros,
                           passados=passados,
                           nome_cliente=session.get("nome", ""))


# ─── PAINEL DO BARBEIRO ───────────────────────────────────────────────────────

@app.route("/barbeiro")
def painel_barbeiro():
    if "usuario_id" not in session or session.get("tipo") != "barbeiro":
        return redirect(url_for("login"))

    barbeiro_id = session["usuario_id"]
    try:
        conexao = obter_conexao()
        cursor = conexao.cursor(dictionary=True)

        cursor.execute("""
            SELECT a.id, a.data, a.horario, c.nome AS cliente
            FROM agendamento a
            JOIN cliente c ON c.id = a.cliente_id
            WHERE a.barbeiro_id = %s
            ORDER BY a.data DESC, a.horario DESC
        """, (barbeiro_id,))
        rows = cursor.fetchall()
        agendamentos = []
        for a in rows:
            cursor2 = conexao.cursor(dictionary=True)
            cursor2.execute("""
                SELECT s.nome, s.preco, s.duracao_min
                FROM agendamento_servicos asv
                JOIN servicos s ON s.id = asv.servico_id
                WHERE asv.agendamento_id = %s
            """, (a["id"],))
            servicos_ag = cursor2.fetchall()
            cursor2.close()
            agendamentos.append({
                "id": a["id"],
                "data": a["data"],
                "horario": fmt_time(a["horario"]),
                "cliente": a["cliente"],
                "servico": ", ".join([s["nome"] for s in servicos_ag]),
                "preco": sum(float(s["preco"]) for s in servicos_ag),
                "duracao_min": sum(s["duracao_min"] for s in servicos_ag)
            })

        hoje = datetime.date.today()
        futuros = [a for a in agendamentos if a["data"] >= hoje]
        passados = [a for a in agendamentos if a["data"] < hoje]

        cursor.execute("SELECT id, nome, `preco` AS preco, descricao, duracao_min FROM servicos")
        rows = cursor.fetchall()
        servicos = [{"id": s["id"], "nome": s["nome"], "preco": float(s["preco"]),
                     "descricao": s["descricao"], "duracao_min": s["duracao_min"]} for s in rows]

        cursor.close()
        conexao.close()
    except Exception as e:
        print(f"ERRO: {e}")
        futuros = []
        passados = []
        servicos = []

    return render_template("painel_barbeiro.html",
                           futuros=futuros,
                           passados=passados,
                           servicos=servicos,
                           nome_barbeiro=session.get("nome", ""),
                           session_barbeiro_id=barbeiro_id)  # ← novo


@app.route("/api/servico", methods=["POST"])
def api_adicionar_servico():
    if "usuario_id" not in session or session.get("tipo") != "barbeiro":
        return jsonify({"ok": False, "erro": "Não autorizado."}), 403

    dados = request.get_json()
    nome = dados.get("nome", "").strip()
    preco = dados.get("preco")
    descricao = dados.get("descricao", "").strip()
    duracao = dados.get("duracao_min")

    if not all([nome, preco, duracao]):
        return jsonify({"ok": False, "erro": "Preencha todos os campos obrigatórios."}), 400

    try:
        conexao = obter_conexao()
        cursor = conexao.cursor()
        cursor.execute(
            "INSERT INTO servicos (nome, `preco`, descricao, duracao_min) VALUES (%s, %s, %s, %s)",
            (nome, float(preco), descricao, int(duracao))
        )
        conexao.commit()
        novo_id = cursor.lastrowid
        cursor.close()
        conexao.close()
        return jsonify({"ok": True, "id": novo_id})
    except Exception as e:
        return jsonify({"ok": False, "erro": str(e)}), 500


@app.route("/api/servico/<int:sid>", methods=["DELETE"])
def api_deletar_servico(sid):
    if "usuario_id" not in session or session.get("tipo") != "barbeiro":
        return jsonify({"ok": False, "erro": "Não autorizado."}), 403
    try:
        conexao = obter_conexao()
        cursor = conexao.cursor()
        cursor.execute("DELETE FROM servicos WHERE id=%s", (sid,))
        conexao.commit()
        cursor.close()
        conexao.close()
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "erro": str(e)}), 500


# ─── AGENDAMENTO ──────────────────────────────────────────────────────────────

@app.route("/agendar", methods=["POST"])
def agendar():
    if "usuario_id" not in session or session.get("tipo") != "cliente":
        return jsonify({"ok": False, "erro": "Não autorizado."}), 403
    try:
        dados = request.get_json()
        nome = dados.get("nome", "").strip()
        barbeiro_id = dados.get("barbeiro_id")
        servico_id = dados.get("servico_id")
        data = dados.get("data")
        horario = dados.get("horario")

        if not all([nome, barbeiro_id, servico_id, data, horario]):
            return jsonify({"ok": False, "erro": "Dados incompletos."}), 400

        cliente_id = session["usuario_id"]

        conexao = obter_conexao()
        cursor = conexao.cursor(dictionary=True)

        cursor.execute(
            "SELECT id FROM agendamento WHERE barbeiro_id=%s AND data=%s AND horario=%s",
            (barbeiro_id, data, horario)
        )
        if cursor.fetchone():
            cursor.close(); conexao.close()
            return jsonify({"ok": False, "erro": "Horário já reservado."}), 409

        servico_ids = dados.get("servico_ids", [servico_id])

        cursor.execute(
            "INSERT INTO agendamento (cliente_id, barbeiro_id, data, horario) VALUES (%s, %s, %s, %s)",
            (cliente_id, barbeiro_id, data, horario)
        )
        conexao.commit()
        agendamento_id = cursor.lastrowid

        for sid in servico_ids:
            cursor.execute(
                "INSERT INTO agendamento_servicos (agendamento_id, servico_id) VALUES (%s, %s)",
                (agendamento_id, sid)
            )
        conexao.commit()
        cursor.close()
        conexao.close()
        return jsonify({"ok": True})

    except Exception as erro:
        print(f"ERRO ao agendar: {erro}")
        return jsonify({"ok": False, "erro": str(erro)}), 500

# ─── CANCELAMENTO DO AGENDAMENTO ───────────────────────────────────────────────────────

@app.route("/api/agendamento/<int:agendamento_id>", methods=["DELETE"])
def api_cancelar_agendamento(agendamento_id):
    if "usuario_id" not in session or session.get("tipo") != "barbeiro":
        return jsonify({"ok": False, "erro": "Não autorizado."}), 403

    barbeiro_id = session["usuario_id"]
    dados = request.get_json() or {}
    motivo = dados.get("motivo", "").strip()

    try:
        conexao = obter_conexao()
        cursor = conexao.cursor(dictionary=True)

        # Garante que o agendamento pertence a este barbeiro
        cursor.execute(
            "SELECT id FROM agendamento WHERE id=%s AND barbeiro_id=%s",
            (agendamento_id, barbeiro_id)
        )
        if not cursor.fetchone():
            cursor.close(); conexao.close()
            return jsonify({"ok": False, "erro": "Agendamento não encontrado."}), 404

        # Remove os serviços vinculados primeiro (FK)
        cursor.execute(
            "DELETE FROM agendamento_servicos WHERE agendamento_id=%s",
            (agendamento_id,)
        )
        # Remove o agendamento
        cursor.execute(
            "DELETE FROM agendamento WHERE id=%s",
            (agendamento_id,)
        )
        conexao.commit()
        cursor.close()
        conexao.close()
        return jsonify({"ok": True})

    except Exception as e:
        print(f"ERRO ao cancelar agendamento: {e}")
        return jsonify({"ok": False, "erro": str(e)}), 500

# ─── AGENDA DO BARBEIRO ───────────────────────────────────────────────────────

@app.route("/api/agenda/padrao", methods=["POST"])
def api_agenda_padrao():
    if "usuario_id" not in session or session.get("tipo") != "barbeiro":
        return jsonify({"ok": False, "erro": "Não autorizado."}), 403

    barbeiro_id = session["usuario_id"]
    dados = request.get_json()

    try:
        conexao = obter_conexao()
        cursor = conexao.cursor()
        cursor.execute("DELETE FROM disponibilidade WHERE barbeiro_id = %s", (barbeiro_id,))
        for d in dados.get("dias", []):
            if d.get("hora_inicio") and d.get("hora_fim"):
                cursor.execute(
                    "INSERT INTO disponibilidade (barbeiro_id, dia_semana, hora_inicio, hora_fim) "
                    "VALUES (%s, %s, %s, %s)",
                    (barbeiro_id, d["dia_semana"], d["hora_inicio"], d["hora_fim"])
                )
        conexao.commit()
        cursor.close()
        conexao.close()
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "erro": str(e)}), 500


@app.route("/api/agenda/excecao", methods=["POST"])
def api_agenda_excecao():
    if "usuario_id" not in session or session.get("tipo") != "barbeiro":
        return jsonify({"ok": False, "erro": "Não autorizado."}), 403

    barbeiro_id = session["usuario_id"]
    dados = request.get_json()
    datas       = dados.get("datas", [])
    hora_inicio = dados.get("hora_inicio") or None
    hora_fim    = dados.get("hora_fim") or None

    if not datas:
        return jsonify({"ok": False, "erro": "Nenhuma data informada."}), 400

    try:
        conexao = obter_conexao()
        cursor = conexao.cursor()
        for data in datas:
            cursor.execute(
                "INSERT INTO disponibilidade_excecao (barbeiro_id, data, hora_inicio, hora_fim) "
                "VALUES (%s, %s, %s, %s) "
                "ON DUPLICATE KEY UPDATE hora_inicio=%s, hora_fim=%s",
                (barbeiro_id, data, hora_inicio, hora_fim, hora_inicio, hora_fim)
            )
        conexao.commit()
        cursor.close()
        conexao.close()
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "erro": str(e)}), 500


@app.route("/api/agenda/excecao", methods=["DELETE"])
def api_agenda_excecao_del():
    if "usuario_id" not in session or session.get("tipo") != "barbeiro":
        return jsonify({"ok": False, "erro": "Não autorizado."}), 403

    barbeiro_id = session["usuario_id"]
    dados = request.get_json()
    datas = dados.get("datas", [])

    try:
        conexao = obter_conexao()
        cursor = conexao.cursor()
        for data in datas:
            cursor.execute(
                "DELETE FROM disponibilidade_excecao WHERE barbeiro_id=%s AND data=%s",
                (barbeiro_id, data)
            )
        conexao.commit()
        cursor.close()
        conexao.close()
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "erro": str(e)}), 500


@app.route("/api/agenda/<int:barbeiro_id>")
def api_agenda_get(barbeiro_id):
    if "usuario_id" not in session:
        return jsonify({"ok": False, "erro": "Não autorizado."}), 403

    mes = request.args.get("mes")
    try:
        conexao = obter_conexao()
        cursor = conexao.cursor(dictionary=True)

        # Padrão semanal
        cursor.execute(
            "SELECT dia_semana, hora_inicio, hora_fim FROM disponibilidade WHERE barbeiro_id=%s",
            (barbeiro_id,)
        )
        padrao = {}
        for r in cursor.fetchall():
            padrao[int(r["dia_semana"])] = {
                "hora_inicio": fmt_time(r["hora_inicio"]),
                "hora_fim":    fmt_time(r["hora_fim"])
            }

        excecoes = {}
        agendados = []
        if mes:
            ano, mo = mes.split('-')

            cursor.execute(
                "SELECT data, hora_inicio, hora_fim FROM disponibilidade_excecao "
                "WHERE barbeiro_id=%s AND YEAR(data)=%s AND MONTH(data)=%s",
                (barbeiro_id, ano, mo)
            )
            for r in cursor.fetchall():
                hi = fmt_time(r["hora_inicio"])
                hf = fmt_time(r["hora_fim"])
                excecoes[r["data"].strftime("%Y-%m-%d")] = None if hi is None else {"hora_inicio": hi, "hora_fim": hf}

            cursor.execute(
                "SELECT DISTINCT data FROM agendamento "
                "WHERE barbeiro_id=%s AND YEAR(data)=%s AND MONTH(data)=%s",
                (barbeiro_id, ano, mo)
            )
            agendados = [r["data"].strftime("%Y-%m-%d") for r in cursor.fetchall()]

        cursor.close()
        conexao.close()
        return jsonify({"ok": True, "padrao": padrao, "excecoes": excecoes, "agendados": agendados})
    except Exception as e:
        print(f"ERRO api_agenda_get: {e}")
        import traceback; traceback.print_exc()
        return jsonify({"ok": False, "erro": str(e)}), 500

if __name__ == "__main__":
    app.run( host="0.0.0.0",port=5000, debug=True)